#!/usr/bin/env python3
"""Review complete semantic-model and identity-integrity tail."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "review/livestock-v20/final_definition_tail_register.csv"
OUTDIR = ROOT / "review/livestock-v22"
OUT = OUTDIR / "ontology_integrity_review.csv"
TRACKS = {"semantic_model", "identity_consolidation", "identity_repair"}
APPROVED = {
    "AOM_001382", "AOM_001561", "AOM_001562", "AOM_001805", "AOM_001871",
    "AOM_001903", "AOM_002200", "AOM_003996", "AOM_001216", "AOM_001389",
    "AOM_001476", "AOM_001892", "AOM_003893", "AOM_006350",
}
SOURCE = {"AOM_001892": "sorghum"}
UNSAFE = {"AOM_000638", "AOM_003359", "AOM_003858", "AOM_003929"}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


rows = []
for item in read(REGISTER):
    if item["remediation_track"] not in TRACKS:
        continue
    cid = item["concept_id"]
    approved = cid in APPROVED
    decision = "approve_bounded_workbook_material_scope" if approved else "hold_integrity_evidence_required"
    rationale = (
        "Canonical AOM identity and hierarchy establish bounded operational material scope; contradictory external mappings remain excluded and no component or process is inferred."
        if approved else
        "Replacement direction, corrected identity, or missing semantic facet requires explicit evidence before changing ontology identity or scope."
    )
    if cid in UNSAFE:
        decision = "hold_unsafe_descriptor_inference"
        rationale = "Shaft or vein cannot be approximated to an existing anatomical facet; retain raw identity until governed model exists."
    rows.append({
        "concept_id": cid, "preferred_label": item["preferred_label"],
        "remediation_track": item["remediation_track"], "prior_blocker": item["blocker_code"],
        "decision": decision, "status": "approved" if approved else "held",
        "governed_source_identity": SOURCE.get(cid, item["preferred_label"]) if approved else "",
        "replacement_id": "", "component_scope": "unspecified", "process_scope": "unspecified",
        "reviewer": "Pete Steward", "review_date": "2026-08-06",
        "evidence": "era_master_sheet.xlsx#AOM;data/livestock-staging/approved_mapping_reviews.csv",
        "blocker_code": "" if approved else item["blocker_code"], "rationale": rationale,
    })
OUTDIR.mkdir(parents=True, exist_ok=True)
with OUT.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
print(f"Reviewed {len(rows)} ontology-integrity concepts: {sum(r['status']=='approved' for r in rows)} approved")
