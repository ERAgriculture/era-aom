#!/usr/bin/env python3
"""Validate ADR 0052 product-contract acceptance record."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECOMMENDATIONS = ROOT / "review/data-model-v7"
ACCEPTANCE = ROOT / "review/data-model-v8"
EXPECTED_HASHES = {
    "guided_decision_recommendations.json": "310141c90ced81901a110adb4d26e61541f7027367a7b83160b09be2965ee8ae",
    "product_field_recommendations.json": "44a5dad5ef19ea680fd0aa9f001232e22b2e1600723a8b0a3291956aacf111ee",
    "consumer_difference_recommendations.json": "3432c591f99f87d1252247f0060c50a9f793411b5a0fced9e189a589fea61b47",
}
SOURCE_SNAPSHOT_SHA256 = (
    "631fa3e461d39c9a5f4dced53363ac2453dae63f8388a762e0098f091602548a"
)
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


def read_json(directory: Path, name: str) -> object:
    path = directory / name
    assert path.is_file(), f"Missing {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


guided = read_json(RECOMMENDATIONS, "guided_decision_recommendations.json")
fields = read_json(RECOMMENDATIONS, "product_field_recommendations.json")
differences = read_json(
    RECOMMENDATIONS, "consumer_difference_recommendations.json"
)
policy = read_json(ACCEPTANCE, "policy_decision_approvals.json")
cohort = read_json(ACCEPTANCE, "cohort_approval.json")
evidence = read_json(ACCEPTANCE, "evidence_register.json")
summary = read_json(ACCEPTANCE, "acceptance_summary.json")
assert isinstance(guided, list)
assert isinstance(fields, list)
assert isinstance(differences, list)
assert isinstance(policy, list)
assert isinstance(cohort, dict)
assert isinstance(evidence, list)
assert isinstance(summary, dict)

assert len(guided) == len(policy) == 12
guided_by_id = {row["review_id"]: row for row in guided}
policy_by_id = {row["review_id"]: row for row in policy}
assert set(guided_by_id) == set(policy_by_id) == {
    f"PC-{index:02d}" for index in range(1, 13)
}
for review_id, approval in policy_by_id.items():
    recommendation = guided_by_id[review_id]
    assert approval["accepted_recommendation"] == recommendation["recommendation"]
    assert approval["conditions_or_holds"] == recommendation["conditions_or_holds"]
    assert approval["final_decision"] == "accepted-as-recommended"
    assert approval["approval_status"] == "accepted"
    assert approval["reviewer"] == "P. Steward"
    assert approval["review_date"] == "2026-09-01"

assert len(fields) == 138
assert (
    Counter(row["recommended_disposition"] for row in fields)
    == EXPECTED_FIELD_COUNTS
)
assert all(row["recommendation_status"] == "proposed" for row in fields)
assert all(
    not row[field]
    for row in fields
    for field in (
        "approved_description",
        "approved_logical_type",
        "approved_derivation",
        "approved_unit_or_basis",
        "approved_controlled_values",
        "human_decision",
        "reviewer",
        "review_date",
        "decision_note",
    )
)

assert len(differences) == 44
assert (
    Counter(row["recommended_disposition"] for row in differences)
    == EXPECTED_DIFFERENCE_COUNTS
)
assert all(row["recommendation_status"] == "proposed" for row in differences)
assert all(
    not row[field]
    for row in differences
    for field in ("human_decision", "reviewer", "review_date", "decision_note")
)

assert cohort["cohort_id"] == "PRODUCT-CONTRACT-COHORT"
assert cohort["final_decision"] == "accepted-as-recommended"
assert cohort["approval_status"] == "accepted"
assert cohort["reviewer"] == "P. Steward"
assert cohort["review_date"] == "2026-09-01"
assert cohort["recommendation_commit"] == (
    "d52142b845925ab1d563988ece2eca1e6741b0b7"
)
assert cohort["source_snapshot_sha256"] == SOURCE_SNAPSHOT_SHA256
assert sha256(RECOMMENDATIONS / "source_snapshot.json") == SOURCE_SNAPSHOT_SHA256
artifacts = {Path(row["artifact"]).name: row for row in cohort["artifacts"]}
assert set(artifacts) == set(EXPECTED_HASHES)
for name, expected_hash in EXPECTED_HASHES.items():
    artifact = (ACCEPTANCE / artifacts[name]["artifact"]).resolve()
    assert artifacts[name]["sha256"] == expected_hash == sha256(artifact)
    records = json.loads(artifact.read_text(encoding="utf-8"))
    assert artifacts[name]["record_count"] == len(records)

assert summary["adr_status"] == "Accepted"
assert summary["acceptance_scope"] == "product-contract-recommendations"
assert summary["policy_decision_count"] == 12
assert summary["policy_decisions_accepted"] == 12
assert summary["product_field_recommendations_accepted"] == 138
assert summary["consumer_difference_recommendations_accepted"] == 44
assert summary["product_field_disposition_counts"] == EXPECTED_FIELD_COUNTS
assert (
    summary["consumer_difference_disposition_counts"]
    == EXPECTED_DIFFERENCE_COUNTS
)
assert summary["separate_ordered_product_profiles_accepted"] is True
assert summary["complete_field_contract_requirement_accepted"] is True
assert summary["package_compatibility_requirement_accepted"] is True
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

assert len(evidence) == 6
assert all(row["supports"] and row["claim_boundary"] for row in evidence)

readme = (ACCEPTANCE / "README.md").read_text(encoding="utf-8")
recommendation_readme = (RECOMMENDATIONS / "README.md").read_text(
    encoding="utf-8"
)
assert "all 12 product-contract governance recommendations accepted" in readme
assert "data-model-v8" in recommendation_readme

adr = (
    ROOT / "docs/decisions/0052-data-model-registry-and-shared-core-contract.md"
).read_text(encoding="utf-8")
assert "data-model-v8/README.md" in adr
assert "P. Steward accepted `PC-01` through `PC-12`" in adr
assert (
    "All 138 field dispositions and all 44 consumer-difference dispositions"
    in " ".join(adr.split())
)

print(
    "Validated ADR 0052 product acceptance: "
    "12 decisions, 138 fields, and 44 differences"
)
