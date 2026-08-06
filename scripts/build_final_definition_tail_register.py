#!/usr/bin/env python3
"""Build decision-ready register for complete unresolved definition tail."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARD = ROOT / "review/livestock-v14/definition_hard_tail_review.csv"
GAPS = ROOT / "review/livestock-v8/definition_gap_queue.csv"
LEXICAL = ROOT / "review/livestock-v4/feed_lexical_identity_candidates.csv"
REVIEW = ROOT / "review/livestock-v20"
COHORT = REVIEW / "final_definition_tail_cohort.csv"
OUT = REVIEW / "final_definition_tail_register.csv"
SUMMARY = REVIEW / "final_definition_tail_summary.json"

POLICY = {
    "granularity_mismatch": ("material_scope", "direct material-grade authority", "high", "domain_expert"),
    "narrower_table_scope": ("material_scope", "table-row or section evidence matching exact material", "high", "domain_expert"),
    "source_material_distinction": ("material_scope", "evidence distinguishing organism/source from feed material", "high", "domain_expert"),
    "composition_state_distinction": ("material_scope", "evidence defining composition or processing state", "high", "domain_expert"),
    "material_scope_unresolved": ("material_scope", "direct evidence defining intended feed material", "high", "domain_expert"),
    "synonym_replacement_review": ("identity_consolidation", "occurrence audit plus accepted-name authority", "critical", "curator"),
    "contradictory_mapping_removed": ("identity_repair", "replacement authority mapping matching exact concept", "critical", "curator"),
    "contradictory_species_mapping": ("identity_repair", "accepted taxon evidence plus occurrence audit", "critical", "curator"),
    "category_or_duplicate_review": ("identity_consolidation", "occurrence audit and canonical replacement decision", "critical", "curator"),
    "unmodelled_derived_material_descriptor": ("semantic_model", "approved facet or explicit new concept model", "high", "ontology_reviewer"),
    "hierarchy_correction_required": ("semantic_model", "approved role and corrected hierarchy parent", "critical", "ontology_reviewer"),
    "public_authority_mismatch": ("authority_repair", "correct exact-scope public authority", "critical", "curator"),
    "source_warning": ("authority_repair", "independent reachable material-grade authority", "high", "curator"),
    "retrieval_failure": ("authority_repair", "archived source or replacement authority", "high", "curator"),
    "external_product_evidence": ("commercial_product", "stable manufacturer and formulation evidence", "high", "domain_expert"),
    "local_identity_evidence": ("local_term", "study-level provenance and local usage definition", "high", "data_steward"),
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
    rows = [{"concept_id": r["concept_id"], "preferred_label": r["preferred_label"]}
            for r in read(HARD) if r["status"] == "held"]
    write(COHORT, rows)
    print(f"Snapshotted {len(rows)} unresolved concepts")
    raise SystemExit

hard = {r["concept_id"]: r for r in read(HARD)}
gaps = {r["concept_id"]: r for r in read(GAPS)}
duplicates = {}
for row in read(LEXICAL):
    ids = row["concept_ids"].split(";")
    for concept_id in ids:
        duplicates.setdefault(concept_id, set()).update(x for x in ids if x != concept_id)

rows = []
for item in read(COHORT):
    cid = item["concept_id"]
    current = hard[cid]
    blocker = current["blocker_code"]
    track, gate, risk, lane = POLICY[blocker]
    gap = gaps.get(cid, {})
    rows.append({
        "concept_id": cid,
        "preferred_label": current["preferred_label"],
        "hierarchy_path": gap.get("hierarchy_path", ""),
        "blocker_code": blocker,
        "remediation_track": track,
        "review_lane": lane,
        "semantic_risk": risk,
        "automation_eligible": "false",
        "candidate_related_ids": ";".join(sorted(duplicates.get(cid, set()))),
        "current_evidence": current["evidence"],
        "resolution_gate": gate,
        "required_action": current["next_action"],
        "proposed_status": "held",
        "reviewer": "TBD",
        "review_date": "",
        "review_notes": "",
    })
write(OUT, rows)
tracks = Counter(r["remediation_track"] for r in rows)
lanes = Counter(r["review_lane"] for r in rows)
risks = Counter(r["semantic_risk"] for r in rows)
SUMMARY.write_text(json.dumps({
    "cohort_size": len(rows),
    "automation_eligible": 0,
    "proposed_held": len(rows),
    "by_remediation_track": dict(sorted(tracks.items())),
    "by_review_lane": dict(sorted(lanes.items())),
    "by_semantic_risk": dict(sorted(risks.items())),
}, indent=2) + "\n", encoding="utf-8")
print(f"Built final definition-tail register: {len(rows)} concepts across {len(tracks)} tracks")
