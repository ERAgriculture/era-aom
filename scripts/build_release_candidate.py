#!/usr/bin/env python3
"""Build deterministic, noncanonical ERA-AOM release-candidate artifacts."""

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from rdflib import Graph, RDF, SKOS, URIRef


if os.environ.get("PYTHONHASHSEED") != "0":
    environment = os.environ.copy()
    environment["PYTHONHASHSEED"] = "0"
    os.execve(sys.executable, [sys.executable, *sys.argv], environment)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_uri(value, base):
    text = str(value)
    prefixes = {
        "urn:era-aom:livestock:": "livestock/",
        "urn:era-aom:scheme:": "scheme/",
        "urn:era-aom:schema:": "schema/",
        "urn:era-aom:binding:": "binding/",
        "urn:era-aom:value-binding:": "value-binding/",
    }
    if text == "urn:era-aom:schema":
        return URIRef(base + "schema")
    for prefix, path in prefixes.items():
        if text.startswith(prefix):
            return URIRef(base + path + text[len(prefix):])
    return value


def rewrite_graph(source, base):
    original = Graph().parse(source)
    result = Graph()
    for prefix, namespace in original.namespaces():
        result.bind(prefix, public_uri(namespace, base))
    for subject, predicate, obj in original:
        result.add((
            public_uri(subject, base),
            public_uri(predicate, base),
            public_uri(obj, base) if isinstance(obj, URIRef) else obj,
        ))
    return result


def materialize_browser_hierarchy(graph):
    """Publish explicit SKOS inverses and top concepts required by browsers."""
    concepts = set(graph.subjects(RDF.type, SKOS.Concept))
    schemes = set(graph.subjects(RDF.type, SKOS.ConceptScheme))
    if len(schemes) != 1:
        raise ValueError(f"Expected one concept scheme, found {len(schemes)}")
    scheme = next(iter(schemes))
    broader = list(graph.subject_objects(SKOS.broader))
    for child, parent in broader:
        graph.add((parent, SKOS.narrower, child))
    roots = {concept for concept in concepts if not any(graph.objects(concept, SKOS.broader))}
    if not roots:
        raise ValueError("Hierarchy has no root concepts")
    for root in roots:
        graph.add((root, SKOS.topConceptOf, scheme))
        graph.add((scheme, SKOS.hasTopConcept, root))
    return roots


def write_graph(graph, path, rdf_format):
    graph.serialize(destination=path, format=rdf_format, encoding="utf-8")


def copy_csv_and_parquet(source, csv_target, parquet_target):
    shutil.copyfile(source, csv_target)
    with source.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    pq.write_table(pa.Table.from_pylist(rows), parquet_target, compression="zstd")


def combine_csv_and_parquet(sources, csv_target, parquet_target):
    rows = []
    fields = []
    for source in sources:
        with source.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fields.extend(field for field in reader.fieldnames if field not in fields)
            rows.extend(reader)
    with csv_target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    pq.write_table(pa.Table.from_pylist(rows), parquet_target, compression="zstd")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    config_path = (root / args.config).resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    release_id = config["release_id"]
    base = config["namespace_base"].rstrip("/") + "/"
    output = root / "dist" / "releases" / release_id
    output.mkdir(parents=True, exist_ok=True)

    sources = root / "dist" / "livestock-staging"
    livestock = rewrite_graph(sources / "aom-livestock.ttl", base)
    materialize_browser_hierarchy(livestock)
    schema = rewrite_graph(sources / "aom-schema.ttl", base)
    bindings = rewrite_graph(sources / "aom-semantic-bindings.ttl", base)

    formats = {
        "ttl": "turtle",
        "jsonld": "json-ld",
        "rdf": "xml",
    }
    for suffix, rdf_format in formats.items():
        write_graph(livestock, output / f"aom-livestock.{suffix}", rdf_format)
    for suffix, rdf_format in {"ttl": "turtle", "rdf": "xml"}.items():
        write_graph(schema, output / f"aom-schema.{suffix}", rdf_format)
    for suffix, rdf_format in {"ttl": "turtle", "jsonld": "json-ld"}.items():
        write_graph(bindings, output / f"aom-semantic-bindings.{suffix}", rdf_format)

    copy_csv_and_parquet(
        sources / "nodes.csv", output / "nodes.csv", output / "nodes.parquet"
    )
    copy_csv_and_parquet(
        sources / "edges.csv", output / "edges.csv", output / "edges.parquet"
    )
    copy_csv_and_parquet(
        root / "data" / "livestock-staging" / "approved_deprecations.csv",
        output / "migration-crosswalk.csv",
        output / "migration-crosswalk.parquet",
    )
    copy_csv_and_parquet(
        root / "data" / "livestock-staging" / "approved_ingredient_harmonization_rules.csv",
        output / "ingredient-harmonization-rules.csv",
        output / "ingredient-harmonization-rules.parquet",
    )
    combine_csv_and_parquet(
        [
            root / "data" / "livestock-staging" / "approved_feed_material_facets.csv",
            root / "data" / "livestock-staging" / "approved_generated_feed_material_facets.csv",
            root / "data" / "livestock-staging" / "approved_hard_tail_feed_material_facets.csv",
        ],
        output / "feed-material-facets.csv",
        output / "feed-material-facets.parquet",
    )
    shutil.copyfile(config_path, output / "release.json")
    shutil.copyfile(root / "LICENSE.md", output / "LICENSE.md")
    shutil.copyfile(root / "CITATION.cff", output / "CITATION.cff")

    files = sorted(path for path in output.iterdir() if path.name not in {
        "manifest.json", "checksums.sha256"
    })
    staging_manifest = sources / "manifest.json"
    manifest = {
        **config,
        "manifest_schema_version": "1.0.0",
        "source_staging_manifest_sha256": sha256(staging_manifest),
        "counts": {
            "livestock_triples": len(livestock),
            "schema_triples": len(schema),
            "semantic_binding_triples": len(bindings),
        },
        "distributions": [
            {
                "path": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in files
        ],
        "publication_gates": {
            "namespace_registered": False,
            "live_content_negotiation": False,
            "skosmos_deployment": False,
            "agroportal_registration": False,
            "named_reviewer": False,
            "canonical_cutover_approved": False,
        },
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    checksum_files = [*files, manifest_path]
    (output / "checksums.sha256").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in checksum_files),
        encoding="utf-8",
    )
    print(
        f"Built {release_id}: {len(livestock)} livestock, {len(schema)} schema, "
        f"{len(bindings)} binding triples."
    )


if __name__ == "__main__":
    main()
