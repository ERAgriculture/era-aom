#!/usr/bin/env python3
"""Validate accepted ADR 0048 implementation and explicit holds."""

import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW = ROOT / "review/livestock-v38"
SCHEMA = "urn:era-aom:schema:"
CONCEPT = "urn:era-aom:livestock:"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


generated_paths = [
    DATA / "approved_component_retention_relations.csv",
    DATA / "approved_concept_retirements.csv",
    DATA / "approved_concept_semantic_types.csv",
    DATA / "approved_definition_enrichments.csv",
    DATA / "approved_definition_overrides.csv",
    DATA / "approved_deprecations.csv",
    DATA / "approved_external_resource_labels.csv",
    DATA / "approved_feed_material_facets.csv",
    DATA / "approved_feed_taxonomy_classifications.csv",
    DATA / "approved_generated_feed_material_facets.csv",
    DATA / "approved_hard_tail_feed_material_facets.csv",
    DATA / "approved_hierarchy_revisions.csv",
    DATA / "approved_ingredient_facet_concepts.csv",
    DATA / "approved_ingredient_harmonization_rules.csv",
    DATA / "approved_label_additions.csv",
    DATA / "approved_label_corrections.csv",
    DATA / "approved_mapping_additions.csv",
    DATA / "approved_new_concepts.csv",
    DATA / "livestock_id_registry.csv",
    ROOT / "review/livestock-v37/component_chemical_review.csv",
    ROOT / "review/livestock-v37/component_chemical_summary.json",
    ROOT / "review/livestock-v37/identity_overlap_review.csv",
    *sorted(REVIEW.iterdir()),
]
subprocess.run(
    ["python3", "scripts/build_component_chemical_identity_implementation.py"],
    cwd=ROOT,
    check=True,
    capture_output=True,
    text=True,
)
first = {path: digest(path) for path in generated_paths}
subprocess.run(
    ["python3", "scripts/build_component_chemical_identity_implementation.py"],
    cwd=ROOT,
    check=True,
    capture_output=True,
    text=True,
)
assert first == {path: digest(path) for path in generated_paths}

summary = json.loads((REVIEW / "component_chemical_implementation_summary.json").read_text())
assert summary == {
    "status": "implemented-candidate",
    "decision": "docs/decisions/0048-chemical-identity-composition-and-component-model.md",
    "reviewed_concepts": 164,
    "approved_dispositions": 145,
    "held_dispositions": 19,
    "new_navigation_concepts": 2,
    "identifier_frontier": 101181,
    "deprecated_with_replacement": 3,
    "retired_without_replacement": 3,
    "external_mappings": 20,
    "exact_external_mappings": 16,
    "related_external_mappings": 1,
    "close_external_mappings": 2,
    "broad_external_mappings": 1,
    "material_assertions_reviewed": 627,
    "material_assertions_removed": 66,
    "material_assertions_retargeted": 1,
    "material_assertions_repredicated": 5,
    "ingredient_part_assertions_retained": 509,
    "anatomical_children_reviewed": 31,
    "anatomical_mappings_held": 14,
    "reviewer": "Pete Steward",
    "implementation_date": "2026-08-20",
}

implementation = read(REVIEW / "component_chemical_implementation_register.csv")
holds = read(REVIEW / "implementation_holds.csv")
migrations = read(REVIEW / "material_assertion_migration_register.csv")
anatomy = read(REVIEW / "anatomical_mapping_implementation.csv")
collisions = read(REVIEW / "identity_collision_audit.csv")
assert len(implementation) == 164
assert Counter(row["review_status"] for row in implementation) == {
    "approved": 145, "held": 19,
}
assert Counter(row["implementation_status"] for row in implementation) == {
    "deprecated-with-replacement": 3,
    "held-no-semantic-change": 17,
    "implemented": 42,
    "retained-for-cohort-e": 99,
    "retired": 1,
    "retired-component-use;material-identity-held": 2,
}
assert len(holds) == 19 and all(row["status"] == "held" for row in holds)
assert len(migrations) == 627
assert Counter(row["implementation_action"] for row in migrations) == {
    "migrated-to-canonical-identity": 1,
    "migrated-to-component-retention-property": 5,
    "removed-tautological-component-assertion": 66,
    "retained-generated-assertion": 483,
    "retained-reviewed-assertion": 72,
}
assert len(anatomy) == 31
assert Counter(row["mapping_action"] for row in anatomy) == {
    "mapping-held": 14,
    "published-exactMatch": 16,
    "published-relatedMatch": 1,
}
assert all(
    "definition reviewed" in row["rationale"]
    for row in anatomy if row["mapping_action"].startswith("published-")
)
assert len(collisions) == 6
assert all(row["decision"].startswith("approved-") for row in collisions)

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
assert labels["AOM_101180"] == "Plant anatomical components"
assert labels["AOM_101181"] == "Animal anatomical components"
assert labels["AOM_101146"] == "Feed-related chemical entities"
assert labels["AOM_101023"] == "Chemical constituent categories"
assert labels["AOM_000196"] == "Feed composition characteristics"
assert labels["AOM_101029"] == "Plant embryo"
assert {("AOM_101180", "AOM_101019"), ("AOM_101181", "AOM_101019")} <= broader
assert ("AOM_101104", "AOM_101143") in broader
assert ("AOM_101115", "AOM_000328") in broader
assert ("AOM_101146", "AOM_000328") in broader
assert ("AOM_001571", "AOM_101146") in broader
assert ("AOM_001616", "AOM_101145") in broader

