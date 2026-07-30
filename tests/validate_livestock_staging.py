#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
DIST = ROOT / "dist/livestock-staging"


def read(name):
    with (DATA / f"{name}.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


concepts, labels = read("concepts"), read("labels")
relations, mappings = read("relations"), read("mappings")
quarantine, gaps, legacy = read("quarantine"), read("hierarchy_gaps"), read("legacy_records")
manifest = json.loads((DIST / "manifest.json").read_text())
ids = [row["concept_id"] for row in concepts]
known = set(ids)
assert len(legacy) == 2503
assert len(ids) == 2500 and len(ids) == len(known)
assert "AOM_006275" not in known
assert {"duplicate_concept_id", "duplicate_derived_path"} <= {row["reason"] for row in quarantine}
assert all(row["subject_id"] in known and row["object_id"] in known for row in relations)
assert all(row["subject_id"] in known and row["status"] == "legacy-unreviewed" for row in mappings)
assert all(row["reviewer"] == "" for row in mappings)
assert all(row["disposition"] == "review_and_mint_or_map_parent" for row in gaps)
pref = Counter(row["concept_id"] for row in labels if row["label_type"] == "pref")
assert set(pref) == known and all(count == 1 for count in pref.values())
parents = {row["subject_id"]: row["object_id"] for row in relations}
for start in ids:
    seen, current = set(), start
    while current in parents:
        current = parents[current]
        assert current not in seen, f"Hierarchy cycle from {start}"
        seen.add(current)
assert manifest["status"] == "staging-not-canonical"
assert manifest["identifier_policy"]["rdf_uri_status"] == "provisional-staging-only"
assert manifest["counts"]["source_records"] == len(legacy)
assert manifest["counts"]["published_staging_concepts"] == len(concepts)
assert manifest["counts"]["hierarchy_relations"] == len(relations)
assert manifest["counts"]["hierarchy_gaps"] == len(gaps)
assert manifest["counts"]["mapping_assertions"] == len(mappings)
print("Livestock staging validation passed:", len(concepts), "concepts,",
      len(relations), "relations,", len(gaps), "gaps,", len(mappings), "mappings")
