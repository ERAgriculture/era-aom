#!/usr/bin/env python3
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW = ROOT / "review/livestock-v10/feedipedia_semantic_review.csv"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


reviews = read(REVIEW)
facets = read(DATA / "approved_feed_material_facets.csv")
overrides = read(DATA / "approved_feed_material_source_overrides.csv")
definitions = read(DATA / "approved_definition_enrichments.csv")

assert len(reviews) == 8
assert sum(row["status"] == "approved" for row in reviews) == 6
assert {row["concept_id"] for row in reviews if row["status"] == "held"} == {
    "AOM_000673", "AOM_003908",
}
promoted = {row["concept_id"] for row in reviews if row["status"] == "approved"}
assert promoted <= {row["concept_id"] for row in overrides}

by_material = defaultdict(set)
for row in facets:
    if row["feed_material_id"] in promoted:
        by_material[row["feed_material_id"]].add(
            (row["target_property"], row["target_concept_id"])
        )
assert by_material == {
    "AOM_000544": {("aom:ingredientConstituent", "AOM_101081")},
    "AOM_000642": {
        ("aom:bulkConsistency", "AOM_101077"),
        ("aom:processingMethod", "AOM_101084"),
        ("aom:productRole", "AOM_101062"),
    },
    "AOM_000678": {("aom:ingredientConstituent", "AOM_101065")},
    "AOM_001289": {("aom:ingredientConstituent", "AOM_101065")},
    "AOM_003208": {("aom:productRole", "AOM_101062")},
    "AOM_003596": {("aom:ingredientPart", "AOM_101038")},
}
defined = {row["concept_id"] for row in definitions}
assert promoted <= defined
source_scope = {
    row["concept_id"] for row in definitions
    if row["definition_method"] == "composed_from_reviewed_feedipedia_source_scope"
}
assert {"AOM_000673", "AOM_003908"} <= source_scope
print("Feedipedia semantic promotion validation passed: 6 promoted; 2 held")
