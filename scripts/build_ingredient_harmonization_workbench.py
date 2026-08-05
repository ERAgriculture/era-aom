#!/usr/bin/env python3
"""Build scalable, deterministic feed-ingredient harmonization proposals."""

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/livestock-staging/legacy_records.csv"
OUT = ROOT / "review/livestock-v5"
DEPRECATIONS = ROOT / "data/livestock-staging/approved_deprecations.csv"
CONCEPTS = ROOT / "data/livestock-staging/concepts.csv"

ALIASES = {
    "corn": "maize", "milled": "ground", "grounded": "ground",
    "ensilation": "ensiled", "silage": "ensiled", "toasted": "roasted",
    "cooked": "heated", "leaves": "leaf", "pods": "pod",
}
PROCESS = {
    "alkali treated": "Alkali treatment", "autoclaved": "Autoclaving",
    "boiled": "Boiling", "chopped": "Chopping", "cracked": "Cracking",
    "crushed": "Crushing", "defatted": "Defatting", "dried": "Drying",
    "ensiled": "Ensiling", "enzyme treated": "Enzyme treatment",
    "extruded": "Extrusion", "fermented": "Fermentation", "ground": "Grinding",
    "heated": "Heating", "hydrolysed": "Hydrolysis", "molasses treated": "Molasses treatment",
    "pelleted": "Pelleting", "pressed": "Pressing", "roasted": "Roasting",
    "soaked": "Soaking", "sprouted": "Sprouting", "urea treated": "Urea treatment",
    "wilted": "Wilting",
}
COMPONENT = {
    "blood": "Blood", "bran": "Bran", "cob": "Cob", "ear": "Ear",
    "grain": "Grain", "head": "Head", "husk": "Husk", "kernel": "Kernel",
    "leaf": "Leaf", "peel": "Peel", "pod": "Pod", "root": "Root",
    "seed": "Seed", "shell": "Shell", "stem": "Stem", "stover": "Stover",
    "straw": "Straw", "tuber": "Tuber", "vine": "Vine",
}
FORM = {
    "block": "Block", "cake": "Cake", "flake": "Flake", "flour": "Flour",
    "hay": "Hay", "liquid": "Liquid", "meal": "Meal", "oil": "Oil",
    "paste": "Paste", "pellet": "Pellet", "powder": "Powder", "pulp": "Pulp",
}
QUALITY = {
    "brown": "Brown", "green": "Green", "low quality": "Low quality",
    "red": "Red", "ripe": "Ripe", "unripe": "Unripe", "white": "White",
    "yellow": "Yellow",
}
AMBIGUOUS = {
    "whole": "whole may mean whole crop, whole grain, whole organism, or physical presentation",
    "meal": "meal may identify product, physical form, or grinding result",
    "hay": "hay may identify conserved material or physical/product form",
    "pulp": "pulp may identify anatomical residue, by-product, or physical form",
    "green": "green may identify colour, maturity, or fresh state",
}
STRUCTURAL_L6 = {
    "Ingredient name", "Ingredient part", "Ingredient proportion",
    "Ingredient source", "Ingredient species",
}


def normalize(value):
    text = re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()
    words = [ALIASES.get(word, word) for word in text.split()]
    return " ".join(words)


def matches(text, vocabulary):
    found = []
    padded = f" {text} "
    for term, value in vocabulary.items():
        if f" {term} " in padded:
            found.append((term, value))
    return found


def strip_terms(text, groups):
    result = f" {text} "
    for term in sorted({term for group in groups for term, _ in group}, key=len, reverse=True):
        result = result.replace(f" {term} ", " ")
    return re.sub(r"\s+", " ", result).strip()


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


with SOURCE.open(encoding="utf-8", newline="") as handle:
    source_rows = list(csv.DictReader(handle))
with DEPRECATIONS.open(encoding="utf-8", newline="") as handle:
    approved_deprecations = list(csv.DictReader(handle))
with CONCEPTS.open(encoding="utf-8", newline="") as handle:
    concept_paths = {row["concept_id"]: row["derived_path"] for row in csv.DictReader(handle)}
deprecated = {row["deprecated_id"]: row["replacement_id"] for row in approved_deprecations}
retained_replacements = set(deprecated.values())
ingredient_occurrences = [
    row for row in source_rows if row["AOM"] and row["L5"] == "Feed Ingredient"
]
by_concept = defaultdict(list)
for row in ingredient_occurrences:
    by_concept[row["AOM"]].append(row)
rows = []
for concept_id, occurrences in by_concept.items():
    governed_path = concept_paths[concept_id]
    rows.append(next(
        (row for row in occurrences if row["Derived_Path"] == governed_path),
        occurrences[0],
    ))
rows.sort(key=lambda row: row["AOM"])

