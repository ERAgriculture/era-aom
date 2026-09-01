#!/usr/bin/env python3
"""Validate recommendation-only ADR 0052 product-contract review."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/data-model-v7"
DIFFS = ROOT / "review/data-model-v1/consumer_contract_diffs.csv"
EXPECTED_HASHES = {
    "agronomy_schema": "a06d2b18da35d5a56004e1abf918df42be1b9d0f0cffe8b4aec53a878794507f",
    "livestock_schema": "6979df8efd8c673e41a75cf0ab847d28cda1ab81b4b19eba3cd7a0d78e525507",
    "package_data": "00318de7341cad728e991ab0bf536fe68aeaeff4f732b7fde0b06e5f68e92091",
    "package_dictionary": "85ff22c5c595888899b0c3c5cbfaab3fe1b377dfedcb52fdb0dd44d322aaffd9",
}
EXPECTED_FIELD_COUNTS = {
    "hold-author-missing-product-documentation": 7,
    "hold-published-only-release-lineage": 2,
    "hold-review-exact-dictionary-candidate": 101,
    "hold-review-explicit-alias-candidate": 2,
    "hold-review-pattern-expansion-candidate": 26,
}
EXPECTED_DIFFERENCE_COUNTS = {
    "hold-dictionary-only-retirement-review": 1,
    "hold-explicit-alias-definition-review": 2,
    "hold-package-only-release-provenance": 1,
    "hold-pattern-alias-definition-review": 2,
    "hold-published-only-release-provenance": 2,
    "hold-review-explicit-alias-candidate": 2,
    "hold-review-pattern-expansion-candidate": 26,
    "hold-undocumented-package-field": 8,
}


def read_json(name: str) -> object:
    path = REVIEW / name
    assert path.is_file(), f"Missing {path}"
    return json.loads(path.read_text(encoding="utf-8"))


snapshot = read_json("source_snapshot.json")
fields = read_json("product_field_recommendations.json")
differences = read_json("consumer_difference_recommendations.json")
guided = read_json("guided_decision_recommendations.json")
authorities = read_json("authority_comparison.json")
evidence = read_json("evidence_register.json")
summary = read_json("disposition_summary.json")
assert isinstance(snapshot, dict)
assert isinstance(fields, list)
assert isinstance(differences, list)
assert isinstance(guided, list)
assert isinstance(authorities, list)
assert isinstance(evidence, list)
assert isinstance(summary, dict)

sources = snapshot["sources"]
assert snapshot["status"] == "read-only-source-evidence"
assert snapshot["source_repositories"] == [
    {
        "repository": "ERAgriculture/era-data",
        "commit": "799ace4f0322cda103781060004816b346bdca1e",
        "clean": True,
    },
    {
        "repository": "ERAgriculture/eragri",
        "commit": "c6594e1f2769cb6fff6d82a2bf66f6785c70f546",
        "clean": True,
    },
]
for source_name, expected_hash in EXPECTED_HASHES.items():
    assert sources[source_name]["sha256"] == expected_hash
assert sources["agronomy_schema"]["column_count"] == 138
assert sources["livestock_schema"]["column_count"] == 138
assert sources["package_data"]["column_count"] == 137
assert sources["package_dictionary"]["row_count"] == 106

agronomy = sources["agronomy_schema"]["columns"]
livestock = sources["livestock_schema"]["columns"]
agronomy_types = {row["name"]: row["physical_type"] for row in agronomy}
livestock_types = {row["name"]: row["physical_type"] for row in livestock}
assert agronomy_types == livestock_types
assert len(agronomy_types) == len(livestock_types) == 138
assert sum(
    first["name"] != second["name"] for first, second in zip(agronomy, livestock)
) == 33
assert all(not row["description"] for row in agronomy + livestock)

assert len(fields) == 138
assert [row["field_name"] for row in fields] == [row["name"] for row in agronomy]
assert Counter(row["recommended_disposition"] for row in fields) == EXPECTED_FIELD_COUNTS
assert sum(row["package_data_present"] for row in fields) == 136
assert sum(not row["same_schema_position"] for row in fields) == 33
assert all(row["physical_type_match"] for row in fields)
assert all(row["recommendation_status"] == "proposed" for row in fields)
assert [row["field_id"] for row in fields] == [f"PF-{index:03d}" for index in range(1, 139)]
assert all(
    row["dictionary_candidate_description"]
    for row in fields
    if row["dictionary_candidate_kind"] != "none"
)
assert {row["field_name"] for row in fields if row["recommended_disposition"] == "hold-published-only-release-lineage"} == {"C14", "T14"}
assert {row["field_name"] for row in fields if row["recommended_disposition"] == "hold-author-missing-product-documentation"} == {
    "Mean.Error.Type",
    "MeanC.Error",
    "MeanT.Error",
    "Mulch.Code",
    "Partial.Outcome.Code",
    "Rep.Animals",
    "Tree.Feed",
}
for field_name in (
    "approved_description",
    "approved_logical_type",
    "approved_derivation",
    "approved_unit_or_basis",
    "approved_controlled_values",
    "human_decision",
    "reviewer",
    "review_date",
    "decision_note",
):
    assert all(not row[field_name] for row in fields)

with DIFFS.open(encoding="utf-8", newline="") as handle:
    source_differences = list(csv.DictReader(handle))
assert len(source_differences) == len(differences) == 44
assert {
    (row["comparison"], row["side"], row["identifier"])
    for row in source_differences
} == {
    (row["comparison"], row["side"], row["identifier"])
    for row in differences
}
assert Counter(row["recommended_disposition"] for row in differences) == EXPECTED_DIFFERENCE_COUNTS
assert all(row["recommendation_status"] == "proposed" for row in differences)
assert [row["difference_id"] for row in differences] == [f"CD-{index:03d}" for index in range(1, 45)]
assert all(
    not row[field_name]
    for row in differences
    for field_name in ("human_decision", "reviewer", "review_date", "decision_note")
)

assert len(guided) == 12
assert {row["review_id"] for row in guided} == {f"PC-{index:02d}" for index in range(1, 13)}
assert all(row["recommendation_status"] == "proposed" for row in guided)
assert all(row["conditions_or_holds"] for row in guided)
assert all(not row["human_decision"] for row in guided)
assert len(authorities) == 6
assert all(row["url"] and row["supports"] and row["limitation"] for row in authorities)
assert len(evidence) == 10
assert all(row["supports"] and row["claim_boundary"] for row in evidence)
assert all(re.fullmatch(r"[0-9a-f]{64}", row["source_sha256"]) for row in evidence)

assert summary["status"] == "recommendation-only"
assert summary["product_field_count"] == 138
assert summary["shared_schema_name_count"] == 138
assert summary["shared_schema_type_match_count"] == 138
assert summary["schema_order_difference_count"] == 33
assert summary["blank_published_description_count"] == 276
assert summary["package_data_field_count"] == 137
assert summary["package_dictionary_row_count"] == 106
assert summary["schema_package_shared_field_count"] == 136
assert summary["schema_package_shared_order_difference_count"] == 130
assert summary["product_field_disposition_counts"] == EXPECTED_FIELD_COUNTS
assert summary["consumer_difference_count"] == 44
assert summary["consumer_difference_disposition_counts"] == EXPECTED_DIFFERENCE_COUNTS
assert summary["guided_decision_count"] == 12
assert summary["human_decision_recorded"] is False
for key in (
    "approved_field_documentation_created",
    "field_identity_mappings_created",
    "source_repository_modified",
    "source_workbook_modified",
    "schema_modified",
    "package_modified",
    "documentation_consumer_modified",
    "release_authorized",
    "consumer_migration_authorized",
    "spreadsheet_artifact_authored",
):
    assert summary[key] is False

readme = (REVIEW / "README.md").read_text(encoding="utf-8")
method = (REVIEW / "METHOD.md").read_text(encoding="utf-8")
guided_markdown = (REVIEW / "GUIDED_PRODUCT_CONTRACT_RECOMMENDATIONS.md").read_text(encoding="utf-8")
assert "human decision pending" in readme
assert "No lexical match" in method
assert guided_markdown.count("| `PC-") == 12

adr = (ROOT / "docs/decisions/0052-data-model-registry-and-shared-core-contract.md").read_text(encoding="utf-8")
assert "data-model-v7/README.md" in adr
assert "Thirty-three field positions" in " ".join(adr.split())

print("Validated ADR 0052 product-contract review: 138 fields and 44 differences")
