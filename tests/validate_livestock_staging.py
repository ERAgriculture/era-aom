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
resolutions = read("approved_identity_resolutions")
replacements = read("approved_mapping_replacements")
deprecations = read("approved_deprecations")
manifest = json.loads((DIST / "manifest.json").read_text())
ids = [row["concept_id"] for row in concepts]
known = set(ids)
assert len(legacy) == 2503
assert len(ids) == 2501 and len(ids) == len(known)
assert "AOM_006275" in known
assert "duplicate_concept_id" not in {row["reason"] for row in quarantine}
assert "duplicate_derived_path" in {row["reason"] for row in quarantine}
assert all(row["subject_id"] in known and row["object_id"] in known for row in relations)
assert all(row["subject_id"] in known for row in mappings)
reviewed = [row for row in mappings if row["status"] == "reviewed"]
assert len(reviewed) == 3
assert {row["subject_id"] for row in reviewed} == {"AOM_006275"}
assert {row["target_id"] for row in reviewed} == {
    "NCBITaxon_3031383", "wfo-0000883036", "413",
}
assert all(row["reviewer"] == "Pete Steward" for row in reviewed)
assert all(
    row["status"] == "legacy-unreviewed" and row["reviewer"] == ""
    for row in mappings if row not in reviewed
)
assert len(resolutions) == 2
assert {row["action"] for row in resolutions} == {"retain", "map_to_existing"}
assert {row["resolved_concept_id"] for row in resolutions} == {
    "AOM_006275", "AOM_001676",
}
assert len(replacements) == 3
assert len(deprecations) == 1
assert deprecations[0]["deprecated_id"] == "AOM_001884"
assert deprecations[0]["replacement_id"] == "AOM_000564"
status = {row["concept_id"]: row["status"] for row in concepts}
assert status["AOM_001884"] == "deprecated"
brewers_pref = next(
    row["label"] for row in labels
    if row["concept_id"] == "AOM_000564" and row["label_type"] == "pref"
)
assert brewers_pref == "Brewers grains, dehydrated"
brewers_aliases = {
    row["label"] for row in labels
    if row["concept_id"] == "AOM_000564" and row["label_type"] == "alt"
}
assert {"Brewers Grain", "Brewers By-Product", "Distillers Grains"} <= brewers_aliases
assert {
    (row["subject_id"], row["relation_type"], row["object_id"])
    for row in relations
    if row["relation_type"] == "replaced_by"
} == {("AOM_001884", "replaced_by", "AOM_000564")}
approved_aliases = {
    row["label"] for row in labels
    if row["concept_id"] == "AOM_001676"
    and row["source_column"] == "approved_identity_resolution"
}
assert approved_aliases == {"Panicum maximum Dried", "Panicum maximum hay"}
assert all(row["disposition"] == "review_and_mint_or_map_parent" for row in gaps)
pref = Counter(row["concept_id"] for row in labels if row["label_type"] == "pref")
assert set(pref) == known and all(count == 1 for count in pref.values())
parents = {
    row["subject_id"]: row["object_id"]
    for row in relations if row["relation_type"] == "broader"
}
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
assert manifest["counts"]["hierarchy_relations"] == len(parents)
assert manifest["counts"]["replacement_relations"] == 1
assert manifest["counts"]["hierarchy_gaps"] == len(gaps)
assert manifest["counts"]["mapping_assertions"] == len(mappings)
assert manifest["counts"]["approved_identity_resolutions"] == len(resolutions)
assert manifest["counts"]["approved_mapping_replacements"] == len(replacements)
assert manifest["counts"]["approved_deprecations"] == len(deprecations)
print("Livestock staging validation passed:", len(concepts), "concepts,",
      len(relations), "relations,", len(gaps), "gaps,", len(mappings), "mappings")
