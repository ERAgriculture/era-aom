#!/usr/bin/env python3
"""Validate committed ADR 0053 guided-review artifacts."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/crop-foundation-v2"


def read_csv(name: str) -> list[dict[str, str]]:
    path = REVIEW / name
    assert path.is_file(), f"Missing {path}"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


summary = json.loads((REVIEW / "acceptance_summary.json").read_text(encoding="utf-8"))
guided = read_csv("guided_decision_recommendations.csv")
hierarchy = read_csv("hierarchy_guided_dispositions.csv")
decompositions = read_csv("same_label_decomposition_review.csv")
source_actions = read_csv("source_issue_action_plan.csv")
economic = read_csv("economic_source_correction_proposals.csv")
mappings = read_csv("external_mapping_dispositions.csv")
energy = read_csv("energy_module_holds.csv")
evidence = read_csv("evidence_register.csv")

assert summary["status"] == "recommendation-only"
assert summary["adr_status"] == "Proposed"
assert summary["implementation_authorized"] is False
assert summary["source_workbook_modified"] is False
assert summary["public_identifiers_allocated"] is False
assert summary["external_mappings_approved"] is False
assert summary["module_assignments_approved"] is False

assert len(guided) == 12
assert {row["review_id"] for row in guided} == {f"GR-{number:02d}" for number in range(1, 13)}
assert all(row["recommendation_status"] == "proposed" for row in guided)
assert all(not row["human_decision"] and not row["reviewer"] and not row["review_date"] for row in guided)

assert len(hierarchy) == 109
assert Counter(row["guided_disposition"] for row in hierarchy) == {
    "hold-for-extensional-concept-versus-collection-review": 53,
    "collection": 35,
    "collapse-generated-parent-into-reviewed-leaf": 13,
    "collection-with-scoped-label": 8,
}
assert all(row["proposed_scoped_collection_label"] for row in hierarchy if row["guided_disposition"] == "collection-with-scoped-label")
assert all(row["target_leaf_id"] for row in hierarchy if row["guided_disposition"] == "collapse-generated-parent-into-reviewed-leaf")

assert len(decompositions) == 4
assert {row["source_id"] for row in decompositions} == {"prac:b23", "prac:b74", "prac:b5", "prac:h55.2"}
assert not next(row for row in decompositions if row["source_id"] == "prac:h55.2")["recommended_identity"]

assert len(source_actions) == 265
assert len({row["issue_id"] for row in source_actions}) == 265
assert all(row["approval_status"] == "pending" for row in source_actions)
assert Counter(row["guided_action_class"] for row in source_actions) == {
    "generator-fix": 147,
    "source-correction": 81,
    "lifecycle-hold": 20,
    "navigation-model-fix": 14,
    "semantic-decomposition": 2,
    "source-owner-decision": 1,
}

assert len(economic) == 8
assert all(row["action"] != "approved" for row in economic)
assert len(mappings) == 26
assert Counter(row["guided_disposition"] for row in mappings) == {
    "reject-identity-use-as-facet-evidence": 20,
    "candidate-close-match": 4,
    "conditional-close-match": 1,
    "hold-definition-overlap": 1,
}
assert all(row["approval_status"] == "pending" for row in mappings)
assert not any(row["candidate_relation"] == "skos:exactMatch" for row in mappings)

assert len(energy) == 14
assert all(row["module_disposition"] == "unassigned-agricultural-or-household-energy" for row in energy)
assert all(row["recommendation_status"] == "held" and row["approval_status"] == "pending" for row in energy)
assert len(evidence) >= 15
assert all(row["claim_boundary"] for row in evidence)

assert summary["guided_decision_count"] == len(guided)
assert summary["hierarchy_node_count"] == len(hierarchy)
assert summary["source_issue_count"] == len(source_actions)
assert summary["external_candidate_count"] == len(mappings)
assert summary["economic_correction_proposal_count"] == len(economic)
assert summary["energy_module_hold_count"] == len(energy)

print(
    "Validated ADR 0053 guided review: "
    f"{len(guided)} decisions, {len(hierarchy)} nodes, {len(source_actions)} issues, "
    f"{len(mappings)} mapping candidates, {len(energy)} energy holds"
)
