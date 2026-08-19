#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, SKOS


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "livestock-staging"
REVIEW = ROOT / "review" / "livestock-v36"
CONCEPT_BASE = "urn:era-aom:livestock:"
SCHEMA_BASE = "urn:era-aom:schema:"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


review_rows = read(ROOT / "review/livestock-v35/process_axis_review.csv")
implementation = read(REVIEW / "process_axis_implementation_register.csv")
collisions = read(REVIEW / "identity_collision_audit.csv")
defatting_holds = read(REVIEW / "defatting_material_migration_holds.csv")
axis_relations = read(DATA / "approved_process_axis_relations.csv")
new_concepts = read(DATA / "approved_new_concepts.csv")
registry = read(DATA / "livestock_id_registry.csv")
semantic_types = read(DATA / "approved_concept_semantic_types.csv")
facet_concepts = read(DATA / "approved_ingredient_facet_concepts.csv")
relations = read(DATA / "relations.csv")
labels = read(DATA / "labels.csv")
definitions = read(DATA / "definitions.csv")
summary = json.loads((REVIEW / "process_axis_implementation_summary.json").read_text())

assert len(review_rows) == len(implementation) == 54
assert Counter(row["status"] for row in review_rows) == {"approved": 51, "held": 3}
assert {row["concept_id"] for row in review_rows if row["status"] == "held"} == {
    "AOM_004500", "AOM_101069", "AOM_101123"
}
assert all(row["reviewer"] == "Pete Steward" for row in implementation)
assert all(row["implementation_date"] == "2026-08-18" for row in implementation)
assert all("0047-feed-process-objective-benefit-and-effect-model.md" in row["decision_record"] for row in implementation)

new_ids = {f"AOM_{number}" for number in range(101163, 101180)}
new_by_id = {row["concept_id"]: row for row in new_concepts}
assert new_ids <= set(new_by_id)
assert new_by_id["AOM_101163"]["broader_id"] == "AOM_000845"
assert new_by_id["AOM_101168"]["broader_id"] == "AOM_000328"
assert not new_by_id["AOM_101168"]["child_ids"]
assert new_by_id["AOM_101069"]["preferred_label"] == "Fat removal"

registered = {row["concept_id"]: row for row in registry}
assert all(registered[concept_id]["status"] == "allocated" for concept_id in new_ids)
assert len(collisions) == 18
assert all(row["decision"] == "approved-no-collision" for row in collisions)
assert all(not row["matched_concept_ids"] and row["external_label_match"] == "false" for row in collisions)

type_by_id = {row["concept_id"]: row["semantic_class"] for row in semantic_types}
for concept_id in {"AOM_100990", "AOM_100991", "AOM_000837", "AOM_000826", "AOM_101163"}:
    assert type_by_id[concept_id] == "aom:ProcessMechanism"
for concept_id in {
    "AOM_101129", "AOM_101130", "AOM_101131", "AOM_000842", "AOM_101069",
    "AOM_101164", "AOM_101165", "AOM_101166", "AOM_101167",
}:
    assert type_by_id[concept_id] == "aom:ProcessTechnicalObjective"
for concept_id in {f"AOM_{number}" for number in range(101168, 101180)}:
    assert type_by_id[concept_id] == "aom:FeedBenefit"
assert type_by_id["AOM_101084"] == "aom:ProductionProcess"

facet_by_id = {row["concept_id"]: row for row in facet_concepts}
assert not {"AOM_101069", "AOM_101129", "AOM_101130", "AOM_101131"} & set(facet_by_id)
assert facet_by_id["AOM_101084"]["target_property"] == "aom:productionProcessProvenance"
assert facet_by_id["AOM_101084"]["value_class"] == "aom:ProductionProcess"

material_facets = []
for filename in [
    "approved_feed_material_facets.csv",
    "approved_generated_feed_material_facets.csv",
    "approved_hard_tail_feed_material_facets.csv",
    "approved_structural_feed_material_facets.csv",
]:
    material_facets.extend(read(DATA / filename))
assert not [row for row in material_facets if row["target_concept_id"] == "AOM_101069"]
sugar_rows = [row for row in material_facets if row["target_concept_id"] == "AOM_101084"]
assert {(row["feed_material_id"], row["target_property"]) for row in sugar_rows} == {
    ("AOM_000642", "aom:productionProcessProvenance"),
    ("AOM_001482", "aom:productionProcessProvenance"),
    ("AOM_006003", "aom:productionProcessProvenance"),
}
assert len(defatting_holds) == 8
assert all(row["status"] == "held" for row in defatting_holds)

assert len(axis_relations) == 166
assert Counter(row["relation_property"] for row in axis_relations) == {
    "aom:processMechanism": 35,
    "aom:technicalProcessObjective": 44,
    "aom:maySupportFeedBenefit": 87,
}
assert len({row["case_id"] for row in axis_relations}) == 166
assert all(row["status"] == "approved" and row["reviewer"] == "Pete Steward" for row in axis_relations)

