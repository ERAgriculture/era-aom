#!/usr/bin/env python3
"""Validate global identity audit coverage and concept-allocation freeze."""

import csv
import json
import re
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

assert len(cohort) == summary["duplicate_preferred_label_groups"]
assert len(detail) == summary["concepts_in_duplicate_groups"]
assert len(detail) - len(cohort) == summary["excess_identifiers"]
assert len({row["collision_id"] for row in cohort}) == len(cohort)
assert {row["collision_id"] for row in detail} == {row["collision_id"] for row in cohort}
assert all(row["review_status"] in {"proposed", "approved", "hold"} for row in cohort)
assert all(row["recommended_action"] for row in cohort)
assert summary["duplicate_preferred_label_groups"] <= BASELINE["maximum_duplicate_preferred_label_groups"]
assert summary["concepts_in_duplicate_groups"] <= BASELINE["maximum_concepts_in_duplicate_groups"]
assert summary["excess_identifiers"] <= BASELINE["maximum_excess_identifiers"]
assert len(remediations) == 16
assert len({row["generated_id"] for row in remediations}) == len(remediations)
assert {row["action"] for row in remediations} == {
    "reuse_existing", "rename_distinct", "hold_ambiguous"
}
assert all(row["status"] in {"approved", "hold"} for row in remediations)
assert (
    summary["reviewed_groups"]
    + summary["applied_reuse_remediations"]
    + summary["applied_rename_remediations"]
) == 16

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
