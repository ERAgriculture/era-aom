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
assert len(value_bindings) == 129
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
guizotia = next(row for row in taxon_candidates if row["source_name"] == "Guizotia abyssinica")
assert guizotia["ncbi_taxon_id"] == "NCBITaxon_4230"

with (FACET_REVIEW / "taxon_mapping_candidates_batch_2.csv").open(encoding="utf-8", newline="") as h:
    taxon_batch_2 = list(csv.DictReader(h))
assert len(taxon_batch_2) == 15
assert all(row["status"] == "proposed-for-review" and not row["reviewer"] for row in taxon_batch_2)
assert {row["rank"] for row in taxon_batch_2 if row["rank"]} == {"species", "genus", "family"}
brassica = next(row for row in taxon_batch_2 if row["source_name"] == "Brassica napus")
assert brassica["legacy_ncbi_taxon_id"] == "NCBITaxon_4710"
assert brassica["proposed_ncbi_taxon_id"] == "NCBITaxon_3708"
assert brassica["decision_action"] == "replace_incorrect"
synonyms = {row["source_name"]: row for row in taxon_batch_2 if row["decision_action"] == "accept_as_synonym"}
assert {name: row["accepted_name"] for name, row in synonyms.items()} == {
    "Acacia tortilis": "Vachellia tortilis",
    "Panicum maximum": "Megathyrsus maximus",
}
assert all(row["legacy_ncbi_taxon_id"] == row["proposed_ncbi_taxon_id"] for row in synonyms.values())
brevoortia = next(row for row in taxon_batch_2 if row["source_name"] == "Brevoortia")
assert brevoortia["legacy_ncbi_taxon_id"] == "NCBITaxon_55119"
assert brevoortia["proposed_ncbi_taxon_id"] == "NCBITaxon_224706"
non_taxon = next(row for row in taxon_batch_2 if row["source_name"] == "sodium carboxymethyl cellulose")
assert non_taxon["decision_action"] == "hold_non_taxon" and not non_taxon["proposed_ncbi_taxon_id"].strip()

with (FACET_REVIEW / "taxon_mapping_candidates_batch_3.csv").open(encoding="utf-8", newline="") as h:
    taxon_batch_3 = list(csv.DictReader(h))
assert len(taxon_batch_3) == 21
assert len({row["source_name"] for row in taxon_batch_3}) == 21
assert {row["rank"] for row in taxon_batch_3} == {"species"}
assert all(row["status"] == "proposed-for-review" and not row["reviewer"] and not row["review_date"] for row in taxon_batch_3)
assert all(row["evidence"].endswith(row["proposed_ncbi_taxon_id"].removeprefix("NCBITaxon_")) for row in taxon_batch_3)
wrong_ids = {row["source_name"]: row for row in taxon_batch_3 if row["decision_action"] == "replace_incorrect"}
assert {name: (row["legacy_ncbi_taxon_id"], row["proposed_ncbi_taxon_id"]) for name, row in wrong_ids.items()} == {
    "Psophocarpus tetragonolobus": ("NCBITaxon_3847", "NCBITaxon_3891"),
    "Theba pisana": ("NCBITaxon_2315439", "NCBITaxon_145622"),
}
normalized_names = {row["source_name"]: row["accepted_name"] for row in taxon_batch_3 if row["source_name"] != row["accepted_name"]}
assert normalized_names == {
    "Gliciridia sepium": "Gliricidia sepium",
    "Opuntia ficus indica": "Opuntia ficus-indica",
    "Pennisetum clandestinum": "Cenchrus clandestinus",
}

with (FACET_REVIEW / "taxon_mapping_candidates_batch_4.csv").open(encoding="utf-8", newline="") as h:
    taxon_batch_4 = list(csv.DictReader(h))
assert len(taxon_batch_4) == 80
assert len({row["source_name"] for row in taxon_batch_4}) == 80
assert {row["rank"] for row in taxon_batch_4} == {"species", "genus", "subspecies"}
assert all(row["status"] == "proposed-for-review" and not row["reviewer"] and not row["review_date"] for row in taxon_batch_4)
assert all(row["evidence"].endswith(row["proposed_ncbi_taxon_id"].removeprefix("NCBITaxon_")) for row in taxon_batch_4)
actions_4 = {action: sum(row["decision_action"] == action for row in taxon_batch_4) for action in {
    "accept_existing", "accept_as_synonym", "replace_incorrect",
    "map_unspecified_species_to_genus", "accept_as_misspelling", "replace_retired",
}}
assert actions_4 == {
    "accept_existing": 55,
    "accept_as_synonym": 11,
    "replace_incorrect": 5,
    "map_unspecified_species_to_genus": 5,
    "accept_as_misspelling": 3,
    "replace_retired": 1,
}
assert sum(row["rank"] == "genus" for row in taxon_batch_4) == 8
assert sum(row["rank"] == "subspecies" for row in taxon_batch_4) == 2

