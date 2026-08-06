#!/usr/bin/env python3
"""Build reviewed definitions from approved concept and facet governance."""
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
OUT = DATA / "approved_definition_enrichments.csv"


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


existing = {
    row["concept_id"] for row in read("definitions.csv")
    if row["source_column"] != "approved_definition_enrichment"
}
concepts = {row["concept_id"]: row for row in read("concepts.csv")}
new_concepts = read("approved_new_concepts.csv")
inventory = {row["concept_id"]: row for row in csv.DictReader(
    (ROOT / "review/livestock-v5/ingredient_harmonization_inventory.csv").open(encoding="utf-8", newline="")
)}
material_facets = read("approved_feed_material_facets.csv") + read("approved_generated_feed_material_facets.csv")

rows = []
for row in new_concepts:
    if row["concept_id"] in existing:
        continue
    rows.append({
        "concept_id": row["concept_id"], "language": "en",
        "definition": row["scope_note"], "definition_method": "promoted_reviewed_scope_note",
        "status": "approved", "reviewer": "Pete Steward", "review_date": "2026-08-06",
        "evidence": row["evidence"],
        "rationale": "Reviewed concept scope text is definition-grade and promoted without semantic expansion.",
    })

by_material = defaultdict(list)
for row in material_facets:
    by_material[row["feed_material_id"]].append(row)
property_label = {
    "aom:ingredientPart": "ingredient part",
    "aom:processingMethod": "processing method",
    "aom:physicalForm": "physical form",
    "aom:productRole": "product role",
    "aom:feedProductType": "feed product type",
    "aom:materialIntegrity": "material integrity",
    "aom:materialComponent": "material component",
    "aom:compositionState": "composition state",
}
for concept_id, facets in sorted(by_material.items()):
    if concept_id in existing or concepts[concept_id]["status"] == "deprecated":
        continue
    source = inventory[concept_id]["source_identity_candidate"].strip()
    if not source:
        raise ValueError(f"Approved facet material lacks governed source identity: {concept_id}")
    grouped = defaultdict(list)
    for facet in facets:
        grouped[facet["target_property"]].append(facet["target_label"])
    characteristics = []
    for prop in sorted(grouped):
        values = ", ".join(sorted(set(grouped[prop])))
        characteristics.append(f"{property_label[prop]} — {values}")
    rows.append({
        "concept_id": concept_id, "language": "en",
        "definition": f"A feed material with governed source identity “{source}” and characteristics: " + "; ".join(characteristics) + ".",
        "definition_method": "composed_from_approved_semantic_facets",
        "status": "approved", "reviewer": "Pete Steward", "review_date": "2026-08-06",
        "evidence": "data/livestock-staging/approved_feed_material_facets.csv;data/livestock-staging/approved_generated_feed_material_facets.csv",
        "rationale": "Definition states only governed source identity and approved semantic assertions; no biological or nutritional claim is inferred.",
    })

rows.sort(key=lambda row: row["concept_id"])
fields = ["concept_id", "language", "definition", "definition_method", "status", "reviewer", "review_date", "evidence", "rationale"]
with OUT.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
print(f"Approved {len(rows)} definition enrichments")
