#!/usr/bin/env python3
"""Build governed feed-material presentation, moisture, role, and label review."""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW = ROOT / "review/livestock-v26"
DATE = "2026-08-11"
REVIEWER = "Pete Steward"
GRINDING_ID = "AOM_000836"
DRYING_ID = "AOM_000843"
COMMINUTED_FORM_ID = "AOM_101125"
DRIED_CONDITION_ID = "AOM_101054"
BYPRODUCT_ROLE_ID = "AOM_101062"
BYPRODUCT_FAMILIES = {"Animal Byproduct", "Crop Byproduct"}
BLOOD_BYPRODUCTS = {"AOM_000536", "AOM_000537", "AOM_001616"}
GRINDING_PRESENTATION_HOLDS = {"AOM_002008", "AOM_001961", "AOM_006004"}
FACET_INPUTS = [
    "approved_feed_material_facets.csv",
    "approved_generated_feed_material_facets.csv",
    "approved_hard_tail_feed_material_facets.csv",
]


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


inventory = read(ROOT / "review/livestock-v5/ingredient_harmonization_inventory.csv")
labels = defaultdict(list)
for row in read(DATA / "labels.csv"):
    if row["language"] == "en":
        labels[row["concept_id"]].append(row["label"])

facets = []
for name in FACET_INPUTS:
    facets.extend(read(DATA / name))
facets_by_material = defaultdict(list)
for row in facets:
    facets_by_material[row["feed_material_id"]].append(row)

assertions = []
review_rows = []
for material in inventory:
    concept_id = material["concept_id"]
    current = facets_by_material[concept_id]
    has_grinding = any(
        row["target_property"] == "aom:processingMethod"
        and row["target_concept_id"] == GRINDING_ID
        for row in current
    )
    has_drying = any(
        row["target_property"] == "aom:processingMethod"
        and row["target_concept_id"] == DRYING_ID
        for row in current
    )
    existing_forms = sorted({
        row["target_label"] for row in current
        if row["target_property"] == "aom:presentationForm"
    })
    existing_moisture = sorted({
        row["target_label"] for row in current
        if row["target_property"] == "aom:moistureCondition"
    })
    existing_roles = sorted({
        row["target_label"] for row in current
        if row["target_property"] == "aom:productRole"
    })
    label_text = " | ".join(labels[concept_id]).casefold()
    has_meal_lexeme = "meal" in label_text.split()

    if existing_forms:
        form_disposition = "approved_existing_specific_form"
        form_target = ";".join(existing_forms)
        form_rationale = "Existing reviewed presentation-form assertion remains authoritative."
    elif concept_id in GRINDING_PRESENTATION_HOLDS:
        form_disposition = "held_grinding_bulk_state_conflict"
        form_target = ""
        form_rationale = (
            "Oil or molasses identity conflicts with automatic particulate-presentation inference; "
            "Grinding process assertion remains held for material-specific evidence review."
        )
    elif has_grinding:
        form_disposition = "approved_comminuted_form"
        form_target = "Comminuted particle form"
        form_rationale = (
            "Approved Grinding process supports broad comminuted-particle presentation; "
            "bulk consistency, moisture, particle size, and meal/powder subtype remain unspecified."
        )
        assertions.append({
            "feed_material_id": concept_id,
            "target_property": "aom:presentationForm",
            "target_concept_id": COMMINUTED_FORM_ID,
            "target_label": "Comminuted particle form",
            "rule_id": "STRUCT-FORM-GRINDING",
            "status": "approved-generated",
            "reviewer": REVIEWER,
            "review_date": DATE,
            "evidence": "data/livestock-staging/approved_generated_feed_material_facets.csv;docs/decisions/0042-feed-process-and-material-state-axes.md",
            "rationale": form_rationale,
        })
    elif has_meal_lexeme:
        form_disposition = "held_meal_without_process_evidence"
        form_target = ""
        form_rationale = (
            "Meal lexical evidence alone may identify a compound feed, material name, "
            "or processed form; no presentation-form assertion promoted."
        )
    else:
        form_disposition = "not_in_form_cohort"
        form_target = ""
        form_rationale = "No reviewed grinding result or governed presentation-form assertion."

    if existing_moisture:
        moisture_disposition = "approved_existing_moisture_condition"
        moisture_target = ";".join(existing_moisture)
        moisture_rationale = "Existing reviewed moisture-condition assertion remains authoritative."
    elif has_drying or concept_id == "AOM_000536":
        moisture_disposition = (
            "approved_dried_from_process"
            if has_drying else "approved_dried_from_blood_meal_evidence"
        )
        moisture_target = "Dried moisture condition"
        moisture_rationale = (
            "Approved Drying process supports dried moisture condition without implying one presentation form."
            if has_drying else
            "Feedipedia Blood meal evidence reports a dried blood product and high dry-matter content; drying route remains unspecified."
        )
        assertions.append({
            "feed_material_id": concept_id,
            "target_property": "aom:moistureCondition",
            "target_concept_id": DRIED_CONDITION_ID,
            "target_label": "Dried moisture condition",
            "rule_id": (
                "STRUCT-MOISTURE-DRYING"
                if has_drying else "STRUCT-MOISTURE-BLOOD-EVIDENCE"
            ),
            "status": "approved-generated",
            "reviewer": REVIEWER,
            "review_date": DATE,
            "evidence": (
                "data/livestock-staging/approved_generated_feed_material_facets.csv;docs/decisions/0042-feed-process-and-material-state-axes.md"
                if has_drying else
                "https://www.feedipedia.org/node/11574;docs/decisions/0042-feed-process-and-material-state-axes.md"
            ),
            "rationale": moisture_rationale,
        })
    else:
        moisture_disposition = "not_in_moisture_cohort"
        moisture_target = ""
        moisture_rationale = "No reviewed drying process or material-specific moisture evidence."

    in_byproduct_branch = material["ingredient_family"] in BYPRODUCT_FAMILIES
    explicit_blood = concept_id in BLOOD_BYPRODUCTS
    if existing_roles:
        role_disposition = "approved_existing_role"
        role_target = ";".join(existing_roles)
        role_rationale = "Existing reviewed product-role assertion remains authoritative."
    elif in_byproduct_branch or explicit_blood:
        role_disposition = (
            "approved_blood_byproduct" if explicit_blood
            else "approved_branch_to_role_translation"
        )
        role_target = "By-product role"
        role_rationale = (
            "Blood collected from slaughter is governed as animal by-product."
            if explicit_blood else
            "Canonical legacy by-product branch classification translated to explicit productRole; compatibility hierarchy retained."
        )
        assertions.append({
            "feed_material_id": concept_id,
            "target_property": "aom:productRole",
            "target_concept_id": BYPRODUCT_ROLE_ID,
            "target_label": "By-product role",
            "rule_id": (
                "STRUCT-ROLE-BLOOD" if explicit_blood
                else "STRUCT-ROLE-LEGACY-BYPRODUCT"
            ),
            "status": "approved-generated",
            "reviewer": REVIEWER,
            "review_date": DATE,
            "evidence": (
                "https://www.feedipedia.org/node/221;docs/decisions/0041-feed-material-structural-model.md"
                if explicit_blood else
                "data/livestock-staging/legacy_records.csv;docs/decisions/0041-feed-material-structural-model.md"
            ),
            "rationale": role_rationale,
        })
    else:
        role_disposition = "not_in_role_cohort"
        role_target = ""
        role_rationale = "No reviewed product-role evidence in this structural cohort."

    review_rows.append({
        "concept_id": concept_id,
        "preferred_label": material["preferred_label"],
        "ingredient_family": material["ingredient_family"],
        "has_approved_grinding": str(has_grinding).lower(),
        "has_approved_drying": str(has_drying).lower(),
        "meal_lexeme_present": str(has_meal_lexeme).lower(),
        "form_disposition": form_disposition,
        "form_target": form_target,
        "moisture_disposition": moisture_disposition,
        "moisture_target": moisture_target,
        "role_disposition": role_disposition,
        "role_target": role_target,
        "evidence": "docs/decisions/0041-feed-material-structural-model.md;docs/decisions/0042-feed-process-and-material-state-axes.md",
        "rationale": form_rationale + " " + moisture_rationale + " " + role_rationale,
    })

