#!/usr/bin/env python3
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


rows = read(ROOT / "review/livestock-v22/ontology_integrity_review.csv")
assert len(rows) == 32 and len({r["concept_id"] for r in rows}) == 32
assert Counter(r["status"] for r in rows) == {"held": 18, "approved": 14}
assert {r["remediation_track"] for r in rows} == {"semantic_model", "identity_consolidation", "identity_repair"}
assert all(r["governed_source_identity"] for r in rows if r["status"] == "approved")
assert all(r["blocker_code"] and not r["replacement_id"] for r in rows if r["status"] == "held")
unsafe = {"AOM_000638", "AOM_003359", "AOM_003858", "AOM_003929"}
assert all(next(r for r in rows if r["concept_id"] == cid)["decision"] == "hold_unsafe_descriptor_inference" for cid in unsafe)
print("Ontology-integrity closure passed: 32 reviewed; 14 approved; 18 held")
