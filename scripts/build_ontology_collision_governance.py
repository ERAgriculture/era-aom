#!/usr/bin/env python3
"""Approve deterministic context dispositions for active preferred-label collisions."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "review/livestock-v4/ontology_pref_label_collision_candidates.csv"
TARGET = ROOT / "data/livestock-staging/approved_ontology_collision_decisions.csv"
DEPRECATIONS = {
    "antiprotozoal": ("AOM_000338;AOM_000350", "AOM_000350"),
    "antiplasmodial": ("AOM_000339;AOM_000351", "AOM_000351"),
    "antitrichomonal": ("AOM_000340;AOM_000352", "AOM_000352"),
    "coccidiostat": ("AOM_000341;AOM_000353", "AOM_000353"),
    "trypanocidal": ("AOM_000342;AOM_000354", "AOM_000354"),
    "strip grazing": ("AOM_000935;AOM_000949", "AOM_000935"),
}


def classify(paths):
    joined = " | ".join(paths)
    if all("Rearing Stage/" in path for path in paths):
        return "species_specific_rearing_stage", "Same stage label is intentionally scoped to different livestock taxa."
    if any(path.startswith("Species/") for path in paths) and any("Feed Ingredient/" in path for path in paths):
        return "taxon_vs_feed_material", "Taxon concept and material derived from that taxon are related but not identical."
    if "Feed Chemical Composition/" in joined and "Feed Ingredient/Supplement/" in joined:
        return "constituent_vs_supplement", "Measured feed constituent and supplement material have different semantic roles."
    if "aquatic system/" in joined and "terrestrial system/" in joined:
        return "production_system_context", "Same controlled value is scoped independently to aquatic and terrestrial system models."
    if "Feed Addition/" in joined and "Feed Substitution/" in joined:
        return "intervention_context", "Addition and substitution are different intervention roles despite shared object label."
    if "/Pesticide/" in joined and "/Antimicrobial/" in joined:
        return "functional_classification_context", "Parallel pesticide and antimicrobial classifications are not proven identical."
    if "Ingredient processing methods/" in joined or "Ingredient anatomical parts/" in joined or "Feed product types/" in joined:
        return "semantic_facet_vs_domain_concept", "Governed facet value and domain concept serve different model layers."
    if "Feed Process/" in joined and "Feed Management/" in joined:
        return "process_vs_intervention", "Process identity and intervention use remain separate model roles."
    return "hierarchy_scoped_context", "Hierarchy paths establish distinct governed contexts; label equality alone does not establish identity."


with SOURCE.open(encoding="utf-8", newline="") as handle:
    candidates = list(csv.DictReader(handle))

rows = []
for row in candidates:
    paths = row["hierarchy_paths"].split(" | ")
    if row["collision_key"] in DEPRECATIONS:
        category = "verified_duplicate"
        decision = "deprecate_replace"
        rationale = (
            "Labels, definitions, and external mappings establish duplicate identity; "
            f"retain {DEPRECATIONS[row['collision_key']][1]} and preserve replacement provenance."
        )
    elif row["collision_key"] == "cotton seed":
        category = "product_role_ambiguity"
        decision = "hold_identity"
        rationale = "Product versus by-product hierarchy and CPC granularity remain unresolved."
    else:
        category, rationale = classify(paths)
        decision = "retain_distinct"
    rows.append({
        "case_id": "PREFCOLL-" + row["collision_key"].upper().replace(" ", "-"),
        "collision_key": row["collision_key"],
        "concept_ids": row["concept_ids"],
        "decision": decision,
        "retained_id": DEPRECATIONS.get(row["collision_key"], ("", ""))[1],
        "context_category": category,
        "status": "approved",
        "reviewer": "Pete Steward",
        "review_date": "2026-08-06",
        "evidence": "docs/decisions/0021-preferred-label-collision-governance.md",
        "rationale": rationale,
    })

present = {row["collision_key"] for row in rows}
for key, (concept_ids, retained_id) in DEPRECATIONS.items():
    if key in present:
        continue
    rows.append({
        "case_id": "PREFCOLL-" + key.upper().replace(" ", "-"),
        "collision_key": key, "concept_ids": concept_ids,
        "decision": "deprecate_replace", "retained_id": retained_id,
        "context_category": "verified_duplicate", "status": "approved",
        "reviewer": "Pete Steward", "review_date": "2026-08-06",
        "evidence": "docs/decisions/0021-preferred-label-collision-governance.md",
        "rationale": f"Labels, definitions, and external mappings establish duplicate identity; retain {retained_id} and preserve replacement provenance.",
    })
rows.sort(key=lambda row: row["collision_key"])

fields = ["case_id", "collision_key", "concept_ids", "decision", "retained_id", "context_category", "status", "reviewer", "review_date", "evidence", "rationale"]
with TARGET.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
print(f"Governed {len(rows)} preferred-label collision groups")
