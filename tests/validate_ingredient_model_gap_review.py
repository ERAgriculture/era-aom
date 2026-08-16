#!/usr/bin/env python3
"""Validate complete consolidation of remaining ingredient model gaps."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/livestock-v7"


def read(name):
    with (REVIEW / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


gaps = read("ingredient_model_gap_families.csv")
clusters = read("ingredient_cluster_recommendations.csv")
labels = read("governed_label_source_audit.csv")
summary = json.loads((REVIEW / "ingredient_model_gap_summary.json").read_text())

assert summary == {
    "remaining_exceptions": 0, "model_gap_families": 0,
    "remaining_signature_clusters": 1, "governed_label_overrides": 26,
    "high_confidence_deprecation_reviews": 0, "automatic_identity_changes": 0,
}
assert not gaps
assert len(clusters) == 1
assert clusters[0]["recommendation"] == "hold-product-role-review"
assert clusters[0]["approval_status"] == "approved-hold"
by_id = {row["concept_id"]: row for row in labels}
assert len(labels) == 26
assert by_id["AOM_001491"]["governed_preferred_label"] == "Formulated feeds"
assert by_id["AOM_006500"]["impact"] == "decomposition-changed"
assert "Decorticated" in by_id["AOM_006500"]["governed_preferred_label"]
assert by_id["AOM_000564"]["impact"] == "decomposition-changed"
assert {"AOM_001265", "AOM_001462"} <= set(by_id)
assert all(
    by_id[concept_id]["impact"] == "identity-text-corrected"
    for concept_id in {"AOM_001265", "AOM_001462", "AOM_003206"}
)
print("Ingredient model-gap review validation passed: 0 exceptions; 1 approved identity hold")
