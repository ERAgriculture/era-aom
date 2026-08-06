#!/usr/bin/env python3
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW = ROOT / "review/livestock-v14"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


cohort = read(REVIEW / "definition_hard_tail_cohort.csv")
rows = read(REVIEW / "definition_hard_tail_review.csv")
facets = read(DATA / "approved_hard_tail_feed_material_facets.csv")
definitions = read(DATA / "approved_definition_enrichments.csv")
assert len(cohort) == len(rows) == 210
assert {row["concept_id"] for row in cohort} == {row["concept_id"] for row in rows}
assert Counter(row["status"] for row in rows) == {"held": 161, "approved": 49}
assert Counter(row["decision"] for row in rows) == {
    "hold_expert_evidence_required": 161,
    "approve_taxon_source_with_explicit_facets": 36,
    "approve_feedipedia_category_scope": 5,
    "approve_feedipedia_alias_scope": 4,
    "approve_core_hierarchy_scope": 2,
    "approve_workbook_source_with_explicit_facets": 2,
}
assert len(facets) == 43
assert Counter(row["target_property"] for row in facets) == {
    "aom:productRole": 20, "aom:ingredientPart": 10,
    "aom:ingredientConstituent": 9, "aom:physicalForm": 3,
    "aom:processingMethod": 1,
}
assert all(row["blocker_code"] and row["next_action"] for row in rows if row["status"] == "held")
assert not any(row["blocker_code"] or row["next_action"] for row in rows if row["status"] == "approved")
defined = {row["concept_id"] for row in definitions}
assert {row["concept_id"] for row in rows if row["status"] == "approved"} <= defined
assert not any("ilri" in value.casefold() for row in rows for value in row.values())
assert "AOM_003879" not in {row["feed_material_id"] for row in facets}  # rhizome is not root
assert "AOM_001880" not in {row["feed_material_id"] for row in facets}  # liver facet missing
assert all(row["evidence"] for row in rows if row["decision"] == "approve_taxon_source_with_explicit_facets")
print("Definition hard-tail review passed: 49 approved; 161 actionable holds; 43 facets")
