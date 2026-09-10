#!/usr/bin/env python3
"""Validate ADR 0054 registry implementation-plan acceptance."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECOMMENDATIONS = ROOT / "review/data-model-v9"
ACCEPTANCE = ROOT / "review/data-model-v10"
EXPECTED_HASHES = {
    "guided_decision_recommendations.json": "bc3433ffa5b9e2aee8e2181016f06b5b56b2eb0a9046bd82dadd8ebe2d226385",
    "artifact_contracts.csv": "54f8f0fa5a58d58c5cf94979e3623d03122d673ca977dc1741ee9456e92ae06e",
    "implementation_waves.csv": "ddeb165cf38ebad3672acae706d5aa912848a6d2d882435c4ef6e34bb7d44f1c",
    "governance_constraints.csv": "0802aaa57b84bd518b13eee53044003e78acb727af7edf1f7323c1fa84e62d57",
}
EXPECTED_RECORD_COUNTS = {
    "guided_decision_recommendations.json": 12,
    "artifact_contracts.csv": 14,
    "implementation_waves.csv": 7,
    "governance_constraints.csv": 11,
}
SOURCE_SNAPSHOT_SHA256 = (
    "fc4864cd508dc22d7708e2b76e60a83693933125b42d73d28c9a0dd1a1d95b8f"
)


def read_json(directory: Path, name: str) -> object:
    path = directory / name
    assert path.is_file(), f"Missing {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def read_records(path: Path) -> list[object]:
    if path.suffix == ".json":
        records = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(records, list)
        return records
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


guided = read_json(RECOMMENDATIONS, "guided_decision_recommendations.json")
policy = read_json(ACCEPTANCE, "policy_decision_approvals.json")
cohort = read_json(ACCEPTANCE, "cohort_approval.json")
evidence = read_json(ACCEPTANCE, "evidence_register.json")
summary = read_json(ACCEPTANCE, "acceptance_summary.json")
proposal_summary = read_json(RECOMMENDATIONS, "implementation_plan_summary.json")
assert isinstance(guided, list)
assert isinstance(policy, list)
assert isinstance(cohort, dict)
assert isinstance(evidence, list)
assert isinstance(summary, dict)
assert isinstance(proposal_summary, dict)

assert len(guided) == len(policy) == 12
guided_by_id = {row["review_id"]: row for row in guided}
policy_by_id = {row["review_id"]: row for row in policy}
assert set(guided_by_id) == set(policy_by_id) == {
    f"RI-{index:02d}" for index in range(1, 13)
}
for review_id, approval in policy_by_id.items():
    recommendation = guided_by_id[review_id]
    assert approval["accepted_recommendation"] == recommendation["recommendation"]
    assert approval["conditions_or_holds"] == recommendation["conditions_or_holds"]
    assert approval["final_decision"] == "accepted-as-recommended"
    assert approval["approval_status"] == "accepted"
    assert approval["reviewer"] == "P. Steward"
    assert approval["review_date"] == "2026-09-10"

assert cohort["cohort_id"] == "REGISTRY-IMPLEMENTATION-PLAN-COHORT"
assert cohort["final_decision"] == "accepted-as-recommended"
assert cohort["approval_status"] == "accepted"
assert cohort["reviewer"] == "P. Steward"
assert cohort["review_date"] == "2026-09-10"
assert cohort["recommendation_commit"] == (
    "9db1e26a87a23db72328e0b9136a0cdba612abd6"
)
assert cohort["source_snapshot_sha256"] == SOURCE_SNAPSHOT_SHA256
assert sha256(RECOMMENDATIONS / "source_snapshot.json") == SOURCE_SNAPSHOT_SHA256
artifacts = {Path(row["artifact"]).name: row for row in cohort["artifacts"]}
assert set(artifacts) == set(EXPECTED_HASHES)
for name, expected_hash in EXPECTED_HASHES.items():
    artifact = (ACCEPTANCE / artifacts[name]["artifact"]).resolve()
    assert artifacts[name]["sha256"] == expected_hash == sha256(artifact)
    assert artifacts[name]["record_count"] == EXPECTED_RECORD_COUNTS[name]
    assert len(read_records(artifact)) == EXPECTED_RECORD_COUNTS[name]

assert proposal_summary["status"] == "recommendation-only"
assert proposal_summary["human_decision_recorded"] is False
assert proposal_summary["stable_identifiers_allocated"] is False
assert summary["adr_status"] == "Accepted"
assert summary["acceptance_scope"] == "cross-repository-registry-implementation-plan"
assert summary["policy_decision_count"] == 12
assert summary["policy_decisions_accepted"] == 12
assert summary["repository_contract_count"] == 6
assert summary["artifact_contract_count"] == 14
assert summary["artifact_contracts_accepted"] == 14
assert summary["implementation_wave_count"] == 7
assert summary["implementation_waves_accepted"] == 7
assert summary["governance_constraint_count"] == 11
assert summary["governance_constraints_accepted"] == 11
assert summary["approved_profile_consolidation_count"] == 13
assert summary["field_hold_count"] == 8
assert summary["lookup_hold_count"] == 41
assert summary["unit_hold_count"] == 66
assert summary["product_field_evidence_hold_count"] == 138
assert summary["consumer_difference_hold_count"] == 44
for key in (
    "canonical_source_authority_retained",
    "immutable_candidate_policy_accepted",
    "issue_closure_order_accepted",
    "opaque_append_only_identifier_policy_accepted",
    "release_based_rollback_accepted",
):
    assert summary[key] is True
for key in (
    "consumer_migration_authorized",
    "documentation_consumer_modified",
    "package_modified",
    "programme_issue_closure_authorized",
    "registry_generated",
    "release_authorized",
    "semantic_bindings_modified",
    "source_repository_modified",
    "source_workbook_modified",
    "stable_identifiers_allocated",
):
    assert summary[key] is False

assert len(evidence) == 6
assert all(row["supports"] and row["claim_boundary"] for row in evidence)

readme = (ACCEPTANCE / "README.md").read_text(encoding="utf-8")
assert "all 12 registry implementation recommendations accepted" in readme
assert "does not allocate stable identifiers" in readme

adr = (
    ROOT
    / "docs/decisions/0054-cross-repository-data-model-registry-implementation-plan.md"
).read_text(encoding="utf-8")
assert "Status: Accepted" in adr
assert "Accepted: 2026-09-10 by P. Steward" in adr
assert "data-model-v10/README.md" in adr
assert "P. Steward accepted `RI-01` through `RI-12`" in adr
assert "No stable identifier was allocated" in adr

print(
    "Validated ADR 0054 acceptance: "
    "12 decisions, 14 artifacts, 7 waves, and 11 constraints"
)
