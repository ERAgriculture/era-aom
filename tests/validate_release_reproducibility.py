#!/usr/bin/env python3
"""Validate deterministic release writers, runtime pins, and clean-worktree gate."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pyarrow.parquet as pq
from rdflib import Graph, Literal, RDF, URIRef


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from release_reproducibility import (
    RUNTIME_CONTRACT,
    validate_runtime_contract,
    write_jsonld,
    write_rdfxml,
)


assert validate_runtime_contract() == RUNTIME_CONTRACT
requirements = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8").splitlines()
assert set(requirements) == {
    "pyshacl==0.40.1",
    "rdflib==7.6.0",
    "pyarrow==24.0.0",
    "PyYAML==6.0.2",
}

subject_a = URIRef("https://example.org/a")
subject_b = URIRef("https://example.org/b")
predicate = URIRef("http://www.w3.org/2004/02/skos/core#prefLabel")
triples = [
    (subject_b, RDF.type, URIRef("http://www.w3.org/2004/02/skos/core#Concept")),
    (subject_a, predicate, Literal("Alpha", lang="en")),
    (subject_b, predicate, Literal("Beta", lang="en")),
]

with tempfile.TemporaryDirectory() as temporary:
    temporary = Path(temporary)
    first = Graph()
    second = Graph()
    for triple in triples:
        first.add(triple)
    for triple in reversed(triples):
        second.add(triple)
    first_json = temporary / "first.jsonld"
    second_json = temporary / "second.jsonld"
    first_rdf = temporary / "first.rdf"
    second_rdf = temporary / "second.rdf"
    write_jsonld(first, first_json)
    write_jsonld(second, second_json)
    write_rdfxml(first, first_rdf)
    write_rdfxml(second, second_rdf)
    assert first_json.read_bytes() == second_json.read_bytes()
    assert first_rdf.read_bytes() == second_rdf.read_bytes()
    assert set(Graph().parse(first_json)) == set(first)
    assert set(Graph().parse(first_rdf)) == set(first)

manifest = json.loads(
    (ROOT / "dist/releases/2026.1-rc.1/manifest.json").read_text(encoding="utf-8")
)
assert manifest["reproducibility_contract"] == {
    "byte_identity": "required",
    "rdf_graph_equivalence": "required",
    "parquet_table_equivalence": "required",
    "runtime": RUNTIME_CONTRACT,
}
for name in (
    "nodes.parquet",
    "edges.parquet",
    "migration-crosswalk.parquet",
    "ingredient-harmonization-rules.parquet",
    "feed-material-facets.parquet",
):
    metadata = pq.read_metadata(ROOT / "dist/releases/2026.1-rc.1" / name)
    assert metadata.created_by == "parquet-cpp-arrow version 24.0.0"

with tempfile.TemporaryDirectory() as temporary:
    repository = Path(temporary)
    subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.org"], cwd=repository, check=True)
    subprocess.run(["git", "config", "user.name", "ERA test"], cwd=repository, check=True)
    tracked = repository / "tracked.txt"
    tracked.write_text("current\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=repository, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", "fixture"], cwd=repository, check=True)
    gate = ROOT / "scripts/validate_clean_rebuild.py"
    clean = subprocess.run([sys.executable, gate, "--root", repository])
    assert clean.returncode == 0
    tracked.write_text("stale\n", encoding="utf-8")
    dirty = subprocess.run(
        [sys.executable, gate, "--root", repository], capture_output=True, text=True
    )
    assert dirty.returncode != 0 and "tracked.txt" in dirty.stderr + dirty.stdout
    subprocess.run(["git", "restore", "tracked.txt"], cwd=repository, check=True)
    (repository / "untracked.txt").write_text("stale\n", encoding="utf-8")
    untracked = subprocess.run(
        [sys.executable, gate, "--root", repository], capture_output=True, text=True
    )
    assert untracked.returncode != 0 and "untracked.txt" in untracked.stderr + untracked.stdout

print("Release reproducibility validation passed: pinned writers, canonical RDF, clean gate")
