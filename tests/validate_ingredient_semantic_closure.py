#!/usr/bin/env python3
"""Validate approved ingredient model and identity closure."""
import csv
from collections import Counter, defaultdict
from pathlib import Path

from rdflib import Graph, URIRef

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


closure = read("approved_ingredient_semantic_closure_decisions.csv")
clusters = read("approved_ingredient_cluster_decisions.csv")
facets = read("approved_feed_material_facets.csv")
deprecations = read("approved_deprecations.csv")

assert len(closure) == 19 and len({row["concept_id"] for row in closure}) == 19
assert Counter(row["model_family"] for row in closure) == {
    "pulp_product_material": 13,
    "formulated_feed_meal": 4,
    "conserved_forage_hay": 1,
    "dairy_composition_state": 1,
}
assert all(row["status"] == "approved" and row["reviewer"] == "Pete Steward" for row in closure)
assert len(clusters) == 7
assert Counter(row["decision"] for row in clusters) == {
    "retain_distinct": 5, "deprecate_replace": 1, "hold_identity": 1,
}
assert any(
    row["deprecated_id"] == "AOM_001898" and row["replacement_id"] == "AOM_001459"
    for row in deprecations
)

by_material = defaultdict(set)
for row in facets:
    by_material[row["feed_material_id"]].add((row["target_property"], row["target_concept_id"]))
for row in closure:
    assert (row["target_property"], row["target_concept_id"]) in by_material[row["concept_id"]]
assert ("aom:processingMethod", "AOM_101071") in by_material["AOM_000687"]
assert not any(
    row["feed_material_id"] in {"AOM_000798", "AOM_000801", "AOM_002109", "AOM_001498"}
    and row["target_property"] == "aom:processingMethod"
    for row in facets
)

graph = Graph().parse(ROOT / "dist/livestock-staging/aom-semantic-bindings.ttl")
for row in closure:
    assert (
        URIRef("urn:era-aom:livestock:" + row["concept_id"]),
        URIRef("urn:era-aom:schema:" + row["target_property"].split(":", 1)[1]),
        URIRef("urn:era-aom:livestock:" + row["target_concept_id"]),
    ) in graph
print("Ingredient semantic closure validation passed: 19 model decisions; 7 cluster decisions")
