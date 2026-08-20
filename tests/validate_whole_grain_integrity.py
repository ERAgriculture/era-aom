#!/usr/bin/env python3
"""Validate reviewed whole-grain component-retention model and cereal mappings."""

import csv
from pathlib import Path

from rdflib import Graph, URIRef

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
DIST = ROOT / "dist/livestock-staging"


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


decisions = read("approved_whole_grain_integrity_decisions.csv")
labels = read("labels.csv")
facets = read("approved_feed_material_facets.csv")

assert len(decisions) == 4
assert all(
    row["status"] == "approved" and row["reviewer"] == "Pete Steward"
    and row["integrity_concept_id"] == "AOM_101110"
    for row in decisions
)
expected_labels = {
    "AOM_000656": "Ground whole-grain rice",
    "AOM_000660": "Ground whole-grain wheat",
    "AOM_001313": "Whole-grain maize",
    "AOM_001324": "Ground whole-grain maize",
}
preferred = {
    row["concept_id"]: row["label"] for row in labels
    if row["language"] == "en" and row["label_type"] == "pref"
}
assert {concept_id: preferred[concept_id] for concept_id in expected_labels} == expected_labels
assert {
    row["feed_material_id"] for row in facets
    if row["target_property"] == "aom:componentRetentionState"
    and row["target_concept_id"] == "AOM_101110"
} == set(expected_labels)

graph = Graph().parse(DIST / "aom-semantic-bindings.ttl")
component_retention_state = URIRef("urn:era-aom:schema:componentRetentionState")
whole_grain = URIRef("urn:era-aom:livestock:AOM_101110")
grinding = URIRef("urn:era-aom:schema:processingMethod")
grinding_value = URIRef("urn:era-aom:livestock:AOM_000836")
presentation_form = URIRef("urn:era-aom:schema:presentationForm")
for concept_id in expected_labels:
    material = URIRef("urn:era-aom:livestock:" + concept_id)
    assert (material, component_retention_state, whole_grain) in graph
for concept_id in {"AOM_000656", "AOM_000660", "AOM_001324"}:
    material = URIRef("urn:era-aom:livestock:" + concept_id)
    assert (material, grinding, grinding_value) in graph
    assert (
        material, presentation_form,
        URIRef("urn:era-aom:livestock:AOM_101125")
    ) in graph
assert not any(graph.objects(
    URIRef("urn:era-aom:livestock:AOM_001313"), presentation_form
))
assert not any(
    value == URIRef("urn:era-aom:livestock:AOM_101076")
    for concept_id in expected_labels
    for value in graph.objects(
        URIRef("urn:era-aom:livestock:" + concept_id), presentation_form
    )
)
assert not any(graph.objects(URIRef("urn:era-aom:livestock:AOM_000649"), component_retention_state))
assert whole_grain not in graph.objects(
    URIRef("urn:era-aom:livestock:AOM_001326"), component_retention_state
)
retains = URIRef("urn:era-aom:schema:retainsMaterialComponent")
assert {
    str(value).rsplit(":", 1)[-1]
    for value in graph.objects(whole_grain, retains)
} == {"AOM_101029", "AOM_101104", "AOM_101153"}
print("Whole-grain component-retention validation passed: 4 reviewed cereal materials")
