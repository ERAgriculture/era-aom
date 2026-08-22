#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
DIST = ROOT / "dist/livestock-staging"


def read(name):
    with (DATA / f"{name}.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


concepts, labels, notes = read("concepts"), read("labels"), read("notes")
relations, mappings = read("relations"), read("mappings")
quarantine, gaps, legacy = read("quarantine"), read("hierarchy_gaps"), read("legacy_records")
resolutions = read("approved_identity_resolutions")
replacements = read("approved_mapping_replacements")
mapping_reviews = read("approved_mapping_reviews")
mapping_additions = read("approved_mapping_additions")
deprecations = read("approved_deprecations")
retirements = read("approved_concept_retirements")
label_corrections = read("approved_label_corrections")
label_additions = read("approved_label_additions")
label_suppressions = read("approved_label_suppressions")
new_concepts = read("approved_new_concepts")
id_registry = read("livestock_id_registry")
semantic_relations = read("approved_semantic_relations")
reparentings = read("approved_reparentings")
hierarchy_revisions = read("approved_hierarchy_revisions")
formulation_classifications = read("approved_feed_formulation_classifications")
taxonomy_classifications = read("approved_feed_taxonomy_classifications")
concept_semantic_types = read("approved_concept_semantic_types")
feed_role_assertions = read("approved_feed_role_assertions")
component_retention_relations = read("approved_component_retention_relations")
process_axis_relations = read("approved_process_axis_relations")
semantic_bindings = read("approved_semantic_bindings")
semantic_value_bindings = read("approved_semantic_value_bindings")
component_classifications = read("approved_ingredient_component_classifications")
facet_concepts = read("approved_ingredient_facet_concepts")
component_value_mappings = read("approved_ingredient_component_value_mappings")
component_decompositions = read("approved_ingredient_component_decompositions")
component_value_holds = read("approved_ingredient_component_value_holds")
harmonization_rules = read("approved_ingredient_harmonization_rules")
generated_material_facets = read("approved_generated_feed_material_facets")
hard_tail_material_facets = read("approved_hard_tail_feed_material_facets")
structural_material_facets = read("approved_structural_feed_material_facets")
whole_grain_decisions = read("approved_whole_grain_integrity_decisions")
source_overrides = read("approved_feed_material_source_overrides")
manifest = json.loads((DIST / "manifest.json").read_text())
ids = [row["concept_id"] for row in concepts]
known = set(ids)
assert len(legacy) == 2503
assert len(ids) == 2814 and len(ids) == len(known)
assert "AOM_006275" in known
assert "duplicate_concept_id" not in {row["reason"] for row in quarantine}
assert "duplicate_derived_path" in {row["reason"] for row in quarantine}
assert all(row["subject_id"] in known and row["object_id"] in known for row in relations)
assert all(row["subject_id"] in known for row in mappings)
reviewed = [row for row in mappings if row["status"] == "reviewed"]
reviewed_related = [row for row in mappings if row["status"] == "reviewed-related"]
review_held = [row for row in mappings if row["status"] == "review-held"]
assert len(reviewed) == 3
assert {row["subject_id"] for row in reviewed} == {"AOM_006275"}
assert {row["target_id"] for row in reviewed} == {
    "NCBITaxon_3031383", "wfo-0000883036", "413",
}
assert all(row["reviewer"] == "Pete Steward" for row in reviewed)
assert len(mapping_reviews) == 383
assert len(mapping_additions) == 28
assert {row["mapping_relation"] for row in mapping_additions} == {
    "broadMatch", "closeMatch", "exactMatch", "narrowMatch", "relatedMatch",
}
assert len(reviewed_related) == 344 and len(review_held) == 12
assert all(row["reviewer"] == "Pete Steward" for row in reviewed_related + review_held)
assert all(row["status"] == "legacy-unreviewed" and row["reviewer"] == "" for row in mappings if row["status"] == "legacy-unreviewed")
assert len(resolutions) == 2
assert {row["action"] for row in resolutions} == {"retain", "map_to_existing"}
assert {row["resolved_concept_id"] for row in resolutions} == {
    "AOM_006275", "AOM_001676",
}
assert len(replacements) == 3
assert len(deprecations) == 38
assert len(retirements) == 11
assert len(taxonomy_classifications) == 229
assert len(concept_semantic_types) == 50
assert len(feed_role_assertions) == 16
assert len(component_retention_relations) == 4
assert len(semantic_bindings) == 13
assert len(semantic_value_bindings) == 298
assert len(component_classifications) == 83
assert len({row["normalized_value"] for row in component_classifications}) == 83
assert all(row["status"] == "approved-classification" for row in component_classifications)
assert all(row["reviewer"] == "Pete Steward" for row in component_classifications)
assert sum(row["disposition"] == "review_single" for row in component_classifications) == 52
assert sum(row["disposition"] == "decompose" for row in component_classifications) == 29
assert sum(row["disposition"] == "hold" for row in component_classifications) == 2
assert len(facet_concepts) == 114
assert len(harmonization_rules) == 37
assert len(generated_material_facets) == 1525
assert len(hard_tail_material_facets) == 153
assert len(structural_material_facets) == 1159
assert len(whole_grain_decisions) == 4
assert len(source_overrides) == 15
assert len(component_value_mappings) == 45
assert len(component_decompositions) == 63
assert len(component_value_holds) == 11
assert len(process_axis_relations) == 166
assert {row["target_concept_id"] for row in component_value_mappings + component_decompositions} <= {
    row["concept_id"] for row in facet_concepts
}
assert all(row["status"] == "approved" and row["reviewer"] == "Pete Steward" for row in facet_concepts + component_value_mappings + component_decompositions + component_value_holds)
assert ({row["source_value"] for row in component_value_mappings} |
        {row["source_value"] for row in component_decompositions} |
        {row["source_value"] for row in component_value_holds}) == {
            row["source_value"] for row in component_classifications
        }
expected_deprecations = {
    (row["deprecated_id"], row["replacement_id"])
    for row in deprecations
}
assert expected_deprecations == {
    ("AOM_001884", "AOM_000564"),
    ("AOM_004000", "AOM_003960"),
    ("AOM_006072", "AOM_001326"),
    ("AOM_001898", "AOM_001459"),
    ("AOM_000338", "AOM_000350"),
    ("AOM_000339", "AOM_000351"),
    ("AOM_000340", "AOM_000352"),
    ("AOM_000341", "AOM_000353"),
    ("AOM_000342", "AOM_000354"),
    ("AOM_000949", "AOM_000935"),
    ("AOM_000146", "AOM_000820"),
    ("AOM_000147", "AOM_000830"),
    ("AOM_000855", "AOM_000850"),
    ("AOM_000874", "AOM_000865"),
    ("AOM_000876", "AOM_000867"),
    ("AOM_000877", "AOM_000868"),
    ("AOM_000878", "AOM_000869"),
    ("AOM_000879", "AOM_000870"),
    ("AOM_000880", "AOM_000871"),
    ("AOM_000883", "AOM_000872"),
    ("AOM_000884", "AOM_000873"),
    ("AOM_000900", "AOM_000885"),
    ("AOM_000922", "AOM_000893"),
    ("AOM_000923", "AOM_000894"),
    ("AOM_000924", "AOM_000895"),
    ("AOM_000925", "AOM_000896"),
    ("AOM_000926", "AOM_000897"),
    ("AOM_000927", "AOM_000898"),
    ("AOM_000841", "AOM_000833"),
    ("AOM_000745", "AOM_101079"),
    ("AOM_000747", "AOM_101151"),
    ("AOM_001917", "AOM_101152"),
    ("AOM_101103", "AOM_001616"),
    ("AOM_101120", "AOM_001571"),
    ("AOM_101144", "AOM_101143"),
    ("AOM_000324", "AOM_101182"),
    ("AOM_101116", "AOM_101134"),
    ("AOM_101080", "AOM_000226"),
}
assert manifest["counts"]["approved_semantic_bindings"] == 13
assert manifest["counts"]["approved_mapping_reviews"] == 383
assert manifest["counts"]["approved_semantic_value_bindings"] == 298
assert manifest["counts"]["approved_ingredient_component_classifications"] == 83
assert manifest["counts"]["approved_ingredient_facet_concepts"] == 114
assert manifest["counts"]["approved_ingredient_harmonization_rules"] == 37
assert manifest["counts"]["approved_generated_feed_material_facets"] == 1525
assert manifest["counts"]["approved_hard_tail_feed_material_facets"] == 153
assert manifest["counts"]["approved_structural_feed_material_facets"] == 1159
assert manifest["counts"]["approved_hierarchy_revisions"] == 148
assert manifest["counts"]["approved_whole_grain_integrity_decisions"] == 4
assert manifest["counts"]["approved_feed_material_source_overrides"] == 15
assert manifest["counts"]["approved_ingredient_component_value_mappings"] == 45
assert manifest["counts"]["approved_ingredient_component_decompositions"] == 63
assert manifest["counts"]["approved_ingredient_component_value_holds"] == 11
assert manifest["counts"]["approved_feed_formulation_classifications"] == 29
assert manifest["counts"]["approved_feed_taxonomy_classifications"] == 229
assert manifest["counts"]["approved_concept_semantic_types"] == 50
assert manifest["counts"]["approved_process_axis_relations"] == 166
assert manifest["counts"]["approved_feed_role_assertions"] == 16
assert manifest["counts"]["approved_component_retention_relations"] == 4
assert manifest["counts"]["approved_concept_retirements"] == 11
assert len(label_corrections) == 36
assert len(label_additions) == 36
assert len(label_suppressions) == 6
assert len(new_concepts) == 313
new_by_case = {row["case_id"]: row for row in new_concepts}
assert {
    "PARENT-006", "PARENT-007", "PARENT-036", "PARENT-078", "PARENT-200",
    "PARENT-227",
    "PARENT-031", "PARENT-032", "PARENT-033", "PARENT-035", "PARENT-037",
    "PARENT-038", "PARENT-040", "PARENT-041", "PARENT-042", "PARENT-044",
    "PARENT-065", "PARENT-066", "PARENT-067", "PARENT-068", "PARENT-070",
    "PARENT-072", "PARENT-074", "PARENT-075", "PARENT-076", "PARENT-077",
} <= set(new_by_case)
remaining_cases = {
    "PARENT-027", "PARENT-028", "PARENT-029", "PARENT-030",
    "PARENT-047", "PARENT-048", "PARENT-049", "PARENT-052",
    "PARENT-053", "PARENT-054", "PARENT-056", "PARENT-058",
    "PARENT-059", "PARENT-061", "PARENT-062", "PARENT-063",
    "PARENT-080", "PARENT-082", "PARENT-083", "PARENT-084",
    "PARENT-085", "PARENT-086", "PARENT-087", "PARENT-088",
    "PARENT-089", "PARENT-090", "PARENT-091", "PARENT-092",
    "PARENT-093", "PARENT-094", "PARENT-096", "PARENT-098",
    "PARENT-099", "PARENT-100", "PARENT-102", "PARENT-103",
    "PARENT-105", "PARENT-106", "PARENT-107", "PARENT-108",
    "PARENT-109", "PARENT-110", "PARENT-111", "PARENT-112",
    "PARENT-113", "PARENT-114",
}
assert remaining_cases <= set(new_by_case)
crop_product_cases = {
    "PARENT-115", "PARENT-116", "PARENT-117", "PARENT-118",
    "PARENT-119", "PARENT-122", "PARENT-123", "PARENT-124",
    "PARENT-125", "PARENT-126", "PARENT-127", "PARENT-129",
    "PARENT-130", "PARENT-131", "PARENT-132", "PARENT-133",
    "PARENT-135", "PARENT-136", "PARENT-137", "PARENT-138",
    "PARENT-139", "PARENT-140", "PARENT-141", "PARENT-142",
}
assert crop_product_cases <= set(new_by_case)
forage_mint_cases = {
    "PARENT-143", "PARENT-144", "PARENT-146", "PARENT-147",
    "PARENT-150", "PARENT-151", "PARENT-152", "PARENT-153",
    "PARENT-155", "PARENT-156", "PARENT-157", "PARENT-158",
    "PARENT-159", "PARENT-160", "PARENT-161", "PARENT-165",
    "PARENT-166", "PARENT-167", "PARENT-168", "PARENT-170",
    "PARENT-173", "PARENT-176", "PARENT-177", "PARENT-180",
    "PARENT-182", "PARENT-184", "PARENT-185", "PARENT-186",
    "PARENT-187", "PARENT-188", "PARENT-234",
}
assert forage_mint_cases <= set(new_by_case)
remaining_feed_mint_cases = {
    "PARENT-008", "PARENT-009", "PARENT-010", "PARENT-011",
    "PARENT-013", "PARENT-014", "PARENT-015", "PARENT-017",
    "PARENT-020", "PARENT-021", "PARENT-022", "PARENT-192",
    "PARENT-193", "PARENT-196", "PARENT-197", "PARENT-198",
    "PARENT-199",
}
assert remaining_feed_mint_cases <= set(new_by_case)
final_mint_cases = {
    "PARENT-002", "PARENT-004", "PARENT-201", "PARENT-202",
    "PARENT-203", "PARENT-205", "PARENT-206", "PARENT-207",
    "PARENT-208", "PARENT-209", "PARENT-210", "PARENT-211",
    "PARENT-215", "PARENT-216", "PARENT-217", "PARENT-218",
    "PARENT-219", "PARENT-220", "PARENT-222", "PARENT-223",
    "PARENT-224", "PARENT-228", "PARENT-229", "PARENT-231",
    "PARENT-232", "PARENT-233",
}
assert final_mint_cases <= set(new_by_case)
assert {row["concept_id"] for row in id_registry} == {
    f"AOM_{number:06d}" for number in range(100849, 101183)
}
assert {
    row["concept_id"] for row in id_registry
    if row["status"] != "retired-before-publication"
} <= known
assert {
    row["concept_id"] for row in id_registry
    if row["status"] == "retired-before-publication"
} == {
    row["generated_id"] for row in read("approved_identity_integrity_remediations")
    if row["action"] == "reuse_existing"
} | {"AOM_101068", "AOM_101109", "AOM_101156", "AOM_101157", "AOM_101158"}
status = {row["concept_id"]: row["status"] for row in concepts}
assert status["AOM_001884"] == "deprecated"
assert status["AOM_004000"] == "deprecated"
assert status["AOM_006072"] == "deprecated"
assert status["AOM_001898"] == "deprecated"
assert all(status[concept_id] == "deprecated" for concept_id in {
    deprecated_id
    for deprecated_id, replacement_id in expected_deprecations
})
assert all(status[row["concept_id"]] == "deprecated" for row in retirements)
retirement_ids = {row["concept_id"] for row in retirements}
assert {
    row["concept_id"] for row in notes
    if row["note_type"] == "history_note"
    and row["source_column"] == "approved_concept_retirement"
} == retirement_ids
assert not any(
    row["subject_id"] in retirement_ids and row["relation_type"] == "broader"
    for row in relations
)
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
} == {(deprecated_id, "replaced_by", replacement_id)
      for deprecated_id, replacement_id in expected_deprecations}