parents = defaultdict(set)
for row in relations:
    if row["relation_type"] == "broader":
        parents[row["subject_id"]].add(row["object_id"])
assert "AOM_101163" in parents["AOM_000820"]
assert not {"AOM_100990", "AOM_000145"} & parents["AOM_000820"]
assert "AOM_101166" in parents["AOM_003202"]
assert "AOM_100991" not in parents["AOM_003202"]
assert parents["AOM_101069"] == {"AOM_101130"}

preferred = {row["concept_id"]: row["label"] for row in labels if row["language"] == "en" and row["label_type"] == "pref"}
assert preferred["AOM_101069"] == "Fat removal"
assert preferred["AOM_101163"] == "Enzymatic or biochemical feed processes"
definition_by_id = {row["concept_id"]: row["definition"] for row in definitions}
assert "does not identify" in definition_by_id["AOM_101069"].lower() or "exact operation" in definition_by_id["AOM_101069"].lower()
assert "resulting effects require separate" in definition_by_id["AOM_000820"].lower()

ontology = Graph().parse(ROOT / "schemas/owl/aom-semantic-model.ttl")
for property_name, domain_name, range_name, label in [
    ("processMechanism", "ProcessingMethod", "ProcessMechanism", "has process mechanism"),
    ("technicalProcessObjective", "ProcessingMethod", "ProcessTechnicalObjective", "has technical process objective"),
    ("maySupportFeedBenefit", "ProcessingMethod", "FeedBenefit", "may support feed benefit"),
    ("productionProcessProvenance", "FeedMaterial", "ProductionProcess", "has production-process provenance"),
    ("observedProcessEffect", "ProcessApplication", "http://www.w3.org/ns/sosa/Observation", "has observed process effect"),
]:
    property_uri = URIRef(SCHEMA_BASE + property_name)
    range_uri = URIRef(range_name if range_name.startswith("http") else SCHEMA_BASE + range_name)
    assert (property_uri, RDFS.domain, URIRef(SCHEMA_BASE + domain_name)) in ontology
    assert (property_uri, RDFS.range, range_uri) in ontology
    assert (property_uri, RDFS.label, Literal(label, lang="en")) in ontology

bindings = Graph().parse(ROOT / "dist/livestock-staging/aom-semantic-bindings.ttl")
def concept(concept_id):
    return URIRef(CONCEPT_BASE + concept_id)

assert (concept("AOM_000836"), URIRef(SCHEMA_BASE + "processMechanism"), concept("AOM_000837")) in bindings
assert (concept("AOM_000836"), URIRef(SCHEMA_BASE + "technicalProcessObjective"), concept("AOM_101129")) in bindings
assert (concept("AOM_000833"), URIRef(SCHEMA_BASE + "processMechanism"), concept("AOM_000826")) in bindings
assert (concept("AOM_000833"), URIRef(SCHEMA_BASE + "processMechanism"), concept("AOM_000837")) in bindings
assert (concept("AOM_000820"), URIRef(SCHEMA_BASE + "processMechanism"), concept("AOM_101163")) in bindings
assert not (concept("AOM_000820"), URIRef(SCHEMA_BASE + "processMechanism"), concept("AOM_100990")) in bindings
assert (concept("AOM_003202"), URIRef(SCHEMA_BASE + "technicalProcessObjective"), concept("AOM_101166")) in bindings
assert not (concept("AOM_003202"), URIRef(SCHEMA_BASE + "processMechanism"), concept("AOM_100991")) in bindings
for material_id in {"AOM_000642", "AOM_001482", "AOM_006003"}:
    assert (concept(material_id), URIRef(SCHEMA_BASE + "productionProcessProvenance"), concept("AOM_101084")) in bindings
assert not list(bindings.triples((None, URIRef(SCHEMA_BASE + "observedProcessEffect"), None)))

assert summary == {
    "status": "implemented-candidate",
    "decision": "docs/decisions/0047-feed-process-objective-benefit-and-effect-model.md",
    "reviewed_rows": 54,
    "approved_rows": 51,
    "held_rows": 3,
    "new_axis_concepts": 17,
    "new_mechanism_concepts": 1,
    "new_objective_concepts": 4,
    "new_benefit_concepts_including_root": 12,
    "explicit_axis_relations": 166,
    "defatting_material_migration_holds": 8,
    "sugar_provenance_migrations": 3,
    "observed_effect_assertions": 0,
    "identifier_frontier": 101179,
    "reviewer": "Pete Steward",
    "implementation_date": "2026-08-18",
}
print("Validated Cohort C process-axis implementation: 54 dispositions, 166 relations, 3 holds")
