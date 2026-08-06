#!/usr/bin/env python3
"""Build frozen pair-level decisions for shared Feedipedia pages."""
import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARD = ROOT / "review/livestock-v14/definition_hard_tail_review.csv"
FEED = ROOT / "review/livestock-v11/feedipedia_source_scope_review.csv"
REVIEW = ROOT / "review/livestock-v17"
COHORT = REVIEW / "shared_page_cohort.csv"
OUT = REVIEW / "shared_page_review.csv"

APPROVED = {
    "AOM_001334": ("pearl millet", "approve_explicit_grain_material", "Heading identifies pearl-millet grain; retained material records source plus seed component."),
    "AOM_001818": ("Ensete ventricosum", "approve_explicit_corm_material", "Heading directly identifies fresh Ensete ventricosum corms; processing state is not asserted."),
    "AOM_001837": ("oil palm processing", "approve_explicit_residue_material", "Heading identifies decanted palm-oil mill effluent; retained material records processing-residue role."),
    "AOM_001914": ("Opuntia ficus-indica", "approve_explicit_cladode_material", "Heading directly identifies fresh prickly-pear cladodes; processing state is not asserted."),
    "AOM_002106": ("cocoa bean", "approve_industry_cake_meal_alias", "Cocoa oil meal establishes pressed cocoa-bean cake material, distinct from unprocessed bean."),
    "AOM_002136": ("linseed", "approve_industry_cake_meal_alias", "Cold-pressed linseed meal establishes linseed cake material, distinct from flaxseed."),
}
SYNONYM_REVIEW = {
    "AOM_001145", "AOM_002206",  # Faidherbia albida / Acacia albida
    "AOM_001149", "AOM_001797",  # Gliricidia spelling duplicate
    "AOM_001208", "AOM_001527",  # Centrosema pubescens / C. molle
}
WRONG_SPECIES = {"AOM_001383", "AOM_001389", "AOM_006350"}
SOURCE_PART = {"AOM_000654", "AOM_000671", "AOM_001166", "AOM_001282", "AOM_002107", "AOM_004255"}


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
        for row in read(HARD) if row["status"] == "held" and row["blocker_code"] == "shared_page"
    ]
    write(COHORT, rows)
    print(f"Snapshotted {len(rows)} shared-page concepts")
    raise SystemExit

feed = {row["concept_id"]: row for row in read(FEED)}
rows = []
for item in read(COHORT):
    cid = item["concept_id"]
    source, decision, status, blocker = "", "hold_narrower_table_scope", "held", "narrower_table_scope"
    rationale = "Shared table describes narrower component or processing state; page co-reference does not define this concept."
    if cid in APPROVED:
        source, decision, rationale = APPROVED[cid]
        status, blocker = "approved", ""
    elif cid in SYNONYM_REVIEW:
        decision, blocker = "hold_synonym_replacement_review", "synonym_replacement_review"
        rationale = "Names may be taxonomic or spelling synonyms; retain both IDs until occurrence evidence selects replacement direction."
    elif cid in WRONG_SPECIES:
        decision, blocker = "hold_contradictory_species_mapping", "contradictory_species_mapping"
        rationale = "Shared page identifies different species; prior assertion-level review excludes contradictory Feedipedia mapping."
    elif cid in SOURCE_PART:
        decision, blocker = "hold_source_material_distinction", "source_material_distinction"
        rationale = "Broader source concept remains distinct from explicit grain, cladode, corm, residue, bean-cake, or seed material partner."
    elif cid in {"AOM_001317", "AOM_001582"}:
        decision, blocker = "hold_composition_state_distinction", "composition_state_distinction"
        rationale = "Generic soybean page cannot establish equivalence between soybean and full-fat soybean material."
    rows.append({
        "concept_id": cid, "preferred_label": item["preferred_label"],
        "feedipedia_url": feed[cid]["feedipedia_url"], "page_heading": feed[cid]["page_heading"],
        "decision": decision, "status": status, "governed_source_identity": source,
        "blocker_code": blocker, "reviewer": "Pete Steward", "review_date": "2026-08-06",
        "evidence": feed[cid]["feedipedia_url"], "rationale": rationale,
    })
write(OUT, rows)
print(f"Reviewed {len(rows)} shared-page concepts: {sum(r['status']=='approved' for r in rows)} approved")
