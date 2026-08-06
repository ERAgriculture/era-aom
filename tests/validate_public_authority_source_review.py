#!/usr/bin/env python3
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW = ROOT / "review/livestock-v12"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


cohort = read(REVIEW / "public_authority_cohort.csv")
rows = read(REVIEW / "public_authority_source_scope_review.csv")
definitions = read(DATA / "approved_definition_enrichments.csv")
facets = read(DATA / "approved_feed_material_facets.csv")
assert len(cohort) == len(rows) == 244
assert {row["concept_id"] for row in cohort} == {row["concept_id"] for row in rows}
assert Counter(row["status"] for row in rows) == {"approved": 155, "held": 89}
assert Counter(row["decision"] for row in rows) == {
    "approve_direct_source_scope": 152,
    "approve_structured_oil_material": 3,
    "hold_derived_material_scope": 67,
    "hold_public_authority_mismatch": 22,
}
source_scope = {
    row["concept_id"] for row in definitions
    if row["definition_method"] == "composed_from_reviewed_public_authority_source_scope"
}
assert source_scope == {
    row["concept_id"] for row in rows if row["decision"] == "approve_direct_source_scope"
}
oil_ids = {"AOM_000651", "AOM_000674", "AOM_001586"}
assert {
    row["feed_material_id"] for row in facets
    if row["target_property"] == "aom:ingredientConstituent"
    and row["target_concept_id"] == "AOM_101081"
} >= oil_ids
assert oil_ids <= {row["concept_id"] for row in definitions}
assert not any("ilri" in value.casefold() for row in rows for value in row.values())
print("Public-authority source review passed: 155 approved; 89 held")
