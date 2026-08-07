#!/usr/bin/env python3
"""Validate Bran classification and Maize Bran compound semantics."""

import csv
from pathlib import Path

from rdflib import Graph, RDF, SKOS, URIRef

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
DIST = ROOT / "dist/livestock-staging"


def rows(name):
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


facet = next(
    row for row in rows("approved_ingredient_facet_concepts.csv")
    if row["concept_id"] == "AOM_101104"
)
assert facet["facet"] == "material_component"
assert facet["target_property"] == "aom:materialComponent"
assert facet["value_class"] == "aom:FeedMaterialComponent"

relation = next(
    row for row in rows("relations.csv")
    if row["subject_id"] == "AOM_101104" and row["relation_type"] == "broader"
)
assert relation["object_id"] == "AOM_101085"

graph = Graph().parse(DIST / "aom-semantic-bindings.ttl")
schema = "urn:era-aom:schema:"
concept = "urn:era-aom:livestock:"
maize_bran = URIRef(concept + "AOM_001614")
expected = {
    "sourceTaxon": URIRef("http://purl.obolibrary.org/obo/NCBITaxon_4577"),
    "materialComponent": URIRef(concept + "AOM_101104"),
    "processingMethod": URIRef(concept + "AOM_000838"),
    "productRole": URIRef(concept + "AOM_101062"),
}
for prop, target in expected.items():
    assert (maize_bran, URIRef(schema + prop), target) in graph
assert not any(graph.objects(maize_bran, URIRef(schema + "ingredientPart")))
assert (
    URIRef(concept + "AOM_101104"),
    RDF.type,
    URIRef(schema + "FeedMaterialComponent"),
) in graph
assert (expected["sourceTaxon"], SKOS.prefLabel, None) in graph

definitions = {
    row["concept_id"]: row["definition"] for row in rows("definitions.csv")
}
assert "separated during milling" in definitions["AOM_001614"]
assert "material fraction" in definitions["AOM_101104"]
print("Bran compound model validation passed: source, component, process, and role asserted")
