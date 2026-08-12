#!/usr/bin/env python3
"""Validate feed/formulation split and linked descriptor/process cohort."""

import csv
import json
from collections import Counter
from pathlib import Path

from rdflib import Graph, RDF, SKOS, URIRef

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW = ROOT / "review/livestock-v28"
DIST = ROOT / "dist/livestock-staging"
AOM = "urn:era-aom:livestock:"
SCHEMA = "urn:era-aom:schema:"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


summary = json.loads((REVIEW / "feed_structure_summary.json").read_text())
classifications = read(DATA / "approved_feed_formulation_classifications.csv")
taxonomy_classifications = read(DATA / "approved_feed_taxonomy_classifications.csv")
constituents = read(REVIEW / "chemical_constituent_assertion_review.csv")
descriptors = read(REVIEW / "feed_descriptor_review.csv")
processes = read(REVIEW / "feed_process_review.csv")
whole = read(REVIEW / "whole_term_review.csv")
assert summary == {
    "constituent_assertions": 25,
    "constituent_dispositions": {
        "composition_state": 2,
        "primary_chemical_constituent": 23,
    },
    "descriptor_concepts": 116,
    "explicit_holds": ["AOM_001500"],
    "formulation_cohort": 29,
    "formulation_dispositions": {
        "category": 1, "feed_additive": 1, "feed_formulation": 23,
        "feed_material": 3, "hold_product_class": 1,
    },
    "hierarchy_revisions": 32,
    "process_concepts": 33,
    "whole_term_concepts": 12,
}
assert len(classifications) == 29
assert len(constituents) == 25
assert len(descriptors) == 116
assert len(processes) == 33
assert len(whole) == 12
assert Counter(row["disposition"] for row in classifications) == {
    "feed_formulation": 23, "feed_material": 3, "category": 1,
    "feed_additive": 1, "hold_product_class": 1,
}

vocabulary = Graph().parse(DIST / "aom-livestock.ttl")
bindings = Graph().parse(DIST / "aom-semantic-bindings.ttl")
concept = lambda identifier: URIRef(AOM + identifier)
schema = lambda name: URIRef(SCHEMA + name)
broader = lambda child, parent: (concept(child), SKOS.broader, concept(parent)) in vocabulary

assert (concept("AOM_100850"), SKOS.prefLabel, None) in vocabulary
assert str(vocabulary.value(concept("AOM_100850"), SKOS.prefLabel)) == "Feed materials"
assert str(vocabulary.value(concept("AOM_001491"), SKOS.prefLabel)) == "Formulated feeds"
assert broader("AOM_001491", "AOM_000328")
assert not broader("AOM_001491", "AOM_100850")
for child, parent in {
    "AOM_001500": "AOM_101142",
    "AOM_001579": "AOM_004433",
    "AOM_001497": "AOM_006334",
    "AOM_001870": "AOM_101142",
}.items():
    assert broader(child, parent)
assert str(vocabulary.value(concept("AOM_006072"), URIRef("urn:era:property:status"))) == "deprecated"

formulation_ids = {
    row["concept_id"] for row in classifications
    if row["semantic_class"] == "aom:FeedFormulation"
}
formulation_ids |= {
    row["concept_id"] for row in taxonomy_classifications
    if row["semantic_class"] == "aom:FeedFormulation"
}
typed_formulations = {
    str(subject).removeprefix(AOM)
    for subject in bindings.subjects(RDF.type, schema("FeedFormulation"))
}
assert typed_formulations == formulation_ids
assert (concept("AOM_001497"), RDF.type, schema("FeedMaterial")) in bindings
assert (concept("AOM_006154"), RDF.type, schema("Feed")) in bindings
assert (concept("AOM_001579"), RDF.type, schema("FeedAdditive")) in bindings
assert (concept("AOM_001870"), RDF.type, schema("Feed")) in bindings
for class_name in {"FeedMaterial", "FeedFormulation", "FeedAdditive"}:
    assert (concept("AOM_001500"), RDF.type, schema(class_name)) not in bindings

assert not any(bindings.triples((None, schema("ingredientConstituent"), None)))
assert len(list(bindings.triples((None, schema("primaryConstituent"), None)))) == 23
assert len(list(bindings.triples((None, schema("compositionState"), concept("AOM_101134"))))) == 2
assert not any(bindings.triples((None, schema("primaryConstituent"), concept("AOM_101066"))))

for child, parent in {
    "AOM_101096": "AOM_000826",
    "AOM_101088": "AOM_101096",
    "AOM_101069": "AOM_101130",
    "AOM_101072": "AOM_101130",
}.items():
    assert broader(child, parent)
for parent in {"AOM_101130", "AOM_000826"}:
    assert broader("AOM_101124", parent)
assert not any(vocabulary.triples((concept("AOM_101068"), None, None)))
assert broader("AOM_000830", "AOM_100990")
assert not any(vocabulary.triples((concept("AOM_101100"), None, None)))
assert not any(vocabulary.triples((concept("AOM_101119"), None, None)))
assert str(vocabulary.value(concept("AOM_003098"), SKOS.prefLabel)) == "Sprouting"
assert str(vocabulary.value(concept("AOM_101099"), SKOS.prefLabel)) == "Soaking"
assert any(str(label) == "Steeping" for label in vocabulary.objects(concept("AOM_101099"), SKOS.altLabel))

assert str(vocabulary.value(concept("AOM_101076"), SKOS.prefLabel)) == "Intact presentation"
assert str(vocabulary.value(concept("AOM_101110"), SKOS.prefLabel)) == "Whole-grain composition"
assert (concept("AOM_101134"), RDF.type, schema("ComponentRetentionState")) in bindings
for identifier, class_name in {
    "AOM_101020": "FeedPresentationForm",
    "AOM_101132": "FeedBulkConsistency",
    "AOM_101133": "FeedMoistureCondition",
    "AOM_101023": "ChemicalConstituent",
}.items():
    assert (concept(identifier), RDF.type, schema(class_name)) in bindings or (
        concept(identifier), RDF.type, schema(class_name)
    ) in vocabulary

print("Feed/formulation structural review passed: 29 classifications; 25 constituent assertions; 1 hold")
