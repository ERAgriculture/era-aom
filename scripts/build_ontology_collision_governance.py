#!/usr/bin/env python3
"""Build governed dispositions for every global preferred-label collision."""

import csv
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DETAIL = ROOT / "review/livestock-v25/global_identity_collision_detail.csv"
TARGET = ROOT / "data/livestock-staging/approved_ontology_collision_decisions.csv"
DEPRECATIONS = ROOT / "data/livestock-staging/approved_deprecations.csv"
REMEDIATIONS = ROOT / "data/livestock-staging/approved_identity_integrity_remediations.csv"
EVIDENCE = "docs/decisions/0040-global-legacy-identity-cohort.md"
REVIEWER = "Pete Steward"
REVIEW_DATE = "2026-08-10"


def read_rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_label(value):
    value = unicodedata.normalize("NFKC", value).casefold().strip()
    return re.sub(r"\s+", " ", value)


def case_id(label):
    return "PREFCOLL-" + re.sub(r"[^A-Z0-9]+", "-", label.upper()).strip("-")


def retain_distinction(members):
    paths = [member["hierarchy_path"] for member in members]
    joined_paths = " | ".join(paths)
    definitions = {member["definition"] for member in members}
    if all("Rearing Stage/" in path for path in paths):
        return (
            "taxon_scoped_rearing_stage",
            "Definitions and source scope identify rearing-stage values for different "
            "livestock taxa; taxon-scoped life stages are not interchangeable.",
        )
    if any(path.startswith("Species/") for path in paths) and any(
        "Feed Ingredient/" in path for path in paths
    ):
        return (
            "taxon_vs_feed_material",
            "Definitions distinguish a biological taxon from a feed material derived "
            "from that taxon; those are different ontological categories.",
        )
    if "Feed Chemical Composition/" in joined_paths and "Feed Ingredient/Supplement/" in joined_paths:
        return (
            "constituent_vs_supplement",
            "Definitions distinguish a measured feed constituent from a supplement "
            "material; their shared label does not establish identity.",
        )
    if "Feed Addition/" in joined_paths and "Feed Substitution/" in joined_paths:
        return (
            "intervention_role",
            "Definitions distinguish adding a feed from substituting it within a basal "
            "diet; the intervention roles are not interchangeable.",
        )
    if "Measurement Method/" in joined_paths:
        return (
            "measurement_vs_subject",
            "Definitions distinguish a measurement method from the measured feed "
            "characteristic or digestibility value.",
        )
    if "Outcomes/" in joined_paths and "Feed Ingredient/" in joined_paths:
        return (
            "outcome_vs_material",
            "Definitions distinguish an outcome variable from a feed material; those "
            "are different ontological categories.",
        )
    if len(definitions) > 1:
        return (
            "definition_scoped_distinction",
            "Public AOM definitions establish distinct meanings despite the normalized "
            "preferred-label collision.",
        )
    return (
        "reviewed_semantic_distinction",
        "Public AOM model class and reviewed scope distinguish these concepts; no "
        "replacement is supported by the available evidence.",
    )


detail = read_rows(DETAIL)
deprecation_by_id = {
    row["deprecated_id"]: row["replacement_id"] for row in read_rows(DEPRECATIONS)
}
generated_holds = {
    row["generated_id"]
    for row in read_rows(REMEDIATIONS)
    if row["action"] == "hold_ambiguous" and row["status"] == "hold"
}

members_by_label = defaultdict(list)
for row in detail:
    members_by_label[normalize_label(row["preferred_label"])].append(row)

rows = []
for label, members in sorted(members_by_label.items()):
    concept_ids = sorted({member["concept_id"] for member in members})
    replacements = {
        deprecation_by_id[concept_id]
        for concept_id in concept_ids if concept_id in deprecation_by_id
    }
    if replacements:
        if len(replacements) != 1:
            raise ValueError(f"Collision has competing replacements: {label}")
        decision = "deprecate_replace"
        retained_id = next(iter(replacements))
        context_category = "verified_duplicate"
        status = "approved"
        rationale = (
            "Approved replacement crosswalk establishes duplicate identity; retain "
            f"{retained_id} and preserve deprecated identifier provenance."
        )
    elif label == "cotton seed":
        decision = "hold_identity"
        retained_id = ""
        context_category = "product_role_ambiguity"
        status = "hold"
        rationale = (
            "Product versus by-product hierarchy and CPC granularity remain unresolved; "
            "no replacement or label change is safe."
        )
    elif generated_holds & set(concept_ids):
        decision = "hold_identity"
        retained_id = ""
        context_category = "ambiguous_legacy_process"
        status = "hold"
        rationale = (
            "Legacy concepts compete with a governed facet value; domain review must "
            "determine polyhierarchy and any replacement target."
        )
    else:
        context_category, rationale = retain_distinction(members)
        decision = "retain_distinct"
        retained_id = ""
        status = "approved"
    rows.append({
        "case_id": case_id(label),
        "collision_key": label,
        "concept_ids": ";".join(concept_ids),
        "decision": decision,
        "retained_id": retained_id,
        "context_category": context_category,
        "status": status,
        "reviewer": REVIEWER,
        "review_date": REVIEW_DATE,
        "evidence": EVIDENCE,
        "rationale": rationale,
    })

fields = [
    "case_id", "collision_key", "concept_ids", "decision", "retained_id",
    "context_category", "status", "reviewer", "review_date", "evidence",
    "rationale",
]
with TARGET.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

counts = Counter(row["decision"] for row in rows)
print(
    f"Governed {len(rows)} global preferred-label collision groups: "
    f"{counts['retain_distinct']} retain, {counts['deprecate_replace']} replace, "
    f"{counts['hold_identity']} hold"
)
