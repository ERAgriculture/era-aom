#!/usr/bin/env python3
"""Resolve evidence-supported cases from frozen final definition hard tail."""
import argparse
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "review/livestock-v8/definition_gap_queue.csv"
REVIEW = ROOT / "review/livestock-v14"
COHORT = REVIEW / "definition_hard_tail_cohort.csv"
OUT = REVIEW / "definition_hard_tail_review.csv"
FACETS = ROOT / "data/livestock-staging/approved_hard_tail_feed_material_facets.csv"
FEEDIPEDIA = ROOT / "review/livestock-v11/feedipedia_source_scope_review.csv"
PUBLIC = ROOT / "review/livestock-v12/public_authority_source_scope_review.csv"
PUBLIC_COHORT = ROOT / "review/livestock-v12/public_authority_cohort.csv"
WORKBOOK = ROOT / "review/livestock-v13/workbook_source_scope_review.csv"

CORE = {"AOM_000106", "AOM_000846"}
FEEDIPEDIA_CATEGORY = {"AOM_000628", "AOM_000644", "AOM_000683", "AOM_000701", "AOM_000735"}
FEEDIPEDIA_ALIAS = {
    "AOM_000605", "AOM_001192", "AOM_001303", "AOM_002101",
}
WORKBOOK_STRUCTURED = {"AOM_001930", "AOM_006200"}

# Longest suffix first. Each match strips descriptor from governed source and
# emits existing approved facet value; no new semantic class is invented here.
DESCRIPTORS = [
    ("processing waste", "aom:productRole", "AOM_101058", "Processing-waste role"),
    ("market waste", "aom:productRole", "AOM_101056", "Market-waste role"),
    ("milling waste", "aom:productRole", "AOM_101061", "Waste role"),
    ("by product", "aom:productRole", "AOM_101062", "By-product role"),
    ("byproduct", "aom:productRole", "AOM_101062", "By-product role"),
    ("hydrolysate", "aom:processingMethod", "AOM_101083", "Hydrolysis"),
    ("discards", "aom:productRole", "AOM_101055", "Discard role"),
    ("residues", "aom:productRole", "AOM_101059", "Residue role"),
    ("residue", "aom:productRole", "AOM_101059", "Residue role"),
    ("leftover", "aom:productRole", "AOM_101061", "Waste role"),
    ("shorts", "aom:productRole", "AOM_101060", "Milling-shorts role"),
    ("offal", "aom:productRole", "AOM_101057", "Offal role"),
    ("waste", "aom:productRole", "AOM_101061", "Waste role"),
    ("peels", "aom:ingredientPart", "AOM_101034", "Peel"),
    ("peel", "aom:ingredientPart", "AOM_101034", "Peel"),
    ("fruits", "aom:ingredientPart", "AOM_101028", "Fruit"),
    ("fruit", "aom:ingredientPart", "AOM_101028", "Fruit"),
    ("cladode", "aom:ingredientPart", "AOM_101025", "Cladode"),
    ("bulb", "aom:ingredientPart", "AOM_101024", "Bulb"),
    ("hulls", "aom:ingredientPart", "AOM_101030", "Hull"),
    ("hull", "aom:ingredientPart", "AOM_101030", "Hull"),
    ("tops", "aom:ingredientPart", "AOM_101048", "Plant top"),
    ("nut", "aom:ingredientPart", "AOM_101038", "Seed"),
    ("starch", "aom:ingredientConstituent", "AOM_101065", "Starch constituent"),
    ("oil", "aom:ingredientConstituent", "AOM_101081", "Oil constituent"),
    ("cake", "aom:physicalForm", "AOM_101052", "Cake form"),
    ("binder", "aom:productRole", "AOM_101079", "Binder role"),
    ("cull", "aom:productRole", "AOM_101055", "Discard role"),
]


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def decompose(label):
    source = label.strip()
    found = []
    changed = True
    while changed:
        changed = False
        folded = re.sub(r"\s+", " ", source.casefold()).strip()
        for term, prop, target, target_label in DESCRIPTORS:
            if folded.endswith(" " + term):
                source = source[:-(len(term))].strip(" -")
                found.append((prop, target, target_label, term)); changed = True; break
    return source, list(reversed(found))


parser = argparse.ArgumentParser()
parser.add_argument("--snapshot", action="store_true")
args = parser.parse_args()
if args.snapshot:
    rows = [{k: row[k] for k in ["concept_id", "preferred_label", "hierarchy_path", "domain", "recommended_route"]}
            for row in read(QUEUE) if row["status"] != "approved"]
    write(COHORT, rows)
    print(f"Snapshotted {len(rows)} hard-tail concepts")
    raise SystemExit

