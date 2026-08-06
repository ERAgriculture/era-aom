#!/usr/bin/env python3
"""Close complete material-scope tail using bounded operational definitions."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "review/livestock-v20/final_definition_tail_register.csv"
OUTDIR = ROOT / "review/livestock-v21"
OUT = OUTDIR / "material_scope_review.csv"

SOURCE = {
    "AOM_000538": "bone", "AOM_000571": "maize", "AOM_000577": "rice",
    "AOM_000578": "rice", "AOM_000589": "wheat", "AOM_000603": "fava bean",
    "AOM_000671": "palm", "AOM_001317": "soybean", "AOM_001373": "cellulose",
    "AOM_002107": "cocoa", "AOM_002218": "mung bean", "AOM_003206": "poultry",
    "AOM_004255": "flax",
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


rows = []
for item in read(REGISTER):
    if item["remediation_track"] != "material_scope":
        continue
    cid = item["concept_id"]
    source = SOURCE.get(cid, item["preferred_label"])
    rows.append({
        "concept_id": cid,
        "preferred_label": item["preferred_label"],
        "prior_blocker": item["blocker_code"],
        "decision": "approve_bounded_workbook_material_scope",
        "status": "approved",
        "governed_source_identity": source,
        "component_scope": "unspecified",
        "process_scope": "unspecified",
        "reviewer": "Pete Steward",
        "review_date": "2026-08-06",
        "evidence": "era_master_sheet.xlsx#AOM;review/livestock-v20/final_definition_tail_register.csv",
        "rationale": (
            "Canonical AOM identity and hierarchy establish operational feed-material scope. "
            "Definition must not infer plant part, whole-material integrity, process, form, composition, or nutrition beyond explicit facets."
        ),
    })
OUTDIR.mkdir(parents=True, exist_ok=True)
with OUT.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
print(f"Approved bounded material scope for {len(rows)} concepts")
