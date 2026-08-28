#!/usr/bin/env python3
"""Validate ADR 0052 field-key and lookup disposition recommendations."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "review/data-model-v1"
REVIEW = ROOT / "review/data-model-v3"


def read_csv(directory: Path, name: str) -> list[dict[str, str]]:
    with (directory / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


summary = json.loads((REVIEW / "disposition_summary.json").read_text(encoding="utf-8"))
source_fields = read_csv(SOURCE, "field_key_issues.csv")
source_lookups = [row for row in read_csv(SOURCE, "lookup_binding_audit.csv") if row["exact_match"] == "no"]
guided = read_csv(REVIEW, "guided_decision_recommendations.csv")
fields = read_csv(REVIEW, "field_key_disposition_recommendations.csv")
lookups = read_csv(REVIEW, "lookup_binding_disposition_recommendations.csv")
evidence = read_csv(REVIEW, "evidence_register.csv")

assert len(guided) == 8
assert {row["review_id"] for row in guided} == {f"SD-{number:02d}" for number in range(1, 9)}
assert all(row["recommendation_status"] == "proposed" for row in guided)
assert all(not row["human_decision"] and not row["reviewer"] and not row["review_date"] for row in guided)

assert len(fields) == len(source_fields) == 21
source_field_columns = list(source_fields[0])
for row, source_row in zip(fields, source_fields, strict=True):
    assert {column: row[column] for column in source_field_columns} == source_row
assert Counter(row["guided_disposition"] for row in fields) == {
    "consolidate-logical-field-with-round-profiles": 13,
    "hold-overlapping-duplicate-source-rows": 3,
    "hold-source-key-correction": 1,
    "hold-classify-metadata-or-remove": 3,
    "hold-assign-table-or-retire": 1,
}
overlap_holds = [row for row in fields if row["guided_disposition"] == "hold-overlapping-duplicate-source-rows"]
assert {(row["Table"], row["Field"]) for row in overlap_holds} == {
    ("Till.Out", "B.Code"),
    ("Animals.Diet", "D.Item.AOM"),
    ("Animals.Diet", "D.Item.Raw"),
}
assert all(row["source_edit_required"] == "no" for row in fields if row["guided_disposition"] == "consolidate-logical-field-with-round-profiles")
assert all(row["source_edit_required"] == "yes" for row in fields if row["guided_disposition"].startswith("hold-"))

assert len(lookups) == len(source_lookups) == 41
source_lookup_columns = list(source_lookups[0])
for row, source_row in zip(lookups, source_lookups, strict=True):
    assert {column: row[column] for column in source_lookup_columns} == source_row
assert Counter(row["guided_disposition"] for row in lookups) == {
    "hold-add-field-or-retire-lookup": 39,
    "hold-table-key-realignment-review": 2,
}
candidate_holds = [row for row in lookups if row["guided_disposition"] == "hold-table-key-realignment-review"]
assert {(row["Table"], row["Field"], row["candidate_registry_keys"]) for row in candidate_holds} == {
    ("Fert.Method", "M.Source", "Res.Method.M.Source"),
    ("Res.Out", "M.Process", "Res.Method.M.Process"),
}
assert all(row["recommendation_status"] == "held" for row in lookups)
assert all(not row["human_decision"] and not row["reviewer"] and not row["review_date"] for row in lookups)

assert summary["status"] == "recommendation-only"
assert summary["adr_status"] == "Accepted"
assert summary["guided_decision_count"] == len(guided)
assert summary["field_issue_count"] == len(fields)
assert summary["lookup_issue_count"] == len(lookups)
assert summary["profile_consolidation_recommendations"] == 13
assert summary["field_holds"] == 8
assert summary["lookup_holds"] == 41
assert summary["source_edit_holds"] == 49
for key in (
    "human_decision_recorded",
    "source_workbook_modified",
    "stable_keys_allocated",
    "bindings_created",
    "schema_regeneration_authorized",
    "release_authorized",
    "consumer_migration_authorized",
):
    assert summary[key] is False
assert len(evidence) == 5
assert all(row["supports"] and row["claim_boundary"] for row in evidence)

adr_text = (ROOT / "docs/decisions/0052-data-model-registry-and-shared-core-contract.md").read_text(encoding="utf-8")
assert "Status: Accepted" in adr_text
assert "data-model-v3/README.md" in adr_text

print("Validated ADR 0052 source dispositions: 21 field cases and 41 lookup holds")
