#!/usr/bin/env python3
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


cohort = read(ROOT / "review/livestock-v16/identity_alias_cohort.csv")
rows = read(ROOT / "review/livestock-v16/identity_alias_review.csv")
facets = read(ROOT / "data/livestock-staging/approved_hard_tail_feed_material_facets.csv")
corrections = read(ROOT / "data/livestock-staging/approved_label_corrections.csv")
assert len(cohort) == len(rows) == 39
assert {row["concept_id"] for row in cohort} == {row["concept_id"] for row in rows}
assert Counter(row["status"] for row in rows) == {"held": 30, "approved": 9}
approved = {row["concept_id"] for row in rows if row["status"] == "approved"}
assert approved == {"AOM_000601", "AOM_001482", "AOM_001811", "AOM_001845", "AOM_002166", "AOM_003072", "AOM_003482", "AOM_003911", "AOM_006008"}
assert all(row["governed_source_identity"] and row["evidence"] for row in rows if row["status"] == "approved")
assert all(row["blocker_code"] for row in rows if row["status"] == "held")
assert approved <= {row["feed_material_id"] for row in facets}
assert {row["concept_id"] for row in corrections if row["case_id"] in {"LABEL-ZIZIPHUS-MAURITIANA", "LABEL-CYNODON-DACTYLON"}} == {"AOM_001265", "AOM_001462"}
assert not any("ilri" in value.casefold() for row in rows for value in row.values())
print("Identity/alias review passed: 39 reviewed; 9 approved; 30 explicit holds")
