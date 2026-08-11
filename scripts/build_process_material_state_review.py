#!/usr/bin/env python3
"""Build governed process-hierarchy and material-state review artifacts."""

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW = ROOT / "review/livestock-v27"
DATE = "2026-08-11"
REVIEWER = "Pete Steward"
EVIDENCE = "docs/decisions/0042-feed-process-and-material-state-axes.md"
PARTICLE_REDUCTION = "AOM_101129"
SEPARATION = "AOM_101130"
SHAPING = "AOM_101131"
BULK_ROOT = "AOM_101132"
MOISTURE_ROOT = "AOM_101133"
GRINDING_PRESENTATION_HOLDS = {
    "AOM_002008": "Oil identity conflicts with automatic particulate-presentation inference.",
    "AOM_001961": "Crude oil identity conflicts with automatic particulate-presentation inference.",
    "AOM_006004": "Molasses identity conflicts with automatic particulate-presentation inference.",
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


hierarchy_specs = [
    ("STATE-FRESH-MOISTURE", "AOM_001510", "AOM_000842", MOISTURE_ROOT, "Fresh is a material condition, not a moisture-removal process."),
    ("PROCESS-CRACKING-PARTICLE", "AOM_101090", "AOM_000845", PARTICLE_REDUCTION, "Cracking primarily reduces particle dimensions."),
    ("PROCESS-PRESSING-SEPARATION", "AOM_101070", "AOM_000845", SEPARATION, "Pressing separates liquid and retained fractions through pressure."),
    ("PROCESS-THRESHING-SEPARATION", "AOM_101073", "AOM_000845", SEPARATION, "Threshing separates grain or seed from other plant material."),
    ("PROCESS-RENDERING-THERMAL", "AOM_101128", "AOM_000845", "AOM_000826", "Rendering uses governed heat treatment and separation."),
    ("PROCESS-CHOPPING-PARTICLE", "AOM_000834", "", PARTICLE_REDUCTION, "Chopping cuts material into smaller pieces."),
    ("PROCESS-CRUSHING-PARTICLE", "AOM_000835", "", PARTICLE_REDUCTION, "Crushing reduces particle dimensions using pressure."),
    ("PROCESS-GRINDING-PARTICLE", "AOM_000836", "", PARTICLE_REDUCTION, "Grinding or milling reduces particle size in dry or wet processing."),
    ("PROCESS-FLOUR-MILLING-PARTICLE", "AOM_000838", "", PARTICLE_REDUCTION, "Flour milling includes particle reduction."),
    ("PROCESS-FLOUR-MILLING-SEPARATION", "AOM_000838", "", SEPARATION, "Flour milling separates flour, bran, and intermediate fractions."),
    ("PROCESS-DECORTICATION-SEPARATION", "AOM_003097", "", SEPARATION, "Decortication separates an outer covering from retained material."),
    ("PROCESS-PELLETING-SHAPING", "AOM_000840", "", SHAPING, "Pelleting agglomerates material through a die."),
    ("PROCESS-EXTRUSION-MECHANICAL", "AOM_000833", "", "AOM_000837", "Extrusion is thermo-mechanical."),
    ("PROCESS-EXTRUSION-SHAPING", "AOM_000833", "", SHAPING, "Extrusion shapes material through a die."),
    ("PROCESS-CRACKING-MECHANICAL", "AOM_101090", "", "AOM_000837", "Cracking uses mechanical force."),
    ("PROCESS-PRESSING-MECHANICAL", "AOM_101070", "", "AOM_000837", "Pressing uses mechanical pressure."),
    ("PROCESS-THRESHING-MECHANICAL", "AOM_101073", "", "AOM_000837", "Threshing uses mechanical separation."),
    ("PROCESS-RENDERING-SEPARATION", "AOM_101128", "", SEPARATION, "Rendering separates stabilized protein, fat, and water fractions."),
]
hierarchy_rows = [{
    "case_id": case_id,
    "child_id": child_id,
    "remove_parent_id": remove_parent_id,
    "add_parent_id": add_parent_id,
    "status": "approved",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": EVIDENCE,
    "rationale": rationale,
} for case_id, child_id, remove_parent_id, add_parent_id, rationale in hierarchy_specs]
write(
    DATA / "approved_hierarchy_revisions.csv",
    list(hierarchy_rows[0]),
    hierarchy_rows,
)

result_rows = [
    {
        "case_id": "PROCESS-RESULT-GRINDING-COMMINUTED",
        "process_concept_id": "AOM_000836",
        "relation_property": "aom:mayResultInPresentationForm",
        "result_concept_id": "AOM_101125",
        "result_class": "aom:IngredientPresentationForm",
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": EVIDENCE,
        "rationale": "Grinding can produce a comminuted particle presentation without establishing bulk consistency, moisture, or particle-size class.",
    },
    {
        "case_id": "PROCESS-RESULT-DRYING-DRIED",
        "process_concept_id": "AOM_000843",
        "relation_property": "aom:mayResultInMoistureCondition",
        "result_concept_id": "AOM_101054",
        "result_class": "aom:IngredientMoistureCondition",
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": EVIDENCE,
        "rationale": "Drying reduces moisture and can result in dried condition without establishing presentation form.",
    },
]
write(
    DATA / "approved_process_state_relations.csv",
    list(result_rows[0]),
    result_rows,
)

facet_specs = [
    ("AOM_101020", "Ingredient presentation forms", "presentation_form", "retained_root", "Presentation axis excludes moisture and bulk consistency."),
    ("AOM_101049", "Block form", "presentation_form", "retained_value", "Block is shaped presentation."),
    ("AOM_101050", "Lick form", "presentation_form", "retained_value", "Lick is shaped presentation."),
    ("AOM_101051", "Powder form", "presentation_form", "retained_value", "Powder is particle presentation; exact threshold remains unspecified."),
    ("AOM_101052", "Cake form", "presentation_form", "retained_value", "Cake is coherent presentation, often but not universally produced by pressing."),
    ("AOM_101053", "Flake form", "presentation_form", "retained_value", "Flake is shaped presentation."),
    ("AOM_101054", "Dried moisture condition", "moisture_condition", "moved_axis", "Dried describes moisture condition, not shape."),
    ("AOM_101075", "Mixed presentation", "presentation_form", "retained_value", "Mixed describes presentation; composition remains separate."),
    ("AOM_101076", "Whole form", "presentation_form", "retained_value", "Whole describes intact presentation; material integrity remains independently governed."),
    ("AOM_101077", "Liquid consistency", "bulk_consistency", "moved_axis", "Liquid describes bulk flow consistency."),
    ("AOM_101078", "Pulp consistency", "bulk_consistency", "moved_axis", "Pulp describes moist fibrous or cellular bulk consistency."),
    ("AOM_101108", "Pellet form", "presentation_form", "retained_value", "Pellet is shaped presentation."),
    ("AOM_101118", "Slurry consistency", "bulk_consistency", "moved_axis", "Slurry requires dispersed solids in a liquid continuous phase."),
    ("AOM_101125", "Comminuted particle form", "presentation_form", "renamed_scope", "Comminuted particles do not entail dry solid bulk state."),
    ("AOM_101126", "Meal form", "presentation_form", "retained_value", "Meal does not globally entail drying."),
    (BULK_ROOT, "Ingredient bulk consistencies", "bulk_consistency", "new_root", "Separates bulk flow and dispersion semantics."),
    (MOISTURE_ROOT, "Ingredient moisture conditions", "moisture_condition", "new_root", "Separates moisture semantics."),
    ("AOM_001510", "Fresh moisture condition", "moisture_condition", "reclassified_legacy", "Fresh is condition rather than dehydration process."),
]
facet_rows = [{
    "concept_id": concept_id,
    "preferred_label": label,
    "review_axis": axis,
    "disposition": disposition,
    "status": "approved",
    "evidence": EVIDENCE,
    "rationale": rationale,
} for concept_id, label, axis, disposition, rationale in facet_specs]
write(REVIEW / "material_state_axis_review.csv", list(facet_rows[0]), facet_rows)

material_inputs = [
    "approved_feed_material_facets.csv",
    "approved_generated_feed_material_facets.csv",
    "approved_hard_tail_feed_material_facets.csv",
    "approved_structural_feed_material_facets.csv",
]
assertions = []
for name in material_inputs:
    assertions.extend(read(DATA / name))
labels = {
    row["concept_id"]: row["label"]
    for row in read(DATA / "labels.csv")
    if row["language"] == "en" and row["label_type"] == "pref"
}
grinding_ids = sorted({
    row["feed_material_id"] for row in assertions
    if row["target_property"] == "aom:processingMethod"
    and row["target_concept_id"] == "AOM_000836"
})
contradiction_rows = [{
    "feed_material_id": concept_id,
    "preferred_label": labels[concept_id],
    "disposition": (
        "hold_particulate_presentation_conflict"
        if concept_id in GRINDING_PRESENTATION_HOLDS
        else "no_identified_bulk_state_conflict"
    ),
    "status": "hold" if concept_id in GRINDING_PRESENTATION_HOLDS else "reviewed",
    "evidence": EVIDENCE,
    "rationale": GRINDING_PRESENTATION_HOLDS.get(
        concept_id,
        "Grinding supports particle-size reduction but does not establish moisture condition or bulk consistency.",
    ),
} for concept_id in grinding_ids]
write(REVIEW / "grinding_state_contradiction_review.csv", list(contradiction_rows[0]), contradiction_rows)

summary = {
    "hierarchy_revisions": len(hierarchy_rows),
    "process_result_relations": len(result_rows),
    "reviewed_material_state_concepts": len(facet_rows),
    "reviewed_grinding_materials": len(contradiction_rows),
    "grinding_dispositions": dict(sorted(Counter(
        row["disposition"] for row in contradiction_rows
    ).items())),
    "unresolved_cases": sorted(GRINDING_PRESENTATION_HOLDS),
}
REVIEW.mkdir(parents=True, exist_ok=True)
(REVIEW / "process_material_state_summary.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(summary, indent=2, sort_keys=True))
