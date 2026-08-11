#!/usr/bin/env python3
"""Validate global identity audit coverage and concept-allocation freeze."""

import csv
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/livestock-v25"
BASELINE = json.loads((ROOT / "config/identity-integrity-baseline.json").read_text())


def rows(name):
    with (REVIEW / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


cohort = rows("global_identity_collision_cohort.csv")
detail = rows("global_identity_collision_detail.csv")
summary = json.loads((REVIEW / "global_identity_collision_summary.json").read_text())
remediations = rows_from_data = list(csv.DictReader(
    (ROOT / "data/livestock-staging/approved_identity_integrity_remediations.csv").open(
        encoding="utf-8", newline=""
    )
))
decisions = list(csv.DictReader(
    (ROOT / "data/livestock-staging/approved_ontology_collision_decisions.csv").open(
        encoding="utf-8", newline=""
    )
))


def normalize_label(value):
    value = unicodedata.normalize("NFKC", value).casefold().strip()
    return re.sub(r"\s+", " ", value)

assert len(cohort) == summary["duplicate_preferred_label_groups"]
assert len(detail) == summary["concepts_in_duplicate_groups"]
assert len(detail) - len(cohort) == summary["excess_identifiers"]
assert len({row["collision_id"] for row in cohort}) == len(cohort)
assert {row["collision_id"] for row in detail} == {row["collision_id"] for row in cohort}
assert all(row["review_status"] in {"proposed", "approved", "hold"} for row in cohort)
assert all(row["recommended_action"] for row in cohort)
assert summary["reviewed_groups"] == len(cohort)
assert summary["approved_groups"] == 92
assert summary["held_groups"] == 1
assert summary["unreviewed_groups"] == 0
assert summary["status"] == "governed_with_holds"
assert all(
    row["reviewer"] and row["review_date"]
    for row in cohort if row["review_status"] in {"approved", "hold"}
)
assert summary["duplicate_preferred_label_groups"] <= BASELINE["maximum_duplicate_preferred_label_groups"]
assert summary["concepts_in_duplicate_groups"] <= BASELINE["maximum_concepts_in_duplicate_groups"]
assert summary["excess_identifiers"] <= BASELINE["maximum_excess_identifiers"]
assert len(remediations) == 17
assert len({row["generated_id"] for row in remediations}) == len(remediations)
assert {row["action"] for row in remediations} == {
    "reuse_existing", "rename_distinct"
}
assert all(row["status"] == "approved" for row in remediations)

decision_by_label = {}
for decision in decisions:
    key = normalize_label(decision["collision_key"])
    assert key not in decision_by_label
    decision_by_label[key] = decision
assert len(decision_by_label) == len(cohort)
for row in cohort:
    decision = decision_by_label[row["normalized_label"]]
    assert set(decision["concept_ids"].split(";")) == set(row["concept_ids"].split(";"))
    if not row["generated_ids"]:
        assert row["recommended_action"] == decision["decision"]
        assert row["candidate_canonical_id"] == decision["retained_id"]
    expected_status = (
        "hold"
        if decision["status"] == "hold" or decision["decision"].startswith("hold_")
        else "approved"
    )
    assert row["review_status"] == expected_status

if BASELINE["new_identifier_allocation_frozen"]:
    with (ROOT / "data/livestock-staging/livestock_id_registry.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        registry = list(csv.DictReader(handle))
    numeric = [int(re.search(r"(\d+)$", row["concept_id"]).group(1)) for row in registry]
    assert max(numeric) <= BASELINE["frozen_generated_identifier_frontier"]

print(
    "Global identity audit validated: "
    f'{len(cohort)} groups, {len(detail)} concepts, '
    f'{len(detail) - len(cohort)} excess identifiers'
)
