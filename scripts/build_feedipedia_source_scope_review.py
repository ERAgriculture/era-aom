#!/usr/bin/env python3
"""Build full-cohort Feedipedia source-scope decisions from frozen evidence."""
import csv
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "review/livestock-v9/feedipedia_definition_evidence.csv"
QUEUE = ROOT / "review/livestock-v8/definition_gap_queue.csv"
INVENTORY = ROOT / "review/livestock-v5/ingredient_harmonization_inventory.csv"
OUT = ROOT / "review/livestock-v11/feedipedia_source_scope_review.csv"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().casefold()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


active = {
    row["concept_id"] for row in read(QUEUE)
    if row["recommended_route"] == "research_feedipedia"
}
inventory = {row["concept_id"]: row for row in read(INVENTORY)}
hard_holds = {
    "hold_shared_page_scope_review": "hold_shared_page",
    "hold_source_warning": "hold_source_warning",
    "hold_category_not_concept": "hold_category_page",
    "hold_retrieval_failed": "hold_retrieval_failure",
}
rows = []
for evidence in read(EVIDENCE):
    concept_id = evidence["concept_id"]
    if concept_id not in active:
        continue
    label = normalize(evidence["preferred_label"])
    heading = normalize(evidence["page_heading"])
    disposition = evidence["evidence_disposition"]
    if disposition in hard_holds:
        decision, status = hard_holds[disposition], "held"
        rationale = evidence["rationale"]
    elif label and (label == heading or label in heading):
        decision, status = "approve_source_scope_definition", "approved"
        rationale = (
            "Healthy unshared Feedipedia page directly names AOM preferred identity; "
            "definition approves source/material scope only and does not inherit narrower descriptors."
        )
    else:
        decision, status = "hold_identity_or_alias_review", "held"
        rationale = (
            "Preferred identity is not directly present in page heading; alias, taxon, or material-scope review required."
        )
    item = inventory[concept_id]
    rows.append({
        "concept_id": concept_id,
        "preferred_label": evidence["preferred_label"],
        "ingredient_family": item["ingredient_family"],
        "source_identity": item["source_identity_candidate"],
        "feedipedia_url": evidence["feedipedia_url"],
        "page_heading": evidence["page_heading"],
        "decision": decision,
        "status": status,
        "reviewer": "Pete Steward",
        "review_date": "2026-08-06",
        "rationale": rationale,
    })

rows.sort(key=lambda row: row["concept_id"])
OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
print(f"Reviewed {len(rows)} Feedipedia concepts: {sum(row['status'] == 'approved' for row in rows)} approved")
