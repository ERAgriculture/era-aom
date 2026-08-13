#!/usr/bin/env python3
import csv
import hashlib
import json
from pathlib import Path

from rdflib import Graph, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import OWL, SKOS


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "livestock-staging"
RELEASE = ROOT / "dist" / "releases" / "2026.1-rc.1"
OUT = ROOT / "review" / "livestock-v32"
LIFECYCLE_PATH = OUT / "ingredient_descriptor_lifecycle_inventory.csv"
PIPELINE_PATH = OUT / "ingredient_descriptor_pipeline_inventory.csv"
SUMMARY_PATH = OUT / "ingredient_descriptor_summary.json"
CONSUMER_AUDIT_PATH = OUT / "ingredient_descriptor_consumer_audit.csv"

CONCEPT_IDS = [
    "AOM_000531",
    "AOM_000532",
    "AOM_000533",
    "AOM_000534",
    "AOM_000535",
]
FEED_MATERIALS = "AOM_100850"
URI_PREFIX = "https://w3id.org/era-aom/livestock/"
SCHEMA_PREFIX = "urn:era-aom:schema:"
ERA = Namespace("urn:era:property:")

PIPELINE_ARTIFACTS = [
    ("data/livestock-staging/concepts.csv", "governed-concept-state", "source"),
    ("data/livestock-staging/relations.csv", "governed-browse-hierarchy", "source"),
    ("data/livestock-staging/approved_concept_retirements.csv", "retirement-decision", "governance"),
    ("data/livestock-staging/approved_semantic_bindings.csv", "legacy-to-schema-contract", "governance"),
    ("schemas/owl/aom-semantic-model.ttl", "formal-schema", "source"),
    ("scripts/normalize_livestock_release.py", "livestock-normalizer", "generator"),
    ("dist/livestock-staging/aom-livestock.ttl", "staging-browser-graph", "generated"),
    ("dist/releases/2026.1-rc.1/aom-livestock.ttl", "canonical-browser-graph", "generated"),
    ("dist/releases/2026.1-rc.1/aom-livestock.jsonld", "canonical-jsonld", "generated"),
    ("dist/releases/2026.1-rc.1/aom-semantic-bindings.ttl", "canonical-binding-graph", "generated"),
    ("config/skosmos/era-aom.ttl", "local-browser-configuration", "deployment"),
    ("config/skosmos/era-aom-production.ttl", "production-browser-configuration", "deployment"),
]


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def qname_to_uri(value):
    prefixes = {
        "aom": SCHEMA_PREFIX,
        "qudt": "http://qudt.org/schema/qudt/",
        "skos": str(SKOS),
        "xsd": "http://www.w3.org/2001/XMLSchema#",
    }
    if ":" not in value:
        return URIRef(value)
    prefix, local = value.split(":", 1)
    return URIRef(prefixes[prefix] + local)


def compact(value):
    if value is None:
        return ""
    text = str(value)
    prefixes = {
        SCHEMA_PREFIX: "aom:",
        "http://qudt.org/schema/qudt/": "qudt:",
        "http://www.w3.org/2001/XMLSchema#": "xsd:",
        str(SKOS): "skos:",
        str(OWL): "owl:",
    }
    for prefix, qname in prefixes.items():
        if text.startswith(prefix):
            return qname + text[len(prefix):]
    return text


concepts = {row["concept_id"]: row for row in read_rows(DATA / "concepts.csv")}
labels = {
    row["concept_id"]: row["label"]
    for row in read_rows(DATA / "labels.csv")
    if row["language"] == "en" and row["label_type"] == "pref"
}
relations = read_rows(DATA / "relations.csv")
retirements = {
    row["concept_id"]: row
    for row in read_rows(DATA / "approved_concept_retirements.csv")
}
bindings = {
    row["legacy_concept_id"]: row
    for row in read_rows(DATA / "approved_semantic_bindings.csv")
}
schema = Graph().parse(DATA.parent.parent / "schemas" / "owl" / "aom-semantic-model.ttl")
release_graph = Graph().parse(RELEASE / "aom-livestock.ttl")

assert set(CONCEPT_IDS) <= concepts.keys()
assert set(CONCEPT_IDS) <= retirements.keys()
assert set(CONCEPT_IDS) <= bindings.keys()
assert all(concepts[concept_id]["status"] == "deprecated" for concept_id in CONCEPT_IDS)
assert all(retirements[concept_id]["status"] == "approved" for concept_id in CONCEPT_IDS)
assert all(bindings[concept_id]["status"] == "approved" for concept_id in CONCEPT_IDS)

