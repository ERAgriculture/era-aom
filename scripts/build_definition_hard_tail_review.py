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
IDENTITY = ROOT / "review/livestock-v16/identity_alias_review.csv"
SHARED = ROOT / "review/livestock-v17/shared_page_review.csv"
WORKBOOK_GAPS = ROOT / "review/livestock-v18/workbook_model_gap_review.csv"
CONSOLIDATED = ROOT / "review/livestock-v19/authority_model_review.csv"
MATERIAL_SCOPE = ROOT / "review/livestock-v21/material_scope_review.csv"
ONTOLOGY_INTEGRITY = ROOT / "review/livestock-v22/ontology_integrity_review.csv"
FINAL_TAIL = ROOT / "review/livestock-v23/final_tail_review.csv"

CORE = {"AOM_000106", "AOM_000846"}
FEEDIPEDIA_CATEGORY = {"AOM_000628", "AOM_000644", "AOM_000683", "AOM_000701", "AOM_000735"}
FEEDIPEDIA_ALIAS = {
    "AOM_000605", "AOM_001192", "AOM_001303", "AOM_002101",
}
WORKBOOK_STRUCTURED = {"AOM_001880", "AOM_001930", "AOM_002120", "AOM_006200"}

COMPOUND_DESCRIPTORS = {
    "deep stacked": [("aom:processingMethod", "AOM_101123", "Stacking", "deep stacked")],
    "protein isolate": [
        ("aom:ingredientConstituent", "AOM_101120", "Protein constituent", "protein"),
        ("aom:processingMethod", "AOM_101072", "Extraction", "isolate"),
    ],
    "steep liquor": [
        ("aom:physicalForm", "AOM_101077", "Liquid form", "liquor"),
        ("aom:processingMethod", "AOM_101119", "Steeping", "steep"),
    ],
    "flower by product": [
        ("aom:ingredientPart", "AOM_101117", "Flower", "flower"),
        ("aom:productRole", "AOM_101062", "By-product role", "by product"),
    ],
    "haulm": [
        ("aom:ingredientPart", "AOM_101047", "Stem", "haulm"),
        ("aom:ingredientPart", "AOM_101033", "Leaf", "haulm"),
        ("aom:productRole", "AOM_101063", "Crop-residue role", "haulm"),
    ],
    "juice": [
        ("aom:physicalForm", "AOM_101077", "Liquid form", "juice"),
        ("aom:processingMethod", "AOM_101072", "Extraction", "juice"),
    ],
    "pollard": [
        ("aom:processingMethod", "AOM_101082", "Milling", "pollard"),
        ("aom:productRole", "AOM_101062", "By-product role", "pollard"),
    ],
    "vinasse": [
        ("aom:physicalForm", "AOM_101077", "Liquid form", "vinasse"),
        ("aom:processingMethod", "AOM_101124", "Distillation", "vinasse"),
        ("aom:productRole", "AOM_101059", "Residue role", "vinasse"),
    ],
    "liver oil": [
        ("aom:ingredientPart", "AOM_101122", "Liver", "liver"),
        ("aom:ingredientConstituent", "AOM_101081", "Oil constituent", "oil"),
    ],
    "hash": [
        ("aom:physicalForm", "AOM_101075", "Mixture form", "hash"),
        ("aom:productRole", "AOM_101062", "By-product role", "hash"),
    ],
    "molasses": [
        ("aom:physicalForm", "AOM_101077", "Liquid form", "molasses"),
        ("aom:processingMethod", "AOM_101084", "Sugar processing", "molasses"),
        ("aom:productRole", "AOM_101062", "By-product role", "molasses"),
    ],
}

IDENTITY_FACETS = {
    "AOM_001811": [("aom:physicalForm", "AOM_101075", "Mixture form", "rumen contents"),
                    ("aom:productRole", "AOM_101062", "By-product role", "rumen contents")],
    "AOM_001845": [("aom:ingredientPart", "AOM_101041", "Sprout", "malt sprout"),
                    ("aom:productRole", "AOM_101062", "By-product role", "malt sprout")],
    "AOM_002166": [("aom:productRole", "AOM_101059", "Residue role", "bagasse")],
    "AOM_003072": [("aom:ingredientPart", "AOM_101038", "Seed", "groundnut")],
    "AOM_003482": [("aom:ingredientPart", "AOM_101037", "Root", "sugar beet")],
    "AOM_003911": [("aom:productRole", "AOM_101059", "Residue role", "sievate")],
    "AOM_006008": [("aom:productRole", "AOM_101062", "By-product role", "manure")],
}