inventory = []
for row in rows:
    label = normalize(row["Edge_Value"])
    process = matches(label, PROCESS)
    component = matches(label, COMPONENT)
    form = matches(label, FORM)
    quality = matches(label, QUALITY)
    ambiguity = [(term, reason) for term, reason in AMBIGUOUS.items() if f" {term} " in f" {label} "]
    base = strip_terms(label, [process, component, form, quality, [(term, term) for term, _ in ambiguity]])
    reasons = [reason for _, reason in ambiguity]
    if row["L6"] in STRUCTURAL_L6:
        reasons.append("structural metadata concept, not feed-material identity")
    if not base:
        reasons.append("no source identity remains after decomposition")
    if not any((process, component, form, quality, ambiguity)):
        confidence, route = "high", "retain_atomic_candidate"
    elif reasons:
        confidence, route = "low", "expert_exception"
    elif len(component) <= 1 and len(form) <= 1 and len(quality) <= 1:
        confidence, route = "high", "rule_application_candidate"
    else:
        confidence, route = "medium", "batch_review"
    signature = "|".join([
        base,
        ";".join(value for _, value in component),
        ";".join(value for _, value in process),
        ";".join(value for _, value in form),
        ";".join(value for _, value in quality),
    ])
    inventory.append({
        "concept_id": row["AOM"], "preferred_label": row["Edge_Value"],
        "ingredient_family": row["L6"], "source_identity_candidate": base,
        "component_candidates": ";".join(value for _, value in component),
        "process_candidates": ";".join(value for _, value in process),
        "form_candidates": ";".join(value for _, value in form),
        "quality_candidates": ";".join(value for _, value in quality),
        "normalized_signature": signature, "confidence": confidence,
        "review_route": route, "exception_reason": "; ".join(reasons),
        "definition_status": "present" if row["Description"].strip() else "missing",
        "governance_state": (
            "approved_deprecated" if row["AOM"] in deprecated else
            "approved_retained_replacement" if row["AOM"] in retained_replacements else
            "unreviewed"
        ),
        "status": "proposed-not-applied", "rule_version": "1.0.0",
    })

by_signature = defaultdict(list)
for row in inventory:
    by_signature[row["normalized_signature"]].append(row)
clusters = []
for number, (signature, members) in enumerate(
    sorted((item for item in by_signature.items() if len(item[1]) > 1)), start=1
):
    member_ids = {row["concept_id"] for row in members}
    resolved_pairs = {
        (old, new) for old, new in deprecated.items() if {old, new} <= member_ids
    }
    clusters.append({
        "cluster_id": f"INGCLUSTER-{number:04d}", "normalized_signature": signature,
        "concept_ids": ";".join(sorted(row["concept_id"] for row in members)),
        "preferred_labels": ";".join(sorted(row["preferred_label"] for row in members)),
        "member_count": len(members), "highest_confidence":
        "high" if all(row["confidence"] == "high" for row in members) else "medium_or_low",
        "recommended_action": "review_as_family; never merge from signature alone",
        "status": "resolved-by-approved-deprecation" if resolved_pairs else "proposed-not-applied",
    })

exceptions = [
    row for row in inventory
    if row["review_route"] == "expert_exception" and row["governance_state"] == "unreviewed"
]
exceptions.sort(key=lambda row: (row["ingredient_family"], row["preferred_label"], row["concept_id"]))
exception_rows = [{
    "exception_id": f"INGEX-{number:04d}", "concept_id": row["concept_id"],
    "preferred_label": row["preferred_label"], "ingredient_family": row["ingredient_family"],
    "exception_reason": row["exception_reason"], "recommended_action":
    "review with definition and source context; approve reusable rule when pattern recurs",
    "status": "expert-review-required",
} for number, row in enumerate(exceptions, start=1)]

rule_rows = []
for dimension, vocabulary in (("process", PROCESS), ("component", COMPONENT), ("form", FORM), ("quality", QUALITY)):
    for term, value in vocabulary.items():
        rule_rows.append({
            "rule_id": f"{dimension.upper()}-{term.upper().replace(' ', '_')}",
            "dimension": dimension, "source_pattern": term, "normalized_value": value,
            "default_confidence": "high", "approval_state": "proposed",
            "safety_constraint": "proposal only; preserve legacy ID; require family review before merge or deprecation",
        })
for term, reason in AMBIGUOUS.items():
    rule_rows.append({
        "rule_id": f"AMBIGUOUS-{term.upper()}", "dimension": "ambiguous",
        "source_pattern": term, "normalized_value": "", "default_confidence": "low",
        "approval_state": "held", "safety_constraint": reason,
    })

counts = Counter(row["review_route"] for row in inventory)
summary = {
    "rule_version": "1.0.0", "source": "data/livestock-staging/legacy_records.csv",
    "ingredient_concepts": len(inventory), "rules": len(rule_rows),
    "signature_clusters": len(clusters), "clustered_concepts": sum(int(row["member_count"]) for row in clusters),
    "unresolved_signature_clusters": sum(row["status"] == "proposed-not-applied" for row in clusters),
    "unresolved_expert_exceptions": len(exception_rows),
    "routes": dict(sorted(counts.items())), "family_counts": dict(sorted(Counter(row["ingredient_family"] for row in inventory).items())),
    "safety": {"automatic_ontology_changes": 0, "legacy_ids_preserved": True, "ilri_identifiers_used": False},
}

OUT.mkdir(parents=True, exist_ok=True)
write_csv(OUT / "ingredient_harmonization_inventory.csv", inventory, list(inventory[0]))
write_csv(OUT / "ingredient_rule_catalog.csv", rule_rows, list(rule_rows[0]))
write_csv(OUT / "ingredient_signature_clusters.csv", clusters, list(clusters[0]))
write_csv(OUT / "ingredient_exception_queue.csv", exception_rows, list(exception_rows[0]))
(OUT / "ingredient_harmonization_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

print(
    f"Classified {len(inventory)} ingredients with {len(rule_rows)} rules: "
    f"{counts['rule_application_candidate']} rule candidates, "
    f"{counts['retain_atomic_candidate']} atomic candidates, "
    f"{counts['batch_review']} batch review, {len(exception_rows)} unresolved exceptions; "
    f"{len(clusters)} duplicate-signature clusters."
)
