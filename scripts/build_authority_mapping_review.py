#!/usr/bin/env python3
"""Build assertion-level review for hard-tail public authority mappings."""
import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARD = ROOT / "review/livestock-v14/definition_hard_tail_review.csv"
MAPPINGS = ROOT / "data/livestock-staging/mappings.csv"
REVIEW = ROOT / "review/livestock-v15"
CONCEPT_COHORT = REVIEW / "authority_mapping_concepts.csv"
ASSERTION_COHORT = REVIEW / "authority_mapping_assertions.csv"
OUT = ROOT / "data/livestock-staging/approved_mapping_reviews.csv"
BLOCKERS = {"identity_or_alias_review", "shared_page", "public_authority_mismatch", "source_warning", "retrieval_failure"}

# Evidence-verified contradictions. Scheme-level key removes every target in that
# source cell only where all targets are wrong for concept.
REMOVE_SCHEMES = {
    ("AOM_001216", "feedipedia"), ("AOM_001383", "feedipedia"),
    ("AOM_001389", "feedipedia"), ("AOM_001476", "feedipedia"),
    ("AOM_001892", "feedipedia"), ("AOM_003893", "feedipedia"),
    ("AOM_004002", "feedipedia"), ("AOM_006350", "feedipedia"),
    ("AOM_001193", "agrovoc"), ("AOM_001308", "agrovoc"),
    ("AOM_001308", "ncbi-taxonomy"), ("AOM_001309", "agrovoc"),
    ("AOM_001309", "ncbi-taxonomy"), ("AOM_001333", "agrovoc"),
    ("AOM_001333", "ncbi-taxonomy"), ("AOM_001675", "agrovoc"),
    ("AOM_001760", "agrovoc"), ("AOM_001760", "ncbi-taxonomy"),
    ("AOM_001761", "agrovoc"), ("AOM_001761", "ncbi-taxonomy"),
    ("AOM_001766", "agrovoc"), ("AOM_001766", "ncbi-taxonomy"),
    ("AOM_001771", "agrovoc"), ("AOM_001817", "agrovoc"),
    ("AOM_001817", "ncbi-taxonomy"), ("AOM_001842", "agrovoc"),
    ("AOM_001842", "ncbi-taxonomy"),
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
    concepts = [
        {k: row[k] for k in ["concept_id", "preferred_label", "recommended_route", "blocker_code"]}
        for row in read(HARD) if row["status"] == "held" and row["blocker_code"] in BLOCKERS
    ]
    ids = {row["concept_id"] for row in concepts}
    assertions = [
        {k: row[k] for k in ["subject_id", "target_scheme", "target_id", "target_uri", "original_value", "evidence", "status"]}
        for row in read(MAPPINGS) if row["subject_id"] in ids and row["target_scheme"] != "ilri-code"
    ]
    write(CONCEPT_COHORT, concepts); write(ASSERTION_COHORT, assertions)
    print(f"Snapshotted {len(concepts)} concepts and {len(assertions)} authority assertions")
    raise SystemExit

concepts = {row["concept_id"]: row for row in read(CONCEPT_COHORT)}
rows = []
for assertion in read(ASSERTION_COHORT):
    cid, scheme = assertion["subject_id"], assertion["target_scheme"]
    blocker = concepts[cid]["blocker_code"]
    if (cid, scheme) in REMOVE_SCHEMES:
        decision, publish, status = "remove_contradictory_mapping", "false", "excluded"
        rationale = "Authority target identifies a different taxon or material; retain original value only in immutable audit cohort."
    elif blocker in {"source_warning", "retrieval_failure"} and scheme == "feedipedia":
        decision, publish, status = "retain_related_evidence_hold", "true", "review-held"
        rationale = "Target may remain discoverable as related evidence but cannot support identity or definition while warned or unreachable."
    else:
        decision, publish, status = "retain_related_nondefinitional", "true", "reviewed-related"
        rationale = "Cross-domain or granularity-mismatched target is useful related evidence, not synonymy or definition-grade identity evidence."
    rows.append({
        "subject_id": cid, "preferred_label": concepts[cid]["preferred_label"],
        "target_scheme": scheme, "target_id": assertion["target_id"], "target_uri": assertion["target_uri"],
        "original_value": assertion["original_value"], "mapping_relation": "relatedMatch",
        "decision": decision, "publish": publish, "status": status,
        "definition_evidence_grade": "insufficient", "reviewer": "Pete Steward", "review_date": "2026-08-06",
        "evidence": assertion["target_uri"] or assertion["target_id"], "rationale": rationale,
    })

rows.sort(key=lambda row: (row["subject_id"], row["target_scheme"], row["target_uri"], row["target_id"]))
write(OUT, rows)
print(f"Reviewed {len(rows)} authority assertions: {sum(r['publish']=='false' for r in rows)} removed")