with (FACET_REVIEW / "taxon_mapping_candidates_final.csv").open(encoding="utf-8", newline="") as h:
    taxon_final = list(csv.DictReader(h))
assert len(taxon_final) == 146
assert len({row["source_name"] for row in taxon_final}) == 146
assert all(row["status"] == "proposed-for-review" and not row["reviewer"] and not row["review_date"] for row in taxon_final)
final_mapped = [row for row in taxon_final if row["proposed_ncbi_taxon_id"]]
final_held = [row for row in taxon_final if not row["proposed_ncbi_taxon_id"]]
assert len(final_mapped) == 91 and len(final_held) == 55
assert all(row["accepted_name"] and row["rank"] and row["evidence"] for row in final_mapped)
assert all(row["evidence"].endswith(row["proposed_ncbi_taxon_id"].removeprefix("NCBITaxon_")) for row in final_mapped)
assert all(row["decision_action"].startswith("hold_") and not row["accepted_name"] for row in final_held)
final_actions = {action: sum(row["decision_action"] == action for row in taxon_final) for action in {
    "accept_existing", "accept_as_synonym", "replace_incorrect",
    "map_unspecified_species_to_genus", "hold_unresolved", "hold_contextual",
}}
assert final_actions == {
    "accept_existing": 75,
    "accept_as_synonym": 6,
    "replace_incorrect": 4,
    "map_unspecified_species_to_genus": 6,
    "hold_unresolved": 50,
    "hold_contextual": 5,
}
ingredient_source_bindings = [row for row in value_bindings if row["target_property"] == "aom:ingredientSource"]
taxon_value_bindings = [row for row in value_bindings if row["target_property"] == "aom:sourceTaxon"]
assert [(row["source_value"], row["binding_action"], row["target_concept_id"]) for row in ingredient_source_bindings] == [
    ("On-farm", "map_to_existing", "AOM_000141"),
    ("Purchased", "map_to_existing", "AOM_000142"),
    ("Unspecified", "hold_ambiguous", ""),
]
assert len(taxon_value_bindings) == 126
assert sum(row["binding_action"] == "map_to_external" for row in taxon_value_bindings) == 125
assert all(
    row["target_uri"].startswith("http://purl.obolibrary.org/obo/NCBITaxon_")
    for row in taxon_value_bindings if row["binding_action"] == "map_to_external"
)
brassica_binding = next(row for row in taxon_value_bindings if row["source_value"] == "Brassica napus")
assert brassica_binding["target_uri"].endswith("NCBITaxon_3708")
chemical_hold = next(row for row in taxon_value_bindings if row["source_value"] == "sodium carboxymethyl cellulose")
assert chemical_hold["binding_action"] == "hold_non_taxon" and not chemical_hold["target_uri"]
corrected_targets = {
    row["source_value"]: row["target_uri"].removeprefix("http://purl.obolibrary.org/obo/")
    for row in taxon_value_bindings
    if row["source_value"] in {"Theba pisana", "Psophocarpus tetragonolobus"}
}
assert corrected_targets == {
    "Psophocarpus tetragonolobus": "NCBITaxon_3891",
    "Theba pisana": "NCBITaxon_145622",
}
integrity_targets = {
    row["source_value"]: row["target_uri"].removeprefix("http://purl.obolibrary.org/obo/")
    for row in taxon_value_bindings
    if row["source_value"] in {"Brevoortia", "Guizotia abyssinica"}
}
assert integrity_targets == {
    "Brevoortia": "NCBITaxon_224706",
    "Guizotia abyssinica": "NCBITaxon_4230",
}
batch_4_sources = {row["source_name"] for row in taxon_batch_4}
approved_batch_4 = {row["source_value"] for row in taxon_value_bindings} & batch_4_sources
assert approved_batch_4 == batch_4_sources
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
assert len(set(binding_graph.subjects(RDF.type, semantic_value_binding))) == 129
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
print("Semantic model validation passed: 50 dispositions; 13 structural, 129 value bindings, 8 facets, 83 value proposals")
