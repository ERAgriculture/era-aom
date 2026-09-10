#!/usr/bin/env python3
"""Validate ADR 0054 cross-repository implementation plan."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/data-model-v9"
EXPECTED_REPOSITORIES = {
    "ERAgriculture/era-data-pipeline": "4df7f01e3cd3a64e22086b16460dc3bf3825b479",
    "ERAgriculture/era-data": "799ace4f0322cda103781060004816b346bdca1e",
    "ERAgriculture/era-aom": "2739057b8a0141e77ce2796f918316b7a0e8ee59",
    "ERAgriculture/eragri": "c6594e1f2769cb6fff6d82a2bf66f6785c70f546",
    "ERAgriculture/era-docs": "afe9af7a9384871d38619a77bc733b0cb05ee778",
    "ERAgriculture/era-program": "c9cdf56766a18dc9bf9e325ceffe91c5ea1db83d",
}
EXPECTED_SOURCE_HASHES = {
    ("ERAgriculture/era-data-pipeline", "R/vocab/build_model_schema.R"): "495d2a8372dd684e7804d128a915eb57895e13d268fff660c72b4258c32d614c",
    ("ERAgriculture/era-data-pipeline", "config/semantic/era-aom-phase2-contract.csv"): "03ed5c8a0e01123207efc578b65388c78bace41d6f8e9088ad13d4d3c8444506",
    ("ERAgriculture/era-data", "vocab/version=2026.1/era_data_model.schema.json"): "3235f0cdf8c04c460e2a4416bc8d10fd462a0ffb2028fa0c5cd7a215f1133fe7",
    ("ERAgriculture/era-data", "vocab/version=2026.1/vocab_manifest.json"): "95e2eb9008c59204b948082d3e4a7bd3414e1eb3c66f8e47c05156639accb3fd",
    ("ERAgriculture/era-data", "schemas/era_compiled.schema.json"): "a06d2b18da35d5a56004e1abf918df42be1b9d0f0cffe8b4aec53a878794507f",
    ("ERAgriculture/era-data", "schemas/era_compiled_ls.schema.json"): "6979df8efd8c673e41a75cf0ab847d28cda1ab81b4b19eba3cd7a0d78e525507",
    ("ERAgriculture/era-aom", "docs/decisions/0052-data-model-registry-and-shared-core-contract.md"): "86c98d733b35d1e2ed5554380d552780162da69b5028245e185107126bc78bac",
    ("ERAgriculture/era-aom", "review/data-model-v4/acceptance_summary.json"): "162af249dad59f04a2ff2d85f83d6003610271da990f164ef5628aeb1a100cfa",
    ("ERAgriculture/era-aom", "review/data-model-v6/acceptance_summary.json"): "5098c50ceb31b91efe0d1d9481fe58e69c2bdb2b25996a74319fd5699e1e74c5",
    ("ERAgriculture/era-aom", "review/data-model-v8/acceptance_summary.json"): "65cecef9acd335e74c7093412d1fcebf020ea8fb6a23dc7033884241a3df2442",
    ("ERAgriculture/era-aom", "review/data-model-v8/cohort_approval.json"): "165f2820a2099817f86e4b975fcdf5beca5f320ea9c5ff7d7bb4494784d8ed07",
    ("ERAgriculture/eragri", "data/ERA.Compiled.rda"): "00318de7341cad728e991ab0bf536fe68aeaeff4f732b7fde0b06e5f68e92091",
    ("ERAgriculture/eragri", "data/ERACompiledFields.rda"): "85ff22c5c595888899b0c3c5cbfaab3fe1b377dfedcb52fdb0dd44d322aaffd9",
    ("ERAgriculture/eragri", "R/data.R"): "c0c6b0bd656ae2d86286bc6533422bcbbc604662579182c6b6a2a5b77025e6d2",
    ("ERAgriculture/eragri", "R/data-extra-docs.R"): "37b470c7111d685cc0619b899dd06130ee335dc1abddd56047f7030189132838",
    ("ERAgriculture/era-docs", "chapters/06-data-model-vocab.qmd"): "f012cdf85f523cbedf85164eea9254aa5e8773f2f69672ad9ad1e086b920b819",
}


def read_csv(name: str) -> list[dict[str, str]]:
    path = REVIEW / name
    assert path.is_file(), f"Missing {path}"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(name: str) -> object:
    path = REVIEW / name
    assert path.is_file(), f"Missing {path}"
    return json.loads(path.read_text(encoding="utf-8"))


snapshot = read_json("source_snapshot.json")
repositories = read_csv("repository_contracts.csv")
artifacts = read_csv("artifact_contracts.csv")
waves = read_csv("implementation_waves.csv")
constraints = read_csv("governance_constraints.csv")
authorities = read_csv("authority_comparison.csv")
evidence = read_csv("evidence_register.csv")
decisions = read_json("guided_decision_recommendations.json")
summary = read_json("implementation_plan_summary.json")

assert isinstance(snapshot, dict)
assert isinstance(decisions, list)
assert isinstance(summary, dict)
assert snapshot["status"] == "read-only-cross-repository-evidence"
assert snapshot["captured_on"] == "2026-09-09"
assert len(snapshot["repositories"]) == len(repositories) == 6
assert all(row["clean"] is True for row in snapshot["repositories"])
assert all(re.fullmatch(r"[0-9a-f]{40}", row["commit"]) for row in snapshot["repositories"])
assert {row["repository"]: row["commit"] for row in snapshot["repositories"]} == EXPECTED_REPOSITORIES
assert len(snapshot["sources"]) == len(evidence) == 16
assert all(re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) for row in snapshot["sources"])
assert {
    (row["repository"], row["path"]): row["sha256"]
    for row in snapshot["sources"]
} == EXPECTED_SOURCE_HASHES
assert {row["source_sha256"] for row in evidence} == {
    row["sha256"] for row in snapshot["sources"]
}
assert all(row["claim_boundary"] for row in evidence)
assert [row["evidence_id"] for row in evidence] == [f"EV-{index:02d}" for index in range(1, 17)]

assert {row["repository"] for row in repositories} == {
    "ERAgriculture/era-data-pipeline",
    "ERAgriculture/era-data",
    "ERAgriculture/era-aom",
    "ERAgriculture/eragri",
    "ERAgriculture/era-docs",
    "ERAgriculture/era-program",
}
assert [row["repository_id"] for row in repositories] == [f"RP-{index:02d}" for index in range(1, 7)]
assert all(row["input_contract"] and row["output_contract"] for row in repositories)
assert all(row["implementation_boundary"] and row["completion_evidence"] for row in repositories)

assert len(artifacts) == 14
assert [row["artifact_id"] for row in artifacts] == [f"AC-{index:02d}" for index in range(1, 15)]
assert {row["artifact"] for row in artifacts} == {
    "source_snapshot",
    "tables",
    "fields",
    "field_profiles",
    "value_sets",
    "value_set_members",
    "field_value_sets",
    "unit_mappings",
    "semantic_bindings",
    "product_profiles",
    "product_fields",
    "consumer_compatibility",
    "release_manifest",
    "catalog_entry",
}
assert all(row["primary_key"] and row["required_content"] and row["release_gate"] for row in artifacts)

assert len(waves) == 7
assert [row["wave_id"] for row in waves] == [f"IW-{index:02d}" for index in range(7)]
assert waves[0]["depends_on"] == "ADR 0052 and accepted v4, v6, v8 cohorts"
assert all(row["entry_gate"] and row["exit_gate"] and row["rollback"] for row in waves)
assert "v2026.1 unchanged" in waves[2]["rollback"]
assert "issues 27, 21, then 17" in waves[6]["exit_gate"]

assert len(constraints) == 11
assert [row["constraint_id"] for row in constraints] == [f"GC-{index:02d}" for index in range(1, 12)]
counts = {row["constraint_id"]: int(row["case_count"]) for row in constraints}
assert counts == {
    "GC-01": 13,
    "GC-02": 8,
    "GC-03": 41,
    "GC-04": 66,
    "GC-05": 138,
    "GC-06": 44,
    "GC-07": 0,
    "GC-08": 1,
    "GC-09": 0,
    "GC-10": 1,
    "GC-11": 0,
}
assert Counter(row["disposition"] for row in constraints)["hold"] == 3
assert all(row["implementation_rule"] and row["release_effect"] for row in constraints)

assert len(authorities) == 6
assert all(row["url"] and row["supports"] and row["limitation"] for row in authorities)
assert len(decisions) == 12
assert {row["review_id"] for row in decisions} == {f"RI-{index:02d}" for index in range(1, 13)}
assert all(row["recommendation_status"] == "proposed" for row in decisions)
assert all(row["conditions_or_holds"] for row in decisions)
assert all(
    not row[field]
    for row in decisions
    for field in ("human_decision", "reviewer", "review_date", "decision_note")
)

assert summary == {
    "approved_profile_consolidation_count": 13,
    "artifact_contract_count": 14,
    "consumer_difference_hold_count": 44,
    "consumer_migration_authorized": False,
    "documentation_consumer_modified": False,
    "evidence_record_count": 16,
    "field_hold_count": 8,
    "governance_constraint_count": 11,
    "guided_decision_count": 12,
    "human_decision_recorded": False,
    "implementation_wave_count": 7,
    "lookup_hold_count": 41,
    "package_modified": False,
    "product_field_evidence_hold_count": 138,
    "programme_issue_closure_authorized": False,
    "registry_generated": False,
    "release_authorized": False,
    "repository_count": 6,
    "semantic_bindings_modified": False,
    "source_repository_modified": False,
    "source_workbook_modified": False,
    "stable_identifiers_allocated": False,
    "status": "recommendation-only",
    "tracking_issue_count": 3,
    "unit_hold_count": 66,
}

for issue in snapshot["tracking_issues"]:
    assert issue["state"] == "OPEN"
    assert issue["number"] in {17, 21, 27}
    assert issue["url"].endswith(f"/{issue['number']}")

guided = (REVIEW / "GUIDED_IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
readme = (REVIEW / "README.md").read_text(encoding="utf-8")
method = (ROOT / "docs/methods/cross-repository-registry-implementation-planning.md").read_text(encoding="utf-8")
adr = (ROOT / "docs/decisions/0054-cross-repository-data-model-registry-implementation-plan.md").read_text(encoding="utf-8")
assert guided.count("| `RI-") == 12
assert guided.count("| `IW-") == 7
assert "recommendation-only" in readme.lower()
assert "Never read implementation success" in method
assert "Status: Proposed" in adr
assert "## Authority comparison" in adr
assert "## Evidence" in adr
assert "does not allocate" in adr

for path in (
    REVIEW / "repository_contracts.csv",
    REVIEW / "artifact_contracts.csv",
    REVIEW / "implementation_waves.csv",
    REVIEW / "governance_constraints.csv",
    REVIEW / "authority_comparison.csv",
    REVIEW / "evidence_register.csv",
    REVIEW / "guided_decision_recommendations.json",
    REVIEW / "implementation_plan_summary.json",
    REVIEW / "GUIDED_IMPLEMENTATION_PLAN.md",
):
    assert hashlib.sha256(path.read_bytes()).hexdigest()

print("Validated ADR 0054 implementation plan: 6 repositories, 14 artifacts, 7 waves")
