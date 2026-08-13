#!/usr/bin/env python3
"""Validate readable predicate labels and concept-specific assertion scope."""

from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDFS

ROOT = Path(__file__).resolve().parents[1]
AOM = "urn:era-aom:livestock:"
SCHEMA = "urn:era-aom:schema:"

schema = Graph().parse(ROOT / "dist/livestock-staging/aom-schema.ttl")
bindings = Graph().parse(ROOT / "dist/livestock-staging/aom-semantic-bindings.ttl")

labels = {
    "sourceTaxon": "has source taxon",
    "materialComponent": "has material component",
    "ingredientPart": "has ingredient part",
    "physicalForm": "has physical descriptor",
    "presentationForm": "has presentation form",
    "bulkConsistency": "has bulk consistency",
    "moistureCondition": "has moisture condition",
    "materialIntegrity": "has material integrity",
    "feedProductType": "has feed product type",
    "compositionState": "has composition state",
    "processingMethod": "has processing method",
    "mayResultInPhysicalForm": "may result in physical descriptor",
    "mayResultInPresentationForm": "may result in presentation form",
    "mayResultInMoistureCondition": "may result in moisture condition",
    "productRole": "has product role",
    "primaryConstituent": "has primary chemical constituent",
    "ingredientConstituent": "has ingredient constituent",
    "ingredientSource": "has acquisition source",
    "ingredientName": "has source ingredient label",
    "legacyComponentDescriptor": "has legacy component descriptor",
    "ingredientProportion": "has ingredient proportion",
    "ingredientProportionBasis": "has ingredient proportion basis",
}
for local_name, label in labels.items():
    assert (
        URIRef(SCHEMA + local_name),
        RDFS.label,
        Literal(label, lang="en"),
    ) in schema

# Feed-specific predicates appear only when asserted; Management receives none.
management = URIRef(AOM + "AOM_000106")
feed_predicates = {URIRef(SCHEMA + local_name) for local_name in labels}
assert not any(predicate in feed_predicates for predicate in bindings.predicates(management))

print("Semantic predicate visibility passed: explicit labels; no Management leakage")
