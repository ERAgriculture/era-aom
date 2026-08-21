#!/usr/bin/env python3
"""Validate accepted ADR 0049 implementation and explicit holds."""

import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

from rdflib import DCTERMS, Graph, Literal, OWL, SKOS, URIRef


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW = ROOT / "review/livestock-v40"
CONCEPT = "urn:era-aom:livestock:"
SCHEMA = "urn:era-aom:schema:"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


generated_paths = [
    ROOT / "config/identity-integrity-baseline.json",
    DATA / "approved_component_retention_relations.csv",
    DATA / "approved_definition_enrichments.csv",
    DATA / "approved_definition_overrides.csv",
    DATA / "approved_deprecations.csv",
    DATA / "approved_external_resource_labels.csv",
    DATA / "approved_feed_material_facets.csv",
    DATA / "approved_feed_taxonomy_classifications.csv",
    DATA / "approved_hard_tail_feed_material_facets.csv",
    DATA / "approved_hierarchy_revisions.csv",
    DATA / "approved_ingredient_component_value_holds.csv",
    DATA / "approved_ingredient_component_value_mappings.csv",
    DATA / "approved_ingredient_facet_concepts.csv",
    DATA / "approved_label_additions.csv",
    DATA / "approved_label_corrections.csv",
    DATA / "approved_mapping_additions.csv",
    DATA / "approved_new_concepts.csv",
    DATA / "livestock_id_registry.csv",
    *sorted(REVIEW.iterdir()),
]
subprocess.run(
    ["python3", "scripts/build_composition_form_implementation.py"],
    cwd=ROOT,
    check=True,
    capture_output=True,
    text=True,
)
first = {path: digest(path) for path in generated_paths}
subprocess.run(
    ["python3", "scripts/build_composition_form_implementation.py"],
    cwd=ROOT,
    check=True,
    capture_output=True,
    text=True,
)
assert first == {path: digest(path) for path in generated_paths}

summary = json.loads((REVIEW / "composition_form_implementation_summary.json").read_text())
assert summary == {
    "status": "implemented-candidate",
    "decision": "docs/decisions/0049-composition-form-and-component-retention-model.md",
    "reviewed_concepts": 40,
    "approved_dispositions": 38,
    "held_dispositions": 2,
    "implementation_status_counts": {
        "confirmed-no-change": 17,
        "deprecated-with-replacement": 3,
        "held-no-semantic-change": 2,
        "implemented": 17,
        "verified-existing-deprecation": 1,
    },
    "new_navigation_concepts": 1,
    "identifier_frontier": 101182,
    "deprecated_with_replacement": 3,
    "renamed_concepts": 6,
    "hierarchy_moves": 3,
    "browse_hierarchy_suppressions": 1,
    "external_mappings": 6,
    "exact_external_mappings": 4,
    "broad_external_mappings": 2,
    "material_assertions_reviewed": 796,
    "material_assertions_retained_unchanged": 792,
    "material_assertions_migrated": 3,
    "material_assertions_removed": 1,
    "material_assertions_added": 1,
    "raw_component_bindings_held": 1,
    "reviewer": "Pete Steward",
    "implementation_date": "2026-08-21",
}

implementation = read(REVIEW / "composition_form_implementation_register.csv")
holds = read(REVIEW / "implementation_holds.csv")
migrations = read(REVIEW / "material_assertion_migration_register.csv")
mappings = read(REVIEW / "chemical_mapping_implementation.csv")
binding_migrations = read(REVIEW / "component_binding_migration_register.csv")
collisions = read(REVIEW / "identity_collision_audit.csv")
specific = read(REVIEW / "specific_material_implementation.csv")
assert len(implementation) == 40
assert Counter(row["review_status"] for row in implementation) == {
    "approved": 38, "held": 2,
}
assert Counter(row["implementation_status"] for row in implementation) == {
    "confirmed-no-change": 17,
    "deprecated-with-replacement": 3,
    "held-no-semantic-change": 2,
    "implemented": 17,
    "verified-existing-deprecation": 1,
}
assert {row["concept_id"] for row in holds} == {"AOM_101050", "AOM_101064"}
assert len(migrations) == 5
assert Counter(row["implementation_action"] for row in migrations) == {
    "migrated-property": 2,
    "migrated-property-and-target": 1,
    "removed-category-error": 1,
    "added-product-role": 1,
}
assert len(mappings) == 6
assert Counter(row["mapping_relation"] for row in mappings) == {
    "exactMatch": 4, "broadMatch": 2,
}
assert len(binding_migrations) == 1
assert binding_migrations[0]["implementation_action"] == "migrated-to-ambiguity-hold"
assert len(collisions) == 9
assert Counter(row["decision"] for row in collisions) == {
    "implemented-no-collision": 7, "rejected-collision": 2,
}
assert len(specific) == 3

