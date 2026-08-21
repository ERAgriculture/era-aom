#!/usr/bin/env python3
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "review" / "livestock-v39"


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


inventory = read_rows(OUT / "composition_form_inventory.csv")
review = read_rows(OUT / "composition_form_review.csv")
assertions = read_rows(OUT / "affected_material_assertions.csv")
specific = read_rows(OUT / "specific_material_review.csv")
overlaps = read_rows(OUT / "axis_overlap_review.csv")
collisions = read_rows(OUT / "label_collision_audit.csv")
evidence = read_rows(OUT / "evidence_register.csv")
authorities = read_rows(OUT / "authority_comparison.csv")
summary = json.loads((OUT / "composition_form_summary.json").read_text())
evidence_ids = {row["evidence_id"] for row in evidence}

assert len(inventory) == len(review) == 40
assert len({row["concept_id"] for row in inventory}) == 40
assert len({row["concept_id"] for row in review}) == 40
assert Counter(row["review_axis"] for row in inventory) == {
    "physical-characteristic": 5,
    "presentation-form": 11,
    "bulk-consistency": 4,
    "moisture-condition": 3,
    "component-retention": 5,
    "dual-use-constituent": 9,
    "specific-material": 3,
}

inventory_by_id = {row["concept_id"]: row for row in inventory}
review_by_id = {row["concept_id"]: row for row in review}
for row in review:
    assert row["preferred_label"] == inventory_by_id[row["concept_id"]]["preferred_label"]
    assert row["recommended_disposition"]
    assert row["recommended_semantic_action"]
    assert row["rationale"]
    assert row["status"] in {"approved", "held"}
    assert set(row["evidence_ids"].split(";")) <= evidence_ids

assert Counter(row["status"] for row in review) == {"approved": 38, "held": 2}
assert review_by_id["AOM_000324"]["recommended_disposition"] == "deprecate-and-replace"
assert review_by_id["AOM_101050"]["status"] == "held"
assert review_by_id["AOM_101115"]["proposed_label"] == "Feed component-retention states"
assert review_by_id["AOM_101116"]["recommended_disposition"] == "deprecate-after-migration"
assert review_by_id["AOM_101134"]["proposed_label"] == "Native-fat retention"
assert review_by_id["AOM_101080"]["recommended_disposition"] == "deprecate-category-error"
assert review_by_id["AOM_101064"]["status"] == "held"
assert review_by_id["AOM_101120"]["recommended_disposition"] == "retain-deprecation"
assert review_by_id["AOM_001938"]["recommended_disposition"] == "retain-and-add-product-role"

assert len(assertions) == 796
assert Counter(row["target_property"] for row in assertions) == {
    "aom:presentationForm": 358,
    "aom:moistureCondition": 400,
    "aom:bulkConsistency": 7,
    "aom:componentRetentionState": 5,
    "aom:compositionState": 3,
    "aom:primaryConstituent": 23,
}
assert all(row["target_concept_id"] in review_by_id for row in assertions)
assert sum("migrate" in row["recommended_assertion_action"] for row in assertions) == 3
assert sum("remove tautological" in row["recommended_assertion_action"] for row in assertions) == 1

assert len(specific) == 3
specific_by_id = {row["concept_id"]: row for row in specific}
assert specific_by_id["AOM_000764"]["recommended_disposition"] == "retain-distinct-formulation"
assert specific_by_id["AOM_000766"]["recommended_disposition"] == "retain-distinct-formulation"
assert specific_by_id["AOM_001938"]["proposed_target"] == "AOM_101062 By-product role"
assert all(set(row["evidence_ids"].split(";")) <= evidence_ids for row in specific)

assert len(overlaps) == 8
assert {row["case_id"] for row in overlaps} == {
    "FORM-001", "FORM-002", "FORM-003", "FORM-004", "FORM-005",
    "RETENTION-001", "CHEMICAL-001", "ROLE-001",
}
assert all(set(row["evidence_ids"].split(";")) <= evidence_ids for row in overlaps)

assert len(collisions) == 9
collision_by_label = {row["candidate_label"]: row for row in collisions}
assert collision_by_label["Starch"]["decision"] == "blocked-collision"
assert collision_by_label["Oil"]["decision"] == "blocked-collision"
assert collision_by_label["Feed physical descriptors"]["candidate_concept_id"] == "UNALLOCATED"

assert len(authorities) == 6
assert all(set(row["evidence_ids"].split(";")) <= evidence_ids for row in authorities)
assert summary["status"] == "accepted-recommendation"
assert summary["reviewed_concepts"] == 40
assert summary["affected_material_assertions"] == 796
assert summary["review_status_counts"] == {"approved": 38, "held": 2}
assert summary["implementation_changes"] == 0
assert summary["allocated_identifiers"] == 0
assert summary["proposed_navigation_concepts_without_ids"] == ["Feed physical descriptors"]

hash_targets = {
    "inventory_sha256": "composition_form_inventory.csv",
    "review_sha256": "composition_form_review.csv",
    "assertions_sha256": "affected_material_assertions.csv",
    "specific_materials_sha256": "specific_material_review.csv",
    "overlap_sha256": "axis_overlap_review.csv",
    "collision_sha256": "label_collision_audit.csv",
    "evidence_sha256": "evidence_register.csv",
    "authority_sha256": "authority_comparison.csv",
}
for key, filename in hash_targets.items():
    assert summary["outputs"][key] == sha256(OUT / filename)

adr = (ROOT / "docs" / "decisions" / "0049-composition-form-and-component-retention-model.md").read_text()
method = (ROOT / "docs" / "methods" / "composition-form-and-retention-governance.md").read_text()
recommendations = (OUT / "RECOMMENDATIONS.md").read_text()
assert "- Status: Accepted" in adr
assert "## Authority comparison" in adr
assert "## Evidence" in adr
assert "40 concepts and 796 affected material" in adr
assert "Status: accepted with ADR 0049." in method
assert "Accepted by Pete Steward on 2026-08-21" in adr
assert "## Authority comparison" in recommendations
assert "## Guided Skosmos acceptance plan" in recommendations

print(json.dumps({
    "status": "pass",
    "reviewed_concepts": len(review),
    "affected_material_assertions": len(assertions),
    "review_status_counts": dict(sorted(Counter(row["status"] for row in review).items())),
    "specific_materials": sorted(specific_by_id),
}, indent=2))