mineral_children = set(new_by_case["PARENT-006"]["child_ids"].split(";"))
assert {
    row["subject_id"] for row in relations
    if row["relation_type"] == "broader" and row["object_id"] == "AOM_100849"
} == mineral_children
assert ("AOM_100849", "broader", "AOM_000196") in {
    (row["subject_id"], row["relation_type"], row["object_id"])
    for row in relations
}
assert not any(row["child_id"] in mineral_children for row in gaps)
ingredient_children = set(new_by_case["PARENT-007"]["child_ids"].split(";"))
moved_ingredient_children = {
    row["child_id"] for row in hierarchy_revisions
    if row["remove_parent_id"] == "AOM_100850"
}
assert {
    row["subject_id"] for row in relations
    if row["relation_type"] == "broader" and row["object_id"] == "AOM_100850"
} >= ingredient_children - moved_ingredient_children
assert not any(
    row["subject_id"] == "AOM_001491" and row["object_id"] == "AOM_100850"
    for row in relations if row["relation_type"] == "broader"
)
assert ("AOM_100850", "broader", "AOM_000328") in {
    (row["subject_id"], row["relation_type"], row["object_id"])
    for row in relations
}
assert not any(row["child_id"] in ingredient_children for row in gaps)
maize_children = set(new_by_case["PARENT-036"]["child_ids"].split(";"))
assert {
    row["subject_id"] for row in relations
    if row["relation_type"] == "broader" and row["object_id"] == "AOM_100851"
} == maize_children
assert not any(row["child_id"] in maize_children for row in gaps)
for case_id in {"PARENT-078", "PARENT-200", "PARENT-227"}:
    new_concept = new_by_case[case_id]
    children = {
        concept_id for concept_id in new_concept["child_ids"].split(";")
        if status[concept_id] != "deprecated"
    }
    assert {
        row["subject_id"] for row in relations
        if row["relation_type"] == "broader"
        and row["object_id"] == new_concept["concept_id"]
    } >= children
    assert not any(row["child_id"] in children for row in gaps)
