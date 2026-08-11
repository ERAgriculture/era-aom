#!/usr/bin/env python3
"""Validate cross-cutting feed-material structural governance and browser RDF."""
import csv
import json
from collections import Counter
from pathlib import Path

from rdflib import Graph, Literal, SKOS, URIRef
from rdflib.namespace import RDFS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW = ROOT / "review/livestock-v26"
DIST = ROOT / "dist/livestock-staging"
LIVESTOCK = "urn:era-aom:livestock:"
SCHEMA = "urn:era-aom:schema:"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


cohort = read(REVIEW / "feed_material_structural_review.csv")
facets = read(DATA / "approved_structural_feed_material_facets.csv")
manual_facets = read(DATA / "approved_feed_material_facets.csv")
external_facets = read(DATA / "approved_feed_material_external_facets.csv")
coverage = read(REVIEW / "feedipedia_external_label_coverage.csv")
summary = json.loads((REVIEW / "feed_material_structural_summary.json").read_text())

assert len(cohort) == 1643 == summary["reviewed_feed_materials"]
assert len({row["concept_id"] for row in cohort}) == len(cohort)
assert len(facets) == 1159 == summary["generated_assertions"]
assert Counter(row["rule_id"] for row in facets) == {
    "STRUCT-FORM-GRINDING": 338,
    "STRUCT-MOISTURE-BLOOD-EVIDENCE": 1,
    "STRUCT-MOISTURE-DRYING": 398,
    "STRUCT-ROLE-BLOOD": 3,
    "STRUCT-ROLE-LEGACY-BYPRODUCT": 419,
}
assert Counter(row["form_disposition"] for row in cohort) == {
    "approved_comminuted_form": 338,
    "approved_existing_specific_form": 19,
    "held_grinding_bulk_state_conflict": 3,
    "held_meal_without_process_evidence": 7,
    "not_in_form_cohort": 1276,
}
assert Counter(row["moisture_disposition"] for row in cohort) == {
    "approved_dried_from_blood_meal_evidence": 1,
    "approved_dried_from_process": 398,
    "not_in_moisture_cohort": 1244,
}
assert Counter(row["role_disposition"] for row in cohort) == {
    "approved_blood_byproduct": 3,
    "approved_branch_to_role_translation": 419,
    "approved_existing_role": 60,
    "not_in_role_cohort": 1161,
}
assert not any(row["target_concept_id"] == "AOM_101126" for row in facets)

structural = {
    (row["feed_material_id"], row["target_property"], row["target_concept_id"])
    for row in facets
}
assert ("AOM_001679", "aom:presentationForm", "AOM_101125") in structural
assert ("AOM_001096", "aom:presentationForm", "AOM_101125") in structural
assert ("AOM_000536", "aom:moistureCondition", "AOM_101054") in structural
assert ("AOM_001616", "aom:productRole", "AOM_101062") in structural
assert ("AOM_000536", "aom:productRole", "AOM_101062") in structural
assert not any(
    row["feed_material_id"] == "AOM_001938"
    and row["target_concept_id"] == "AOM_101126"
    for row in facets
)
assert {
    (row["feed_material_id"], row["target_property"], row["target_concept_id"])
    for row in manual_facets
} >= {
    ("AOM_001938", "aom:presentationForm", "AOM_101126"),
    ("AOM_101127", "aom:presentationForm", "AOM_101126"),
    ("AOM_101127", "aom:moistureCondition", "AOM_101054"),
    ("AOM_101127", "aom:processingMethod", "AOM_000836"),
    ("AOM_101127", "aom:processingMethod", "AOM_000843"),
    ("AOM_101127", "aom:processingMethod", "AOM_101128"),
    ("AOM_101127", "aom:productRole", "AOM_101062"),
}
assert {
    (row["feed_material_id"], row["target_uri"])
    for row in external_facets
} >= {
    ("AOM_001096", "http://purl.obolibrary.org/obo/NCBITaxon_9031"),
    ("AOM_001938", "http://purl.obolibrary.org/obo/NCBITaxon_9031"),
}
assert len(coverage) == 335
assert Counter(row["disposition"] for row in coverage) == {
    "approved_label_available": 177,
    "held_label_not_cached": 158,
}

livestock = Graph().parse(DIST / "aom-livestock.ttl")
bindings = Graph().parse(DIST / "aom-semantic-bindings.ttl")
concept = lambda identifier: URIRef(LIVESTOCK + identifier)
assert (concept("AOM_101125"), SKOS.broader, concept("AOM_101020")) in livestock
assert (concept("AOM_101126"), SKOS.broader, concept("AOM_101125")) in livestock
assert (concept("AOM_101051"), SKOS.broader, concept("AOM_101125")) in livestock
assert (concept("AOM_101127"), SKOS.broader, concept("AOM_003206")) in livestock
assert (concept("AOM_100983"), SKOS.related, concept("AOM_000025")) in livestock
assert (concept("AOM_101127"), SKOS.exactMatch,
        URIRef("https://www.feedipedia.org/node/214")) in livestock
assert (concept("AOM_101127"), SKOS.narrowMatch,
        URIRef("https://www.feedipedia.org/node/12911")) in livestock
assert (concept("AOM_001614"), SKOS.relatedMatch,
        URIRef("https://www.feedipedia.org/node/12280")) in livestock
assert (concept("AOM_000836"), URIRef(SCHEMA + "mayResultInPresentationForm"),
        concept("AOM_101125")) in bindings
assert (URIRef("https://www.feedipedia.org/node/12280"), RDFS.label,
        Literal("Maize bran", lang="en")) in bindings
assert (URIRef("https://www.feedipedia.org/node/12474"), RDFS.label,
        Literal("Poultry offal meal", lang="en")) in bindings
assert (URIRef("https://www.feedipedia.org/node/214"), RDFS.label,
        Literal("Poultry by-product meal", lang="en")) in bindings

labels = read(DATA / "labels.csv")
poultry_labels = {
    row["label"].casefold() for row in labels if row["concept_id"] == "AOM_003206"
}
assert "poultry by-products" in poultry_labels
assert "chicken offal" not in poultry_labels
assert "poultry by-product meal" not in poultry_labels

print("Feed-material structural review passed: 1,643 materials; 1,159 assertions; 335 Feedipedia resources")
