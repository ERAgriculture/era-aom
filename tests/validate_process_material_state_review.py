#!/usr/bin/env python3
"""Validate feed-process polyhierarchy and independent material-state axes."""

import csv
import json
from pathlib import Path

from rdflib import Graph, RDF, SKOS, URIRef
from rdflib.namespace import DCTERMS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW = ROOT / "review/livestock-v27"
DIST = ROOT / "dist/livestock-staging"
AOM = "urn:era-aom:livestock:"
SCHEMA = "urn:era-aom:schema:"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


summary = json.loads((REVIEW / "process_material_state_summary.json").read_text())
hierarchy_revisions = read(DATA / "approved_hierarchy_revisions.csv")
process_results = read(DATA / "approved_process_state_relations.csv")
state_review = read(REVIEW / "material_state_axis_review.csv")
grinding_review = read(REVIEW / "grinding_state_contradiction_review.csv")

assert summary == {
    "grinding_dispositions": {
        "hold_particulate_presentation_conflict": 3,
        "no_identified_bulk_state_conflict": 340,
    },
    "hierarchy_revisions": 18,
    "process_result_relations": 2,
    "reviewed_grinding_materials": 343,
    "reviewed_material_state_concepts": 18,
    "unresolved_cases": ["AOM_001961", "AOM_002008", "AOM_006004"],
}
assert len(hierarchy_revisions) == 138
assert len(process_results) == 2
assert len(state_review) == 18
assert len(grinding_review) == 343
assert {
    row["feed_material_id"] for row in grinding_review if row["status"] == "hold"
} == {"AOM_001961", "AOM_002008", "AOM_006004"}

vocabulary = Graph().parse(DIST / "aom-livestock.ttl")
bindings = Graph().parse(DIST / "aom-semantic-bindings.ttl")
concept = lambda identifier: URIRef(AOM + identifier)
broader = lambda child, parent: (
    concept(child), SKOS.broader, concept(parent)
) in vocabulary

assert not any(vocabulary.triples((concept("AOM_101021"), None, None)))
assert not any(vocabulary.triples((concept("AOM_101093"), None, None)))
assert (
    concept("AOM_000841"), DCTERMS.isReplacedBy, concept("AOM_000833")
) in vocabulary
for parent in {"AOM_000826", "AOM_000837", "AOM_101131"}:
    assert broader("AOM_000833", parent)
for parent in {"AOM_000837", "AOM_101129", "AOM_101130"}:
    assert broader("AOM_000838", parent)
for child in {"AOM_000834", "AOM_000835", "AOM_000836", "AOM_101090"}:
    assert broader(child, "AOM_101129")
for child in {"AOM_003097", "AOM_101070", "AOM_101073"}:
    assert broader(child, "AOM_101130")
assert broader("AOM_101128", "AOM_000826")
assert not broader("AOM_101128", "AOM_101130")
assert broader("AOM_000840", "AOM_101131")

assert broader("AOM_101054", "AOM_101133")
assert broader("AOM_001510", "AOM_101133")
assert broader("AOM_101077", "AOM_101132")
assert broader("AOM_101118", "AOM_101132")
assert not broader("AOM_101118", "AOM_101077")
assert broader("AOM_101126", "AOM_101125")
assert broader("AOM_101051", "AOM_101125")

assert (
    concept("AOM_000836"),
    URIRef(SCHEMA + "mayResultInPresentationForm"),
    concept("AOM_101125"),
) in bindings
assert (
    concept("AOM_000843"),
    URIRef(SCHEMA + "mayResultInMoistureCondition"),
    concept("AOM_101054"),
) in bindings
assert not any(bindings.triples((None, URIRef(SCHEMA + "physicalForm"), None)))
assert not any(bindings.triples((None, URIRef(SCHEMA + "mayResultInPhysicalForm"), None)))

maize_bran = concept("AOM_001614")
assert (
    maize_bran, URIRef(SCHEMA + "processingMethod"), concept("AOM_000838")
) in bindings
for property_name in {"presentationForm", "bulkConsistency", "moistureCondition"}:
    assert not any(bindings.objects(maize_bran, URIRef(SCHEMA + property_name)))

blood_ground = concept("AOM_000536")
assert (
    blood_ground, URIRef(SCHEMA + "moistureCondition"), concept("AOM_101054")
) in bindings
assert (
    blood_ground, URIRef(SCHEMA + "presentationForm"), concept("AOM_101125")
) in bindings
assert (
    blood_ground, URIRef(SCHEMA + "processingMethod"), concept("AOM_000843")
) not in bindings

poultry_meal = concept("AOM_101127")
for property_name, target in {
    "presentationForm": "AOM_101126",
    "moistureCondition": "AOM_101054",
    "processingMethod": "AOM_101128",
}.items():
    assert (
        poultry_meal, URIRef(SCHEMA + property_name), concept(target)
    ) in bindings

for identifier in summary["unresolved_cases"]:
    assert not any(bindings.objects(
        concept(identifier), URIRef(SCHEMA + "presentationForm")
    ))

material_assertions = []
for name in [
    "approved_feed_material_facets.csv",
    "approved_generated_feed_material_facets.csv",
    "approved_hard_tail_feed_material_facets.csv",
    "approved_structural_feed_material_facets.csv",
]:
    material_assertions.extend(read(DATA / name))
drying_materials = {
    row["feed_material_id"] for row in material_assertions
    if row["target_property"] == "aom:processingMethod"
    and row["target_concept_id"] == "AOM_000843"
}
assert len(drying_materials) == 399
for identifier in drying_materials:
    assert (
        concept(identifier),
        URIRef(SCHEMA + "moistureCondition"),
        concept("AOM_101054"),
    ) in bindings

facet_classes = {
    "AOM_101125": "FeedPresentationForm",
    "AOM_101077": "FeedBulkConsistency",
    "AOM_101054": "FeedMoistureCondition",
    "AOM_001510": "FeedMoistureCondition",
}
for identifier, class_name in facet_classes.items():
    assert (
        concept(identifier), RDF.type, URIRef(SCHEMA + class_name)
    ) in bindings or (
        concept(identifier), RDF.type, URIRef(SCHEMA + class_name)
    ) in vocabulary

definitions = {
    row["concept_id"]: row["definition"]
    for row in read(DATA / "definitions.csv")
}
for identifier in {
    "AOM_000826", "AOM_000833", "AOM_000834", "AOM_000835",
    "AOM_000836", "AOM_000837", "AOM_000838", "AOM_000839",
    "AOM_000840", "AOM_000842", "AOM_000843", "AOM_000845",
    "AOM_001510", "AOM_003097",
}:
    assert "GPT4" not in definitions[identifier]

print("Process/material-state review passed: 138 hierarchy revisions; 3 explicit holds")
