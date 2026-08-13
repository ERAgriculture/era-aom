#!/usr/bin/env python3
"""Validate user-facing semantic facts for Maize Bran concept card."""
import csv
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDFS, SKOS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
AOM = "urn:era-aom:livestock:"
SCHEMA = "urn:era-aom:schema:"

graph = Graph().parse(ROOT / "dist/livestock-staging/aom-semantic-bindings.ttl")
vocab = Graph().parse(ROOT / "dist/livestock-staging/aom-livestock.ttl")
schema = Graph().parse(ROOT / "schemas/owl/aom-semantic-model.ttl")
maize_bran = URIRef(AOM + "AOM_001614")
bran = URIRef(AOM + "AOM_101104")
byproduct = URIRef(AOM + "AOM_101062")
maize = URIRef("http://purl.obolibrary.org/obo/NCBITaxon_4577")

assert (maize_bran, URIRef(SCHEMA + "materialComponent"), bran) in graph
assert (maize_bran, URIRef(SCHEMA + "productRole"), byproduct) in graph
assert (maize_bran, URIRef(SCHEMA + "processingMethod"), URIRef(AOM + "AOM_000838")) in graph
assert (maize_bran, URIRef(SCHEMA + "sourceTaxon"), maize) in graph
assert (maize, RDFS.label, Literal("Zea mays", lang="en")) in graph
assert (URIRef(SCHEMA + "sourceTaxon"), RDFS.label, Literal("has source taxon", lang="en")) in schema
assert (URIRef(SCHEMA + "materialComponent"), RDFS.label, Literal("has material component", lang="en")) in schema
assert (URIRef(SCHEMA + "productRole"), RDFS.label, Literal("has product role", lang="en")) in schema
bran_definition = str(next(vocab.objects(bran, SKOS.definition))).casefold()
assert "milling fraction" in bran_definition and "endosperm" in bran_definition
assert "principal product" in str(next(vocab.objects(byproduct, SKOS.definition))).casefold()
assert "by-product" in str(next(vocab.objects(maize_bran, SKOS.definition))).casefold()
feedipedia = URIRef("https://www.feedipedia.org/node/12280")
assert (maize_bran, SKOS.relatedMatch, feedipedia) in vocab
assert (feedipedia, RDFS.label, Literal("Maize bran", lang="en")) in graph

with (DATA / "approved_feed_material_external_facets.csv").open(encoding="utf-8", newline="") as handle:
    external = list(csv.DictReader(handle))
assert len(external) == 3
assert any(row["feed_material_id"] == "AOM_001614" for row in external)
print("Maize Bran card validation passed: source link, species, Bran component, and by-product role")
