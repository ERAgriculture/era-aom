#!/usr/bin/env python3
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


cohort = read(ROOT / "review/livestock-v19/authority_model_cohort.csv")
rows = read(ROOT / "review/livestock-v19/authority_model_review.csv")
facets = read(ROOT / "data/livestock-staging/approved_hard_tail_feed_material_facets.csv")
assert len(cohort) == len(rows) == 63
assert Counter(row["status"] for row in rows) == {"held": 46, "approved": 17}
approved = {row["concept_id"] for row in rows if row["status"] == "approved"}
assert approved == {"AOM_000557", "AOM_000610", "AOM_000611", "AOM_000616", "AOM_001193", "AOM_001254", "AOM_001297", "AOM_001308", "AOM_001439", "AOM_001603", "AOM_001675", "AOM_001761", "AOM_001817", "AOM_001842", "AOM_001846", "AOM_006003", "AOM_006169"}
assert approved <= {row["feed_material_id"] for row in facets}
assert all(row["governed_source_identity"] and row["evidence"] for row in rows if row["status"] == "approved")
for cid in {"AOM_000638", "AOM_001805", "AOM_003359", "AOM_003858", "AOM_003929"}:
    row = next(row for row in rows if row["concept_id"] == cid)
    assert row["decision"] == "hold_unsafe_descriptor_inference"
assert not any("ilri" in value.casefold() for row in rows for value in row.values())
print("Consolidated authority/model review passed: 63 reviewed; 17 approved; 46 holds")
