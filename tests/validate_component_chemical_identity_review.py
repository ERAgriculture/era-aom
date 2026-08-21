#!/usr/bin/env python3
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "review" / "livestock-v37"
def read_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


review_rows = read_rows(OUT / "component_chemical_review.csv")
inventory_rows = read_rows(OUT / "component_chemical_inventory.csv")
usage_rows = read_rows(OUT / "material_usage_inventory.csv")
anatomy_rows = read_rows(OUT / "anatomical_authority_mapping.csv")
collision_rows = read_rows(OUT / "identity_overlap_review.csv")
evidence_ids = {
    row["evidence_id"] for row in read_rows(OUT / "evidence_register.csv")
}
summary = json.loads((OUT / "component_chemical_summary.json").read_text())
expected_axes = {
    axis: {row["concept_id"] for row in inventory_rows if row["review_axis"] == axis}
    for axis in {"chemical-identity", "composition", "material-component"}
}

assert len(review_rows) == len(inventory_rows) == 164
assert len({row["concept_id"] for row in review_rows}) == 164
for axis, expected_ids in expected_axes.items():
    actual_ids = {
        row["concept_id"] for row in review_rows if row["review_axis"] == axis
    }
    assert actual_ids == expected_ids, (axis, expected_ids ^ actual_ids)

review_by_id = {row["concept_id"]: row for row in review_rows}
inventory_by_id = {row["concept_id"]: row for row in inventory_rows}
for row in review_rows:
    assert row["preferred_label"] == inventory_by_id[row["concept_id"]]["preferred_label"]
    assert row["recommended_disposition"]
    assert row["recommended_semantic_action"]
    assert row["rationale"]
    assert row["status"] in {"approved", "held"}
    assert set(row["evidence_ids"].split(";")) <= evidence_ids

assert review_by_id["AOM_101146"]["proposed_label"] == "Feed-related chemical entities"
assert review_by_id["AOM_000196"]["proposed_label"] == "Feed composition characteristics"
assert review_by_id["AOM_101023"]["proposed_label"] == "Chemical constituent categories"
assert review_by_id["AOM_101120"]["recommended_disposition"] == "deprecate-after-migration"
assert review_by_id["AOM_101103"]["recommended_disposition"] == "deprecate-after-reuse-review"
assert review_by_id["AOM_101144"]["recommended_disposition"] == "retire-structural-wrapper"
assert review_by_id["AOM_101154"]["recommended_disposition"] == "retire-category-error"
assert review_by_id["AOM_101029"]["recommended_disposition"] == "split-meaning"
assert review_by_id["AOM_101153"]["mapping_candidate"].startswith("PO:0009089")
assert review_by_id["AOM_101116"]["recommended_disposition"] == "hold-for-cohort-e"

assert len(anatomy_rows) == len({row["concept_id"] for row in anatomy_rows}) == 31
assert sum(row["mapping_status"] == "exact-label-candidate" for row in anatomy_rows) == 16
assert not any(row["recommended_group"] == "Other anatomical components" for row in anatomy_rows)

assert len(collision_rows) == 9
assert {row["case_id"] for row in collision_rows} == {
    f"IDENTITY-{number:03d}" for number in range(1, 10)
}
assert all(set(row["evidence_ids"].split(";")) <= evidence_ids for row in collision_rows)

assert len(usage_rows) == 627
property_counts = Counter(row["target_property"] for row in usage_rows)
assert property_counts == {
    "aom:ingredientPart": 509,
    "aom:materialComponent": 87,
    "aom:primaryConstituent": 23,
    "aom:compositionState": 8,
}
assert all(row["target_concept_id"] in review_by_id for row in usage_rows)

assert summary["status"] == "accepted-recommendation"
assert summary["decision_status"] == "row-dispositions-approved-with-explicit-holds"
assert summary["reviewed_concepts"] == 164
assert summary["affected_material_assertions"] == 627
assert summary["identity_overlap_cases"] == 9
assert summary["implementation_changes"] == 0
assert summary["allocated_identifiers"] == 0
assert summary["review_status_counts"] == {"approved": 145, "held": 19}
assert summary["outputs"]["review_sha256"] == sha256(OUT / "component_chemical_review.csv")
assert summary["outputs"]["identity_overlap_sha256"] == sha256(OUT / "identity_overlap_review.csv")
assert summary["proposed_navigation_concepts_without_ids"] == [
    "Plant anatomical components",
    "Animal anatomical components",
]

adr = (
    ROOT
    / "docs"
    / "decisions"
    / "0048-chemical-identity-composition-and-component-model.md"
).read_text()
assert "- Status: Accepted" in adr
assert "Accepted by Pete Steward on 2026-08-20." in adr

print(
    json.dumps(
        {
            "status": "pass",
            "reviewed_concepts": len(review_rows),
            "affected_material_assertions": len(usage_rows),
            "anatomical_children_reviewed": len(anatomy_rows),
            "review_status_counts": dict(sorted(Counter(row["status"] for row in review_rows).items())),
        },
        indent=2,
    )
)
