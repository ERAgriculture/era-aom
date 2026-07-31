#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "review/livestock-v2/04_priority_recommendations.csv"
with PATH.open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))

expected = {
    "ID-AOM-006275", "PATH-BREWERS-GRAIN", "PARENT-006", "PARENT-007",
    "PARENT-036", "PARENT-078", "PARENT-200", "PARENT-227",
}
assert {row["case_id"] for row in rows} == expected
assert len(rows) == len(expected)
assert all(row["recommended_disposition"] for row in rows)
assert all(row["internal_evidence"] and row["external_evidence"] for row in rows)
assert all(row["reviewer_decision"] == "" for row in rows)
assert all(row["reviewer"] == "" and row["review_date"] == "" for row in rows)
assert all(row["confidence"] in {"medium", "high"} for row in rows)
print("Priority recommendation validation passed:", len(rows), "review cases")