replacement_by_id = {
    row["deprecated_id"]: row["replacement_id"]
    for row in read(DATA / "approved_deprecations.csv")
}
assert {key: replacement_by_id[key] for key in {
    "AOM_101103", "AOM_101120", "AOM_101144",
}} == {
    "AOM_101103": "AOM_001616",
    "AOM_101120": "AOM_001571",
    "AOM_101144": "AOM_101143",
}
retired = {"AOM_101105", "AOM_101106", "AOM_101154"}
assert retired <= {row["concept_id"] for row in read(DATA / "approved_concept_retirements.csv")}
assert all(concepts[concept_id]["status"] == "deprecated" for concept_id in retired)
assert not any(subject in retired for subject, _ in broader)

mapping_additions = [
    row for row in read(DATA / "approved_mapping_additions.csv")
    if row["case_id"].startswith("COMPONENT-CHEMICAL-")
]
assert len(mapping_additions) == 20
assert Counter(row["mapping_relation"] for row in mapping_additions) == {
    "broadMatch": 1, "closeMatch": 2, "exactMatch": 16, "relatedMatch": 1,
}

facet_files = [
    "approved_feed_material_facets.csv",
    "approved_generated_feed_material_facets.csv",
    "approved_hard_tail_feed_material_facets.csv",
    "approved_structural_feed_material_facets.csv",
]
facets = [row for name in facet_files for row in read(DATA / name)]
assert len(facets) == 2884
assert not any(row["target_concept_id"] in retired for row in facets)
assert sum(row["target_property"] == "aom:ingredientPart" for row in facets) == 509
retention = [row for row in facets if row["target_property"] == "aom:componentRetentionState"]
assert len(retention) == 5
assert {row["target_concept_id"] for row in retention} == {"AOM_101086", "AOM_101110"}
assert not any(
    row["target_property"] == "aom:compositionState"
    and row["target_concept_id"] in {"AOM_101086", "AOM_101110"}
    for row in facets
)
assert sum(
    row["target_property"] == "aom:primaryConstituent"
    and row["target_concept_id"] == "AOM_001571"
    for row in facets
) >= 1

schema = Graph().parse(ROOT / "dist/livestock-staging/aom-schema.ttl")
bindings = Graph().parse(ROOT / "dist/livestock-staging/aom-semantic-bindings.ttl")
retention_property = URIRef(SCHEMA + "componentRetentionState")
assert (retention_property, RDFS.label, Literal("has component-retention state", lang="en")) in schema
assert (
    URIRef(CONCEPT + "AOM_001326"),
    retention_property,
    URIRef(CONCEPT + "AOM_101086"),
) in bindings
for old_id, replacement_id in replacement_by_id.items():
    if old_id not in {"AOM_101103", "AOM_101120", "AOM_101144"}:
        continue
    assert (
        URIRef(CONCEPT + old_id), DCTERMS.isReplacedBy, URIRef(CONCEPT + replacement_id)
    ) in Graph().parse(ROOT / "dist/livestock-staging/aom-livestock.ttl")
assert (
    URIRef(CONCEPT + "AOM_101029"),
    SKOS.relatedMatch,
    URIRef("http://purl.obolibrary.org/obo/PO_0009009"),
) in Graph().parse(ROOT / "dist/livestock-staging/aom-livestock.ttl")
assert (
    URIRef(CONCEPT + "AOM_101180"), RDF.type, URIRef(SCHEMA + "FeedMaterialPartCategory")
) in bindings

adr = (ROOT / "docs/decisions/0048-chemical-identity-composition-and-component-model.md").read_text()
method = (ROOT / "docs/methods/component-chemical-identity-governance.md").read_text()
assert "- Status: Accepted" in adr and "## Evidence" in adr
assert "## External mapping gate" in method and "## Holds" in method
assert "`build_definition_enrichment.py` must run before process-axis" in method

print("Validated ADR 0048 implementation: 164 dispositions, 627 assertion migrations, 19 holds")
