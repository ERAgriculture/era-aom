#!/usr/bin/env python3
"""Build canonical-workbook source-scope decisions from a frozen cohort."""
import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "review/livestock-v8/definition_gap_queue.csv"
INVENTORY = ROOT / "review/livestock-v5/ingredient_harmonization_inventory.csv"
REVIEW = ROOT / "review/livestock-v13"
COHORT = REVIEW / "workbook_source_cohort.csv"
OUT = REVIEW / "workbook_source_scope_review.csv"
WORKBOOK_SHA256 = "f834c4f7837927774499eff4340c912784a3db10c2e19bd5d75a7f753df41438"

# Commercial names and locally ambiguous labels need product documentation or
# domain review. Workbook hierarchy alone cannot establish their material scope.
HOLDS = {
    "AOM_000693", "AOM_000695", "AOM_000748", "AOM_000749", "AOM_000765",
    "AOM_001105", "AOM_001486", "AOM_001497", "AOM_001500", "AOM_001501", "AOM_001508",
    "AOM_001579", "AOM_001826", "AOM_001831", "AOM_001868", "AOM_001870",
    "AOM_001880", "AOM_001921", "AOM_001930", "AOM_002081", "AOM_002120",
    "AOM_003567", "AOM_003747", "AOM_003749", "AOM_006006", "AOM_006200", "AOM_006331",
}

CATEGORY_LABELS = {
    "Ingredient source", "Animal", "Animal Manures", "Cereal ByProducts",
    "Cereal Products", "Fruit Product", "Legume Products", "Oil Plant Products",
    "Forage Trees", "Other Forage Plants", "Supplement", "Amino Acid", "Binder",
    "Digestibility Marker", "Mineral", "Vitamin Mix", "Vitamin",
    "Minerals and Vitamins Mix", "Mixture", "Other Ingredients", "Antitoxins",
    "Unspecified", "Unspecified Filler", "Unspecified Yeast", "Commercial Feed",
    "Concentrate", "Preformulated Feed", "Prebiotic", "Probiotic",
    "Essential Fatty Acid", "Herb or Extract", "Organic Acid", "Grazing",
    "Pasture", "Forb", "Unspecified Grass", "Unspecified Forage",
    "Unspecified Crop Residue", "Crop Byproduct",
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


parser = argparse.ArgumentParser()
parser.add_argument("--snapshot", metavar="AOM_CSV", help="Freeze cohort from canonical workbook AOM-sheet CSV")
args = parser.parse_args()

if args.snapshot:
    source = Path(args.snapshot)
    workbook = {row["AOM"]: row for row in read(source) if row.get("AOM")}
    queue = [row for row in read(QUEUE) if row["recommended_route"] == "research_source_workbook"]
    rows = []
    for item in queue:
        source_row = workbook[item["concept_id"]]
        current_path = source_row["Path"].strip()
        rows.append({
            "concept_id": item["concept_id"], "preferred_label": item["preferred_label"],
            "canonical_path": current_path, "queue_path": item["hierarchy_path"],
            "path_alignment": "aligned" if current_path == item["hierarchy_path"] else "workbook_path_differs",
            "workbook_description": source_row.get("Description", "").strip(),
            "workbook_sha256": WORKBOOK_SHA256,
        })
    write(COHORT, rows)
    print(f"Snapshotted {len(rows)} canonical-workbook concepts")
    raise SystemExit

inventory = {row["concept_id"]: row for row in read(INVENTORY)}
rows = []
for item in read(COHORT):
    concept_id = item["concept_id"]
    material = inventory[concept_id]
    label = item["preferred_label"]
    parent = item["canonical_path"].split("/")[-2] if "/" in item["canonical_path"] else "AOM"
    if concept_id in HOLDS:
        decision, status, scope = "hold_ambiguous_workbook_identity", "held", ""
        rationale = (
            "Workbook supplies label and hierarchy only; commercial/local identity, category conflict, or compound "
            "component/process semantics require citable evidence and structured review."
        )
    elif label in CATEGORY_LABELS:
        decision, status, scope = "approve_hierarchy_category_scope", "approved", "category"
        rationale = "Canonical workbook path establishes controlled classification role; definition adds no biological, chemical, or nutritional claim."
    else:
        decision, status, scope = "approve_workbook_identity_scope", "approved", "identity"
        rationale = "Canonical workbook establishes governed ingredient identity and hierarchy; all unasserted material facets remain unspecified."
    rows.append({
        "concept_id": concept_id, "preferred_label": label,
        "ingredient_family": material["ingredient_family"], "canonical_path": item["canonical_path"],
        "parent_label": parent, "definition_scope": scope, "decision": decision,
        "status": status, "reviewer": "Pete Steward", "review_date": "2026-08-06",
        "evidence": f"era_master_sheet.xlsx#AOM;sha256:{WORKBOOK_SHA256}", "rationale": rationale,
    })

rows.sort(key=lambda row: row["concept_id"])
write(OUT, rows)
print(f"Reviewed {len(rows)} workbook concepts: {sum(row['status'] == 'approved' for row in rows)} approved; {sum(row['status'] == 'held' for row in rows)} held")
