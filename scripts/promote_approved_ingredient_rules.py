#!/usr/bin/env python3
"""Record approved ingredient rules and generate guarded semantic assertions."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/livestock-v6"
WORKBENCH = ROOT / "review/livestock-v5"
DATA = ROOT / "data/livestock-staging"
REVIEWER = "Pete Steward"
DATE = "2026-08-05"
APPROVED_RULE_IDS = {
    "PROCESS-ALKALI_TREATED", "PROCESS-AUTOCLAVED", "PROCESS-BOILED",
    "PROCESS-CRACKED", "PROCESS-CRUSHED", "PROCESS-DRIED",
    "PROCESS-ENSILED", "PROCESS-ENZYME_TREATED", "PROCESS-EXTRUDED",
    "PROCESS-FERMENTED", "PROCESS-GROUND", "PROCESS-HEATED",
    "PROCESS-MOLASSES_TREATED", "PROCESS-PRESSED", "PROCESS-ROASTED",
    "PROCESS-SOAKED", "PROCESS-SPROUTED", "PROCESS-UREA_TREATED", "PROCESS-WILTED",
    "COMPONENT-BLOOD", "COMPONENT-BRAN", "COMPONENT-COB", "COMPONENT-GRAIN",
    "COMPONENT-HUSK", "COMPONENT-KERNEL", "COMPONENT-LEAF", "COMPONENT-PEEL",
    "COMPONENT-POD", "COMPONENT-ROOT", "COMPONENT-SEED", "COMPONENT-SHELL",
    "COMPONENT-STEM", "COMPONENT-TUBER",
    "COMPONENT-VINE", "FORM-BLOCK", "FORM-PELLET", "FORM-POWDER",
}
APPROVAL_OVERRIDES = {
    "COMPONENT-BLOOD": {
        "approval_scope": "approve-with-guard",
        "required_guard": "Apply only when non-empty source identity remains; otherwise route to expert exception.",
        "rationale": "Component terms generalize across families but may also be standalone material identities.",
    },
}

FIELD_BY_DIMENSION = {
    "component": "component_candidates",
    "process": "process_candidates",
    "form": "form_candidates",
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


assessment = read(REVIEW / "ingredient_rule_quality_assessment.csv")
inventory = read(WORKBENCH / "ingredient_harmonization_inventory.csv")
facet_concepts = read(DATA / "approved_ingredient_facet_concepts.csv")
manual_assertions = read(DATA / "approved_feed_material_facets.csv")

approved = [
    row for row in assessment
    if row["rule_id"] in APPROVED_RULE_IDS
]
assert len(approved) == len(APPROVED_RULE_IDS) == 37
assert {row["rule_id"] for row in approved} == APPROVED_RULE_IDS
approved_rows = []
for row in approved:
    preserved = APPROVAL_OVERRIDES.get(row["rule_id"], {})
    approved_rows.append({
        "rule_id": row["rule_id"], "dimension": row["dimension"],
        "source_pattern": row["source_pattern"], "normalized_value": row["normalized_value"],
        "approval_scope": preserved.get("approval_scope", row["recommendation"]),
        "required_guard": preserved.get("required_guard", row["required_guard"]),
        "status": "approved", "reviewer": REVIEWER, "review_date": DATE,
        "evidence": "review/livestock-v6/ingredient_rule_quality_assessment.csv",
        "rationale": preserved.get("rationale", row["rationale"]),
    })
write(
    DATA / "approved_ingredient_harmonization_rules.csv", approved_rows,
    list(approved_rows[0]),
)

facet_by_label = {
    (row["facet"], row["preferred_label"]): row
    for row in facet_concepts if row["concept_role"] == "facet_value"
}
facet_name = {
    "component": "anatomical_part",
    "process": "processing_method",
    "form": "presentation_form",
}
component_facet_override = {
    "Bran": "material_component",
}
existing = {
    (row["feed_material_id"], row["target_property"], row["target_concept_id"])
    for row in manual_assertions
}
assertions = []
for material in inventory:
    if material["governance_state"] == "approved_deprecated":
        continue
    for rule in approved_rows:
        field = FIELD_BY_DIMENSION[rule["dimension"]]
        if rule["normalized_value"] not in material[field].split(";"):
            continue
        if rule["approval_scope"] == "approve-with-guard" and not material["source_identity_candidate"]:
            continue
        lookup_label = (
            rule["normalized_value"] + " form"
            if rule["dimension"] == "form" else rule["normalized_value"]
        )
        target_facet = (
            component_facet_override.get(lookup_label, facet_name[rule["dimension"]])
            if rule["dimension"] == "component" else facet_name[rule["dimension"]]
        )
        target = facet_by_label[(target_facet, lookup_label)]
        triple = (material["concept_id"], target["target_property"], target["concept_id"])
        if triple in existing:
            continue
        assertions.append({
            "feed_material_id": material["concept_id"],
            "target_property": target["target_property"],
            "target_concept_id": target["concept_id"],
            "target_label": target["preferred_label"],
            "rule_id": rule["rule_id"], "status": "approved-generated",
            "reviewer": REVIEWER, "review_date": DATE,
            "evidence": "data/livestock-staging/approved_ingredient_harmonization_rules.csv",
            "rationale": "Generated from approved rule under recorded guard; legacy material identity preserved.",
        })

assertions.sort(key=lambda row: (
    row["feed_material_id"], row["target_property"], row["target_concept_id"]
))
assert len({
    (row["feed_material_id"], row["target_property"], row["target_concept_id"])
    for row in assertions
}) == len(assertions)
write(
    DATA / "approved_generated_feed_material_facets.csv", assertions,
    list(assertions[0]),
)
(DATA / "ingredient_rule_promotion_manifest.json").write_text(
    json.dumps({
        "rule_version": "1.1.0", "status": "approved-and-promoted",
        "reviewer": REVIEWER, "review_date": DATE,
        "approved_rules": len(approved_rows),
        "generated_assertions": len(assertions),
        "unapproved_rules": len(assessment) - len(approved_rows),
        "legacy_identifiers_preserved": True,
        "ilri_identifiers_used": False,
    }, indent=2) + "\n",
    encoding="utf-8",
)
print(f"Approved {len(approved_rows)} rules; generated {len(assertions)} guarded assertions")