SHARED_PAGE_FACETS = {
    "AOM_001334": [("aom:ingredientPart", "AOM_101038", "Seed", "grain")],
    "AOM_001818": [("aom:ingredientPart", "AOM_101027", "Corm", "corm")],
    "AOM_001837": [("aom:productRole", "AOM_101059", "Residue role", "mill effluent")],
    "AOM_001914": [("aom:ingredientPart", "AOM_101025", "Cladode", "cladode")],
    "AOM_002106": [("aom:physicalForm", "AOM_101052", "Cake form", "oil meal"),
                    ("aom:productRole", "AOM_101062", "By-product role", "oil meal")],
    "AOM_002136": [("aom:physicalForm", "AOM_101052", "Cake form", "cold-pressed meal"),
                    ("aom:processingMethod", "AOM_101070", "Pressing", "cold-pressed"),
                    ("aom:productRole", "AOM_101062", "By-product role", "meal")],
}

WORKBOOK_GAP_FACETS = {
    "AOM_001486": [("aom:productRole", "AOM_101079", "Binder role", "binder")],
    "AOM_001826": [("aom:productRole", "AOM_101079", "Binder role", "binder")],
    "AOM_002081": [("aom:physicalForm", "AOM_101075", "Mixture form", "mixed"),
                    ("aom:processingMethod", "AOM_101083", "Hydrolysis", "hydrolysate"),
                    ("aom:productRole", "AOM_101062", "By-product role", "animal by-product")],
    "AOM_003567": [("aom:productRole", "AOM_101059", "Residue role", "residue")],
}

CONSOLIDATED_FACETS = {
    "AOM_000611": [("aom:ingredientConstituent", "AOM_101066", "Fat constituent", "full fat"),
                    ("aom:physicalForm", "AOM_101052", "Cake form", "cake"),
                    ("aom:processingMethod", "AOM_101070", "Pressing", "cake")],
    "AOM_001675": [("aom:ingredientPart", "AOM_101047", "Stem", "stalk")],
    "AOM_001846": [("aom:processingMethod", "AOM_101082", "Milling", "pollard"),
                    ("aom:productRole", "AOM_101062", "By-product role", "pollard")],
    "AOM_006003": [("aom:physicalForm", "AOM_101077", "Liquid form", "molasses"),
                    ("aom:processingMethod", "AOM_101084", "Sugar processing", "molasses"),
                    ("aom:productRole", "AOM_101062", "By-product role", "molasses")],
}

MATERIAL_SCOPE_FACETS = {
    "AOM_000538": [("aom:ingredientConstituent", "AOM_101080", "Ash constituent", "ash")],
    "AOM_000571": [("aom:productRole", "AOM_101057", "Offal role", "offal")],
    "AOM_000577": [("aom:productRole", "AOM_101057", "Offal role", "offal")],
    "AOM_000578": [("aom:processingMethod", "AOM_101082", "Milling", "polish"),
                    ("aom:productRole", "AOM_101062", "By-product role", "polish")],
    "AOM_000589": [("aom:productRole", "AOM_101057", "Offal role", "offal")],
    "AOM_000603": COMPOUND_DESCRIPTORS["haulm"],
    "AOM_000671": [("aom:ingredientConstituent", "AOM_101081", "Oil constituent", "oil")],
    "AOM_001317": [("aom:ingredientConstituent", "AOM_101066", "Fat constituent", "full fat")],
    "AOM_001373": [("aom:productRole", "AOM_101079", "Binder role", "binder hierarchy")],
    "AOM_002107": [("aom:ingredientPart", "AOM_101038", "Seed", "bean")],
    "AOM_002218": COMPOUND_DESCRIPTORS["haulm"],
    "AOM_003206": [("aom:productRole", "AOM_101062", "By-product role", "byproduct")],
    "AOM_004255": [("aom:ingredientPart", "AOM_101038", "Seed", "seed")],
}

ONTOLOGY_INTEGRITY_FACETS = {
    "AOM_001892": [("aom:processingMethod", "AOM_101073", "Threshing", "threshed"),
                    ("aom:ingredientPart", "AOM_101048", "Plant top", "top")],
}

