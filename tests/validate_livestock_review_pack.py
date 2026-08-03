#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/livestock-v2"
DATA = ROOT / "data/livestock-staging"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


collisions = read(REVIEW / "01_identity_collisions.csv")
parents = read(REVIEW / "02_missing_parent_candidates.csv")
decisions = read(REVIEW / "03_review_decisions.csv")
gaps = read(DATA / "hierarchy_gaps.csv")
relations = read(DATA / "relations.csv")
summary = json.loads((REVIEW / "summary.json").read_text())

assert len(collisions) == 4
assert {row["case_id"] for row in collisions} == {
    "ID-AOM-006275", "PATH-BREWERS-GRAIN"
}
assert len(parents) == summary["missing_parent_candidates"]
assert sum(
    int(row["affected_child_count"])
    for row in parents if row["priority"] != "resolved"
) == len(gaps)
assert len({row["case_id"] for row in parents}) == len(parents)
assert len(decisions) == len(parents) + 2
assert len({row["case_id"] for row in decisions}) == len(decisions)
approved = [row for row in decisions if row["decision"]]
assert len(approved) == 3
assert {row["case_id"] for row in approved} == {
    "ID-AOM-006275", "PATH-BREWERS-GRAIN", "PARENT-006",
}
identity_decision = next(row for row in approved if row["case_id"] == "ID-AOM-006275")
assert identity_decision["decision"] == "retain_and_map_existing"
assert identity_decision["approved_id"] == "AOM_006275"
brewers_decision = next(row for row in approved if row["case_id"] == "PATH-BREWERS-GRAIN")
assert brewers_decision["decision"] == "deprecate_with_replacement"
assert brewers_decision["approved_id"] == "AOM_000564"
mineral_decision = next(row for row in approved if row["case_id"] == "PARENT-006")
assert mineral_decision["decision"] == "mint"
assert mineral_decision["approved_id"] == "AOM_100849"
assert all(row["reviewer"] == "Pete Steward" for row in approved)
assert all(row["decision"] == "" for row in decisions if row not in approved)
collision_recommendation = next(
    row for row in read(REVIEW / "04_priority_recommendations.csv")
    if row["case_id"] == "ID-AOM-006275"
)
assert "existing AOM_001676" in collision_recommendation["recommended_disposition"]
assert "do not mint another concept" in collision_recommendation["recommended_disposition"]
collision_records = [
    row for row in collisions
    if row["case_id"] == "ID-AOM-006275"
]
assert {row["decision"] for row in collision_records} == {"retain", "map_to_existing"}
assert {row["replacement_id"] for row in collision_records} == {"", "AOM_001676"}
assert all(row["reviewer"] == "Pete Steward" for row in collision_records)
assert summary["safety"] == {
    "semantic_decisions_applied": 3,
    "identifiers_minted": 1,
    "hierarchy_changes_applied": 14,
}
assert "AOM_000230" not in {row["child_id"] for row in gaps}
assert "AOM_000230" in {row["subject_id"] for row in relations}
print("Livestock review-pack validation passed:", len(parents), "parent candidates")
