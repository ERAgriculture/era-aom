#!/usr/bin/env python3
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "livestock-staging"
REVIEW_V29 = ROOT / "review" / "livestock-v29"
REVIEW_V30 = ROOT / "review" / "livestock-v30"
REVIEW_V31 = ROOT / "review" / "livestock-v31"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


v29 = read(REVIEW_V29 / "feed_taxonomy_adversarial_review.csv")
classifications = read(DATA / "approved_feed_taxonomy_classifications.csv")
implementation = read(REVIEW_V30 / "feed_taxonomy_implementation_register.csv")
product_kind_review = read(REVIEW_V31 / "feed_product_kind_review.csv")
evidence = read(REVIEW_V30 / "evidence_register.csv")
new_concepts = read(DATA / "approved_new_concepts.csv")
retirements = read(DATA / "approved_concept_retirements.csv")
deprecations = read(DATA / "approved_deprecations.csv")
semantic_types = read(DATA / "approved_concept_semantic_types.csv")
role_assertions = read(DATA / "approved_feed_role_assertions.csv")
role_review = read(REVIEW_V30 / "feed_product_role_review.csv")
retention_relations = read(DATA / "approved_component_retention_relations.csv")
registry = read(DATA / "livestock_id_registry.csv")
concepts = read(DATA / "concepts.csv")
labels = read(DATA / "labels.csv")
definitions = read(DATA / "definitions.csv")
relations = read(DATA / "relations.csv")
decompositions = read(DATA / "approved_ingredient_component_decompositions.csv")
summary = json.loads((REVIEW_V30 / "feed_taxonomy_implementation_summary.json").read_text())

v29_ids = {row["concept_id"] for row in v29}
classification_by_id = {row["concept_id"]: row for row in classifications}
implementation_by_id = {row["concept_id"]: row for row in implementation}
assert len(v29) == len(v29_ids) == 220
assert set(implementation_by_id) == v29_ids
assert v29_ids <= set(classification_by_id)
assert summary == {
    "component_retention_relations": 5,
    "concept_semantic_types": 21,
    "evidence_sources": 15,
    "generated_ids_retired_before_publication": ["AOM_101068", "AOM_101109"],
    "implementation_statuses": {
        "hold": 66,
        "implemented": 67,
        "implemented-structural": 81,
        "outside-scope": 6,
    },
    "new_concepts": 21,
    "product_role_concepts_reviewed": 10,
    "reviewed_concepts": 220,
    "role_assertions": 16,
    "semantic_classes": {
        "aom:Feed": 62,
        "aom:FeedAdditive": 15,
        "aom:FeedFormulation": 16,
        "aom:FeedMaterial": 42,
        "none": 85,
    },
    "source_concept_retirements": 8,
}
superseded_ids = {row["concept_id"] for row in product_kind_review}
cohort_d_superseded_ids = {
    "AOM_001571", "AOM_101019", "AOM_101029", "AOM_101103", "AOM_101104", "AOM_101105", "AOM_101106",
    "AOM_101115", "AOM_101120", "AOM_101144", "AOM_101146", "AOM_101154",
}
for concept_id in v29_ids - superseded_ids - cohort_d_superseded_ids:
    current = classification_by_id[concept_id]
    historical = implementation_by_id[concept_id]
    for field in {
        "preferred_label", "implementation_status", "semantic_class",
        "target_parent_id", "reviewer", "review_date", "rationale",
    }:
        assert current[field] == historical[field], (concept_id, field)
    assert "0044-feed-taxonomy-axis-reclassification.md" in current["evidence"]
    assert "feed-taxonomy-governance.md" in current["evidence"]

new_rows = [row for row in new_concepts if row["case_id"].startswith("FEED-TAXONOMY-")]
new_ids = {f"AOM_{number:06d}" for number in range(101135, 101156)}
assert len(new_rows) == 21
assert {row["concept_id"] for row in new_rows} == new_ids
registered = {row["concept_id"]: row for row in registry}
assert all(registered[concept_id]["status"] == "allocated" for concept_id in new_ids)

labels_by_value = {}
for row in labels:
    labels_by_value.setdefault(row["label"].casefold(), set()).add(row["concept_id"])
for row in new_rows:
    if row["concept_id"] in cohort_d_superseded_ids:
        continue
    assert labels_by_value[row["preferred_label"].casefold()] == {row["concept_id"]}

retired_generated = {"AOM_101068", "AOM_101109"}
known = {row["concept_id"] for row in concepts}
assert retired_generated.isdisjoint(known)
assert retired_generated.isdisjoint(row["concept_id"] for row in labels)
assert retired_generated.isdisjoint(row["concept_id"] for row in definitions)
assert retired_generated.isdisjoint(row["target_concept_id"] for row in decompositions)
assert all(registered[concept_id]["status"] == "retired-before-publication" for concept_id in retired_generated)

