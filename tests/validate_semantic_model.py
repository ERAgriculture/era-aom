#!/usr/bin/env python3
import csv
from pathlib import Path

from pyshacl import validate
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
OWL = ROOT / "schemas/owl/aom-semantic-model.ttl"
SHAPES = ROOT / "schemas/shacl/semantic-model.ttl"
REVIEW = ROOT / "review/livestock-v2"
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

valid_graph = Graph().parse(FIXTURES / "semantic-model-valid.ttl")
invalid_graph = Graph().parse(FIXTURES / "semantic-model-invalid.ttl")
valid_result, _, _ = validate(valid_graph, shacl_graph=shapes, ont_graph=ontology)
invalid_result, _, _ = validate(invalid_graph, shacl_graph=shapes, ont_graph=ontology)
assert valid_result
assert not invalid_result
print("Semantic model validation passed: 50 dispositions; valid/invalid fixtures behave")
