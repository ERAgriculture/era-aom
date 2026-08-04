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
label_corrections = read("approved_label_corrections")
new_concepts = read("approved_new_concepts")
id_registry = read("livestock_id_registry")
semantic_relations = read("approved_semantic_relations")
reparentings = read("approved_reparentings")
semantic_bindings = read("approved_semantic_bindings")
semantic_value_bindings = read("approved_semantic_value_bindings")
manifest = json.loads((DIST / "manifest.json").read_text())
ids = [row["concept_id"] for row in concepts]
known = set(ids)
assert len(legacy) == 2503
assert len(ids) == 2671 and len(ids) == len(known)
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
assert len(deprecations) == 2
assert len(semantic_bindings) == 13
assert len(semantic_value_bindings) == 49
assert {
    (row["deprecated_id"], row["replacement_id"])
    for row in deprecations
} == {
    ("AOM_001884", "AOM_000564"),
    ("AOM_004000", "AOM_003960"),
}
assert manifest["counts"]["approved_semantic_bindings"] == 13
assert manifest["counts"]["approved_semantic_value_bindings"] == 49
assert len(label_corrections) == 6
assert len(new_concepts) == 170
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
    f"AOM_{number:06d}" for number in range(100849, 101019)
}
assert {row["concept_id"] for row in id_registry} <= known
status = {row["concept_id"]: row["status"] for row in concepts}
assert status["AOM_001884"] == "deprecated"
assert status["AOM_004000"] == "deprecated"
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
} == {
    ("AOM_001884", "replaced_by", "AOM_000564"),
    ("AOM_004000", "replaced_by", "AOM_003960"),
}
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
assert {
    row["subject_id"] for row in relations
    if row["relation_type"] == "broader" and row["object_id"] == "AOM_100850"
} >= ingredient_children
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
    children = set(new_concept["child_ids"].split(";"))
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
assert len(semantic_relations) == 21
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
}
assert len(reparentings) == 64
for reparenting in reparentings:
    children = set(reparenting["child_ids"].split(";"))
    assert {
        row["subject_id"] for row in relations
        if row["relation_type"] == "broader"
        and row["object_id"] == reparenting["target_parent_id"]
    } >= children
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
assert gaps == []
corrected_labels = {
    row["concept_id"]: row["label"] for row in labels
    if row["source_column"] == "approved_label_correction"
}
assert corrected_labels == {
    "AOM_001898": "Bothriochloa dried",
    "AOM_006373": "Ficus exasperata leaves and twigs",
    "AOM_002090": "Harrisonia abyssinica leaves",
    "AOM_003981": "Ziziphus jujuba leaves",
    "AOM_002507": "Fourth trimester",
    "AOM_001084": "Variable cost—inoculants",
}
for correction in label_corrections:
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
assert manifest["counts"]["replacement_relations"] == 2
assert manifest["counts"]["semantic_relations"] == len(semantic_relations)
assert manifest["counts"]["hierarchy_gaps"] == len(gaps)
assert manifest["counts"]["mapping_assertions"] == len(mappings)
assert manifest["counts"]["approved_identity_resolutions"] == len(resolutions)
assert manifest["counts"]["approved_mapping_replacements"] == len(replacements)
assert manifest["counts"]["approved_deprecations"] == len(deprecations)
assert manifest["counts"]["approved_label_corrections"] == len(label_corrections)
assert manifest["counts"]["approved_new_concepts"] == len(new_concepts)
assert manifest["counts"]["registered_livestock_ids"] == len(id_registry)
assert manifest["counts"]["approved_semantic_relations"] == len(semantic_relations)
assert manifest["counts"]["approved_reparentings"] == len(reparentings)
print("Livestock staging validation passed:", len(concepts), "concepts,",
      len(relations), "relations,", len(gaps), "gaps,", len(mappings), "mappings")