retirement_ids = {row["concept_id"] for row in retirements}
assert retirement_ids == {
    "AOM_000531", "AOM_000532", "AOM_000533", "AOM_000534",
    "AOM_000535", "AOM_000736", "AOM_000781", "AOM_001507",
    "AOM_101105", "AOM_101106", "AOM_101154",
}
concept_status = {row["concept_id"]: row["status"] for row in concepts}
assert all(concept_status[concept_id] == "deprecated" for concept_id in retirement_ids)
assert all(row["status"] == "approved" and row["history_note"] for row in retirements)
assert not any(
    row["relation_type"] == "broader" and row["subject_id"] in retirement_ids
    for row in relations
)
assert not any(
    row["relation_type"] == "broader"
    and row["object_id"] in retirement_ids
    and concept_status[row["subject_id"]] != "deprecated"
    for row in relations
)

replacement_by_id = {row["deprecated_id"]: row["replacement_id"] for row in deprecations}
assert {key: replacement_by_id[key] for key in {"AOM_000745", "AOM_000747", "AOM_001917"}} == {
    "AOM_000745": "AOM_101079",
    "AOM_000747": "AOM_101151",
    "AOM_001917": "AOM_101152",
}
assert len(role_assertions) == 16
assert len({(row["subject_id"], row["relation_property"], row["role_concept_id"]) for row in role_assertions}) == 16
assert {row["relation_property"] for row in role_assertions} == {"aom:functionalRole", "aom:experimentalRole"}
assert len(role_review) == len({row["concept_id"] for row in role_review}) == 10
assert {
    (row["concept_id"], row["target_parent_id"])
    for row in role_review
} == {
    ("AOM_101148", "AOM_101022"),
    ("AOM_101062", "AOM_101148"),
    ("AOM_101061", "AOM_101148"),
    ("AOM_101055", "AOM_101061"),
    ("AOM_101056", "AOM_101061"),
    ("AOM_101058", "AOM_101061"),
    ("AOM_101057", "AOM_101062"),
    ("AOM_101059", "AOM_101062"),
    ("AOM_101060", "AOM_101062"),
    ("AOM_101063", "AOM_101062"),
}
assert len(retention_relations) == 5
assert len({(row["state_concept_id"], row["relation_property"], row["retained_concept_id"]) for row in retention_relations}) == 5
semantic_type_by_id = {row["concept_id"]: row["semantic_class"] for row in semantic_types}
assert len(semantic_types) == len(semantic_type_by_id) == 50
assert semantic_type_by_id["AOM_000809"] == "aom:ChemicalConstituent"
assert semantic_type_by_id["AOM_001865"] == "aom:ChemicalConstituent"
assert "AOM_001068" not in semantic_type_by_id

broader = {
    (row["subject_id"], row["object_id"])
    for row in relations if row["relation_type"] == "broader"
}
assert {
    ("AOM_101104", "AOM_101143"),
    ("AOM_101143", "AOM_101085"),
    ("AOM_101019", "AOM_101085"),
    ("AOM_101145", "AOM_101085"),
    ("AOM_101110", "AOM_101115"),
    ("AOM_101115", "AOM_000328"),
    ("AOM_101130", "AOM_000845"),
    ("AOM_004433", "AOM_101135"),
    ("AOM_001579", "AOM_004433"),
    ("AOM_001497", "AOM_006334"),
    ("AOM_101062", "AOM_101148"),
    ("AOM_101061", "AOM_101148"),
    ("AOM_101055", "AOM_101061"),
    ("AOM_101056", "AOM_101061"),
    ("AOM_101058", "AOM_101061"),
    ("AOM_101057", "AOM_101062"),
    ("AOM_101059", "AOM_101062"),
    ("AOM_101060", "AOM_101062"),
    ("AOM_101063", "AOM_101062"),
} <= broader
assert ("AOM_101128", "AOM_000826") in broader
assert ("AOM_101128", "AOM_101130") not in broader

preferred = {
    row["concept_id"]: row["label"]
    for row in labels if row["language"] == "en" and row["label_type"] == "pref"
}
assert preferred["AOM_101104"] == "Bran"
assert preferred["AOM_101110"] == "Whole-grain composition"
assert preferred["AOM_101130"] == "Feed component separation processes"
assert preferred["AOM_004433"] == "Coccidiostats and histomonostats"
assert preferred["AOM_006334"] == "Rumen-protected fat feed materials"
assert preferred["AOM_101055"] == "Discarded-material waste role"
assert preferred["AOM_101057"] == "Offal by-product role"
assert preferred["AOM_101059"] == "Production-residue by-product role"
assert preferred["AOM_101060"] == "Milling by-product role"
assert preferred["AOM_101063"] == "Crop-residue by-product role"

assert len(evidence) == len({row["evidence_id"] for row in evidence}) == 15
assert all(row["uri"].startswith("https://") and row["supports"] and row["limitations"] for row in evidence)
methods = (ROOT / "docs" / "methods" / "feed-taxonomy-governance.md").read_text()
adr = (ROOT / "docs" / "decisions" / "0044-feed-taxonomy-axis-reclassification.md").read_text()
assert "## Authority comparison" in methods
assert "## Evidence trail" in methods
assert "Status: accepted for staging" in adr
assert "## Evidence" in adr

print("Validated 220 v30 feed-taxonomy implementations with preserved evidence trail.")
