#!/usr/bin/env python3
"""Validate evidence-bounded definition enrichment."""
import csv
import json
from collections import Counter
from pathlib import Path

from rdflib import Graph, SKOS, URIRef

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


approved = read("approved_definition_enrichments.csv")
definitions = read("definitions.csv")
concepts = read("concepts.csv")
assert len(approved) == 2105
assert len({row["concept_id"] for row in approved}) == 2105
assert Counter(row["definition_method"] for row in approved) == {
    "composed_from_approved_semantic_facets": 1092,
    "composed_from_bounded_workbook_material_scope": 72,
    "promoted_reviewed_scope_note": 263,
    "composed_from_governed_hierarchy_role": 243,
    "composed_from_reviewed_feedipedia_source_scope": 101,
    "composed_from_reviewed_public_authority_source_scope": 152,
    "composed_from_canonical_workbook_identity_scope": 134,
    "composed_from_canonical_workbook_category_scope": 39,
    "composed_from_reviewed_feedipedia_category_scope": 5,
    "composed_from_governed_core_hierarchy_scope": 2,
    "composed_from_reviewed_compound_model": 2,
}
assert all(row["status"] == "approved" and row["reviewer"] == "Pete Steward" for row in approved)
assert all(
    "governed source identity" in row["definition"] for row in approved
    if row["definition_method"] == "composed_from_approved_semantic_facets"
)
assert sum(row["source_column"] == "approved_definition_enrichment" for row in definitions) == 2105
defined = {row["concept_id"] for row in definitions}
active = [row for row in concepts if row["status"] != "deprecated"]
assert sum(row["concept_id"] not in defined for row in active) == 18

graph = Graph().parse(ROOT / "dist/livestock-staging/aom-livestock.ttl")
maize = URIRef("urn:era-aom:livestock:AOM_001313")
definition = str(next(graph.objects(maize, SKOS.definition)))
assert "source identity “maize”" in definition and "Whole grain" in definition
manifest = json.loads((ROOT / "dist/livestock-staging/manifest.json").read_text())
assert manifest["counts"]["approved_definition_enrichments"] == 2105
print("Definition enrichment validation passed: 2,105 definitions; 18 active integrity holds remain")
