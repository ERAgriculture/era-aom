#!/usr/bin/env python3
import csv
import json
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, URIRef
from rdflib.namespace import RDF

ROOT = Path(__file__).resolve().parents[1]
OWL = ROOT / "schemas/owl/aom-semantic-model.ttl"
SHAPES = ROOT / "schemas/shacl/semantic-model.ttl"
REVIEW = ROOT / "review/livestock-v2"
FACET_REVIEW = ROOT / "review/livestock-v3"
DATA = ROOT / "data/livestock-staging"
DIST = ROOT / "dist/livestock-staging"
FIXTURES = ROOT / "tests/fixtures"

ontology = Graph().parse(OWL)
shapes = Graph().parse(SHAPES)
assert len(ontology) > 40
assert len(shapes) > 40

with (REVIEW / "schema_remodeling_candidates.csv").open(encoding="utf-8", newline="") as h:
    candidates = list(csv.DictReader(h))
with (REVIEW / "semantic_model_dispositions.csv").open(encoding="utf-8", newline="") as h:
    dispositions = list(csv.DictReader(h))

assert len(candidates) == 50 == len(dispositions)
assert {row["concept_id"] for row in candidates} == {
    row["concept_id"] for row in dispositions
}
assert all(row["status"] == "design-approved" for row in dispositions)
assert {row["migration_phase"] for row in dispositions} <= {"2", "3"}

with (DATA / "approved_semantic_bindings.csv").open(encoding="utf-8", newline="") as h:
    bindings = list(csv.DictReader(h))
with (DATA / "approved_semantic_value_bindings.csv").open(encoding="utf-8", newline="") as h:
    value_bindings = list(csv.DictReader(h))
phase_2 = {row["concept_id"] for row in dispositions if row["migration_phase"] == "2"}
assert len(bindings) == 13
assert {row["legacy_concept_id"] for row in bindings} == phase_2
assert {row["binding_kind"] for row in bindings} == {
    "property", "quantified_component", "observable_property"
}
assert all(row["status"] == "approved" and row["reviewer"] == "Pete Steward" for row in bindings)
assert sum(row["binding_kind"] == "observable_property" for row in bindings) == 8
assert all(
    row["quantity_kind_uri"].startswith("http://qudt.org/vocab/quantitykind/")
    and row["unit_requirement"] == "required"
    for row in bindings if row["binding_kind"] in {"quantified_component", "observable_property"}
)
ingredient_part_binding = next(row for row in bindings if row["legacy_concept_id"] == "AOM_000532")
assert ingredient_part_binding["target_property"] == "aom:legacyComponentDescriptor"
assert ingredient_part_binding["value_class"] == "xsd:string"
assert ingredient_part_binding["compatibility_policy"] == "preserve_raw_descriptor_until_reviewed_facet_decomposition"

with (FACET_REVIEW / "ingredient_component_facets.csv").open(encoding="utf-8", newline="") as h:
    facets = list(csv.DictReader(h))
assert len(facets) == 8
assert len({row["facet_id"] for row in facets}) == 8
assert all(row["status"] == "design-approved" and row["reviewer"] == "Pete Steward" for row in facets)
assert {row["target_property"] for row in facets if row["target_property"]} == {
    "aom:legacyComponentDescriptor", "aom:ingredientPart", "aom:physicalForm",
    "aom:processingMethod", "aom:productRole", "aom:ingredientConstituent",
}

with (FACET_REVIEW / "ingredient_component_value_candidates.csv").open(encoding="utf-8", newline="") as h:
    facet_candidates = list(csv.DictReader(h))
candidate_schema = json.loads(
    (ROOT / "schemas/json/ingredient-component-value-candidate.schema.json").read_text()
)
allowed_facets = set(candidate_schema["properties"]["proposed_facet"]["enum"])
allowed_secondary = allowed_facets - {"composite_descriptor", "unresolved_descriptor"}
assert len(facet_candidates) == 83
assert len({row["normalized_value"] for row in facet_candidates}) == 83
assert all(row["normalized_value"] == " ".join(row["source_value"].strip().lower().split()) for row in facet_candidates)
assert all(row["proposed_facet"] in allowed_facets for row in facet_candidates)
assert all(
    not row["secondary_facets"] or set(row["secondary_facets"].split(";")) <= allowed_secondary
    for row in facet_candidates
)
assert all(row["status"] == "proposed-for-review" for row in facet_candidates)
assert all(not row["reviewer"] and not row["review_date"] for row in facet_candidates)
assert all(row["evidence"] == "aggregate-only-livestock-profile" for row in facet_candidates)
assert all(
    (row["proposed_facet"] == "composite_descriptor" and row["disposition"] == "decompose")
    or (row["proposed_facet"] == "unresolved_descriptor" and row["disposition"] == "hold")
    or (row["proposed_facet"] not in {"composite_descriptor", "unresolved_descriptor"}
        and row["disposition"] == "review_single")
    for row in facet_candidates
)
assert sum(row["proposed_facet"] == "anatomical_part" for row in facet_candidates) == 30
assert sum(row["proposed_facet"] == "composite_descriptor" for row in facet_candidates) == 28

