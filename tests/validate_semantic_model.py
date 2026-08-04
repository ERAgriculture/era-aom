#!/usr/bin/env python3
import csv
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, URIRef
from rdflib.namespace import RDF

ROOT = Path(__file__).resolve().parents[1]
OWL = ROOT / "schemas/owl/aom-semantic-model.ttl"
SHAPES = ROOT / "schemas/shacl/semantic-model.ttl"
REVIEW = ROOT / "review/livestock-v2"
DATA = ROOT / "data/livestock-staging"
DIST = ROOT / "dist/livestock-staging"
FIXTURES = ROOT / "tests/fixtures"

ontology = Graph().parse(OWL)
shapes = Graph().parse(SHAPES)
assert len(ontology) > 40
assert len(shapes) > 40

with (REVIEW / "schema_remodeling_candidates.csv").open(encoding="utf-8", newline="") as h:
    candidates = list(csv.DictReader(h))
with (REVIEW / "semantic_model_dispositions.csv").open(encoding="utf-8", newline="") as h:
    dispositions = list(csv.DictReader(h))

assert len(candidates) == 50 == len(dispositions)
assert {row["concept_id"] for row in candidates} == {
    row["concept_id"] for row in dispositions
}
assert all(row["status"] == "design-approved" for row in dispositions)
assert {row["migration_phase"] for row in dispositions} <= {"2", "3"}

with (DATA / "approved_semantic_bindings.csv").open(encoding="utf-8", newline="") as h:
    bindings = list(csv.DictReader(h))
phase_2 = {row["concept_id"] for row in dispositions if row["migration_phase"] == "2"}
assert len(bindings) == 13
assert {row["legacy_concept_id"] for row in bindings} == phase_2
assert {row["binding_kind"] for row in bindings} == {
    "property", "quantified_component", "observable_property"
}
assert all(row["status"] == "approved" and row["reviewer"] == "Pete Steward" for row in bindings)
assert sum(row["binding_kind"] == "observable_property" for row in bindings) == 8
assert all(
    row["quantity_kind_uri"].startswith("http://qudt.org/vocab/quantitykind/")
    and row["unit_requirement"] == "required"
    for row in bindings if row["binding_kind"] in {"quantified_component", "observable_property"}
)

binding_graph = Graph().parse(DIST / "aom-semantic-bindings.ttl")
jsonld_binding_graph = Graph().parse(DIST / "aom-semantic-bindings.jsonld")
assert len(binding_graph) == len(jsonld_binding_graph)
semantic_binding = URIRef("urn:era-aom:schema:SemanticBinding")
observable_property = URIRef("http://www.w3.org/ns/sosa/ObservableProperty")
assert len(set(binding_graph.subjects(RDF.type, semantic_binding))) == 13
assert {
    str(subject).removeprefix("urn:era-aom:livestock:")
    for subject in binding_graph.subjects(RDF.type, observable_property)
} == {row["legacy_concept_id"] for row in bindings if row["binding_kind"] == "observable_property"}
binding_result, _, report = validate(binding_graph, shacl_graph=shapes, ont_graph=ontology)
assert binding_result, report

valid_graph = Graph().parse(FIXTURES / "semantic-model-valid.ttl")
invalid_graph = Graph().parse(FIXTURES / "semantic-model-invalid.ttl")
valid_result, _, _ = validate(valid_graph, shacl_graph=shapes, ont_graph=ontology)
invalid_result, _, _ = validate(invalid_graph, shacl_graph=shapes, ont_graph=ontology)
assert valid_result
assert not invalid_result
print("Semantic model validation passed: 50 dispositions; valid/invalid fixtures behave")
