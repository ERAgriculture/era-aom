#!/usr/bin/env python3
"""Validate ADR 0053 human acceptance record."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECOMMENDATIONS = ROOT / "review/crop-foundation-v2"
ACCEPTANCE = ROOT / "review/crop-foundation-v3"


def read_csv(directory: Path, name: str) -> list[dict[str, str]]:
    path = directory / name
    assert path.is_file(), f"Missing {path}"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


summary = json.loads((ACCEPTANCE / "acceptance_summary.json").read_text(encoding="utf-8"))
recommendations = read_csv(RECOMMENDATIONS, "guided_decision_recommendations.csv")
approvals = read_csv(ACCEPTANCE, "guided_decision_approvals.csv")
correction_proposals = read_csv(RECOMMENDATIONS, "economic_source_correction_proposals.csv")
correction_approvals = read_csv(ACCEPTANCE, "source_correction_approvals.csv")
mapping_dispositions = read_csv(RECOMMENDATIONS, "external_mapping_dispositions.csv")
energy_holds = read_csv(RECOMMENDATIONS, "energy_module_holds.csv")
evidence = read_csv(ACCEPTANCE, "evidence_register.csv")

expected_review_ids = {f"GR-{number:02d}" for number in range(1, 13)}
assert len(approvals) == 12
assert {row["review_id"] for row in approvals} == expected_review_ids
assert {row["review_id"] for row in recommendations} == expected_review_ids
assert all(row["approval_status"] == "accepted" for row in approvals)
assert all(row["reviewer"] == "P. Steward" for row in approvals)
assert all(row["review_date"] == "2026-08-28" for row in approvals)
assert {
    row["review_id"]: row["recommended_decision"] for row in approvals
} == {
    row["review_id"]: row["recommended_decision"] for row in recommendations
}

assert len(correction_approvals) == len(correction_proposals) == 8
assert {row["source_id"] for row in correction_approvals} == {
    row["source_id"] for row in correction_proposals
}
assert Counter(row["final_decision"] for row in correction_approvals) == {
    "approved": 7,
    "held": 1,
}
held_correction = next(row for row in correction_approvals if row["final_decision"] == "held")
assert held_correction["source_id"] == "out_econ:row:47"

assert len(mapping_dispositions) == 26
assert Counter(row["guided_disposition"] for row in mapping_dispositions) == {
    "candidate-close-match": 4,
    "conditional-close-match": 1,
    "hold-definition-overlap": 1,
    "reject-identity-use-as-facet-evidence": 20,
}
assert len(energy_holds) == 14
assert all(row["recommendation_status"] == "held" for row in energy_holds)

assert summary["adr_status"] == "Accepted"
assert summary["guided_decision_count"] == len(approvals)
assert summary["guided_decisions_accepted"] == len(approvals)
assert summary["economic_source_corrections_approved"] == 7
assert summary["economic_source_corrections_held"] == 1
assert summary["external_candidate_dispositions_accepted"] == len(mapping_dispositions)
assert summary["external_close_matches_approved_for_later_implementation"] == 4
assert summary["external_mapping_holds"] == 2
assert summary["external_identity_mappings_rejected"] == 20
assert summary["energy_module_hold_count"] == len(energy_holds)
assert summary["source_correction_authorized"] is True
assert summary["canonical_source_modified"] is False
assert summary["mapping_decisions_approved"] is True
assert summary["mapping_assertions_implemented"] is False
assert summary["public_identifier_allocation_authorized"] is False
assert summary["semantic_implementation_authorized"] is False
assert summary["energy_module_assignment_approved"] is False
assert summary["release_authorized"] is False
assert summary["consumer_migration_authorized"] is False
assert len(evidence) == 5
assert all(row["claim_boundary"] for row in evidence)

print(
    "Validated ADR 0053 acceptance: "
    f"{len(approvals)} decisions, 7 source corrections, 1 source hold, "
    "4 close matches, 2 mapping holds, 20 mapping rejections, 14 energy holds"
)
