#!/usr/bin/env python3
"""Build frozen identity/alias decisions for remaining Feedipedia hard tail."""
import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARD = ROOT / "review/livestock-v14/definition_hard_tail_review.csv"
FEED = ROOT / "review/livestock-v11/feedipedia_source_scope_review.csv"
REVIEW = ROOT / "review/livestock-v16"
COHORT = REVIEW / "identity_alias_cohort.csv"
OUT = REVIEW / "identity_alias_review.csv"

APPROVED = {
    "AOM_000601": ("cowpea", "approve_exact_material_identity", "Feedipedia heading directly identifies cowpea haulms."),
    "AOM_001482": ("sugar beet", "approve_word_order_alias", "Beet molasses and sugar beet molasses identify same material."),
    "AOM_001811": ("ruminant digestive contents", "approve_datasheet_identity", "Feedipedia datasheet identifies rumen contents independently of fresh, dried, or ensiled variants."),
    "AOM_001845": ("barley malt", "approve_industry_alias", "Feedipedia identifies malt culms as barley sprouts and rootlets."),
    "AOM_002166": ("sugarcane", "approve_source_material_identity", "Feedipedia identifies bagasse as sugarcane processing residue; table dehydration is narrower than retained source material."),
    "AOM_003072": ("groundnut", "approve_common_name_identity", "Peanut and groundnut are common names for same governed crop source; table identifies unshelled seed material."),
    "AOM_003482": ("sugar beet", "approve_source_material_identity", "Feedipedia identifies fresh sugar-beet root; governed concept retains source plus root component."),
    "AOM_003911": ("cassava", "approve_spelling_variant_identity", "Feedipedia spelling “sievate” and workbook “sieviate” identify same cassava processing residue."),
    "AOM_006008": ("chicken", "approve_narrower_source_identity", "Chicken is governed poultry source; Feedipedia datasheet establishes poultry manure independently of dehydration variant."),
}
CONTRADICTORY = {"AOM_001216", "AOM_001476", "AOM_001892", "AOM_003893", "AOM_004002"}
SPELLING = {"AOM_001265", "AOM_001462"}


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
        for row in read(HARD)
        if row["status"] == "held" and row["blocker_code"] == "identity_or_alias_review"
    ]
    write(COHORT, rows)
    print(f"Snapshotted {len(rows)} identity/alias concepts")
    raise SystemExit

feed = {row["concept_id"]: row for row in read(FEED)}
rows = []
for item in read(COHORT):
    cid = item["concept_id"]
    source, decision, rationale = "", "hold_granularity_mismatch", "Feedipedia target is broader, narrower, or differently processed; related evidence does not establish concept identity."
    status, blocker = "held", "granularity_mismatch"
    if cid in APPROVED:
        source, decision, rationale = APPROVED[cid]
        status, blocker = "approved", ""
    elif cid in CONTRADICTORY:
        decision, blocker = "hold_contradictory_mapping_removed", "contradictory_mapping_removed"
        rationale = "Prior assertion-level review removed Feedipedia target because page identifies different taxon or material."
    elif cid in SPELLING:
        decision, blocker = "hold_material_scope_after_label_correction", "material_scope_unresolved"
        rationale = "Scientific-name spelling can be corrected, but table describes narrower plant component or processing state."
    elif cid in {"AOM_000615", "AOM_006160"}:
        decision, blocker = "hold_broad_category_or_duplicate", "category_or_duplicate_review"
        rationale = "Broad by-product label may overlap existing governed category or retained material; replacement decision needs occurrence evidence."
    rows.append({
        "concept_id": cid, "preferred_label": item["preferred_label"],
        "feedipedia_url": feed[cid]["feedipedia_url"], "page_heading": feed[cid]["page_heading"],
        "decision": decision, "status": status, "governed_source_identity": source,
        "blocker_code": blocker, "reviewer": "Pete Steward", "review_date": "2026-08-06",
        "evidence": feed[cid]["feedipedia_url"], "rationale": rationale,
    })
write(OUT, rows)
print(f"Reviewed {len(rows)} identity/alias concepts: {sum(r['status']=='approved' for r in rows)} approved")
