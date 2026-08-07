#!/usr/bin/env python3
"""Validate complete preferred-label collision governance."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW = ROOT / "review/livestock-v4"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


decisions = read(DATA / "approved_ontology_collision_decisions.csv")
active = read(REVIEW / "ontology_pref_label_collision_candidates.csv")
deprecations = read(DATA / "approved_deprecations.csv")
summary = read(REVIEW / "ontology_quality_summary.csv")

assert len(decisions) == 92
assert len({row["collision_key"] for row in decisions}) == 92
assert Counter(row["decision"] for row in decisions) == {
    "retain_distinct": 85, "deprecate_replace": 6, "hold_identity": 1,
}
assert all(row["status"] == "approved" and row["reviewer"] == "Pete Steward" for row in decisions)
assert len(active) == 86
assert Counter(row["status"] for row in active) == {
    "approved-retain-distinct": 85,
    "approved-identity-hold": 1,
}
assert next(row for row in active if row["collision_key"] == "cotton seed")["status"] == "approved-identity-hold"

replacement_pairs = {(row["deprecated_id"], row["replacement_id"]) for row in deprecations}
assert {
    ("AOM_000338", "AOM_000350"), ("AOM_000339", "AOM_000351"),
    ("AOM_000340", "AOM_000352"), ("AOM_000341", "AOM_000353"),
    ("AOM_000342", "AOM_000354"), ("AOM_000949", "AOM_000935"),
} <= replacement_pairs
signals = {(row["scope"], row["quality_signal"]): int(row["count"]) for row in summary}
assert signals[("all AOM", "normalized preferred-label collisions")] == 86
assert signals[("all AOM", "unresolved preferred-label collisions")] == 0
manifest = json.loads((ROOT / "dist/livestock-staging/manifest.json").read_text())
assert manifest["counts"]["approved_ontology_collision_decisions"] == 92
print("Ontology collision governance validation passed: 92 decisions; 0 unresolved legacy groups")
