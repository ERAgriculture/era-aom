#!/usr/bin/env python3
"""Validate reviewed standalone feed-material source overrides."""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW = ROOT / "review/livestock-v5"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


overrides = read(DATA / "approved_feed_material_source_overrides.csv")
inventory = read(REVIEW / "ingredient_harmonization_inventory.csv")
generated = read(DATA / "approved_generated_feed_material_facets.csv")

assert len(overrides) == 15
assert all(
    row["status"] == "approved" and row["reviewer"] == "Pete Steward"
    and row["review_date"] == "2026-08-06"
    for row in overrides
)
by_id = {row["concept_id"]: row for row in inventory}
for concept_id in {"AOM_001616", "AOM_000537", "AOM_000536"}:
    assert by_id[concept_id]["source_identity_candidate"] == "blood"
    assert not by_id[concept_id]["component_candidates"]
for concept_id in {"AOM_000558", "AOM_006194"}:
    assert by_id[concept_id]["source_identity_candidate"] == "shell"
    assert not by_id[concept_id]["component_candidates"]
assert by_id["AOM_001333"]["source_identity_candidate"] == "oil"
assert not by_id["AOM_001333"]["form_candidates"]
assert all(by_id[row["concept_id"]]["governance_state"] == "approved_source_override" for row in overrides)

assert not any(
    row["feed_material_id"] in {item["concept_id"] for item in overrides}
    and row["target_property"] in {
        "aom:ingredientPart", "aom:presentationForm", "aom:bulkConsistency"
    }
    for row in generated
)
assert {
    (row["target_property"], row["target_label"])
    for row in generated if row["feed_material_id"] == "AOM_000537"
} == {
    ("aom:processingMethod", "Drying"),
    ("aom:processingMethod", "Grinding"),
    ("aom:processingMethod", "Heating"),
}
assert {
    (row["target_property"], row["target_label"])
    for row in generated if row["feed_material_id"] == "AOM_006194"
} == {("aom:processingMethod", "Grinding")}
assert by_id["AOM_000544"]["source_identity_candidate"] == "fish"
assert not by_id["AOM_000544"]["form_candidates"]
assert by_id["AOM_000678"]["source_identity_candidate"] == "cassava"
assert by_id["AOM_001289"]["source_identity_candidate"] == "maize"
assert by_id["AOM_003208"]["source_identity_candidate"] == "bambara groundnut"
assert by_id["AOM_003596"]["source_identity_candidate"] == "grape"
for concept_id, source in {
    "AOM_000651": "maize", "AOM_000674": "sunflower", "AOM_001586": "soybean",
}.items():
    assert by_id[concept_id]["source_identity_candidate"] == source
    assert not by_id[concept_id]["form_candidates"]
print("Feed-material source override validation passed: 15 governed identities")
