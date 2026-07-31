#!/usr/bin/env python3
"""Build domain-review queues from normalized public livestock staging."""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
OUT = ROOT / "review/livestock-v2"
LEVELS = [f"L{i}" for i in range(1, 11)]


def read(name):
    with (DATA / f"{name}.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write(name, fields, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


legacy = read("legacy_records")
concepts = read("concepts")
gaps = read("hierarchy_gaps")
quarantine = read("quarantine")
labels = read("labels")

legacy_by_id = {
    row["AOM"]: row for row in legacy
    if row["AOM"] and row["AOM"] != "AOM_006275"
}
legacy_by_source = {row["source_row"]: row for row in legacy}
pref = {row["concept_id"]: row["label"] for row in labels if row["label_type"] == "pref"}
concept_path_to_id = {}
label_to_ids = defaultdict(list)
for concept in concepts:
    row = legacy_by_id[concept["concept_id"]]
    key = tuple(row[level] for level in LEVELS if row[level])
    concept_path_to_id[key] = concept["concept_id"]
    label_to_ids[pref[concept["concept_id"]].casefold()].append(concept["concept_id"])

collision_rows = []
for row in quarantine:
    source = legacy_by_source[row["source_row"]]
    case = (
        "ID-AOM-006275" if row["reason"] == "duplicate_concept_id"
        else "PATH-BREWERS-GRAIN"
    )
    question = (
        "Should AOM_006275 remain with Panicum antidotale Dried and the "
        "Panicum maximum Dried row resolve to existing AOM_001676?"
        if row["reason"] == "duplicate_concept_id"
        else "Are concepts identical, distinct despite same path, or should one be deprecated?"
    )
    observation = (
        "Two rows have different labels/scientific names but reuse same AOM, NCBI, and WFO identifiers; existing AOM_001676 represents Megathyrsus maximus Dried."
        if row["reason"] == "duplicate_concept_id"
        else "Two IDs share same label, path, and Feedipedia target."
    )
    collision_rows.append({
        "case_id": case,
        "priority": "blocker",
        "issue_type": row["reason"],
        "source_row": row["source_row"],
        "concept_id": row["concept_id"],
        "preferred_label": row["preferred_label"],
        "derived_path": row["derived_path"],
        "description": source["Description"],
        "synonym": source["Synonym"],
        "scientific_name": source["Scientific Name"],
        "agrovoc": source["Agrovoc"],
        "ncbi": source["NCBI"],
        "wfo": source["WFO"],
        "feedipedia": source["Feedipedia"],
        "evidence_observation": observation,
        "review_question": question,
        "decision": "",
        "retained_id": "",
        "replacement_id": "",
        "reviewer": "",
        "review_date": "",
        "rationale": "",
    })

gap_ids = {row["child_id"] for row in gaps}
groups = defaultdict(list)
for child_id in sorted(gap_ids):
    source = legacy_by_id[child_id]
    levels = tuple(source[level] for level in LEVELS if source[level])
    groups[levels[:-1]].append(child_id)

parent_rows = []
batch_counts = Counter()
for number, parent_key in enumerate(sorted(groups), 1):
    children = groups[parent_key]
    parent_label = parent_key[-1]
    nearest_id = ""
    nearest_path = ""
    for depth in range(len(parent_key) - 1, 0, -1):
        ancestor_key = parent_key[:depth]
        if ancestor_key in concept_path_to_id:
            nearest_id = concept_path_to_id[ancestor_key]
            nearest_path = "/".join(ancestor_key)
            break
    same_label_ids = sorted(label_to_ids[parent_label.casefold()])
    impact = len(children)
    priority = "high" if impact >= 10 else "medium" if impact >= 3 else "normal"
    branch = parent_key[0] if parent_key else "Unclassified"
    subbranch = parent_key[1] if len(parent_key) > 1 else ""
    batch = f"{branch} / {subbranch}" if subbranch else branch
    batch_counts[batch] += 1
    parent_rows.append({
        "case_id": f"PARENT-{number:03d}",
        "priority": priority,
        "top_branch": branch,
        "review_batch": batch,
        "candidate_parent_label": parent_label,
        "candidate_parent_path": "/".join(parent_key),
        "candidate_depth": len(parent_key),
        "affected_child_count": impact,
        "affected_child_ids": ";".join(children),
        "sample_child_labels": "; ".join(pref[child] for child in children[:5]),
        "nearest_explicit_ancestor_id": nearest_id,
        "nearest_explicit_ancestor_path": nearest_path,
        "same_label_existing_ids": ";".join(same_label_ids),
        "review_question": (
            "Mint explicit intermediate concept, map to existing concept, "
            "reparent children, or reject hierarchy?"
        ),
        "decision": "",
        "approved_parent_id": "",
        "reviewer": "",
        "review_date": "",
        "evidence": "",
        "rationale": "",
    })

decision_rows = []
for case_id, issue_type, question in [
    ("ID-AOM-006275", "duplicate_concept_id",
     "Assign retained ID, replacement ID, and explicit crosswalk."),
    ("PATH-BREWERS-GRAIN", "duplicate_derived_path",
     "Decide identity, distinction, merge, or deprecation."),
]:
    decision_rows.append({
        "case_id": case_id, "case_type": issue_type, "priority": "blocker",
        "review_question": question, "decision": "", "approved_id": "",
        "reviewer": "", "review_date": "", "evidence": "", "rationale": "",
    })
for row in parent_rows:
    decision_rows.append({
        "case_id": row["case_id"], "case_type": "missing_explicit_parent",
        "priority": row["priority"], "review_question": row["review_question"],
        "decision": "", "approved_id": "", "reviewer": "",
        "review_date": "", "evidence": "", "rationale": "",
    })

write("01_identity_collisions.csv", list(collision_rows[0]), collision_rows)
write("02_missing_parent_candidates.csv", list(parent_rows[0]), parent_rows)
write("03_review_decisions.csv", list(decision_rows[0]), decision_rows)

summary = {
    "status": "review-input-only",
    "source": "AOM Livestock v2 normalized public staging",
    "identity_cases": 2,
    "identity_records": len(collision_rows),
    "missing_parent_candidates": len(parent_rows),
    "affected_child_relations": len(gaps),
    "priority": dict(Counter(row["priority"] for row in parent_rows)),
    "review_batches": dict(sorted(batch_counts.items())),
    "safety": {
        "semantic_decisions_applied": 0,
        "identifiers_minted": 0,
        "hierarchy_changes_applied": 0,
    },
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

batch_lines = "\n".join(
    f"| {batch} | {count} |" for batch, count in sorted(batch_counts.items())
)
high_lines = "\n".join(
    f"| {row['case_id']} | {row['affected_child_count']} | "
    f"{row['candidate_parent_path']} | {row['same_label_existing_ids'] or '—'} |"
    for row in parent_rows if row["priority"] == "high"
)
(OUT / "README.md").write_text(f"""# AOM Livestock v2 domain-review pack

Review input generated from public normalized staging. No decision in this
directory changes AOM.

## Review order

1. Resolve two blocking identity cases in `01_identity_collisions.csv`.
2. Review {len(parent_rows)} missing-parent candidates in
   `02_missing_parent_candidates.csv`, grouped into batches below.
3. Record signed decisions in `03_review_decisions.csv`.
4. Apply approved decisions through separate validated pull request.

Evidence-backed recommendations for eight priority cases:
[`PRIORITY_RECOMMENDATIONS.md`](PRIORITY_RECOMMENDATIONS.md). Structured copy:
`04_priority_recommendations.csv`.

## Missing-parent batches

| Batch | Candidate parents |
|---|---:|
{batch_lines}

{len(gaps)} child relations depend on these {len(parent_rows)} candidate
parents. High priority means at least 10 affected children; medium means 3–9.
Priority measures impact, not semantic confidence.

## High-impact parent cases

| Case | Children | Candidate path | Same-label existing ID |
|---|---:|---|---|
{high_lines}

## Allowed decisions

Identity collision:

- retain one ID and mint replacement;
- confirm distinct concepts and distinguish paths;
- merge/deprecate with replacement link;
- request more evidence.

Missing parent:

- mint explicit intermediate concept;
- map to existing concept;
- reparent affected children;
- reject proposed hierarchy;
- request more evidence.

Reviewer must supply identity, date, evidence, and rationale. Empty decision
fields are intentional. AI may summarize evidence but cannot approve.

## Safety

- identifiers minted: 0;
- hierarchy changes applied: 0;
- semantic decisions applied: 0;
- private workbook content used: 0.
""", encoding="utf-8")

print(
    f"Built review pack: 2 identity cases, {len(parent_rows)} parent candidates, "
    f"{len(gaps)} affected child relations."
)