expected_new_parents = {
    "PARENT-078": "AOM_000615",
    "PARENT-200": "AOM_000107",
    "PARENT-227": "AOM_003110",
}
broader_triples = {
    (row["subject_id"], row["object_id"])
    for row in relations if row["relation_type"] == "broader"
}
for case_id, parent_id in expected_new_parents.items():
    assert (new_by_case[case_id]["concept_id"], parent_id) in broader_triples
assert new_by_case["PARENT-227"]["derived_path"] == (
    "Outcomes/Productivity/Economics/Costs/Variable Cost/"
    "Management activity variable cost"
)
assert len(semantic_relations) == 29
assert {
    (row["subject_id"], row["relation_type"], row["object_id"])
    for row in relations if row["relation_type"] == "related"
} >= {
    ("AOM_100851", "related", "AOM_000648"),
    ("AOM_100852", "related", "AOM_001582"),
    ("AOM_100856", "related", "AOM_001202"),
    ("AOM_100859", "related", "AOM_000654"),
    ("AOM_100860", "related", "AOM_001895"),
    ("AOM_100863", "related", "AOM_001316"),
    ("AOM_100864", "related", "AOM_001319"),
    ("AOM_100868", "related", "AOM_002228"),
    ("AOM_100869", "related", "AOM_003072"),
    ("AOM_100873", "related", "AOM_002226"),
    ("AOM_100874", "related", "AOM_001314"),
    ("AOM_100983", "related", "AOM_000025"),
    ("AOM_003206", "related", "AOM_000024"),
    ("AOM_101127", "related", "AOM_000024"),
}
assert {
    ("AOM_000830", "AOM_000145"),
    ("AOM_000865", "AOM_000848"),
    ("AOM_000893", "AOM_000848"),
    ("AOM_000885", "AOM_000848"),
    ("AOM_000850", "AOM_000849"),
} <= broader_triples
staging_graph = json.loads((DIST / "aom-livestock.jsonld").read_text())["@graph"]
staging_nodes = {
    row["@id"].rsplit(":", 1)[-1]: row
    for row in staging_graph if "@id" in row
}
expected_polyhierarchies = {
    "AOM_000820": {"AOM_101163", "AOM_101164"},
    "AOM_000830": {"AOM_000145", "AOM_100990", "AOM_101164", "AOM_101165"},
    "AOM_000850": {"AOM_000848", "AOM_000849"},
    "AOM_000865": {"AOM_000848", "AOM_000849"},
    "AOM_000885": {"AOM_000848", "AOM_000849"},
    "AOM_000893": {"AOM_000848", "AOM_000849"},
    "AOM_000833": {"AOM_000826", "AOM_000837", "AOM_101131"},
    "AOM_000838": {"AOM_000837", "AOM_101129", "AOM_101130"},
    "AOM_101124": {"AOM_000826", "AOM_101130"},
}
for concept_id, expected_parents in expected_polyhierarchies.items():
    actual_parents = staging_nodes[concept_id]["skos:broader"]
    assert isinstance(actual_parents, list)
    assert {
        value["@id"].rsplit(":", 1)[-1]
        for value in actual_parents
    } == expected_parents
