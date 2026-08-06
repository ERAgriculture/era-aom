#!/usr/bin/env python3
"""Consolidate remaining ingredient exceptions and signature clusters by model gap."""

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW5 = ROOT / "review/livestock-v5"
DATA = ROOT / "data/livestock-staging"
OUT = ROOT / "review/livestock-v7"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


exceptions = read(REVIEW5 / "ingredient_exception_queue.csv")
clusters = read(REVIEW5 / "ingredient_signature_clusters.csv")
legacy = read(DATA / "legacy_records.csv")
labels = read(DATA / "labels.csv")

gap_design = {
    "standalone_material_identity": (
        "source-identity fallback", "derive material source from reviewed hierarchy/context, not stripped label",
        "engine gap; no new facet until source identity is reviewed",
    ),
    "whole_grain_integrity": (
        "material integrity", "aom:materialIntegrity -> Whole grain",
        "separate grain integrity from whole crop and physical form",
    ),
    "dairy_composition_state": (
        "composition state", "future dairy composition/fat-state facet",
        "whole milk denotes composition, not whole physical form",
    ),
    "pulp_product_material": (
        "feed product type", "future reviewed pulp product/material class",
        "pulp may be processing product, residue, anatomical material, or form",
    ),
    "conserved_forage_hay": (
        "conservation product/state", "future hay conservation state plus evidenced drying process",
        "hay is conserved forage identity, not mere physical form",
    ),
    "formulated_feed_meal": (
        "formulated-feed category", "future target-species/feed-purpose classification",
        "ration meal names do not imply grinding or anatomical material",
    ),
}


def gap_for(row):
    reason = row["exception_reason"]
    label = row["preferred_label"].casefold()
    if "no source identity" in reason:
        return "standalone_material_identity"
    if "whole may mean" in reason:
        return "dairy_composition_state" if "milk" in label else "whole_grain_integrity"
    if "pulp may identify" in reason:
        return "pulp_product_material"
    if "hay may identify" in reason:
        return "conserved_forage_hay"
    if "meal may identify" in reason:
        return "formulated_feed_meal"
    raise AssertionError(row)


grouped = defaultdict(list)
for row in exceptions:
    grouped[gap_for(row)].append(row)
gap_rows = []
for gap_id, members in sorted(grouped.items()):
    model_area, proposal, rationale = gap_design[gap_id]
    gap_rows.append({
        "gap_id": gap_id, "model_area": model_area, "concept_count": len(members),
        "concept_ids": ";".join(row["concept_id"] for row in members),
        "representative_labels": ";".join(row["preferred_label"] for row in members[:5]),
        "proposed_model_response": proposal, "rationale": rationale,
        "recommendation": "design-family-model", "approval_status": "proposed",
        "reviewer": "", "review_date": "",
    })

cluster_recommendation = {
    "INGCLUSTER-0001": ("deprecate-replace-review", "AOM_001459", "Corrected labels and public mappings coincide; confirm downstream references before deprecating AOM_001898."),
    "INGCLUSTER-0002": ("hold-product-role-review", "", "Cotton records share label/taxon/Feedipedia but differ in product/by-product hierarchy and CPC scope."),
    "INGCLUSTER-0003": ("retain-distinct-integrity-specified", "", "Whole-grain ground maize explicitly retains integrity; generic grain-ground maize does not establish it."),
    "INGCLUSTER-0004": ("retain-distinct-integrity-specified", "", "Whole-grain maize explicitly retains integrity; generic maize grain does not establish it."),
    "INGCLUSTER-0005": ("retain-distinct-pending-composition", "", "Milk and whole milk differ by composition state, not physical form."),
    "INGCLUSTER-0006": ("retain-distinct-integrity-specified", "", "Whole-grain ground rice explicitly retains integrity; generic rice-grain ground does not establish it."),
    "INGCLUSTER-0007": ("retain-distinct-integrity-specified", "", "Whole-grain ground wheat explicitly retains integrity; generic wheat-grain ground does not establish it."),
}
cluster_rows = []
for row in clusters:
    action, retained_id, rationale = cluster_recommendation[row["cluster_id"]]
    cluster_rows.append({
        "cluster_id": row["cluster_id"], "concept_ids": row["concept_ids"],
        "preferred_labels": row["preferred_labels"], "recommendation": action,
        "retained_id_if_approved": retained_id, "rationale": rationale,
        "approval_status": "proposed", "reviewer": "", "review_date": "",
    })

preferred = {
    row["concept_id"]: row["label"] for row in labels
    if row["language"] == "en" and row["label_type"] == "pref"
}
first_occurrence = {}
for row in legacy:
    if row["AOM"] and row["L5"] == "Feed Ingredient":
        first_occurrence.setdefault(row["AOM"], row)
label_audit = []
for concept_id, row in sorted(first_occurrence.items()):
    governed = preferred[concept_id]
    if governed == row["Edge_Value"]:
        continue
    label_audit.append({
        "concept_id": concept_id, "legacy_edge_label": row["Edge_Value"],
        "governed_preferred_label": governed,
        "harmonization_source": "governed-preferred-label",
        "impact": (
            "decomposition-changed" if concept_id in {"AOM_000564", "AOM_006500"}
            else "identity-text-corrected"
        ),
        "status": "applied-to-workbench",
    })

summary = {
    "remaining_exceptions": len(exceptions), "model_gap_families": len(gap_rows),
    "remaining_signature_clusters": len(cluster_rows),
    "governed_label_overrides": len(label_audit),
    "high_confidence_deprecation_reviews": sum(
        row["recommendation"] == "deprecate-replace-review" for row in cluster_rows
    ),
    "automatic_identity_changes": 0,
}
OUT.mkdir(parents=True, exist_ok=True)
write(OUT / "ingredient_model_gap_families.csv", gap_rows, list(gap_rows[0]))
write(OUT / "ingredient_cluster_recommendations.csv", cluster_rows, list(cluster_rows[0]))
write(OUT / "governed_label_source_audit.csv", label_audit, list(label_audit[0]))
(OUT / "ingredient_model_gap_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(
    f"Consolidated {len(exceptions)} exceptions into {len(gap_rows)} model gaps; "
    f"reviewed {len(cluster_rows)} clusters and {len(label_audit)} governed-label overrides"
)
