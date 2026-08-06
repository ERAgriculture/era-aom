#!/usr/bin/env python3
"""Review consolidated authority, model-gap, warning, and product cohort."""
import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARD = ROOT / "review/livestock-v14/definition_hard_tail_review.csv"
PUBLIC = ROOT / "review/livestock-v12/public_authority_cohort.csv"
FEED = ROOT / "review/livestock-v11/feedipedia_source_scope_review.csv"
WORKBOOK = ROOT / "review/livestock-v13/workbook_source_scope_review.csv"
REVIEW = ROOT / "review/livestock-v19"
COHORT = REVIEW / "authority_model_cohort.csv"
OUT = REVIEW / "authority_model_review.csv"
BLOCKS = {"public_authority_mismatch", "unmodelled_derived_material_descriptor", "source_warning", "retrieval_failure", "external_product_evidence"}

APPROVED = {
    "AOM_000557": ("oyster", "approve_independent_taxon_with_shell", "Independent taxon mapping plus explicit shell descriptor establishes material without relying on warned Feedipedia page."),
    "AOM_000610": ("soybean", "approve_authority_source_with_facets", "Public source mappings establish soybean; explicit cake descriptor supplies bounded material form."),
    "AOM_000611": ("soybean", "approve_authority_source_with_facets", "Public source mappings establish soybean; explicit full-fat cake descriptors supply bounded characteristics."),
    "AOM_000616": ("canola", "approve_authority_source_with_facets", "Public source mappings establish canola; explicit cake descriptor supplies bounded material form."),
    "AOM_001193": ("groundnut", "approve_authority_source_with_facets", "Public source mappings establish groundnut; explicit oil descriptor supplies bounded constituent."),
    "AOM_001254": ("groundnut", "approve_authority_source_with_facets", "Public source mappings establish groundnut; explicit cake descriptor supplies bounded material form."),
    "AOM_001297": ("maize", "approve_authority_source_with_facets", "Public source mappings establish maize; explicit sheath descriptor supplies bounded anatomical part."),
    "AOM_001308": ("canola", "approve_authority_source_with_facets", "Public source mappings establish canola; explicit oil descriptor supplies bounded constituent."),
    "AOM_001439": ("beetroot", "approve_authority_source_with_facets", "Public source mappings establish beetroot; explicit discard descriptor supplies bounded product role."),
    "AOM_001603": ("Acacia tortilis", "approve_authority_source_with_facets", "Public taxon mappings establish Acacia tortilis; explicit fruit descriptor supplies bounded anatomical part."),
    "AOM_001675": ("maize", "approve_authority_source_with_facets", "Public source mappings establish maize; explicit baby-corn stalk descriptor supplies bounded stem part."),
    "AOM_001761": ("Acacia etbaica", "approve_authority_source_with_facets", "Public taxon mapping establishes Acacia etbaica; explicit fruit descriptor supplies bounded anatomical part."),
    "AOM_001817": ("legume", "approve_authority_source_with_facets", "Public classification establishes legume source; explicit residue descriptor supplies bounded product role."),
    "AOM_001842": ("cabbage", "approve_authority_source_with_facets", "Public source mappings establish cabbage; explicit discard descriptor supplies bounded product role."),
    "AOM_001846": ("cereal milling", "approve_industry_material_with_facets", "Pollard is retained as named cereal-milling by-product; no cereal species is inferred."),
    "AOM_006003": ("sugar processing", "approve_generic_material_with_facets", "Generic molasses identity is represented through liquid, sugar-processing, and by-product facets."),
    "AOM_006169": ("groundnut", "approve_authority_source_with_facets", "Public source mappings establish groundnut; explicit residue descriptor supplies bounded product role."),
}


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
    rows = [{"concept_id": r["concept_id"], "preferred_label": r["preferred_label"], "prior_blocker": r["blocker_code"], "recommended_route": r["recommended_route"]}
            for r in read(HARD) if r["status"] == "held" and r["blocker_code"] in BLOCKS]
    write(COHORT, rows); print(f"Snapshotted {len(rows)} consolidated concepts"); raise SystemExit

public = {r["concept_id"]: r for r in read(PUBLIC)}
feed = {r["concept_id"]: r for r in read(FEED)}
workbook = {r["concept_id"]: r for r in read(WORKBOOK)}
rows = []
for item in read(COHORT):
    cid, blocker = item["concept_id"], item["prior_blocker"]
    source, decision, status = "", "hold_evidence_boundary", "held"
    rationale = "Available authority does not establish complete public material identity; retain explicit hold."
    if cid in APPROVED:
        source, decision, rationale = APPROVED[cid]; status, blocker = "approved", ""
    elif blocker == "external_product_evidence":
        decision = "hold_external_product_evidence"
        rationale = "Branded product needs stable manufacturer, formulation, and product evidence before public definition."
    elif blocker in {"source_warning", "retrieval_failure"}:
        decision = "hold_unreliable_source"
        rationale = "Warned or unreachable source cannot support definition and no independent material-grade authority is available."
    elif cid in {"AOM_001805", "AOM_003359", "AOM_003858", "AOM_003929", "AOM_000638"}:
        decision = "hold_unsafe_descriptor_inference"
        rationale = "Larva, vein/vine, or shaft descriptor cannot be approximated to existing organism or anatomical facets."
    evidence = ""
    if cid in public: evidence = public[cid].get("public_mapping_targets", "")
    if not evidence and cid in feed: evidence = feed[cid].get("feedipedia_url", "")
    if not evidence and cid in workbook: evidence = workbook[cid].get("evidence", "")
    rows.append({"concept_id": cid, "preferred_label": item["preferred_label"], "prior_blocker": item["prior_blocker"],
                 "decision": decision, "status": status, "governed_source_identity": source, "blocker_code": blocker,
                 "reviewer": "Pete Steward", "review_date": "2026-08-06", "evidence": evidence, "rationale": rationale})
write(OUT, rows)
print(f"Reviewed {len(rows)} consolidated concepts: {sum(r['status']=='approved' for r in rows)} approved")
