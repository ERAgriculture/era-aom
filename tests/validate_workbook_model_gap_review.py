#!/usr/bin/env python3
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


cohort = read(ROOT / "review/livestock-v18/workbook_model_gap_cohort.csv")
rows = read(ROOT / "review/livestock-v18/workbook_model_gap_review.csv")
facets = read(ROOT / "data/livestock-staging/approved_hard_tail_feed_material_facets.csv")
assert len(cohort) == len(rows) == 23
assert {row["concept_id"] for row in cohort} == {row["concept_id"] for row in rows}
assert Counter(row["status"] for row in rows) == {"held": 19, "approved": 4}
approved = {row["concept_id"] for row in rows if row["status"] == "approved"}
assert approved == {"AOM_001486", "AOM_001826", "AOM_002081", "AOM_003567"}
assert approved <= {row["feed_material_id"] for row in facets}
assert all(row["governed_source_identity"] and row["evidence"] for row in rows if row["status"] == "approved")
assert all(row["blocker_code"] for row in rows if row["status"] == "held")
lp = next(row for row in rows if row["concept_id"] == "AOM_001508")
assert lp["decision"] == "hold_hierarchy_correction_required"
assert "not a prebiotic" in lp["rationale"]
assert not any("ilri" in value.casefold() for row in rows for value in row.values())
print("Workbook model-gap review passed: 23 reviewed; 4 approved; 19 explicit holds")