assert {
    value["@id"].rsplit(":", 1)[-1]
    for value in staging_nodes["AOM_101128"]["skos:broader"]
} == {"AOM_000826", "AOM_101165"}
assert len(reparentings) == 64
assert len(hierarchy_revisions) == 148
assert len(formulation_classifications) == 29
for reparenting in reparentings:
    children = set(reparenting["child_ids"].split(";"))
    subsequently_moved = {
        row["child_id"] for row in hierarchy_revisions
        if row["remove_parent_id"] == reparenting["target_parent_id"]
    }
    assert {
        row["subject_id"] for row in relations
        if row["relation_type"] == "broader"
        and row["object_id"] == reparenting["target_parent_id"]
    } >= children - subsequently_moved
    assert not any(row["child_id"] in children for row in gaps)
assert new_by_case["PARENT-099"]["broader_id"] == "AOM_000615"
assert new_by_case["PARENT-099"]["preferred_label"] == "African yam bean by-products"
assert new_by_case["PARENT-098"]["preferred_label"] == "Other plant by-products"
assert new_by_case["PARENT-115"]["preferred_label"] == "Crop product"
assert new_by_case["PARENT-135"]["preferred_label"] == "Black cumin by-products"
assert ("AOM_001818", "AOM_100937") in broader_triples
assert new_by_case["PARENT-143"]["preferred_label"] == "Bothriochloa forage materials"
assert new_by_case["PARENT-157"]["preferred_label"] == "Harrisonia abyssinica forage materials"
assert new_by_case["PARENT-177"]["preferred_label"] == "Ziziphus jujuba forage materials"
assert ("AOM_100969", "AOM_000102") in {
    (row["subject_id"], row["object_id"])
    for row in relations if row["relation_type"] == "related"
}
assert new_by_case["PARENT-017"]["preferred_label"] == "Animal by-products"
assert new_by_case["PARENT-197"]["broader_id"] == "AOM_000845"
assert new_by_case["PARENT-199"]["preferred_label"] == "Diet source"
assert new_by_case["PARENT-206"]["preferred_label"] == "Reproductive status"
assert new_by_case["PARENT-233"]["preferred_label"] == "Porcine animals"
assert {row["child_id"] for row in gaps} <= {
    concept_id for concept_id, concept_status in status.items()
    if concept_status == "deprecated"
}
corrected_labels = {
    row["concept_id"]: row["label"] for row in labels
    if row["source_column"] == "approved_label_correction"
}
assert corrected_labels == {
    "AOM_000656": "Ground whole-grain rice",
    "AOM_000660": "Ground whole-grain wheat",
    "AOM_001313": "Whole-grain maize",
    "AOM_001324": "Ground whole-grain maize",
    "AOM_001898": "Bothriochloa dried",
    "AOM_006373": "Ficus exasperata leaves and twigs",
    "AOM_002090": "Harrisonia abyssinica leaves",
    "AOM_003981": "Ziziphus jujuba leaves",
    "AOM_001265": "Ziziphus mauritiana",
    "AOM_001462": "Cynodon dactylon",
    "AOM_002507": "Fourth trimester",
    "AOM_001084": "Variable cost—inoculants",
    "AOM_000831": "Ensiling",
    "AOM_003206": "Poultry by-products",
    "AOM_000845": "Feed processes",
    "AOM_000837": "Mechanical feed processes",
    "AOM_000826": "Thermal feed processes",
    "AOM_000842": "Moisture-removal feed processes",
    "AOM_000838": "Flour milling",
    "AOM_000839": "Hammer milling",
    "AOM_003097": "Decortication",
    "AOM_001510": "Fresh moisture condition",
    "AOM_001491": "Formulated feeds",
    "AOM_003098": "Sprouting",
    "AOM_000736": "Unresolved supplement classifications",
    "AOM_000779": "Unresolved mineral classifications",
    "AOM_000781": "Unresolved other-ingredient classifications",
    "AOM_000795": "Mineral and vitamin feed mixtures",
    "AOM_001832": "Starch feed material",
    "AOM_004433": "Coccidiostats and histomonostats",
    "AOM_006334": "Rumen-protected fat feed materials",
    "AOM_000559": "Feeds of animal origin",
    "AOM_000735": "Forage materials",
    "AOM_000196": "Feed composition characteristics",
    "AOM_000326": "Feed physical characteristics",
}
for correction in label_corrections:
    if correction["old_label"].casefold() != correction["new_label"].casefold():
        assert any(
            row["concept_id"] == correction["concept_id"]
            and row["label_type"] == "alt"
            and row["label"] == correction["old_label"]
            for row in labels
        )
