#!/usr/bin/env python3
"""Build global preferred-label identity-collision review cohort."""

import csv
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
OUT = ROOT / "review/livestock-v25"


def read_csv(name):
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_label(value):
    value = unicodedata.normalize("NFKC", value).casefold().strip()
    return re.sub(r"\s+", " ", value)


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


labels = read_csv("labels.csv")
concepts = {row["concept_id"]: row for row in read_csv("concepts.csv")}
definitions = {
    row["concept_id"]: row["definition"] for row in read_csv("definitions.csv")
    if row["language"] == "en"
}
relations = read_csv("relations.csv")
parents = defaultdict(list)
for row in relations:
    if row["relation_type"] == "broader":
        parents[row["subject_id"]].append(row["object_id"])

preferred = [row for row in labels if row["label_type"] == "pref"]
label_by_id = {row["concept_id"]: row["label"] for row in preferred}
groups = defaultdict(list)
for row in preferred:
    groups[normalize_label(row["label"])].append(row["concept_id"])
groups = {label: sorted(set(ids)) for label, ids in groups.items() if len(set(ids)) > 1}

new_concepts = {row["concept_id"]: row for row in read_csv("approved_new_concepts.csv")}
facet_concepts = {
    row["concept_id"]: row for row in read_csv("approved_ingredient_facet_concepts.csv")
}
remediations = {
    row["generated_id"]: row
    for row in read_csv("approved_identity_integrity_remediations.csv")
}
decision_rows = read_csv("approved_ontology_collision_decisions.csv")
decisions_by_label = {}
for row in decision_rows:
    key = normalize_label(row["collision_key"])
    if key in decisions_by_label:
        raise ValueError(f"Duplicate identity-collision decision key: {key}")
    decisions_by_label[key] = row
facet_sources = [
    "approved_feed_material_facets.csv",
    "approved_generated_feed_material_facets.csv",
    "approved_hard_tail_feed_material_facets.csv",
]
uses = defaultdict(list)
for name in facet_sources:
    for row in read_csv(name):
        uses[row["target_concept_id"]].append(
            f'{row["feed_material_id"]}:{row["target_property"]}'
        )

cohort = []
detail = []
for index, (normalized, ids) in enumerate(sorted(groups.items()), start=1):
    generated = [cid for cid in ids if cid in new_concepts]
    inherited = [cid for cid in ids if cid not in new_concepts]
    if generated and inherited:
        recommendation = "review_reuse_existing"
        candidate = sorted(inherited)[0]
        rationale = "Generated concept duplicates inherited preferred label; property context alone cannot establish distinct identity."
    elif generated:
        recommendation = "review_generated_collision"
        candidate = ""
        rationale = "Multiple generated concepts share preferred label; definitions and intended dimensions require identity review."
    else:
        recommendation = "review_legacy_identity"
        candidate = ""
        rationale = "Inherited concepts share preferred label; retain separately only with evidence-backed semantic distinction."
    reviewed = [remediations[cid] for cid in generated if cid in remediations]
    decision = decisions_by_label.get(normalized)
    if generated and len(reviewed) == len(generated):
        recommendation = ";".join(sorted({row["action"] for row in reviewed}))
        candidate = ";".join(sorted(filter(None, (row["canonical_id"] for row in reviewed))))
        review_status = "approved" if all(row["status"] == "approved" for row in reviewed) else "hold"
        rationale = " ".join(row["rationale"] for row in reviewed)
        reviewer = ";".join(sorted({row["reviewer"] for row in reviewed}))
        review_date = ";".join(sorted({row["review_date"] for row in reviewed}))
    elif decision and set(decision["concept_ids"].split(";")) == set(ids):
        recommendation = decision["decision"]
        candidate = decision["retained_id"]
        review_status = (
            "hold"
            if decision["status"] == "hold" or decision["decision"].startswith("hold_")
            else "approved"
            if decision["status"] == "approved"
            else "proposed"
        )
        rationale = decision["rationale"]
        reviewer = decision["reviewer"]
        review_date = decision["review_date"]
    elif decision:
        recommendation = "review_decision_drift"
        candidate = ""
        review_status = "proposed"
        rationale = (
            "Existing collision decision does not cover the current concept set: "
            + decision["concept_ids"]
        )
        reviewer = ""
        review_date = ""
    else:
        review_status = "proposed"
        reviewer = ""
        review_date = ""
    cohort.append({
        "collision_id": f"IDENTITY-{index:03d}",
        "normalized_label": normalized,
        "display_labels": " | ".join(sorted({label_by_id[cid] for cid in ids})),
        "concept_ids": ";".join(ids),
        "concept_count": len(ids),
        "generated_ids": ";".join(generated),
        "inherited_ids": ";".join(inherited),
        "recommended_action": recommendation,
        "candidate_canonical_id": candidate,
        "review_status": review_status,
        "reviewer": reviewer,
        "review_date": review_date,
        "rationale": rationale,
    })
    collision_id = cohort[-1]["collision_id"]
    for cid in ids:
        concept = concepts[cid]
        facet = facet_concepts.get(cid, {})
        detail.append({
            "collision_id": collision_id,
            "concept_id": cid,
            "preferred_label": label_by_id[cid],
            "origin": "generated" if cid in new_concepts else "inherited",
            "concept_type": concept["concept_type"],
            "hierarchy_path": concept["derived_path"],
            "broader_ids": ";".join(sorted(set(parents[cid]))),
            "broader_labels": ";".join(label_by_id.get(x, x) for x in sorted(set(parents[cid]))),
            "facet_kind": facet.get("facet", ""),
            "target_property": facet.get("target_property", ""),
            "value_class": facet.get("value_class", ""),
            "definition": definitions.get(cid, ""),
            "semantic_use_count": len(uses[cid]),
            "semantic_use_examples": ";".join(sorted(uses[cid])[:5]),
        })

summary = {
    "generated_at": "2026-08-07",
    "duplicate_preferred_label_groups": len(cohort),
    "concepts_in_duplicate_groups": len(detail),
    "excess_identifiers": len(detail) - len(cohort),
    "generated_vs_inherited_groups": sum(bool(row["generated_ids"] and row["inherited_ids"]) for row in cohort),
    "reviewed_groups": sum(row["review_status"] in {"approved", "hold"} for row in cohort),
    "approved_groups": sum(row["review_status"] == "approved" for row in cohort),
    "held_groups": sum(row["review_status"] == "hold" for row in cohort),
    "unreviewed_groups": sum(row["review_status"] == "proposed" for row in cohort),
    "applied_reuse_remediations": sum(
        row["action"] == "reuse_existing" and row["status"] == "approved"
        and row["generated_id"] not in concepts
        for row in remediations.values()
    ),
    "applied_rename_remediations": sum(
        row["action"] == "rename_distinct" and row["status"] == "approved"
        and label_by_id.get(row["generated_id"]) == row["replacement_label"]
        for row in remediations.values()
    ),
}
summary["status"] = (
    "review_required" if summary["unreviewed_groups"]
    else "governed_with_holds" if summary["held_groups"]
    else "governed"
)

write_csv(OUT / "global_identity_collision_cohort.csv", list(cohort[0]), cohort)
write_csv(OUT / "global_identity_collision_detail.csv", list(detail[0]), detail)
(OUT / "global_identity_collision_summary.json").write_text(
    json.dumps(summary, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(summary, indent=2))
