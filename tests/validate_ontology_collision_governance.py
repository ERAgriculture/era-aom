#!/usr/bin/env python3
"""Validate governed dispositions for every global label collision."""

import csv
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW = ROOT / "review/livestock-v25"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_label(value):
    value = unicodedata.normalize("NFKC", value).casefold().strip()
    return re.sub(r"\s+", " ", value)


decisions = read(DATA / "approved_ontology_collision_decisions.csv")
cohort = read(REVIEW / "global_identity_collision_cohort.csv")
deprecations = read(DATA / "approved_deprecations.csv")
summary = json.loads((REVIEW / "global_identity_collision_summary.json").read_text())

assert len(decisions) == 93
assert len(cohort) == 92
assert Counter(row["decision"] for row in decisions) == {
    "retain_distinct": 66,
    "deprecate_replace": 26,
    "hold_identity": 1,
}
assert Counter(row["status"] for row in decisions) == {"approved": 92, "hold": 1}
assert all(row["reviewer"] == "Pete Steward" and row["review_date"] for row in decisions)

decisions_by_label = {}
for decision in decisions:
    label = normalize_label(decision["collision_key"])
    assert label not in decisions_by_label
    decisions_by_label[label] = decision
assert {row["normalized_label"] for row in cohort} <= set(decisions_by_label)
for group in cohort:
    decision = decisions_by_label[group["normalized_label"]]
    assert set(decision["concept_ids"].split(";")) == set(group["concept_ids"].split(";"))
    expected_status = "hold" if decision["decision"] == "hold_identity" else "approved"
    assert group["review_status"] == expected_status

holds = {
    row["collision_key"] for row in decisions if row["decision"] == "hold_identity"
}
assert holds == {"cotton seed"}

replacement_pairs = {
    (row["deprecated_id"], row["replacement_id"]) for row in deprecations
}
for decision in decisions:
    if decision["decision"] != "deprecate_replace":
        continue
    concept_ids = set(decision["concept_ids"].split(";"))
    assert any(
        deprecated_id in concept_ids and replacement_id == decision["retained_id"]
        for deprecated_id, replacement_id in replacement_pairs
    )

assert summary["reviewed_groups"] == 92
assert summary["approved_groups"] == 91
assert summary["held_groups"] == 1
assert summary["unreviewed_groups"] == 0
assert summary["status"] == "governed_with_holds"

manifest = json.loads((ROOT / "dist/livestock-staging/manifest.json").read_text())
assert manifest["counts"]["approved_ontology_collision_decisions"] == len(decisions)
print("Ontology collision governance validation passed: 93 decisions; 92 active groups; 0 unreviewed")
