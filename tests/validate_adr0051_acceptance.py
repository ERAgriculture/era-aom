#!/usr/bin/env python3
"""Validate ADR 0051 human acceptance record."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECOMMENDATIONS = ROOT / "review/whole-vocabulary-v2"
ACCEPTANCE = ROOT / "review/whole-vocabulary-v3"


def read_csv(directory: Path, name: str) -> list[dict[str, str]]:
    path = directory / name
    assert path.is_file(), f"Missing {path}"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


summary = json.loads((ACCEPTANCE / "acceptance_summary.json").read_text(encoding="utf-8"))
guided = read_csv(RECOMMENDATIONS, "guided_decision_recommendations.csv")
policy_approvals = read_csv(ACCEPTANCE, "policy_decision_approvals.csv")
routes = read_csv(RECOMMENDATIONS, "resource_routing_recommendations.csv")
route_approvals = read_csv(ACCEPTANCE, "resource_route_approvals.csv")
evidence = read_csv(ACCEPTANCE, "evidence_register.csv")

assert len(guided) == len(policy_approvals) == 8
assert {row["review_id"] for row in guided} == {row["review_id"] for row in policy_approvals}
assert {row["review_id"]: row["recommended_decision"] for row in guided} == {
    row["review_id"]: row["final_decision"] for row in policy_approvals
}
assert len(routes) == len(route_approvals) == 33
assert {row["route_id"] for row in routes} == {row["route_id"] for row in route_approvals}
assert {
    row["route_id"]: (row["sheet"], row["recommended_decision"]) for row in routes
} == {
    row["route_id"]: (row["sheet"], row["final_decision"]) for row in route_approvals
}
assert all(row["approval_status"] == "accepted" for row in policy_approvals + route_approvals)
assert all(row["reviewer"] == "P. Steward" for row in policy_approvals + route_approvals)
assert all(row["review_date"] == "2026-08-28" for row in policy_approvals + route_approvals)

assert Counter(row["final_decision"] for row in route_approvals) == {
    "accept-exclusion-with-retained-provenance": 7,
    "accept-proposed-route-with-row-review": 17,
    "accept-supporting-evidence-route": 3,
    "hold-provenance-review": 1,
    "hold-publication-review": 1,
    "retain-confirmed-restricted-exclusion": 1,
    "revise-to-cross-domain-row-routing": 3,
}

assert summary["adr_status"] == "Accepted"
assert summary["policy_decision_count"] == summary["policy_decisions_accepted"] == len(policy_approvals)
assert summary["resource_route_count"] == summary["resource_routes_accepted"] == len(route_approvals)
assert summary["cross_domain_route_revisions"] == 3
assert summary["explicit_route_holds"] == 2
assert summary["confirmed_restricted_exclusions"] == 1
assert summary["provenance_retaining_exclusions"] == 7
assert summary["supporting_livestock_routes"] == 3
for key in (
    "product_boundaries_accepted",
    "resource_routing_policy_accepted",
    "migration_sequence_accepted",
    "coverage_contract_accepted",
    "adr0052_dependency_accepted",
    "adr0053_dependency_accepted",
):
    assert summary[key] is True
for key in (
    "source_workbook_modified",
    "row_semantics_approved",
    "public_identifiers_allocated",
    "semantic_implementation_authorized",
    "publication_authorized",
    "release_authorized",
    "consumer_migration_authorized",
    "canonical_cutover_authorized",
):
    assert summary[key] is False
assert len(evidence) == 5
assert all(row["supports"] and row["claim_boundary"] for row in evidence)

adr_text = (ROOT / "docs/decisions/0051-whole-vocabulary-resource-boundaries-and-migration-sequence.md").read_text(encoding="utf-8")
assert "Status: Accepted" in adr_text
assert "whole-vocabulary-v3/README.md" in adr_text

print("Validated ADR 0051 acceptance: 8 policy decisions and 33 resource routes")