concepts = {row["concept_id"]: row for row in read(DATA / "concepts.csv")}
labels = {
    row["concept_id"]: row["label"]
    for row in read(DATA / "labels.csv")
    if row["label_type"] == "pref" and row["language"] == "en"
}
relations = read(DATA / "relations.csv")
broader = {
    (row["subject_id"], row["object_id"])
    for row in relations if row["relation_type"] == "broader"
}
assert labels["AOM_000326"] == "Feed physical characteristics"
assert labels["AOM_101182"] == "Feed physical descriptors"
assert labels["AOM_101115"] == "Feed component-retention states"
assert labels["AOM_101086"] == "Whole-crop component retention"
assert labels["AOM_101110"] == "Whole-grain component retention"
assert labels["AOM_101134"] == "Native-fat retention"
assert labels["AOM_101067"] == "Essential oil constituent"
assert ("AOM_101182", "AOM_000328") in broader
assert {
    ("AOM_101020", "AOM_101182"),
    ("AOM_101132", "AOM_101182"),
    ("AOM_101133", "AOM_101182"),
    ("AOM_101086", "AOM_101115"),
    ("AOM_101110", "AOM_101115"),
    ("AOM_101134", "AOM_101115"),
} <= broader
assert ("AOM_101050", "AOM_101020") in broader
assert ("AOM_101064", "AOM_101023") in broader

replacement_by_id = {
    row["deprecated_id"]: row["replacement_id"]
    for row in read(DATA / "approved_deprecations.csv")
}
expected_replacements = {
    "AOM_000324": "AOM_101182",
    "AOM_101116": "AOM_101134",
    "AOM_101080": "AOM_000226",
}
assert {key: replacement_by_id[key] for key in expected_replacements} == expected_replacements
assert all(concepts[concept_id]["status"] == "deprecated" for concept_id in expected_replacements)
assert not any(subject in expected_replacements for subject, _ in broader)
revisions = [
    row for row in read(DATA / "approved_hierarchy_revisions.csv")
    if row["case_id"].startswith("COMPOSITION-FORM-")
]
assert len(revisions) == 4
removal_only = [row for row in revisions if not row["add_parent_id"]]
assert len(removal_only) == 1
assert removal_only[0]["child_id"] == "AOM_000324"
assert removal_only[0]["remove_parent_id"] == "AOM_000326"

mapping_additions = [
    row for row in read(DATA / "approved_mapping_additions.csv")
    if row["case_id"].startswith("COMPOSITION-FORM-")
]
assert len(mapping_additions) == 6
assert Counter(row["mapping_relation"] for row in mapping_additions) == {
    "exactMatch": 4, "broadMatch": 2,
}

facet_files = [
    "approved_feed_material_facets.csv",
    "approved_generated_feed_material_facets.csv",
    "approved_hard_tail_feed_material_facets.csv",
    "approved_structural_feed_material_facets.csv",
]
facets = [row for name in facet_files for row in read(DATA / name)]
assert len(facets) == 2884
assert not any(row["target_property"] == "aom:compositionState" for row in facets)
retention = {
    (row["feed_material_id"], row["target_concept_id"])
    for row in facets if row["target_property"] == "aom:componentRetentionState"
}
assert len(retention) == 8
assert {
    ("AOM_000555", "AOM_101134"),
    ("AOM_000611", "AOM_101134"),
    ("AOM_001317", "AOM_101134"),
} <= retention
assert not any(
    row["feed_material_id"] == "AOM_000538"
    and row["target_concept_id"] == "AOM_101080"
    for row in facets
)
assert any(
    row["feed_material_id"] == "AOM_001938"
    and row["target_property"] == "aom:productRole"
    and row["target_concept_id"] == "AOM_101062"
    for row in facets
)
assert any(
    row["feed_material_id"] == "AOM_000764"
    and row["target_property"] == "aom:presentationForm"
    and row["target_concept_id"] == "AOM_101049"
    for row in facets
)
assert not any(
    row["feed_material_id"] == "AOM_000766"
    and row["target_property"] == "aom:presentationForm"
    for row in facets
)

