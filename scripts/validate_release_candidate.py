#!/usr/bin/env python3
"""Validate ERA-AOM release semantics, packaging, and browser contracts."""

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import pyarrow.parquet as pq
from pyshacl import validate
from rdflib import Graph, Literal, RDF, SKOS, URIRef


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def graph(path):
    return Graph().parse(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", required=True)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    release = root / "dist" / "releases" / args.release
    manifest = json.loads((release / "manifest.json").read_text(encoding="utf-8"))
    base = manifest["namespace_base"].rstrip("/") + "/"

    assert manifest["release_status"] == "release-candidate-not-canonical"
    assert manifest["canonical_cutover"] is False
    assert manifest["compatibility_policy"] == "dual_publish"
    assert manifest["reviewer"] == "TBD"
    assert not any(manifest["publication_gates"].values())

    for item in manifest["distributions"]:
        path = release / item["path"]
        assert path.stat().st_size == item["bytes"]
        assert sha256(path) == item["sha256"]

    livestock_ttl = graph(release / "aom-livestock.ttl")
    livestock_jsonld = graph(release / "aom-livestock.jsonld")
    livestock_rdf = graph(release / "aom-livestock.rdf")
    assert set(livestock_ttl) == set(livestock_jsonld) == set(livestock_rdf)
    assert len(livestock_ttl) == manifest["counts"]["livestock_triples"]

    concepts = set(livestock_ttl.subjects(RDF.type, SKOS.Concept))
    schemes = set(livestock_ttl.subjects(RDF.type, SKOS.ConceptScheme))
    assert len(concepts) == 2777 and len(schemes) == 1
    assert all(str(item).startswith(base) for item in concepts | schemes)
    assert not any(
        isinstance(term, URIRef) and str(term).startswith("urn:era-aom:")
        for triple in livestock_ttl for term in triple
    )
    assert all(
        any(isinstance(label, Literal) and label.language for label in livestock_ttl.objects(item, SKOS.prefLabel))
        for item in concepts
    )

    internal_relations = (SKOS.broader, SKOS.related)
    for relation in internal_relations:
        assert all(target in concepts for target in livestock_ttl.objects(None, relation))

    children = defaultdict(set)
    for child, parent in livestock_ttl.subject_objects(SKOS.broader):
        children[child].add(parent)
    visiting, visited = set(), set()

    def visit(node):
        assert node not in visiting, f"Hierarchy cycle at {node}"
        if node in visited:
            return
        visiting.add(node)
        for parent in children[node]:
            visit(parent)
        visiting.remove(node)
        visited.add(node)

    for concept in concepts:
        visit(concept)

    scheme = next(iter(schemes))
    roots = {concept for concept in concepts if not any(livestock_ttl.objects(concept, SKOS.broader))}
    declared_top = set(livestock_ttl.subjects(SKOS.topConceptOf, scheme))
    assert roots == declared_top == set(livestock_ttl.objects(scheme, SKOS.hasTopConcept))
    assert len(roots) == 4
    broader_pairs = set(livestock_ttl.subject_objects(SKOS.broader))
    narrower_pairs = {(child, parent) for parent, child in livestock_ttl.subject_objects(SKOS.narrower)}
    assert broader_pairs == narrower_pairs

    conforms, _, report = validate(
        livestock_ttl,
        shacl_graph=graph(root / "schemas" / "shacl" / "concepts.ttl"),
        inference="rdfs",
    )
    assert conforms, report

    schema_ttl = graph(release / "aom-schema.ttl")
    schema_rdf = graph(release / "aom-schema.rdf")
    bindings_ttl = graph(release / "aom-semantic-bindings.ttl")
    bindings_jsonld = graph(release / "aom-semantic-bindings.jsonld")
    assert set(schema_ttl) == set(schema_rdf)
    assert set(bindings_ttl) == set(bindings_jsonld)
    assert len(schema_ttl) == manifest["counts"]["schema_triples"]
    assert len(bindings_ttl) == manifest["counts"]["semantic_binding_triples"]

    nodes = pq.read_table(release / "nodes.parquet")
    edges = pq.read_table(release / "edges.parquet")
    crosswalk = pq.read_table(release / "migration-crosswalk.parquet")
    rules = pq.read_table(release / "ingredient-harmonization-rules.parquet")
    material_facets = pq.read_table(release / "feed-material-facets.parquet")
    assert nodes.num_rows == 2777 and edges.num_rows == 2804
    assert crosswalk.num_rows == 10
    assert rules.num_rows == 40 and material_facets.num_rows == 1728
    assert ("AOM_006072", "AOM_001326") in set(zip(
        crosswalk.column("deprecated_id").to_pylist(),
        crosswalk.column("replacement_id").to_pylist(),
    ))
    assert ("AOM_001898", "AOM_001459") in set(zip(
        crosswalk.column("deprecated_id").to_pylist(),
        crosswalk.column("replacement_id").to_pylist(),
    ))
    assert pq.read_schema(release / "nodes.parquet").names == [
        "node_id", "label", "node_type", "module", "status"
    ]

    skosmos = graph(root / "config" / "skosmos" / "era-aom.ttl")
    assert len(skosmos) > 0
    print(
        f"Validated {args.release}: {len(concepts)} concepts, "
        f"{len(livestock_ttl)} equivalent triples across Turtle/JSON-LD/RDF/XML."
    )


if __name__ == "__main__":
    main()
