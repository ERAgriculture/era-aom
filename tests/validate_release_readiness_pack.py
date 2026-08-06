#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "review/livestock-v24"
with (DIR / "integrity_hold_reviewer_pack.csv").open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))
summary = json.loads((DIR / "release_readiness_summary.json").read_text())
assert len(rows) == len({r["concept_id"] for r in rows}) == 18
assert all(r["semantic_risk"] and r["blocker_code"] and r["evidence_gate"] and r["current_next_action"] for r in rows)
assert all(r["reviewer"] == "TBD" and not r["decision"] and not r["evidence"] for r in rows)
assert summary["remaining_integrity_holds"] == 18
assert summary["automated_local_acceptance"] == "pass"
assert summary["manual_visual_acceptance"] == "pending"
assert summary["hosting"] == "deferred" and summary["canonical_cutover"] is False
print("Release-readiness pack passed: 18 explicit holds; deployment gates remain separate")