with (FACET_REVIEW / "taxon_mapping_candidates_batch_1.csv").open(encoding="utf-8", newline="") as h:
    taxon_candidates = list(csv.DictReader(h))
assert len(taxon_candidates) == 10
assert len({row["source_name"] for row in taxon_candidates}) == 10
assert all(row["status"] == "proposed-for-review" and not row["reviewer"] and not row["review_date"] for row in taxon_candidates)
assert all(row["ncbi_uri"].endswith(row["ncbi_taxon_id"]) for row in taxon_candidates)
assert {row["rank"] for row in taxon_candidates} == {"species", "genus", "family"}
renamed = next(row for row in taxon_candidates if row["source_name"] == "Pennisetum purpureum")
assert renamed["accepted_name"] == "Cenchrus purpureus" and renamed["ncbi_taxon_id"] == "NCBITaxon_154765"
assert [(row["source_value"], row["binding_action"], row["target_concept_id"]) for row in value_bindings] == [
    ("On-farm", "map_to_existing", "AOM_000141"),
    ("Purchased", "map_to_existing", "AOM_000142"),
    ("Unspecified", "hold_ambiguous", ""),
]
assert all(row["status"] == "approved" and row["reviewer"] == "Pete Steward" for row in value_bindings)

with (DATA / "labels.csv").open(encoding="utf-8", newline="") as h:
    labels = list(csv.DictReader(h))
preferred = {row["concept_id"]: row["label"] for row in labels if row["language"] == "en" and row["label_type"] == "pref"}
for row in value_bindings:
    if row["target_concept_id"]:
        assert preferred[row["target_concept_id"]] == row["target_label"] == row["source_value"]

binding_graph = Graph().parse(DIST / "aom-semantic-bindings.ttl")
jsonld_binding_graph = Graph().parse(DIST / "aom-semantic-bindings.jsonld")
assert len(binding_graph) == len(jsonld_binding_graph)
semantic_binding = URIRef("urn:era-aom:schema:SemanticBinding")
semantic_value_binding = URIRef("urn:era-aom:schema:SemanticValueBinding")
ingredient_source_category = URIRef("urn:era-aom:schema:IngredientSourceCategory")
observable_property = URIRef("http://www.w3.org/ns/sosa/ObservableProperty")
assert len(set(binding_graph.subjects(RDF.type, semantic_binding))) == 13
assert len(set(binding_graph.subjects(RDF.type, semantic_value_binding))) == 3
assert {
    str(subject).removeprefix("urn:era-aom:livestock:")
    for subject in binding_graph.subjects(RDF.type, ingredient_source_category)
} == {"AOM_000141", "AOM_000142"}
assert {
    str(subject).removeprefix("urn:era-aom:livestock:")
    for subject in binding_graph.subjects(RDF.type, observable_property)
} == {row["legacy_concept_id"] for row in bindings if row["binding_kind"] == "observable_property"}
binding_result, _, report = validate(binding_graph, shacl_graph=shapes, ont_graph=ontology)
assert binding_result, report

valid_graph = Graph().parse(FIXTURES / "semantic-model-valid.ttl")
invalid_graph = Graph().parse(FIXTURES / "semantic-model-invalid.ttl")
invalid_value_binding_graph = Graph().parse(FIXTURES / "semantic-value-binding-invalid.ttl")
invalid_facet_graph = Graph().parse(FIXTURES / "semantic-facet-invalid.ttl")
valid_result, _, _ = validate(valid_graph, shacl_graph=shapes, ont_graph=ontology)
invalid_result, _, _ = validate(invalid_graph, shacl_graph=shapes, ont_graph=ontology)
invalid_value_binding_result, _, _ = validate(invalid_value_binding_graph, shacl_graph=shapes, ont_graph=ontology)
invalid_facet_result, _, _ = validate(invalid_facet_graph, shacl_graph=shapes, ont_graph=ontology)
assert valid_result
assert not invalid_result
assert not invalid_value_binding_result
assert not invalid_facet_result
print("Semantic model validation passed: 50 dispositions; 13 structural, 3 value bindings, 8 facets, 83 value proposals")
