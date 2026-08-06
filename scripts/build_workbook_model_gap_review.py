#!/usr/bin/env python3
"""Build frozen decisions for workbook-only identity and model gaps."""
import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARD = ROOT / "review/livestock-v14/definition_hard_tail_review.csv"
WORKBOOK = ROOT / "review/livestock-v13/workbook_source_scope_review.csv"
REVIEW = ROOT / "review/livestock-v18"
COHORT = REVIEW / "workbook_model_gap_cohort.csv"
OUT = REVIEW / "workbook_model_gap_review.csv"

APPROVED = {
    "AOM_001486": ("Lignobond", "approve_workbook_binder_role", "Canonical workbook classifies named material as binder; composition remains unspecified."),
    "AOM_001826": ("ChemBind", "approve_workbook_binder_role", "Canonical workbook classifies named material as binder; composition remains unspecified."),
    "AOM_002081": ("mixed marine material", "approve_workbook_hydrolysate", "Canonical workbook identifies mixed marine hydrolysate under animal by-product hydrolysates."),
    "AOM_003567": ("cheka", "approve_workbook_residue", "Canonical workbook identifies Cheka residue under cereal by-products."),
}
LOCAL = {"AOM_000693", "AOM_000695", "AOM_001105", "AOM_001831", "AOM_001921", "AOM_006006"}
COMMERCIAL = {
    "AOM_000748", "AOM_000749", "AOM_000765", "AOM_001497", "AOM_001500", "AOM_001501",
    "AOM_001579", "AOM_001868", "AOM_001870", "AOM_003747", "AOM_003749", "AOM_006331",
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


parser = argparse.ArgumentParser()
parser.add_argument("--snapshot", action="store_true")
args = parser.parse_args()
if args.snapshot:
    rows = [
        {"concept_id": row["concept_id"], "preferred_label": row["preferred_label"]}
        for row in read(HARD) if row["status"] == "held" and row["blocker_code"] == "workbook_identity_or_model_gap"
    ]
    write(COHORT, rows)
    print(f"Snapshotted {len(rows)} workbook model-gap concepts")
    raise SystemExit

workbook = {row["concept_id"]: row for row in read(WORKBOOK)}
rows = []
for item in read(COHORT):
    cid = item["concept_id"]
    source, decision, status, blocker = "", "hold_external_product_evidence", "held", "external_product_evidence"
    rationale = "Workbook classification alone does not establish branded product composition, manufacturer, or stable identity."
    if cid in APPROVED:
        source, decision, rationale = APPROVED[cid]
        status, blocker = "approved", ""
    elif cid in LOCAL:
        decision, blocker = "hold_local_identity_evidence", "local_identity_evidence"
        rationale = "Local or ambiguous name lacks geographic, biological, or product identity needed for public definition."
    elif cid == "AOM_001508":
        decision, blocker = "hold_hierarchy_correction_required", "hierarchy_correction_required"
        rationale = "Lactobacillus plantarum is a microbial taxon, not a prebiotic; approve taxon identity and probiotic role before definition."
    elif cid not in COMMERCIAL:
        decision, blocker = "hold_domain_identity_evidence", "domain_identity_evidence"
        rationale = "Workbook path does not establish stable public material identity or composition."
    rows.append({
        "concept_id": cid, "preferred_label": item["preferred_label"],
        "canonical_path": workbook[cid]["canonical_path"], "decision": decision,
        "status": status, "governed_source_identity": source, "blocker_code": blocker,
        "reviewer": "Pete Steward", "review_date": "2026-08-06",
        "evidence": workbook[cid]["evidence"], "rationale": rationale,
    })
write(OUT, rows)
print(f"Reviewed {len(rows)} workbook model-gap concepts: {sum(r['status']=='approved' for r in rows)} approved")
