#!/usr/bin/env python3
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW = ROOT / "review/livestock-v13"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


cohort = read(REVIEW / "workbook_source_cohort.csv")
rows = read(REVIEW / "workbook_source_scope_review.csv")
definitions = read(DATA / "approved_definition_enrichments.csv")
assert len(cohort) == len(rows) == 200
assert {row["concept_id"] for row in cohort} == {row["concept_id"] for row in rows}
assert Counter(row["status"] for row in rows) == {"approved": 173, "held": 27}
assert Counter(row["decision"] for row in rows) == {
    "approve_workbook_identity_scope": 134,
    "approve_hierarchy_category_scope": 39,
    "hold_ambiguous_workbook_identity": 27,
}
assert Counter(row["path_alignment"] for row in cohort) == {"aligned": 198, "workbook_path_differs": 2}
approved = {row["concept_id"] for row in rows if row["status"] == "approved"}
defined = {
    row["concept_id"] for row in definitions
    if row["definition_method"] in {
        "composed_from_canonical_workbook_category_scope",
        "composed_from_canonical_workbook_identity_scope",
    }
}
facet_composed = {
    row["concept_id"] for row in definitions
    if row["definition_method"] == "composed_from_approved_semantic_facets"
}
structure_replaced = {
    row["concept_id"] for row in definitions
    if row["definition_method"] in {
        "feed_structure_definition_replacement",
        "feed_taxonomy_axis_definition_replacement",
        "feed_product_kind_definition_replacement",
    }
}
assert defined <= approved
assert defined | (facet_composed & approved) | (structure_replaced & approved) == approved
assert all(row["workbook_sha256"] == "f834c4f7837927774499eff4340c912784a3db10c2e19bd5d75a7f753df41438" for row in cohort)
assert not any("ilri" in value.casefold() for row in rows for value in row.values())
print("Canonical-workbook source review passed: 173 approved; 27 held")