raw_mappings = read(DATA / "approved_ingredient_component_value_mappings.csv")
raw_holds = read(DATA / "approved_ingredient_component_value_holds.csv")
assert not any(
    row["source_value"] == "Ash" and row["target_concept_id"] == "AOM_101080"
    for row in raw_mappings
)
assert any(
    row["source_value"] == "Ash" and row["binding_action"] == "hold_ambiguous"
    for row in raw_holds
)

definitions = {row["concept_id"]: row["definition"] for row in read(DATA / "definitions.csv")}
assert "measurable or observable" in definitions["AOM_000326"].casefold()
assert "categorical physical descriptors" in definitions["AOM_101182"]
assert "Positive states" in definitions["AOM_101115"]
assert "positive retention of native fat" in definitions["AOM_101134"]
assert "consumption method" in definitions["AOM_000764"]
assert "consumption by licking" in definitions["AOM_000766"]
assert "product role — By-product role" in definitions["AOM_001938"]
assert "Rendering" not in definitions["AOM_001938"]
assert "Whole-grain component retention" in definitions["AOM_001313"]
assert "Whole-crop component retention" in definitions["AOM_001326"]

livestock = Graph().parse(ROOT / "dist/livestock-staging/aom-livestock.ttl")
bindings = Graph().parse(ROOT / "dist/livestock-staging/aom-semantic-bindings.ttl")
for old_id, replacement_id in expected_replacements.items():
    old = URIRef(CONCEPT + old_id)
    assert (old, OWL.deprecated, Literal(True)) in livestock
    assert not any(livestock.objects(old, SKOS.broader))
    assert (old, DCTERMS.isReplacedBy, URIRef(CONCEPT + replacement_id)) in livestock
for concept_id, relation, target_uri in [
    ("AOM_001577", SKOS.exactMatch, "https://www.ebi.ac.uk/chebi/CHEBI%3A16646"),
    ("AOM_001571", SKOS.exactMatch, "https://www.ebi.ac.uk/chebi/CHEBI%3A36080"),
    ("AOM_101065", SKOS.exactMatch, "https://www.ebi.ac.uk/chebi/CHEBI%3A28017"),
    ("AOM_101067", SKOS.exactMatch, "https://www.ebi.ac.uk/chebi/CHEBI%3A83630"),
    ("AOM_101066", SKOS.broadMatch, "https://www.ebi.ac.uk/chebi/CHEBI%3A18059"),
    ("AOM_101081", SKOS.broadMatch, "https://www.ebi.ac.uk/chebi/CHEBI%3A18059"),
]:
    assert (URIRef(CONCEPT + concept_id), relation, URIRef(target_uri)) in livestock
for material_id in {"AOM_000555", "AOM_000611", "AOM_001317"}:
    assert (
        URIRef(CONCEPT + material_id),
        URIRef(SCHEMA + "componentRetentionState"),
        URIRef(CONCEPT + "AOM_101134"),
    ) in bindings
assert (
    URIRef(CONCEPT + "AOM_001938"),
    URIRef(SCHEMA + "productRole"),
    URIRef(CONCEPT + "AOM_101062"),
) in bindings

adr = (ROOT / "docs/decisions/0049-composition-form-and-component-retention-model.md").read_text()
method = (ROOT / "docs/methods/composition-form-and-retention-governance.md").read_text()
assert "- Status: Accepted" in adr and "## Evidence" in adr
assert "accepted by pete" in adr.casefold()
assert "Held Lick and" in method and "external mapping when exact" in method

print("Validated ADR 0049 implementation: 40 dispositions, 796 assertions, 2 holds")
