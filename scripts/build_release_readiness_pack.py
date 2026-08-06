#!/usr/bin/env python3
"""Build final integrity-hold reviewer pack and readiness summary."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARD = ROOT / "review/livestock-v14/definition_hard_tail_review.csv"
REGISTER = ROOT / "review/livestock-v20/final_definition_tail_register.csv"
OUTDIR = ROOT / "review/livestock-v24"
OUT = OUTDIR / "integrity_hold_reviewer_pack.csv"
SUMMARY = OUTDIR / "release_readiness_summary.json"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


register = {r["concept_id"]: r for r in read(REGISTER)}
rows = []
for current in read(HARD):
    if current["status"] != "held":
        continue
    source = register[current["concept_id"]]
    rows.append({
        "concept_id": current["concept_id"],
        "preferred_label": current["preferred_label"],
        "remediation_track": source["remediation_track"],
        "semantic_risk": source["semantic_risk"],
        "blocker_code": current["blocker_code"],
        "candidate_related_ids": source["candidate_related_ids"],
        "decision_required": (
            "retain_hold | approve_bounded_definition | deprecate_with_replacement | correct_identity | add_facet_then_approve"
        ),
        "evidence_gate": source["resolution_gate"],
        "current_next_action": current["next_action"],
        "reviewer": "TBD",
        "review_date": "",
        "decision": "",
        "evidence": "",
        "rationale": "",
    })
OUTDIR.mkdir(parents=True, exist_ok=True)
with OUT.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
summary = {
    "release_candidate": "2026.1-rc.1",
    "automated_local_acceptance": "pass",
    "manual_visual_acceptance": "pending",
    "hosting": "deferred",
    "canonical_cutover": False,
    "remaining_integrity_holds": len(rows),
    "by_track": dict(sorted(Counter(r["remediation_track"] for r in rows).items())),
    "by_blocker": dict(sorted(Counter(r["blocker_code"] for r in rows).items())),
}
SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(f"Built release-readiness pack for {len(rows)} integrity holds")
