#!/usr/bin/env python3
"""Validate committed ADR 0051 guided-review artifacts."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "review/whole-vocabulary-v1"
REVIEW = ROOT / "review/whole-vocabulary-v2"


def read_csv(directory: Path, name: str) -> list[dict[str, str]]:
    path = directory / name
    assert path.is_file(), f"Missing {path}"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


summary = json.loads((REVIEW / "acceptance_summary.json").read_text(encoding="utf-8"))
source_routes = read_csv(SOURCE, "resource_coverage.csv")
guided = read_csv(REVIEW, "guided_decision_recommendations.csv")
routes = read_csv(REVIEW, "resource_routing_recommendations.csv")
evidence = read_csv(REVIEW, "evidence_register.csv")

assert summary["status"] == "recommendation-only"
assert summary["adr_status"] == "Proposed"
assert summary["human_decision_recorded"] is False
assert summary["resource_routes_approved"] is False
assert summary["source_workbook_modified"] is False
assert summary["semantic_implementation_authorized"] is False
assert summary["public_identifiers_allocated"] is False
assert summary["publication_authorized"] is False
assert summary["release_authorized"] is False
assert summary["consumer_migration_authorized"] is False
assert summary["canonical_cutover_authorized"] is False

assert len(guided) == 8
assert {row["review_id"] for row in guided} == {f"GV-{number:02d}" for number in range(1, 9)}
assert Counter(row["recommended_decision"] for row in guided) == {
    "accept": 4,
    "accept-with-conditions": 2,
    "accept-with-revision": 1,
    "accept-with-holds": 1,
}
assert all(row["recommendation_status"] == "proposed" for row in guided)
assert all(not row["human_decision"] and not row["reviewer"] and not row["review_date"] for row in guided)

assert len(routes) == len(source_routes) == 33
assert [row["sheet"] for row in routes] == [row["sheet"] for row in source_routes]
assert [row["route_id"] for row in routes] == [f"RR-{number:02d}" for number in range(1, 34)]
source_columns = list(source_routes[0])
for route, source in zip(routes, source_routes, strict=True):
    assert {column: route[column] for column in source_columns} == source
assert Counter(row["recommended_decision"] for row in routes) == {
    "accept-exclusion-with-retained-provenance": 7,
    "accept-proposed-route-with-row-review": 17,
    "accept-supporting-evidence-route": 3,
    "hold-provenance-review": 1,
    "hold-publication-review": 1,
    "retain-confirmed-restricted-exclusion": 1,
    "revise-to-cross-domain-row-routing": 3,
}
assert all(row["recommendation_status"] == "proposed" for row in routes)
assert all(not row["human_decision"] and not row["reviewer"] and not row["review_date"] for row in routes)
assert next(row for row in routes if row["sheet"] == "site_list")["recommended_decision"] == "hold-publication-review"
assert next(row for row in routes if row["sheet"] == "ssa_feedsdb")["recommended_decision"] == "retain-confirmed-restricted-exclusion"
assert next(row for row in routes if row["sheet"] == "scio - Custom Terms")["recommended_decision"] == "hold-provenance-review"
assert {
    next(row for row in routes if row["sheet"] == sheet)["recommended_decision"]
    for sheet in {"ani_diet", "ani_process", "AOM_diets"}
} == {"accept-supporting-evidence-route"}
assert {
    next(row for row in routes if row["sheet"] == sheet)["recommended_decision"]
    for sheet in {"prac", "out", "out_econ"}
} == {"revise-to-cross-domain-row-routing"}

assert summary["guided_decision_count"] == len(guided)
assert summary["resource_route_count"] == len(routes)
assert summary["publication_dispositions"] == {"exclude": 9, "public": 23, "review": 1}
assert summary["explicit_route_holds"] == 2
assert summary["confirmed_restricted_exclusions"] == 1
assert len(evidence) == 7
assert all(row["supports"] and row["claim_boundary"] for row in evidence)

adr_text = (ROOT / "docs/decisions/0051-whole-vocabulary-resource-boundaries-and-migration-sequence.md").read_text(encoding="utf-8")
assert "Status: Proposed" in adr_text
assert "whole-vocabulary-v2/README.md" in adr_text

print("Validated ADR 0051 guided review: 8 decisions and 33 resource routes")
