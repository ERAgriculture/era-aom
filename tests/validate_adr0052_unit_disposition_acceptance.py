#!/usr/bin/env python3
"""Validate ADR 0052 unit-disposition acceptance record."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECOMMENDATIONS = ROOT / "review/data-model-v5"
ACCEPTANCE = ROOT / "review/data-model-v6"
EXPECTED_HASHES = {
    "guided_decision_recommendations.json": "68b318366e620c6391ab66b966f9e96b4fc3f91b2d19d7eb2cca043dfdd6878a",
    "unit_disposition_recommendations.json": "d5d5ed94a8e3f8e66eab5c989abc5a124f0994cf533d1e9375327706ce42ecec",
}
EXPECTED_DISPOSITIONS = {
    "hold-basis-or-qualifier-model": 11,
    "hold-currency-and-basis-review": 3,
    "hold-currency-effective-context": 2,
    "hold-missing-value-source-correction": 2,
    "hold-non-unit-source-correction": 21,
    "hold-ratio-decomposition": 16,
    "hold-source-fragment-correction": 3,
    "hold-symbol-case-and-context-review": 8,
}


def read_json(directory: Path, name: str) -> object:
    path = directory / name
    assert path.is_file(), f"Missing {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


guided = read_json(RECOMMENDATIONS, "guided_decision_recommendations.json")
cases = read_json(RECOMMENDATIONS, "unit_disposition_recommendations.json")
policy = read_json(ACCEPTANCE, "policy_decision_approvals.json")
cohort = read_json(ACCEPTANCE, "cohort_approval.json")
evidence = read_json(ACCEPTANCE, "evidence_register.json")
summary = read_json(ACCEPTANCE, "acceptance_summary.json")
assert isinstance(guided, list)
assert isinstance(cases, list)
assert isinstance(policy, list)
assert isinstance(cohort, dict)
assert isinstance(evidence, list)
assert isinstance(summary, dict)

assert len(guided) == len(policy) == 12
assert {row["review_id"] for row in guided} == {row["review_id"] for row in policy}
assert {row["review_id"]: row["recommended_decision"] for row in guided} == {
    row["review_id"]: row["final_decision"] for row in policy
}
assert all(row["recommended_decision"] == row["final_decision"] for row in policy)
assert all(row["approval_status"] == "accepted" for row in policy)
assert all(row["reviewer"] == "P. Steward" for row in policy)
assert all(row["review_date"] == "2026-08-31" for row in policy)
assert all(row["conditions_or_holds"] for row in policy)

assert len(cases) == 66
assert Counter(row["recommended_disposition"] for row in cases) == EXPECTED_DISPOSITIONS
assert Counter(row["source_mapping_status"] for row in cases) == {
    "conflicting-canonical-label": 2,
    "unresolved": 64,
}
for field in (
    "canonical_unit_uri",
    "quantity_kind_uri",
    "conversion_rule",
    "human_decision",
    "reviewer",
    "review_date",
    "decision_note",
):
    assert all(not row[field] for row in cases)

assert cohort["cohort_id"] == "UNIT-DISPOSITION-COHORT"
assert cohort["final_decision"] == "accepted-as-recommended"
assert cohort["approval_status"] == "accepted"
assert cohort["reviewer"] == "P. Steward"
assert cohort["review_date"] == "2026-08-31"
artifacts = {Path(row["artifact"]).name: row for row in cohort["artifacts"]}
assert set(artifacts) == set(EXPECTED_HASHES)
for name, expected_hash in EXPECTED_HASHES.items():
    artifact = (ACCEPTANCE / artifacts[name]["artifact"]).resolve()
    assert artifacts[name]["sha256"] == expected_hash == sha256(artifact)
    records = json.loads(artifact.read_text(encoding="utf-8"))
    assert artifacts[name]["record_count"] == len(records)

assert summary["adr_status"] == "Accepted"
assert summary["acceptance_scope"] == "unit-dispositions"
assert summary["policy_decision_count"] == summary["policy_decisions_accepted"] == 12
assert summary["held_cases_accepted"] == 66
assert summary["unresolved_cases_accepted_as_holds"] == 64
assert summary["conflicting_cases_accepted_as_holds"] == 2
assert summary["unit_disposition_policy_accepted"] is True
for key in (
    "canonical_unit_mappings_created",
    "quantity_kind_mappings_created",
    "conversion_rules_created",
    "source_csv_modified",
    "source_workbook_modified",
    "schema_regeneration_authorized",
    "release_authorized",
    "consumer_migration_authorized",
    "spreadsheet_artifact_authored",
):
    assert summary[key] is False

assert len(evidence) == 5
assert all(row["supports"] and row["claim_boundary"] for row in evidence)

adr = (ROOT / "docs/decisions/0052-data-model-registry-and-shared-core-contract.md").read_text(encoding="utf-8")
assert "data-model-v6/README.md" in adr
assert "P. Steward accepted `UD-01` through `UD-12`" in adr
assert "data-model-v6/README.md" in (RECOMMENDATIONS / "README.md").read_text(encoding="utf-8")

print("Validated ADR 0052 unit acceptance: 12 decisions and 66 retained holds")
