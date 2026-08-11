#!/usr/bin/env python3
"""Validate complete and public-safe definition-gap routing."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/livestock-v8"

with (REVIEW / "definition_gap_queue.csv").open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))
summary = json.loads((REVIEW / "definition_gap_summary.json").read_text())

assert len(rows) == 258 and len({row["concept_id"] for row in rows}) == 258
assert Counter(row["domain"] for row in rows) == {
    "feed_material": 18, "outcome": 80, "rearing_stage": 67,
    "taxon": 45, "management": 35, "farming_system": 13,
}
assert summary == {
    "prior_active_gaps": 258,
    "approved_structural_definitions": 240,
    "research_required": 18,
    "expert_review_required": 0,
    "remaining_after_approval": 18,
    "routes": {
        "approved_structural_definition": 240,
        "research_related_mapping_insufficient": 10,
        "research_source_workbook": 1,
        "research_taxon_insufficient_for_material": 7,
    },
    "closed_identifiers_used_for_routing": False,
}
assert not any("ilri" in row["public_mapping_schemes"].casefold() or "ilri" in row["public_mapping_targets"].casefold() for row in rows)
assert not any(row["recommended_route"] == "manual_core_definition" for row in rows)
print("Definition-gap classification validation passed: 258 routed; 18 integrity holds remain")
