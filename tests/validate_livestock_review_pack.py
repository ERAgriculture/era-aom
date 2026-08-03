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
remodeling = read(REVIEW / "schema_remodeling_candidates.csv")
cereal_brief = (REVIEW / "CEREAL_BYPRODUCT_RECOMMENDATIONS.md").read_text()
legume_brief = (REVIEW / "LEGUME_BYPRODUCT_RECOMMENDATIONS.md").read_text()
identity_review = read(REVIEW / "identity_review_candidates.csv")

assert len(collisions) == 4
assert summary["status"] == "review-and-governance"
assert "14 missing-parent cases" in cereal_brief
assert "13 missing-parent cases" in legume_brief
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
assert len(approved) == 35
assert {row["case_id"] for row in approved} == {
    "ID-AOM-006275", "PATH-BREWERS-GRAIN", "PARENT-006", "PARENT-007",
    "PARENT-036", "PARENT-078", "PARENT-200", "PARENT-227",
    "PARENT-031", "PARENT-032", "PARENT-033", "PARENT-034", "PARENT-035",
    "PARENT-037", "PARENT-038", "PARENT-039", "PARENT-040", "PARENT-041",
    "PARENT-042", "PARENT-043", "PARENT-044", "PARENT-045",
    "PARENT-065", "PARENT-066", "PARENT-067", "PARENT-068", "PARENT-069",
    "PARENT-070", "PARENT-071", "PARENT-072", "PARENT-073", "PARENT-074",
    "PARENT-075", "PARENT-076", "PARENT-077",
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
ingredient_decision = next(row for row in approved if row["case_id"] == "PARENT-007")
assert ingredient_decision["decision"] == "mint"
assert ingredient_decision["approved_id"] == "AOM_100850"
maize_decision = next(row for row in approved if row["case_id"] == "PARENT-036")
assert maize_decision["decision"] == "mint"
assert maize_decision["approved_id"] == "AOM_100851"
for case_id, approved_id in {
    "PARENT-078": "AOM_100852",
    "PARENT-200": "AOM_100853",
    "PARENT-227": "AOM_100854",
}.items():
    decision = next(row for row in approved if row["case_id"] == case_id)
    assert decision["decision"] == "mint"
    assert decision["approved_id"] == approved_id
for case_id, approved_id in {
    "PARENT-031": "AOM_100855", "PARENT-032": "AOM_100856",
    "PARENT-033": "AOM_100857", "PARENT-035": "AOM_100858",
    "PARENT-037": "AOM_100859", "PARENT-038": "AOM_100860",
    "PARENT-040": "AOM_100861", "PARENT-041": "AOM_100862",
    "PARENT-042": "AOM_100863", "PARENT-044": "AOM_100864",
}.items():
    decision = next(row for row in approved if row["case_id"] == case_id)
    assert decision["decision"] == "mint" and decision["approved_id"] == approved_id
for case_id, approved_id in {
    "PARENT-034": "AOM_000594", "PARENT-039": "AOM_100860",
    "PARENT-043": "AOM_100863", "PARENT-045": "AOM_100864",
}.items():
    decision = next(row for row in approved if row["case_id"] == case_id)
    assert decision["decision"] == "reparent" and decision["approved_id"] == approved_id
for case_id, approved_id in {
    "PARENT-065": "AOM_100865", "PARENT-066": "AOM_100866",
    "PARENT-067": "AOM_100867", "PARENT-068": "AOM_100868",
    "PARENT-070": "AOM_100869", "PARENT-072": "AOM_100870",
    "PARENT-074": "AOM_100871", "PARENT-075": "AOM_100872",
    "PARENT-076": "AOM_100873", "PARENT-077": "AOM_100874",
}.items():
    decision = next(row for row in approved if row["case_id"] == case_id)
    assert decision["decision"] == "mint" and decision["approved_id"] == approved_id
for case_id, approved_id in {
    "PARENT-069": "AOM_100866", "PARENT-071": "AOM_100869",
    "PARENT-073": "AOM_100866",
}.items():
    decision = next(row for row in approved if row["case_id"] == case_id)
    assert decision["decision"] == "reparent" and decision["approved_id"] == approved_id
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
assert {row["concept_id"] for row in remodeling} == {
    "AOM_000531", "AOM_000532", "AOM_000533", "AOM_000534", "AOM_000535",
    "AOM_000612", "AOM_002020", "AOM_000944", "AOM_000945", "AOM_000946",
    "AOM_000947", "AOM_000948", "AOM_000950", "AOM_000951", "AOM_000954",
    "AOM_001178", "AOM_002013", "AOM_001618", "AOM_006143", "AOM_001276",
    "AOM_006316", "AOM_002086", "AOM_000587",
    "AOM_001646", "AOM_001366",
}
assert all(row["status"] == "deferred" for row in remodeling)
assert {row["trigger_case"] for row in remodeling} == {
    "PARENT-007", "PARENT-078", "PARENT-200", "PARENT-032", "PARENT-038",
    "PARENT-042", "PARENT-043", "PARENT-044",
    "PARENT-067", "PARENT-072",
}
assert len(identity_review) == 1
assert identity_review[0]["case_id"] == "IDENTITY-BEAN-VINE"
assert identity_review[0]["status"] == "pending"
assert summary["safety"] == {
    "semantic_decisions_applied": 35,
    "identifiers_minted": 26,
    "hierarchy_changes_applied": 167,
}
assert "AOM_000230" not in {row["child_id"] for row in gaps}
assert "AOM_000230" in {row["subject_id"] for row in relations}
print("Livestock review-pack validation passed:", len(parents), "parent candidates")
