#!/usr/bin/env python3
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    with (ROOT / "review/livestock-v23" / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


cohort, rows = read("final_tail_cohort.csv"), read("final_tail_review.csv")
assert len(cohort) == len(rows) == 55
assert {r["concept_id"] for r in cohort} == {r["concept_id"] for r in rows}
assert Counter(r["status"] for r in rows) == {"approved": 37, "held": 18}
assert {r["remediation_track"] for r in rows if r["status"] == "approved"} == {
    "authority_repair", "commercial_product", "local_term"
}
assert all(r["governed_source_identity"] and not r["blocker_code"] for r in rows if r["status"] == "approved")
assert all(r["blocker_code"] and not r["governed_source_identity"] for r in rows if r["status"] == "held")
print("Final definition-tail closure passed: 55 reviewed; 37 approved; 18 integrity holds")
