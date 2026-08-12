#!/usr/bin/env python3
import csv
from pathlib import Path

from rdflib import Graph, Literal, URIRef

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


decisions = read("approved_maize_identity_decisions.csv")
deprecations = read("approved_deprecations.csv")
corrections = read("approved_label_corrections.csv")
facets = read("approved_feed_material_facets.csv")

assert len(decisions) == 2
assert all(row["status"] == "approved" and row["reviewer"] == "Pete Steward" for row in decisions)
assert not any("ilri" in " ".join(row.values()).lower() for row in decisions)
assert any(
    row["deprecated_id"] == "AOM_006072"
    and row["replacement_id"] == "AOM_001326"
    for row in deprecations
)
assert any(
    row["concept_id"] == "AOM_001326"
    and row["new_label"] == "Whole-crop maize silage"
    for row in corrections
)
assert {
    (row["target_property"], row["target_concept_id"])
    for row in facets if row["feed_material_id"] == "AOM_001326"
} == {
    ("aom:compositionState", "AOM_101086"),
    ("aom:processingMethod", "AOM_000831"),
}
assert not any(row["feed_material_id"] == "AOM_006072" for row in facets)

graph = Graph().parse(ROOT / "dist/livestock-staging/aom-livestock.ttl")
old = URIRef("urn:era-aom:livestock:AOM_006072")
new = URIRef("urn:era-aom:livestock:AOM_001326")
assert (old, URIRef("http://purl.org/dc/terms/isReplacedBy"), new) in graph
assert (old, URIRef("urn:era:property:status"), Literal("deprecated")) in graph
print("Maize identity implementation validation passed: retained AOM_001326; deprecated AOM_006072")
