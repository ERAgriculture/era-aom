#!/usr/bin/env python3
"""Build machine-readable semantic-model dispositions for deferred cases."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "review/livestock-v2/schema_remodeling_candidates.csv"
OUTPUT = ROOT / "review/livestock-v2/semantic_model_dispositions.csv"

with SOURCE.open(encoding="utf-8", newline="") as handle:
    candidates = list(csv.DictReader(handle))

parity_targets = {
    "AOM_002501": ("aom:ParityStatus", "migrate_to_parity_scheme"),
    "AOM_002502": ("aom:ParityStatus", "migrate_to_parity_scheme"),
    "AOM_002503": ("evidence_required", "hold_ambiguous_reproductive_status"),
    "AOM_002504": ("aom:GestationalStage", "migrate_to_gestational_stage_scheme"),
    "AOM_002505": ("aom:GestationalStage", "migrate_to_gestational_stage_scheme"),
    "AOM_002506": ("aom:GestationalStage", "migrate_to_gestational_stage_scheme"),
    "AOM_002507": ("evidence_required", "hold_nonstandard_fourth_trimester"),
}

rows = []
for candidate in candidates:
    model = candidate["recommended_model"]
    concept_id = candidate["concept_id"]
    if model in {"data_property_or_schema_field", "data_property_or_reference", "taxon_reference_property"}:
        target_layer = "domain_data"
        target_type = {
            "AOM_000531": "aom:ingredientName",
            "AOM_000532": "aom:ingredientPart",
            "AOM_000533": "aom:sourceTaxon",
            "AOM_000535": "aom:ingredientSource",
        }[concept_id]
        disposition = "replace_concept_usage_with_property"
        phase = "2"
        compatibility = "retain_legacy_concept_deprecated_after_consumer_cutover"
    elif model == "quantitative_schema_field":
        target_layer = "observation_data"
        target_type = "aom:QuantitativeObservation+sosa:observedProperty+qudt:QuantityValue"
        disposition = "retain_as_observable_property_and_migrate_values"
        phase = "2"
        compatibility = "retain_concept_uri_as_observed_property"
    elif model in {
        "processed_feed_material_classification", "processed_whole_product_classification",
        "product_byproduct_classification", "feed_material_classification",
    }:
        target_layer = "domain_data_and_vocabulary"
        target_type = "aom:FeedMaterial+sourceTaxon+ingredientPart+processingMethod+productRole"
        disposition = "retain_concept_add_facets_pending_reclassification"
        phase = "3"
        compatibility = "retain_concept_uri_and_legacy_broader_until_reviewed_reparenting"
    elif model == "separate_parity_and_gestational_stage_dimensions":
        target_layer = "controlled_vocabulary"
        target_type, disposition = parity_targets[concept_id]
        phase = "3"
        compatibility = "retain_concept_uri; change hierarchy only through governed migration"
    else:
        raise ValueError(f"Unhandled semantic model: {model}")
    if concept_id == "AOM_000534":
        target_layer = "domain_data"
        target_type = "aom:IngredientComponent+aom:ingredientProportion+qudt:QuantityValue"
        disposition = "replace_concept_usage_with_quantified_component_property"
        phase = "2"
        compatibility = "retain_legacy_concept_deprecated_after_consumer_cutover"
    rows.append({
        "concept_id": concept_id,
        "current_label": candidate["current_label"],
        "target_layer": target_layer,
        "target_type": target_type,
        "disposition": disposition,
        "migration_phase": phase,
        "backward_compatibility": compatibility,
        "status": "design-approved",
        "reviewer": "Pete Steward",
        "review_date": "2026-08-04",
        "source_case": candidate["trigger_case"],
        "rationale": candidate["rationale"],
    })

assert len(rows) == 50
assert len({row["concept_id"] for row in rows}) == 50
with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
print(f"Built {len(rows)} semantic-model dispositions")
