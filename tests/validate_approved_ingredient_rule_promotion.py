#!/usr/bin/env python3
"""Validate signed ingredient-rule promotion and guarded generated assertions."""

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW5 = ROOT / "review/livestock-v5"
REVIEW6 = ROOT / "review/livestock-v6"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


approved = read(DATA / "approved_ingredient_harmonization_rules.csv")
generated = read(DATA / "approved_generated_feed_material_facets.csv")
manual = read(DATA / "approved_feed_material_facets.csv")
facets = read(DATA / "approved_ingredient_facet_concepts.csv")
inventory = read(REVIEW5 / "ingredient_harmonization_inventory.csv")
assessment = read(REVIEW6 / "ingredient_rule_quality_assessment.csv")
manifest = json.loads((DATA / "ingredient_rule_promotion_manifest.json").read_text())

recommended = {
    row["rule_id"] for row in assessment
    if row["recommendation"] in {"approve-bulk", "approve-with-guard"}
}
held = {
    row["rule_id"] for row in assessment
    if row["recommendation"].startswith("hold")
}
assert len(approved) == len(recommended) == 40
assert recommended - {row["rule_id"] for row in approved} == {"PROCESS-DEHULLED"}
assert {row["rule_id"] for row in approved} - recommended == {"COMPONENT-BLOOD"}
assert not ({row["rule_id"] for row in approved} & held)
assert all(
    row["status"] == "approved" and row["reviewer"] == "Pete Steward"
    and row["review_date"] == "2026-08-05"
    for row in approved
)
assert len(generated) == 1599
assert manifest == {
    "rule_version": "1.0.0", "status": "approved-and-promoted",
    "reviewer": "Pete Steward", "review_date": "2026-08-05",
    "approved_rules": 40, "generated_assertions": 1599,
    "unapproved_rules": 28, "legacy_identifiers_preserved": True,
    "ilri_identifiers_used": False,
}
assert len({
    (row["feed_material_id"], row["target_property"], row["target_concept_id"])
    for row in generated
}) == len(generated)
assert all(row["status"] == "approved-generated" and row["reviewer"] == "Pete Steward" for row in generated)
assert {row["target_concept_id"] for row in generated} <= {
    row["concept_id"] for row in facets
}

inventory_by_id = {row["concept_id"]: row for row in inventory}
approval_by_id = {row["rule_id"]: row for row in approved}
for row in generated:
    material = inventory_by_id[row["feed_material_id"]]
    rule = approval_by_id[row["rule_id"]]
    assert material["governance_state"] != "approved_deprecated"
    if rule["approval_scope"] == "approve-with-guard":
        assert material["source_identity_candidate"]

by_material = defaultdict(set)
for row in generated + manual:
    by_material[row["feed_material_id"]].add((row["target_property"], row["target_label"]))
assert by_material["AOM_000536"] == {("aom:processingMethod", "Grinding")}
assert ("aom:processingMethod", "Grinding") in by_material["AOM_001324"]
assert by_material["AOM_001326"] == {
    ("aom:materialComponent", "Whole crop"),
    ("aom:processingMethod", "Ensiling"),
}
assert "AOM_006072" not in by_material
assert ("aom:processingMethod", "Soaking") in by_material["AOM_006500"]
assert ("aom:materialIntegrity", "Whole-grain integrity") in by_material["AOM_001313"]
assert ("aom:ingredientPart", "Grain") in by_material["AOM_001313"]
assert not any(row["rule_id"] == "PROCESS-DEHULLED" for row in generated)
assert not any(row["target_label"] in {"Cake form", "Pulp form"} for row in generated)
assert "AOM_001898" not in {row["feed_material_id"] for row in generated}
assert ("aom:compositionState", "Whole-milk composition") in by_material["AOM_000555"]
assert ("aom:feedProductType", "Compound feed") in by_material["AOM_000801"]
assert ("aom:feedProductType", "Processing pulp") in by_material["AOM_001836"]
assert by_material["AOM_000687"] >= {
    ("aom:feedProductType", "Hay product type"), ("aom:processingMethod", "Drying")
}

families_with_candidates = {
    row["ingredient_family"] for row in inventory
    if row["review_route"] == "rule_application_candidate"
}
families_with_assertions = {
    inventory_by_id[row["feed_material_id"]]["ingredient_family"] for row in generated
}
assert families_with_candidates <= families_with_assertions
print(
    f"Approved ingredient rule promotion validation passed: {len(approved)} rules, "
    f"{len(generated)} guarded assertions"
)