assert next(
    row["label"] for row in labels
    if row["concept_id"] == "AOM_003960" and row["label_type"] == "pref"
) == "Common bean vine"
assert {row["label"] for row in labels if row["concept_id"] == "AOM_003960"} >= {
    "Green Bean Vine", "Haricot Bean Vine", "Common bean vine",
}
approved_aliases = {
    row["label"] for row in labels
    if row["concept_id"] == "AOM_001676"
    and row["source_column"] == "approved_identity_resolution"
}
assert approved_aliases == {"Panicum maximum Dried", "Panicum maximum hay"}
assert all(row["disposition"] == "review_and_mint_or_map_parent" for row in gaps)
pref = Counter(row["concept_id"] for row in labels if row["label_type"] == "pref")
assert set(pref) == known and all(count == 1 for count in pref.values())
parents = defaultdict(set)
for row in relations:
    if row["relation_type"] == "broader":
        parents[row["subject_id"]].add(row["object_id"])
for concept_id in ids:
    pending = [(concept_id, {concept_id})]
    while pending:
        current_id, path = pending.pop()
        for parent_id in parents[current_id]:
            assert parent_id not in path, f"Hierarchy cycle from {concept_id}"
            pending.append((parent_id, path | {parent_id}))
assert manifest["status"] == "staging-not-canonical"
assert manifest["identifier_policy"]["rdf_uri_status"] == "provisional-staging-only"
assert manifest["counts"]["source_records"] == len(legacy)
assert manifest["counts"]["published_staging_concepts"] == len(concepts)
assert manifest["counts"]["hierarchy_relations"] == sum(
    row["relation_type"] == "broader" for row in relations
)
assert manifest["counts"]["replacement_relations"] == len(expected_deprecations)
assert manifest["counts"]["semantic_relations"] == sum(
    row["relation_type"] == "related" for row in semantic_relations
)
assert manifest["counts"]["hierarchy_gaps"] == len(gaps)
assert manifest["counts"]["mapping_assertions"] == len(mappings)
assert manifest["counts"]["approved_identity_resolutions"] == len(resolutions)
assert manifest["counts"]["approved_mapping_replacements"] == len(replacements)
assert manifest["counts"]["approved_mapping_additions"] == len(mapping_additions)
assert manifest["counts"]["approved_deprecations"] == len(deprecations)
assert manifest["counts"]["approved_label_corrections"] == len(label_corrections)
assert manifest["counts"]["approved_label_additions"] == len(label_additions)
assert manifest["counts"]["approved_label_suppressions"] == len(label_suppressions)
assert manifest["counts"]["approved_new_concepts"] == len(new_concepts)
assert manifest["counts"]["registered_livestock_ids"] == len(id_registry)
assert manifest["counts"]["approved_semantic_relations"] == len(semantic_relations)
assert manifest["counts"]["approved_reparentings"] == len(reparentings)
print("Livestock staging validation passed:", len(concepts), "concepts,",
      len(relations), "relations,", len(gaps), "gaps,", len(mappings), "mappings")