parents = {
    concept_id: sorted(
        row["object_id"]
        for row in relations
        if row["subject_id"] == concept_id and row["relation_type"] == "broader"
    )
    for concept_id in CONCEPT_IDS
}
assert all(parent_ids == [FEED_MATERIALS] for parent_ids in parents.values())

recommendations = {
    "AOM_000531": {
        "card": "Preferred term; source-record label only in provenance view",
        "scope": "skos:prefLabel for canonical material; row-local source label on aom:IngredientComponent",
    },
    "AOM_000532": {
        "card": "Resolved material component, form, process, role, and constituent facets",
        "scope": "aom:legacyComponentDescriptor on aom:IngredientComponent only as unresolved provenance",
    },
    "AOM_000533": {
        "card": "Biological source",
        "scope": "aom:sourceTaxon on canonical aom:FeedMaterial; preserve row-local taxon assertion provenance",
    },
    "AOM_000534": {
        "card": "Inclusion proportion on formulation component",
        "scope": "aom:ingredientProportion on aom:IngredientComponent with qudt:QuantityValue and explicit unit/basis",
    },
    "AOM_000535": {
        "card": "Acquisition source",
        "scope": "aom:ingredientSource relabeled and scoped to aom:IngredientComponent or procurement assertion",
    },
}

lifecycle_fields = [
    "concept_id",
    "preferred_label",
    "concept_status",
    "concept_type",
    "current_parent_ids",
    "current_parent_labels",
    "retirement_status",
    "retirement_rationale",
    "binding_kind",
    "target_class",
    "target_property",
    "target_property_type",
    "target_property_domain",
    "target_property_range",
    "value_class",
    "quantity_kind_uri",
    "unit_requirement",
    "compatibility_policy",
    "rdf_era_status_present",
    "rdf_owl_deprecated_present",
    "rdf_feed_material_browse_edge_present",
    "recommended_lifecycle",
    "recommended_browser_visibility",
    "recommended_card_field",
    "recommended_semantic_scope",
]

lifecycle_rows = []
for concept_id in CONCEPT_IDS:
    binding = bindings[concept_id]
    property_uri = qname_to_uri(binding["target_property"])
    concept_uri = URIRef(URI_PREFIX + concept_id)
    parent_uri = URIRef(URI_PREFIX + FEED_MATERIALS)
    property_types = sorted(compact(value) for value in schema.objects(property_uri, RDF.type))
    property_domains = sorted(compact(value) for value in schema.objects(property_uri, RDFS.domain))
    property_ranges = sorted(compact(value) for value in schema.objects(property_uri, RDFS.range))
    lifecycle_rows.append(
        {
            "concept_id": concept_id,
            "preferred_label": labels[concept_id],
            "concept_status": concepts[concept_id]["status"],
            "concept_type": concepts[concept_id]["concept_type"],
            "current_parent_ids": ";".join(parents[concept_id]),
            "current_parent_labels": ";".join(labels[parent_id] for parent_id in parents[concept_id]),
            "retirement_status": retirements[concept_id]["status"],
            "retirement_rationale": retirements[concept_id]["rationale"],
            "binding_kind": binding["binding_kind"],
            "target_class": binding["target_class"],
            "target_property": binding["target_property"],
            "target_property_type": ";".join(property_types),
            "target_property_domain": ";".join(property_domains),
            "target_property_range": ";".join(property_ranges),
            "value_class": binding["value_class"],
            "quantity_kind_uri": binding["quantity_kind_uri"],
            "unit_requirement": binding["unit_requirement"],
            "compatibility_policy": binding["compatibility_policy"],
            "rdf_era_status_present": str((concept_uri, ERA.status, None) in release_graph).lower(),
            "rdf_owl_deprecated_present": str((concept_uri, OWL.deprecated, None) in release_graph).lower(),
            "rdf_feed_material_browse_edge_present": str((concept_uri, SKOS.broader, parent_uri) in release_graph).lower(),
            "recommended_lifecycle": "retain-stable-id-as-deprecated-schema-identifier",
            "recommended_browser_visibility": "searchable-deprecated-card;exclude-from-active-feed-material-hierarchy",
            "recommended_card_field": recommendations[concept_id]["card"],
            "recommended_semantic_scope": recommendations[concept_id]["scope"],
        }
    )

