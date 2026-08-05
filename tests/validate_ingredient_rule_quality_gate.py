#!/usr/bin/env python3
"""Validate rule-quality review packet and promotion safety gate."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/livestock-v6"


def read(name):
    with (REVIEW / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


rules = read("ingredient_rule_quality_assessment.csv")
families = read("ingredient_family_rollout_plan.csv")
summary = json.loads((REVIEW / "ingredient_rule_quality_summary.json").read_text())

assert len(rules) == summary["rules_assessed"] == 68
assert len({row["rule_id"] for row in rules}) == 68
assert len(families) == summary["families"] == 20
assert sum(int(row["concept_count"]) for row in families) == 1643
assert all(row["approval_status"] == "proposed-for-bulk-review" for row in rules)
assert all(not row["reviewer"] and not row["review_date"] for row in rules)
assert summary["promotion_gate"]["status"] == "blocked-pending-human-rule-approval"
assert summary["promotion_gate"]["automatic_changes"] == 0

by_rule = {row["rule_id"]: row for row in rules}
assert by_rule["PROCESS-ENSILED"]["recommendation"] == "approve-bulk"
assert by_rule["PROCESS-GROUND"]["matched_concept_count"] == "342"
assert by_rule["COMPONENT-GRAIN"]["recommendation"] == "approve-with-guard"
for rule_id in {"FORM-CAKE", "FORM-OIL", "FORM-PULP", "FORM-MEAL", "FORM-HAY"}:
    assert by_rule[rule_id]["recommendation"] == "hold-model-gap"
for rule_id in {"QUALITY-YELLOW", "QUALITY-RIPE"}:
    assert by_rule[rule_id]["recommendation"] == "hold-model-gap"
assert by_rule["QUALITY-GREEN"]["recommendation"] == "defer-no-occurrences"
assert by_rule["PROCESS-DEHULLED"]["recommendation"] == "approve-bulk"
assert by_rule["AMBIGUOUS-WHOLE"]["recommendation"] == "hold-ambiguous"
assert all(
    row["sample_concepts"] or row["recommendation"] == "defer-no-occurrences"
    for row in rules
)
assert not any("ilri" in value.casefold() for row in rules for value in row.values())
print(
    f"Ingredient rule quality gate validation passed: {len(rules)} rules, "
    f"{len(families)} families; promotion blocked pending approval"
)