assert len(review_rows) == 1643
assert len({row["concept_id"] for row in review_rows}) == len(review_rows)
assert len({
    (row["feed_material_id"], row["target_property"], row["target_concept_id"])
    for row in assertions
}) == len(assertions)
assert not any(
    row["target_concept_id"] == "AOM_101126"
    for row in assertions
), "Meal form requires concept-specific evidence, never lexical bulk promotion"

mapping_rows = read(DATA / "mappings.csv")
evidence_rows = read(ROOT / "review/livestock-v9/feedipedia_definition_evidence.csv")
labelled_urls = {
    row["final_url"] or row["feedipedia_url"]
    for row in evidence_rows
    if row["http_status"] == "200" and row["page_heading"]
}
labelled_urls.update(
    row["target_uri"] for row in read(DATA / "approved_external_resource_labels.csv")
)
feedipedia_urls = sorted({
    row["target_uri"] for row in mapping_rows
    if row["target_scheme"] == "feedipedia" and row["target_uri"]
} | {
    row["target_uri"] for row in read(DATA / "approved_mapping_additions.csv")
    if row["target_scheme"] == "feedipedia" and row["target_uri"]
})
coverage_rows = [{
    "target_uri": uri,
    "disposition": "approved_label_available" if uri in labelled_urls else "held_label_not_cached",
    "evidence": (
        "review/livestock-v9/feedipedia_definition_evidence.csv;data/livestock-staging/approved_external_resource_labels.csv"
        if uri in labelled_urls else "data/livestock-staging/mappings.csv"
    ),
    "rationale": (
        "Feedipedia page heading is frozen and published as external-resource label."
        if uri in labelled_urls else
        "Mapping remains visible by URI; page heading awaits frozen retrieval evidence."
    ),
} for uri in feedipedia_urls]

write(
    DATA / "approved_structural_feed_material_facets.csv",
    list(assertions[0]),
    sorted(assertions, key=lambda row: (
        row["feed_material_id"], row["target_property"], row["target_concept_id"]
    )),
)
write(
    REVIEW / "feed_material_structural_review.csv",
    list(review_rows[0]),
    review_rows,
)
write(
    REVIEW / "feedipedia_external_label_coverage.csv",
    list(coverage_rows[0]),
    coverage_rows,
)

summary = {
    "reviewed_feed_materials": len(review_rows),
    "generated_assertions": len(assertions),
    "assertions_by_rule": dict(sorted(Counter(
        row["rule_id"] for row in assertions
    ).items())),
    "form_dispositions": dict(sorted(Counter(
        row["form_disposition"] for row in review_rows
    ).items())),
    "role_dispositions": dict(sorted(Counter(
        row["role_disposition"] for row in review_rows
    ).items())),
    "moisture_dispositions": dict(sorted(Counter(
        row["moisture_disposition"] for row in review_rows
    ).items())),
    "feedipedia_resource_labels": Counter(
        row["disposition"] for row in coverage_rows
    ),
}
(REVIEW / "feed_material_structural_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(summary, indent=2, sort_keys=True))
