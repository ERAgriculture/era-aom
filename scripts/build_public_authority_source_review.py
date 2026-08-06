#!/usr/bin/env python3
"""Build public-authority source-scope decisions from a frozen cohort."""
import argparse
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "review/livestock-v8/definition_gap_queue.csv"
INVENTORY = ROOT / "review/livestock-v5/ingredient_harmonization_inventory.csv"
REVIEW = ROOT / "review/livestock-v12"
COHORT = REVIEW / "public_authority_cohort.csv"
AGROVOC = REVIEW / "agrovoc_label_evidence.csv"
OUT = REVIEW / "public_authority_source_scope_review.csv"
ROUTES = {"research_taxon_insufficient_for_material", "research_public_ontology"}
DESCRIPTORS = set("""
oil juice slurry leaf leaves seed seeds flower flowers top tops haulm haulms
waste residue residues shaft peel peels shorts bulb cake discards stalk sheath
fruit fruits full fat processing manure ash meal hull husk pulp bran fodder
straw sprout sprouts root roots tuber tubers offal contents head heads cladode
cladodes starch larvae protein isolate rhizome rhizomes nut nuts mixture mixtures
weeds veins
""".split())
PLANT_FAMILIES = {"Forage Plants", "Crop Product"}
ANIMAL_FAMILIES = {"Animal", "Probiotic"}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalized(value):
    value = " ".join(re.sub(r"[^a-z0-9]+", " ", value.casefold()).split())
    return {"pigeon peas": "pigeon pea"}.get(value, value)


parser = argparse.ArgumentParser()
parser.add_argument("--snapshot", action="store_true", help="Freeze current routed cohort before approvals")
args = parser.parse_args()
if args.snapshot:
    rows = [
        {
            "concept_id": row["concept_id"], "preferred_label": row["preferred_label"],
            "recommended_route": row["recommended_route"],
            "public_mapping_schemes": row["public_mapping_schemes"],
            "public_mapping_targets": row["public_mapping_targets"],
        }
        for row in read(QUEUE) if row["recommended_route"] in ROUTES
    ]
    write(COHORT, rows)
    print(f"Snapshotted {len(rows)} public-authority concepts")
    raise SystemExit

cohort = read(COHORT)
inventory = {row["concept_id"]: row for row in read(INVENTORY)}
agrovoc = {row["uri"]: row for row in read(AGROVOC)}
rows = []
for item in cohort:
    concept_id = item["concept_id"]
    material = inventory[concept_id]
    family = material["ingredient_family"]
    schemes = set(item["public_mapping_schemes"].split(";"))
    targets = item["public_mapping_targets"].split(";")
    words = set(re.findall(r"[a-z]+", item["preferred_label"].casefold()))
    authority_uri = ""
    decision, status = "hold_derived_material_scope", "held"
    rationale = "Taxon or broad ontology mapping identifies source but does not establish derived material scope."

    if item["recommended_route"] == "research_taxon_insufficient_for_material" and not words & DESCRIPTORS:
        if family in PLANT_FAMILIES and "world-flora-online" in schemes:
            authority_uri = next(value for value in targets if value.startswith("wfo-"))
            decision, status = "approve_direct_source_scope", "approved"
        elif family in ANIMAL_FAMILIES and "ncbi-taxonomy" in schemes:
            authority_uri = next(value for value in targets if "NCBITaxon_" in value)
            decision, status = "approve_direct_source_scope", "approved"
        if status == "approved":
            rationale = "Canonical feed-material hierarchy plus taxonomic authority support direct source identity; derived facets remain unspecified."

    if item["recommended_route"] == "research_public_ontology":
        matched = []
        for target in targets:
            if target in agrovoc and normalized(agrovoc[target]["preferred_label"]) == normalized(item["preferred_label"]):
                matched.append(target)
        if matched and concept_id in {"AOM_000651", "AOM_000674", "AOM_001586"}:
            authority_uri = matched[0]
            decision, status = "approve_structured_oil_material", "approved"
            rationale = "Exact AGROVOC material identity supports source plus oil-constituent decomposition; oil is not physical form."
        elif matched and concept_id == "AOM_001314":
            authority_uri = matched[0]
            decision, status = "approve_direct_source_scope", "approved"
            rationale = "Exact AGROVOC preferred label supports direct source identity; derived facets remain unspecified."
        elif any(target in agrovoc for target in targets):
            decision = "hold_public_authority_mismatch"
            rationale = "AGROVOC preferred label is broader, narrower, or conflicts with AOM identity; no automatic definition approved."

    rows.append({
        "concept_id": concept_id, "preferred_label": item["preferred_label"],
        "ingredient_family": family,
        "governed_identity": item["preferred_label"] if decision == "approve_structured_oil_material" else material["source_identity_candidate"],
        "authority_uri": authority_uri, "decision": decision, "status": status,
        "reviewer": "Pete Steward", "review_date": "2026-08-06", "rationale": rationale,
    })

rows.sort(key=lambda row: row["concept_id"])
write(OUT, rows)
print(f"Reviewed {len(rows)} public-authority concepts: {sum(row['status'] == 'approved' for row in rows)} approved")
