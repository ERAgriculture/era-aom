#!/usr/bin/env python3
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "livestock-staging"
REVIEW = ROOT / "review" / "livestock-v34"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


review_rows = read(ROOT / "review/livestock-v31/feed_product_kind_review.csv")
implementation = read(REVIEW / "feed_product_kind_implementation_register.csv")
evidence = read(REVIEW / "evidence_register.csv")
collisions = read(REVIEW / "identity_collision_audit.csv")
temporary = read(REVIEW / "temporary_unclassified_register.csv")
new_concepts = read(DATA / "approved_new_concepts.csv")
registry = read(DATA / "livestock_id_registry.csv")
classifications = read(DATA / "approved_feed_taxonomy_classifications.csv")
semantic_types = read(DATA / "approved_concept_semantic_types.csv")
concepts = read(DATA / "concepts.csv")
labels = read(DATA / "labels.csv")
definitions = read(DATA / "definitions.csv")
relations = read(DATA / "relations.csv")
summary = json.loads((REVIEW / "feed_product_kind_implementation_summary.json").read_text())

assert len(review_rows) == len(implementation) == 32
assert {row["concept_id"] for row in review_rows} == {row["concept_id"] for row in implementation}
assert all(row["reviewer"] == "Pete Steward" and row["implementation_date"] == "2026-08-16" for row in implementation)
assert all("0045-feed-product-kind-and-source-navigation.md" in row["decision_record"] for row in implementation)
assert len(evidence) == 14
assert len(collisions) == 7
assert all(row["decision"] == "approved-no-collision" and not row["matched_concept_ids"] for row in collisions)
assert temporary == [{
    "concept_id": "AOM_001866",
    "preferred_label": "Glycerol",
    "reason": "FeedMaterial status is supported but generic concept scope does not distinguish crude glycerine, refined glycerine, or chemical glycerol.",
    "evidence_gap": "Align AOM scope to applicable catalogue entries and represented source records.",
    "owner": "Pete Steward",
    "target_cohort": "Cohort A follow-up; era-program issue 52",
    "review_date": "2026-08-16",
    "resolution_deadline": "before next public livestock release",
    "status": "temporary-unclassified",
}]

new_by_id = {row["concept_id"]: row for row in new_concepts}
expected_new = {
    "AOM_101159": ("Plant products and by-products", "AOM_100850"),
    "AOM_101160": ("Other feeds", "AOM_100850"),
    "AOM_101161": ("Other biological feed materials", "AOM_101160"),
    "AOM_101162": ("Unclassified feed materials", "AOM_101160"),
}
for concept_id, (label, parent) in expected_new.items():
    assert new_by_id[concept_id]["preferred_label"] == label
    assert new_by_id[concept_id]["broader_id"] == parent

registered = {row["concept_id"]: row for row in registry}
assert {row["concept_id"] for row in registry} == {f"AOM_{number:06d}" for number in range(100849, 101182)}
for concept_id in {"AOM_101156", "AOM_101157", "AOM_101158"}:
    assert registered[concept_id]["status"] == "retired-before-publication"
for concept_id in expected_new:
    assert registered[concept_id]["status"] == "allocated"

known = {row["concept_id"] for row in concepts}
rejected = {"AOM_101156", "AOM_101157", "AOM_101158"}
assert rejected.isdisjoint(known)
assert rejected.isdisjoint(row["concept_id"] for row in labels)
assert rejected.isdisjoint(row["concept_id"] for row in definitions)
assert rejected.isdisjoint(row["subject_id"] for row in relations)
assert rejected.isdisjoint(row["object_id"] for row in relations)

pref = {row["concept_id"]: row["label"] for row in labels if row["label_type"] == "pref"}
assert pref["AOM_000559"] == "Feeds of animal origin"
assert pref["AOM_000735"] == "Forage materials"
assert pref["AOM_101147"] == "Chemical substances"
for concept_id, (label, _) in expected_new.items():
    assert pref[concept_id] == label

parents = {}
for row in relations:
    if row["relation_type"] == "broader":
        parents.setdefault(row["subject_id"], set()).add(row["object_id"])
assert parents["AOM_100850"] == {"AOM_000328"}
assert {
    child for child, parent_ids in parents.items() if "AOM_100850" in parent_ids
} == {"AOM_000559", "AOM_000735", "AOM_101159", "AOM_101160"}
expected_parents = {
    "AOM_100976": "AOM_000559",
    "AOM_001916": "AOM_101159",
    "AOM_100921": "AOM_101159",
    "AOM_001832": "AOM_101159",
    "AOM_100987": "AOM_101160",
    "AOM_101139": "AOM_101160",
    "AOM_006334": "AOM_101160",
    "AOM_100989": "AOM_101161",
    "AOM_006241": "AOM_101161",
    "AOM_001866": "AOM_101162",
    "AOM_000561": "AOM_101142",
    "AOM_001922": "AOM_101142",
    "AOM_006349": "AOM_101142",
    "AOM_001068": "AOM_101142",
    "AOM_002072": "AOM_101142",
    "AOM_000809": "AOM_101146",
    "AOM_001865": "AOM_101146",
}
for concept_id, parent in expected_parents.items():
    assert parents[concept_id] == {parent}, (concept_id, parents[concept_id])

classification_by_id = {row["concept_id"]: row for row in classifications}
for concept_id in {"AOM_000561", "AOM_001922", "AOM_006349", "AOM_001068"}:
    assert classification_by_id[concept_id]["status"] == "hold"
    assert not classification_by_id[concept_id]["semantic_class"]
for concept_id in {"AOM_001866", "AOM_006241"} | set(expected_new):
    assert classification_by_id[concept_id]["semantic_class"] == "aom:FeedMaterial"

semantic_type_by_id = {row["concept_id"]: row["semantic_class"] for row in semantic_types}
assert semantic_type_by_id["AOM_000809"] == "aom:ChemicalConstituent"
assert semantic_type_by_id["AOM_001865"] == "aom:ChemicalConstituent"
assert "AOM_001068" not in semantic_type_by_id

assert summary == {
    "status": "implemented-candidate",
    "decision": "docs/decisions/0045-feed-product-kind-and-source-navigation.md",
    "reviewed_rows": 32,
    "approved_rows": 21,
    "held_rows": 11,
    "new_navigation_concepts": 4,
    "reserved_rejected_identifiers": ["AOM_101156", "AOM_101157", "AOM_101158"],
    "label_changes": 3,
    "hierarchy_revisions": 12,
    "temporary_unclassified_members": 1,
    "feed_material_direct_children": ["AOM_000559", "AOM_000735", "AOM_101159", "AOM_101160"],
    "reviewer": "Pete Steward",
    "implementation_date": "2026-08-16",
}
print("Validated Cohort A product-kind implementation: 32 dispositions, 4 navigation concepts, 6 holds")