FINAL_TAIL_FACETS = {
    "AOM_000664": [("aom:ingredientPart", "AOM_101028", "Fruit", "avocado")],
    "AOM_000672": [("aom:ingredientConstituent", "AOM_101081", "Oil constituent", "oil")],
    "AOM_000676": [("aom:ingredientConstituent", "AOM_101081", "Oil constituent", "oil")],
    "AOM_003172": [("aom:productRole", "AOM_101061", "Waste role", "waste")],
}

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
    ("shells", "aom:ingredientPart", "AOM_101040", "Shell"),
    ("shell", "aom:ingredientPart", "AOM_101040", "Shell"),
    ("sheath", "aom:ingredientPart", "AOM_101039", "Sheath"),
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
    ("flower", "aom:ingredientPart", "AOM_101117", "Flower"),
    ("slurry", "aom:physicalForm", "AOM_101118", "Slurry form"),
    ("rhizomes", "aom:ingredientPart", "AOM_101121", "Rhizome"),
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
        for term, assertions in COMPOUND_DESCRIPTORS.items():
            if folded.endswith(" " + term):
                source = source[:-(len(term))].strip(" -")
                found.extend(assertions); changed = True; break
        if changed:
            continue
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
identity = {row["concept_id"]: row for row in read(IDENTITY)}
shared = {row["concept_id"]: row for row in read(SHARED)}
workbook_gaps = {row["concept_id"]: row for row in read(WORKBOOK_GAPS)}
consolidated = {row["concept_id"]: row for row in read(CONSOLIDATED)}
material_scope = {row["concept_id"]: row for row in read(MATERIAL_SCOPE)}
ontology_integrity = {row["concept_id"]: row for row in read(ONTOLOGY_INTEGRITY)}
final_tail = {row["concept_id"]: row for row in read(FINAL_TAIL)} if FINAL_TAIL.exists() else {}
review_rows, facet_rows = [], []
for item in read(COHORT):
    cid, label, route = item["concept_id"], item["preferred_label"], item["recommended_route"]
    source, facets = decompose(label)
    if cid in IDENTITY_FACETS:
        facets = IDENTITY_FACETS[cid]
    if cid in SHARED_PAGE_FACETS:
        facets = SHARED_PAGE_FACETS[cid]
    if cid in WORKBOOK_GAP_FACETS:
        facets = WORKBOOK_GAP_FACETS[cid]
    if cid in CONSOLIDATED_FACETS:
        facets = CONSOLIDATED_FACETS[cid]
    if cid in MATERIAL_SCOPE_FACETS:
        facets = MATERIAL_SCOPE_FACETS[cid]
    if cid in ONTOLOGY_INTEGRITY_FACETS:
        facets = ONTOLOGY_INTEGRITY_FACETS[cid]
    if cid in FINAL_TAIL_FACETS:
        facets = FINAL_TAIL_FACETS[cid]
    # These compound sources retain an uncovered component after generic suffix
    # stripping; partial decomposition would misstate governed identity.
    if cid in {"AOM_003930"}:
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
    elif (route == "research_taxon_insufficient_for_material" and facets and source
          and not (cid in consolidated and consolidated[cid]["status"] == "approved")):
        decision, status = "approve_taxon_source_with_explicit_facets", "approved"
        evidence = public_cohort[cid]["public_mapping_targets"]
        rationale = "Existing public taxon mapping establishes biological source; explicit label descriptors map only to pre-approved structured facet values."
    elif cid in WORKBOOK_STRUCTURED and facets and source:
        decision, status = "approve_workbook_source_with_explicit_facets", "approved"
        evidence = "review/livestock-v13/workbook_source_cohort.csv"
        rationale = "Canonical workbook path establishes source; explicit oil descriptor maps to approved constituent facet, not physical form."
    elif cid in identity and identity[cid]["status"] == "approved" and facets:
        source = identity[cid]["governed_source_identity"]
        decision, status = "approve_identity_alias_with_explicit_facets", "approved"
        evidence = identity[cid]["evidence"]
        rationale = identity[cid]["rationale"] + " Definition adds only reviewed structured facets."
    elif cid in shared and shared[cid]["status"] == "approved" and facets:
        source = shared[cid]["governed_source_identity"]
        decision, status = "approve_shared_page_material_with_explicit_facets", "approved"
        evidence = shared[cid]["evidence"]
        rationale = shared[cid]["rationale"] + " Definition adds only reviewed structured facets."
    elif cid in workbook_gaps and workbook_gaps[cid]["status"] == "approved" and facets:
        source = workbook_gaps[cid]["governed_source_identity"]
        decision, status = "approve_workbook_model_gap_with_explicit_facets", "approved"
        evidence = workbook_gaps[cid]["evidence"]
        rationale = workbook_gaps[cid]["rationale"] + " Definition adds only reviewed structured facets."
    elif cid in consolidated and consolidated[cid]["status"] == "approved" and facets:
        source = consolidated[cid]["governed_source_identity"]
        decision, status = "approve_consolidated_authority_with_explicit_facets", "approved"
        evidence = consolidated[cid]["evidence"]
        rationale = consolidated[cid]["rationale"] + " Definition adds only reviewed structured facets."
    elif cid in material_scope and material_scope[cid]["status"] == "approved":
        source = material_scope[cid]["governed_source_identity"]
        decision, status = "approve_bounded_workbook_material_scope", "approved"
        evidence = material_scope[cid]["evidence"]
        rationale = material_scope[cid]["rationale"]
    elif cid in ontology_integrity and ontology_integrity[cid]["status"] == "approved":
        source = ontology_integrity[cid]["governed_source_identity"]
        decision, status = "approve_bounded_workbook_material_scope", "approved"
        evidence = ontology_integrity[cid]["evidence"]
        rationale = ontology_integrity[cid]["rationale"]
    elif cid in final_tail and final_tail[cid]["status"] == "approved":
        source = final_tail[cid]["governed_source_identity"]
        decision, status = "approve_bounded_workbook_material_scope", "approved"
        evidence = final_tail[cid]["evidence"]
        rationale = final_tail[cid]["rationale"]
    if status == "held":
        consolidated_hold = consolidated.get(cid)
        if consolidated_hold and consolidated_hold["status"] == "held":
            blocker = consolidated_hold["blocker_code"]
            next_action = consolidated_hold["rationale"]
        integrity_hold = ontology_integrity.get(cid)
        if integrity_hold and integrity_hold["status"] == "held":
            blocker = integrity_hold["blocker_code"]
            next_action = integrity_hold["rationale"]
        final_hold = final_tail.get(cid)
        if final_hold and final_hold["status"] == "held":
            blocker = final_hold["blocker_code"]
            next_action = final_hold["rationale"]
        if route == "research_feedipedia":
            prior = feed[cid]["decision"]
            identity_hold = identity.get(cid)
            blocker = identity_hold["blocker_code"] if identity_hold and identity_hold["status"] == "held" else prior.removeprefix("hold_")
            next_action = {
                "hold_shared_page": "Review every co-referenced AOM concept; retain distinct scopes or approve synonym/replacement with occurrence evidence.",
                "hold_identity_or_alias_review": "Verify scientific/common-name equivalence and material part against taxonomic or feed authority.",
                "hold_source_warning": "Find independent citable feed or taxonomic authority; warned page cannot support approval.",
                "hold_retrieval_failure": "Recover archived page or replace mapping with reachable authoritative evidence.",
            }.get(prior, "Review mapping granularity and replace discovery-only evidence.")
            if identity_hold and identity_hold["status"] == "held":
                next_action = identity_hold["rationale"]
            shared_hold = shared.get(cid)
            if shared_hold and shared_hold["status"] == "held":
                blocker = shared_hold["blocker_code"]
                next_action = shared_hold["rationale"]
        elif route == "research_public_ontology":
            blocker = public[cid]["decision"].removeprefix("hold_")
            next_action = "Correct or narrow public mapping, then establish material component/product scope with direct authority evidence."
        elif route == "research_source_workbook":
            workbook_hold = workbook_gaps.get(cid)
            blocker = workbook_hold["blocker_code"] if workbook_hold else "workbook_identity_or_model_gap"
            next_action = workbook_hold["rationale"] if workbook_hold else "Obtain product/domain evidence or add reviewed component/process facet before definition approval."
        elif route == "research_taxon_insufficient_for_material":
            blocker = "unmodelled_derived_material_descriptor"
            next_action = "Review descriptor meaning; map to existing facet or approve new facet concept before composing definition."
        if consolidated_hold and consolidated_hold["status"] == "held":
            blocker = consolidated_hold["blocker_code"]
            next_action = consolidated_hold["rationale"]
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