OUT.mkdir(parents=True, exist_ok=True)
with LIFECYCLE_PATH.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=lifecycle_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(lifecycle_rows)

pipeline_fields = [
    "artifact_path",
    "artifact_role",
    "artifact_class",
    "sha256",
    "legacy_concept_ids_present",
    "target_properties_present",
    "current_effect",
]
pipeline_rows = []
property_names = sorted({binding["target_property"].split(":", 1)[1] for binding in bindings.values() if binding["legacy_concept_id"] in CONCEPT_IDS})
for relative_path, role, artifact_class in PIPELINE_ARTIFACTS:
    path = ROOT / relative_path
    text = path.read_text(encoding="utf-8")
    present_ids = [concept_id for concept_id in CONCEPT_IDS if concept_id in text]
    present_properties = [name for name in property_names if name in text]
    effects = {
        "governed-concept-state": "marks all five deprecated",
        "governed-browse-hierarchy": "still places all five directly beneath Feed materials",
        "retirement-decision": "approves retirement without replacement concepts",
        "legacy-to-schema-contract": "binds all five to properties or quantified component representation",
        "formal-schema": "defines replacement properties; four current domain choices require review",
        "livestock-normalizer": "applies custom status and retirement but retains derived broader edges and omits owl:deprecated",
        "staging-browser-graph": "publishes custom deprecated status plus Feed-material broader edges",
        "canonical-browser-graph": "deploys custom deprecated status plus Feed-material broader edges",
        "canonical-jsonld": "deploys same lifecycle and hierarchy semantics as Turtle",
        "canonical-binding-graph": "publishes machine-readable migration bindings",
        "local-browser-configuration": "enables notation search but does not declare deprecated visibility policy",
        "production-browser-configuration": "matches local deprecated visibility behavior",
    }
    pipeline_rows.append(
        {
            "artifact_path": relative_path,
            "artifact_role": role,
            "artifact_class": artifact_class,
            "sha256": file_sha256(path),
            "legacy_concept_ids_present": ";".join(present_ids),
            "target_properties_present": ";".join(present_properties),
            "current_effect": effects[role],
        }
    )

with PIPELINE_PATH.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=pipeline_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(pipeline_rows)

consumer_rows = read_rows(CONSUMER_AUDIT_PATH)
implementation_consumers = [
    row for row in consumer_rows
    if row["disposition"] == "consumer-migration-required"
]
assert len(consumer_rows) == 11
assert [row["repository"] for row in implementation_consumers] == ["era-data-pipeline"]

summary = {
    "status": "recommendation-only",
    "decision_status": "accepted-for-implementation-planning",
    "reviewer": "Pete Steward",
    "review_date": "2026-08-13",
    "review_issue": "https://github.com/ERAgriculture/era-program/issues/53",
    "source_commit": "2b9d5b4",
    "reviewed_legacy_concepts": len(CONCEPT_IDS),
    "deprecated_concepts": sum(row["concept_status"] == "deprecated" for row in lifecycle_rows),
    "approved_retirements": sum(row["retirement_status"] == "approved" for row in lifecycle_rows),
    "approved_semantic_bindings": len(lifecycle_rows),
    "current_feed_material_browse_edges": sum(row["rdf_feed_material_browse_edge_present"] == "true" for row in lifecycle_rows),
    "current_owl_deprecation_assertions": sum(row["rdf_owl_deprecated_present"] == "true" for row in lifecycle_rows),
    "pipeline_artifacts_audited": len(pipeline_rows),
    "repositories_audited": len(consumer_rows),
    "implementation_consumers_requiring_migration": len(implementation_consumers),
    "recommended_active_descriptor_branches": 0,
    "implementation_changes": 0,
    "allocated_identifiers": 0,
    "inputs": {
        "concepts_sha256": file_sha256(DATA / "concepts.csv"),
        "relations_sha256": file_sha256(DATA / "relations.csv"),
        "retirements_sha256": file_sha256(DATA / "approved_concept_retirements.csv"),
        "bindings_sha256": file_sha256(DATA / "approved_semantic_bindings.csv"),
        "release_turtle_sha256": file_sha256(RELEASE / "aom-livestock.ttl"),
    },
}
SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
