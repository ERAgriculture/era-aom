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

assert len(rows) == 882 and len({row["concept_id"] for row in rows}) == 882
assert Counter(row["domain"] for row in rows) == {
    "feed_material": 637, "outcome": 80, "rearing_stage": 67,
    "taxon": 45, "management": 35, "farming_system": 16, "core_root": 2,
}
assert summary == {
    "prior_active_gaps": 882,
    "approved_structural_definitions": 243,
    "research_required": 637,
    "expert_review_required": 2,
    "remaining_after_approval": 639,
    "routes": {
        "approved_structural_definition": 243,
        "manual_core_definition": 2,
        "research_feedipedia": 193,
        "research_public_ontology": 26,
        "research_source_workbook": 200,
        "research_taxon_insufficient_for_material": 218,
    },
    "closed_identifiers_used_for_routing": False,
}
assert not any("ilri" in row["public_mapping_schemes"].casefold() or "ilri" in row["public_mapping_targets"].casefold() for row in rows)
assert {row["preferred_label"] for row in rows if row["recommended_route"] == "manual_core_definition"} == {"Management", "Farming System"}
print("Definition-gap classification validation passed: 882 routed; 639 remain")
