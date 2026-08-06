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
    "remaining_exceptions": 19, "model_gap_families": 4,
    "remaining_signature_clusters": 7, "governed_label_overrides": 12,
    "high_confidence_deprecation_reviews": 1, "automatic_identity_changes": 0,
}
assert sum(int(row["concept_count"]) for row in gaps) == 19
assert {row["gap_id"] for row in gaps} == {
    "dairy_composition_state", "pulp_product_material",
    "conserved_forage_hay", "formulated_feed_meal",
}
assert all(row["approval_status"] == "proposed" and not row["reviewer"] for row in gaps + clusters)
assert len({item for row in gaps for item in row["concept_ids"].split(";")}) == 19
assert len(clusters) == 7
by_cluster = {row["cluster_id"]: row for row in clusters}
assert by_cluster["INGCLUSTER-0001"]["retained_id_if_approved"] == "AOM_001459"
assert all(
    row["recommendation"].startswith("retain-distinct")
    for key, row in by_cluster.items() if key in {"INGCLUSTER-0003", "INGCLUSTER-0004", "INGCLUSTER-0005", "INGCLUSTER-0006", "INGCLUSTER-0007"}
)
by_id = {row["concept_id"]: row for row in labels}
assert len(labels) == 12
assert by_id["AOM_006500"]["impact"] == "decomposition-changed"
assert "Decorticated" in by_id["AOM_006500"]["governed_preferred_label"]
assert by_id["AOM_000564"]["impact"] == "decomposition-changed"
print("Ingredient model-gap review validation passed: 19 exceptions -> 4 model families; 7 clusters")
