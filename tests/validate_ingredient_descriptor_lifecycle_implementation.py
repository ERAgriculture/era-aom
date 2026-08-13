#!/usr/bin/env python3
"""Validate governed ingredient-descriptor retirement and normalized contracts."""

import csv
from pathlib import Path

from rdflib import Graph, Literal, OWL, SKOS, URIRef
from rdflib.namespace import RDFS


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
DIST = ROOT / "dist/livestock-staging"
AOM = "urn:era-aom:livestock:"
SCHEMA = "urn:era-aom:schema:"
DESCRIPTORS = {
    "AOM_000531", "AOM_000532", "AOM_000533", "AOM_000534", "AOM_000535",
}


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


retirements = {row["concept_id"]: row for row in read("approved_concept_retirements.csv")}
relations = read("relations.csv")
notes = read("notes.csv")
bindings = {row["legacy_concept_id"]: row for row in read("approved_semantic_bindings.csv")}
assert DESCRIPTORS <= retirements.keys()
assert all(
    retirements[concept_id]["status"] == "approved"
    and "0046-ingredient-descriptor-lifecycle" in retirements[concept_id]["evidence"]
    and retirements[concept_id]["history_note"]
    for concept_id in DESCRIPTORS
)
assert not any(
    row["relation_type"] == "broader" and row["subject_id"] in retirements
    for row in relations
)
assert {
    row["concept_id"] for row in notes
    if row["note_type"] == "history_note"
} >= DESCRIPTORS

ttl = Graph().parse(DIST / "aom-livestock.ttl")
jsonld = Graph().parse(DIST / "aom-livestock.jsonld")
assert set(ttl) == set(jsonld)
for concept_id in DESCRIPTORS:
    concept = URIRef(AOM + concept_id)
    assert (concept, OWL.deprecated, Literal(True)) in ttl
    assert not any(ttl.objects(concept, SKOS.broader))
    assert any(ttl.objects(concept, SKOS.historyNote))
    assert str(ttl.value(concept, SKOS.notation)) == concept_id
    assert any(ttl.objects(concept, SKOS.prefLabel))

schema = Graph().parse(ROOT / "schemas/owl/aom-semantic-model.ttl")
expected = {
    "AOM_000531": ("IngredientComponent", "ingredientName"),
    "AOM_000532": ("IngredientComponent", "legacyComponentDescriptor"),
    "AOM_000533": ("FeedMaterial", "sourceTaxon"),
    "AOM_000534": ("IngredientComponent", "ingredientProportion"),
    "AOM_000535": ("IngredientComponent", "ingredientSource"),
}
for concept_id, (class_name, property_name) in expected.items():
    assert bindings[concept_id]["target_class"] == f"aom:{class_name}"
    assert bindings[concept_id]["target_property"] == f"aom:{property_name}"
    assert (
        URIRef(SCHEMA + property_name),
        RDFS.domain,
        URIRef(SCHEMA + class_name),
    ) in schema
assert bindings["AOM_000534"]["quantity_kind_uri"].endswith("DimensionlessRatio")

for config in ("era-aom.ttl", "era-aom-production.ttl"):
    assert "skosmos:showDeprecated true" in (ROOT / "config/skosmos" / config).read_text()

register = read("../../review/livestock-v33/ingredient_descriptor_implementation_register.csv")
assert {row["concept_id"] for row in register} == DESCRIPTORS
assert all(row["status"] == "implemented" for row in register)
print("Ingredient descriptor lifecycle passed: 5 retired cards; normalized properties; RDF parity")
