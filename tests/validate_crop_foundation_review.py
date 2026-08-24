#!/usr/bin/env python3
"""Validate committed crop-foundation recommendation artifacts."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/crop-foundation-v1"


def read_csv(name: str) -> list[dict[str, str]]:
    path = REVIEW / name
    assert path.is_file(), f"Missing {path}"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


summary = json.loads((REVIEW / "review_summary.json").read_text(encoding="utf-8"))
dispositions = read_csv("source_row_dispositions.csv")
nodes = read_csv("hierarchy_node_review.csv")
edges = read_csv("hierarchy_edge_review.csv")
collisions = read_csv("identity_collision_audit.csv")
quality = read_csv("source_quality_issues.csv")
authority_candidates = read_csv("authority_label_candidates.csv")
core = read_csv("shared_core_candidate_review.csv")
guided = read_csv("guided_review.csv")
evidence = read_csv("evidence_register.csv")
contracts = read_csv("pilot_contract_audit.csv")
snapshot = read_csv("source_snapshot.csv")

assert summary["status"] == "recommendation-only"
assert summary["implementation_authorized"] is False
assert len(dispositions) == 377
assert Counter(row["source_sheet"] for row in dispositions) == {"prac": 196, "out": 116, "out_econ": 65}
assert len({(row["source_sheet"], row["source_row"]) for row in dispositions}) == 377
assert all(row["decision_status"] in {"proposed", "held"} for row in dispositions)
assert not any(row["decision_status"] == "approved" for row in dispositions)
assert all(row["reviewer"] == "" and row["review_date"] == "" for row in dispositions)
assert len(nodes) == 109
assert len(edges) == 405
assert all(row["status"] == "held" for row in nodes + edges)
assert len(contracts) == 12 and all(row["status"] == "open" for row in contracts)
assert len(core) == 15
assert len(guided) == 12 and all(row["review_status"] == "pending" for row in guided)
assert len(snapshot) == 3
assert {row["source_sheet"]: int(row["row_count"]) for row in snapshot} == {"prac": 196, "out": 116, "out_econ": 65}
assert len(evidence) >= 13
assert all(row["claim_boundary"] for row in evidence)
assert all(row["claim_boundary"] for row in authority_candidates)
assert any(row["issue_type"] == "literal-na-sentinel" for row in quality)
assert any(row["issue_type"] == "pilot-notation-mutation" for row in quality)
assert any(row["issue_type"] == "placeholder-identifier" for row in quality)
assert any(row["recommended_disposition"] == "reuse-existing-aom-id-candidate" for row in collisions)
assert any(row["recommended_disposition"] == "retain-distinct-context-pending-scope-definition" for row in collisions)
assert summary["source_row_total"] == len(dispositions)
assert summary["pilot_intermediate_nodes_reviewed"] == len(nodes)
assert summary["pilot_hierarchy_edges_reviewed"] == len(edges)
assert summary["identity_collision_records"] == len(collisions)
assert summary["source_quality_issue_count"] == len(quality)
assert summary["authority_label_candidate_count"] == len(authority_candidates)

print(
    "Validated crop foundation review: "
    f"{len(dispositions)} source rows, {len(nodes)} nodes, {len(edges)} edges, "
    f"{len(collisions)} collision records, {len(quality)} source issues"
)
