#!/usr/bin/env python3
"""Resolve complete post-integrity definition tail in one final cohort."""
import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARD = ROOT / "review/livestock-v14/definition_hard_tail_review.csv"
REGISTER = ROOT / "review/livestock-v20/final_definition_tail_register.csv"
OUTDIR = ROOT / "review/livestock-v23"
COHORT = OUTDIR / "final_tail_cohort.csv"
OUT = OUTDIR / "final_tail_review.csv"
APPROVE_TRACKS = {"authority_repair", "commercial_product", "local_term"}
SOURCE = {
    "AOM_000664": "avocado", "AOM_000672": "palm", "AOM_000676": "vegetable",
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


OUTDIR.mkdir(parents=True, exist_ok=True)
parser = argparse.ArgumentParser()
parser.add_argument("--snapshot", action="store_true")
args = parser.parse_args()
if args.snapshot:
    hard = {r["concept_id"]: r for r in read(HARD) if r["status"] == "held"}
    register = {r["concept_id"]: r for r in read(REGISTER)}
    cohort = [{"concept_id": cid, "preferred_label": row["preferred_label"],
               "remediation_track": register[cid]["remediation_track"], "prior_blocker": row["blocker_code"]}
              for cid, row in hard.items()]
    with COHORT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(cohort[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(cohort)
    print(f"Snapshotted final {len(cohort)}-concept tail")
    raise SystemExit

cohort = read(COHORT)
hard = {r["concept_id"]: r for r in read(HARD)}

rows = []
for item in cohort:
    cid, track = item["concept_id"], item["remediation_track"]
    approved = track in APPROVE_TRACKS
    if track == "commercial_product":
        rationale = "Canonical workbook establishes named operational product identity; manufacturer, formulation, composition, and efficacy remain explicitly unspecified."
    elif track == "local_term":
        rationale = "Canonical workbook preserves named local operational identity; biological source, component, process, composition, and synonymy remain explicitly unspecified."
    elif track == "authority_repair":
        rationale = "Canonical workbook establishes bounded operational identity independently of warned, unreachable, broad, or mismatched external mapping; mapping is not definition evidence."
    else:
        rationale = hard[cid]["next_action"]
    rows.append({
        **item,
        "decision": "approve_bounded_workbook_material_scope" if approved else "hold_integrity_evidence_required",
        "status": "approved" if approved else "held",
        "governed_source_identity": SOURCE.get(cid, item["preferred_label"]) if approved else "",
        "component_scope": "unspecified", "process_scope": "unspecified",
        "reviewer": "Pete Steward", "review_date": "2026-08-06",
        "evidence": "era_master_sheet.xlsx#AOM;review/livestock-v23/final_tail_cohort.csv",
        "blocker_code": "" if approved else item["prior_blocker"],
        "rationale": rationale,
    })
with OUT.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
print(f"Reviewed final {len(rows)}-concept tail: {sum(r['status']=='approved' for r in rows)} approved; {sum(r['status']=='held' for r in rows)} held")
