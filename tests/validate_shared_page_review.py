#!/usr/bin/env python3
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


cohort = read(ROOT / "review/livestock-v17/shared_page_cohort.csv")
rows = read(ROOT / "review/livestock-v17/shared_page_review.csv")
facets = read(ROOT / "data/livestock-staging/approved_hard_tail_feed_material_facets.csv")
assert len(cohort) == len(rows) == 32
assert {row["concept_id"] for row in cohort} == {row["concept_id"] for row in rows}
assert Counter(row["status"] for row in rows) == {"held": 26, "approved": 6}
approved = {row["concept_id"] for row in rows if row["status"] == "approved"}
assert approved == {"AOM_001334", "AOM_001818", "AOM_001837", "AOM_001914", "AOM_002106", "AOM_002136"}
assert approved <= {row["feed_material_id"] for row in facets}
assert all(row["governed_source_identity"] and row["evidence"] for row in rows if row["status"] == "approved")
assert all(row["blocker_code"] for row in rows if row["status"] == "held")
assert Counter(row["feedipedia_url"] for row in rows) == {url: 2 for url in {row["feedipedia_url"] for row in rows}}
assert not any("ilri" in value.casefold() for row in rows for value in row.values())
print("Shared-page review passed: 16 pairs; 6 approved; 26 explicit holds")
