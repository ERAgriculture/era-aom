#!/usr/bin/env python3
"""Assess ingredient rules for bulk approval without applying ontology changes."""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/livestock-v5"
OUT = ROOT / "review/livestock-v6"

FIELD_BY_DIMENSION = {
    "component": "component_candidates",
    "process": "process_candidates",
    "form": "form_candidates",
    "quality": "quality_candidates",
}
FORM_MODEL_GAPS = {"Cake", "Hay", "Meal", "Oil", "Pulp"}


def read(name):
    with (REVIEW / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


inventory = read("ingredient_harmonization_inventory.csv")
rules = read("ingredient_rule_catalog.csv")

assessment = []
for rule in rules:
    dimension = rule["dimension"]
    value = rule["normalized_value"]
    if dimension in FIELD_BY_DIMENSION:
        field = FIELD_BY_DIMENSION[dimension]
        matches = [row for row in inventory if value in row[field].split(";")]
    else:
        matches = [
            row for row in inventory
            if rule["safety_constraint"] in row["exception_reason"]
        ]
    families = sorted({row["ingredient_family"] for row in matches})
    samples = []
    seen_families = set()
    for row in sorted(matches, key=lambda item: (item["ingredient_family"], item["preferred_label"], item["concept_id"])):
        if row["ingredient_family"] not in seen_families:
            samples.append(f'{row["concept_id"]}: {row["preferred_label"]}')
            seen_families.add(row["ingredient_family"])
        if len(samples) == 5:
            break

    if not matches:
        recommendation = "defer-no-occurrences"
        risk = "unknown"
        guard = "Require observed source cases before approval."
        rationale = "Rule has no current governed ingredient occurrence."
    elif dimension == "process":
        recommendation = "approve-bulk"
        risk = "low"
        guard = "Assert process independently; never replace source identity or imply sequence beyond source evidence."
        rationale = "Explicit process participle maps to established processing dimension."
    elif dimension == "component":
        recommendation = "approve-with-guard"
        risk = "medium"
        guard = "Apply only when non-empty source identity remains; otherwise route to expert exception."
        rationale = "Component terms generalize across families but may also be standalone material identities."
    elif dimension == "form" and value not in FORM_MODEL_GAPS:
        recommendation = "approve-with-guard"
        risk = "medium"
        guard = "Apply only as presentation/form when source context confirms; preserve original material identity."
        rationale = "Term can describe physical presentation but requires a retained source identity."
    elif dimension in {"form", "quality"}:
        recommendation = "hold-model-gap"
        risk = "high"
        guard = "Do not promote until dedicated product-state, maturity, colour, or material-role model is approved."
        rationale = "Term can encode identity, product role, state, maturity, or quality rather than proposed dimension."
    else:
        recommendation = "hold-ambiguous"
        risk = "high"
        guard = rule["safety_constraint"]
        rationale = "Existing ambiguity rule correctly prevents automatic decomposition."

    assessment.append({
        "rule_id": rule["rule_id"], "dimension": dimension,
        "source_pattern": rule["source_pattern"], "normalized_value": value,
        "matched_concept_count": len(matches), "ingredient_family_count": len(families),
        "sample_concepts": " | ".join(samples), "risk": risk,
        "recommendation": recommendation, "required_guard": guard,
        "rationale": rationale, "approval_status": "proposed-for-bulk-review",
        "reviewer": "", "review_date": "",
    })

family_rows = []
for family in sorted({row["ingredient_family"] for row in inventory}):
    members = [row for row in inventory if row["ingredient_family"] == family]
    routes = Counter(row["review_route"] for row in members)
    family_rows.append({
        "ingredient_family": family, "concept_count": len(members),
        "rule_application_candidates": routes["rule_application_candidate"],
        "retain_atomic_candidates": routes["retain_atomic_candidate"],
        "batch_review": routes["batch_review"],
        "expert_exceptions": sum(
            row["review_route"] == "expert_exception" and row["governance_state"] == "unreviewed"
            for row in members
        ),
        "recommended_rollout": "approve_rules_then_validate_family_sample",
        "promotion_status": "blocked-until-rule-approval",
    })

recommendations = Counter(row["recommendation"] for row in assessment)
matched_by_recommendation = defaultdict(int)
for row in assessment:
    matched_by_recommendation[row["recommendation"]] += int(row["matched_concept_count"])
summary = {
    "rule_version": "1.0.0", "rules_assessed": len(assessment),
    "recommendations": dict(sorted(recommendations.items())),
    "rule_matches_by_recommendation": dict(sorted(matched_by_recommendation.items())),
    "families": len(family_rows),
    "promotion_gate": {
        "status": "blocked-pending-human-rule-approval",
        "automatic_changes": 0,
        "required_before_promotion": [
            "named reviewer approves selected rules and guards",
            "held rules remain excluded",
            "stratified family samples pass",
            "generated assertions pass semantic and regression validation",
            "legacy identifiers and approved replacements remain resolvable",
        ],
    },
}

OUT.mkdir(parents=True, exist_ok=True)
write(OUT / "ingredient_rule_quality_assessment.csv", assessment, list(assessment[0]))
write(OUT / "ingredient_family_rollout_plan.csv", family_rows, list(family_rows[0]))
(OUT / "ingredient_rule_quality_summary.json").write_text(
    json.dumps(summary, indent=2) + "\n", encoding="utf-8"
)
print(
    f"Assessed {len(assessment)} rules across {len(family_rows)} families: "
    + ", ".join(f"{value} {key}" for key, value in sorted(recommendations.items()))
)
