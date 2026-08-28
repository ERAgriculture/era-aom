#!/usr/bin/env python3
"""Validate ADR 0052 source-disposition acceptance record."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECOMMENDATIONS = ROOT / "review/data-model-v3"
ACCEPTANCE = ROOT / "review/data-model-v4"

EXPECTED_HASHES = {
    "FIELD-KEY-COHORT": "9422667f8bd138c87fe3529f5acbb438e107c90e534e9bb5afae366c038f3ee8",
    "LOOKUP-BINDING-COHORT": "13c7927bfa8423132fd022f0aa9bbab83f0f0e74689e3edcc4fd794e8a26cfad",
}


def read_csv(directory: Path, name: str) -> list[dict[str, str]]:
    path = directory / name
    assert path.is_file(), f"Missing {path}"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


guided = read_csv(RECOMMENDATIONS, "guided_decision_recommendations.csv")
fields = read_csv(RECOMMENDATIONS, "field_key_disposition_recommendations.csv")
lookups = read_csv(RECOMMENDATIONS, "lookup_binding_disposition_recommendations.csv")
policy = read_csv(ACCEPTANCE, "policy_decision_approvals.csv")
cohorts = read_csv(ACCEPTANCE, "cohort_approvals.csv")
evidence = read_csv(ACCEPTANCE, "evidence_register.csv")
summary = json.loads((ACCEPTANCE / "acceptance_summary.json").read_text(encoding="utf-8"))

assert len(guided) == len(policy) == 8
assert {row["review_id"] for row in guided} == {row["review_id"] for row in policy}
assert {row["review_id"]: row["recommended_decision"] for row in guided} == {
    row["review_id"]: row["final_decision"] for row in policy
}
assert all(row["approval_status"] == "accepted" for row in policy + cohorts)
assert all(row["reviewer"] == "P. Steward" for row in policy + cohorts)
assert all(row["review_date"] == "2026-08-28" for row in policy + cohorts)
assert all(not row["human_decision"] for row in guided + fields + lookups)

assert len(fields) == 21
assert Counter(row["guided_disposition"] for row in fields) == {
    "consolidate-logical-field-with-round-profiles": 13,
    "hold-assign-table-or-retire": 1,
    "hold-classify-metadata-or-remove": 3,
    "hold-overlapping-duplicate-source-rows": 3,
    "hold-source-key-correction": 1,
}
assert Counter(row["source_edit_required"] for row in fields) == {"no": 13, "yes": 8}
assert len(lookups) == 41
assert Counter(row["guided_disposition"] for row in lookups) == {
    "hold-add-field-or-retire-lookup": 39,
    "hold-table-key-realignment-review": 2,
}
assert all(row["source_edit_required"] == "yes" for row in lookups)

assert len(cohorts) == 2
cohorts_by_id = {row["cohort_id"]: row for row in cohorts}
assert set(cohorts_by_id) == set(EXPECTED_HASHES)
for cohort_id, expected_hash in EXPECTED_HASHES.items():
    row = cohorts_by_id[cohort_id]
    artifact = (ACCEPTANCE / row["artifact"]).resolve()
    assert row["sha256"] == expected_hash == sha256(artifact)
    assert int(row["row_count"]) == len(read_csv(artifact.parent, artifact.name))
    assert row["final_decision"] == "accepted-as-recommended"

assert summary["adr_status"] == "Accepted"
assert summary["acceptance_scope"] == "source-dispositions"
assert summary["policy_decision_count"] == summary["policy_decisions_accepted"] == 8
assert summary["field_recommendation_count"] == summary["field_recommendations_accepted"] == 21
assert summary["profile_consolidations_approved"] == 13
assert summary["field_holds"] == 8
assert summary["lookup_recommendation_count"] == summary["lookup_recommendations_accepted"] == 41
assert summary["lookup_holds"] == 41
assert summary["source_edit_holds"] == 49
assert summary["source_disposition_policy_accepted"] is True
for key in (
    "canonical_workbook_modified",
    "stable_keys_allocated",
    "profiles_created",
    "bindings_created",
    "schema_regeneration_authorized",
    "release_authorized",
    "consumer_migration_authorized",
):
    assert summary[key] is False
assert len(evidence) == 5
assert all(row["supports"] and row["claim_boundary"] for row in evidence)

adr_text = (ROOT / "docs/decisions/0052-data-model-registry-and-shared-core-contract.md").read_text(encoding="utf-8")
adr_text_normalized = " ".join(adr_text.split())
assert "data-model-v4/README.md" in adr_text
assert "13 profile consolidations approved" in adr_text_normalized
assert "49 source-edit cases retained as holds" in adr_text_normalized
assert "data-model-v4/README.md" in (RECOMMENDATIONS / "README.md").read_text(encoding="utf-8")

print(
    "Validated ADR 0052 source-disposition acceptance: 8 policies, "
    "13 profile consolidations, and 49 source-edit holds"
)
