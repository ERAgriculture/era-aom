#!/usr/bin/env python3
"""Validate deterministic feed identity audit and critical candidate coverage."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/livestock-v4"


def read(name):
    with (REVIEW / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


lexical = read("feed_lexical_identity_candidates.csv")
external = read("feed_external_granularity_candidates.csv")
cereals = read("cereal_feed_material_review.csv")
summary = read("ontology_quality_summary.csv")
preferred_collisions = read("ontology_pref_label_collision_candidates.csv")
assert len(lexical) == 16
assert len(external) == 191
assert len(cereals) == 369
assert len(preferred_collisions) == 99
assert not any(row["status"] == "review-required" for row in preferred_collisions)
assert all(row["status"] == "review-required" for row in lexical)
assert all(row["status"] == "granularity-review-required" for row in external)
assert any({"AOM_000564", "AOM_001884"} <= set(row["concept_ids"].split(";"))
           for row in lexical)
assert {row["mapping_system"] for row in external} == {"Feedipedia", "CPC_Code_Product"}
assert all("ilri" not in row["mapping_system"].casefold() for row in external)
assert any(row["mapping_system"] == "Feedipedia" and "AOM_001313" in row["concept_ids"].split(";")
           for row in external)
by_id = {row["concept_id"]: row for row in cereals}
assert by_id["AOM_006072"]["process_terms"] == "ensiled"
assert by_id["AOM_006072"]["component_or_form_terms"] == "whole"
signals = {(row["scope"], row["quality_signal"]): int(row["count"]) for row in summary}
assert signals[("all AOM", "source rows")] == 2503
assert signals[("legacy source", "missing source definitions")] == 1865
assert signals[("active governed vocabulary", "missing definitions")] == 645
assert signals[("all AOM", "unresolved preferred-label collisions")] == 0
assert signals[("cereal feed materials", "missing definitions")] == 138
release = json.loads((ROOT / "config/releases/2026.1-rc.1.json").read_text())
baseline = release["content_baseline"]
assert baseline["era_workbook_snapshot_modified"] == "2026-07-09T11:29:11+03:00"
assert baseline["era_workbook_rows"] == 2503
assert baseline["aom_id_mismatches"] == 0
assert baseline["hierarchy_level_mismatches"] == 0
assert baseline["private_workbook_fingerprint_published"] is False
print(f"Feed identity audit validation passed: {len(lexical)} lexical, {len(external)} external, {len(cereals)} cereal candidates")
