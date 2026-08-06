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
assert Counter(row["status"] for row in rows) == {"held": 55, "approved": 155}
assert Counter(row["decision"] for row in rows) == {
    "hold_expert_evidence_required": 55,
    "approve_taxon_source_with_explicit_facets": 50,
    "approve_feedipedia_category_scope": 5,
    "approve_feedipedia_alias_scope": 4,
    "approve_core_hierarchy_scope": 2,
    "approve_workbook_source_with_explicit_facets": 4,
    "approve_identity_alias_with_explicit_facets": 9,
    "approve_shared_page_material_with_explicit_facets": 6,
    "approve_workbook_model_gap_with_explicit_facets": 4,
    "approve_consolidated_authority_with_explicit_facets": 17,
    "approve_bounded_workbook_material_scope": 54,
}
assert len(facets) == 149
assert Counter(row["target_property"] for row in facets) == {
    "aom:productRole": 56, "aom:ingredientPart": 44,
    "aom:ingredientConstituent": 17, "aom:physicalForm": 18,
    "aom:processingMethod": 14,
}
assert all(row["blocker_code"] and row["next_action"] for row in rows if row["status"] == "held")
assert not any(row["blocker_code"] or row["next_action"] for row in rows if row["status"] == "approved")
defined = {row["concept_id"] for row in definitions}
assert {row["concept_id"] for row in rows if row["status"] == "approved"} <= defined
assert not any("ilri" in value.casefold() for row in rows for value in row.values())
facet_pairs = {(row["feed_material_id"], row["target_concept_id"]) for row in facets}
assert ("AOM_003879", "AOM_101121") in facet_pairs  # rhizome remains distinct from root
assert ("AOM_003879", "AOM_101037") not in facet_pairs
assert {("AOM_001880", "AOM_101122"), ("AOM_001880", "AOM_101081")} <= facet_pairs
assert "AOM_001805" not in {row["feed_material_id"] for row in facets}  # plant taxon cannot establish larval biomass
assert all(row["evidence"] for row in rows if row["decision"] == "approve_taxon_source_with_explicit_facets")
print("Definition hard-tail review passed: 155 approved; 55 actionable holds; 149 facets")