feed = {row["concept_id"]: row for row in read(FEEDIPEDIA)}
public = {row["concept_id"]: row for row in read(PUBLIC)}
public_cohort = {row["concept_id"]: row for row in read(PUBLIC_COHORT)}
workbook = {row["concept_id"]: row for row in read(WORKBOOK)}
review_rows, facet_rows = [], []
for item in read(COHORT):
    cid, label, route = item["concept_id"], item["preferred_label"], item["recommended_route"]
    source, facets = decompose(label)
    # These compound sources retain an uncovered component after generic suffix
    # stripping; partial decomposition would misstate governed identity.
    if cid in {"AOM_003930", "AOM_006323"}:
        facets = []
    decision, status, evidence = "hold_expert_evidence_required", "held", ""
    rationale = "Available mapping or workbook evidence does not establish complete material identity and structured scope."
    blocker, next_action = "", ""
    if cid in CORE:
        decision, status, source = "approve_core_hierarchy_scope", "approved", label
        evidence = "data/livestock-staging/concepts.csv"
        rationale = "Governed top-level hierarchy establishes core classification role."
        facets = []
    elif cid in FEEDIPEDIA_CATEGORY:
        decision, status, source = "approve_feedipedia_category_scope", "approved", label
        evidence = feed[cid]["feedipedia_url"]
        rationale = "Canonical hierarchy and current Feedipedia category page establish controlled feed category, not one material identity."
        facets = []
    elif cid in FEEDIPEDIA_ALIAS:
        decision, status, source = "approve_feedipedia_alias_scope", "approved", source
        evidence = feed[cid]["feedipedia_url"]
        rationale = "Current Feedipedia heading establishes direct common-name, spelling, or word-order equivalence at same material scope."
    elif route == "research_taxon_insufficient_for_material" and facets and source:
        decision, status = "approve_taxon_source_with_explicit_facets", "approved"
        evidence = public_cohort[cid]["public_mapping_targets"]
        rationale = "Existing public taxon mapping establishes biological source; explicit label descriptors map only to pre-approved structured facet values."
    elif cid in WORKBOOK_STRUCTURED and facets and source:
        decision, status = "approve_workbook_source_with_explicit_facets", "approved"
        evidence = "review/livestock-v13/workbook_source_cohort.csv"
        rationale = "Canonical workbook path establishes source; explicit oil descriptor maps to approved constituent facet, not physical form."
    if status == "held":
        if route == "research_feedipedia":
            prior = feed[cid]["decision"]
            blocker = prior.removeprefix("hold_")
            next_action = {
                "hold_shared_page": "Review every co-referenced AOM concept; retain distinct scopes or approve synonym/replacement with occurrence evidence.",
                "hold_identity_or_alias_review": "Verify scientific/common-name equivalence and material part against taxonomic or feed authority.",
                "hold_source_warning": "Find independent citable feed or taxonomic authority; warned page cannot support approval.",
                "hold_retrieval_failure": "Recover archived page or replace mapping with reachable authoritative evidence.",
            }.get(prior, "Review mapping granularity and replace discovery-only evidence.")
        elif route == "research_public_ontology":
            blocker = public[cid]["decision"].removeprefix("hold_")
            next_action = "Correct or narrow public mapping, then establish material component/product scope with direct authority evidence."
        elif route == "research_source_workbook":
            blocker = "workbook_identity_or_model_gap"
            next_action = "Obtain product/domain evidence or add reviewed component/process facet before definition approval."
        elif route == "research_taxon_insufficient_for_material":
            blocker = "unmodelled_derived_material_descriptor"
            next_action = "Review descriptor meaning; map to existing facet or approve new facet concept before composing definition."
    if status == "approved":
        for order, (prop, target, target_label, term) in enumerate(facets, 1):
            facet_rows.append({
                "feed_material_id": cid, "target_property": prop, "target_concept_id": target,
                "target_label": target_label, "status": "approved", "reviewer": "Pete Steward",
                "review_date": "2026-08-06", "evidence": evidence,
                "rationale": f"Explicit descriptor “{term}” mapped through hard-tail decision {cid}; assertion {order}.",
            })
    review_rows.append({
        "concept_id": cid, "preferred_label": label, "recommended_route": route,
        "governed_source_identity": source if status == "approved" else "",
        "structured_facet_count": len(facets) if status == "approved" else 0,
        "decision": decision, "status": status, "reviewer": "Pete Steward", "review_date": "2026-08-06",
        "evidence": evidence, "blocker_code": blocker, "next_action": next_action, "rationale": rationale,
    })

write(OUT, review_rows)
facet_fields = ["feed_material_id", "target_property", "target_concept_id", "target_label", "status", "reviewer", "review_date", "evidence", "rationale"]
write(FACETS, facet_rows, facet_fields)
print(f"Reviewed {len(review_rows)} hard-tail concepts: {sum(r['status']=='approved' for r in review_rows)} approved; {len(facet_rows)} facets")
