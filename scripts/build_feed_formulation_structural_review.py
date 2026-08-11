#!/usr/bin/env python3
"""Build governed feed/formulation, descriptor, and process structural review."""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW = ROOT / "review/livestock-v28"
DATE = "2026-08-11"
REVIEWER = "Pete Steward"
ADR = "docs/decisions/0043-feed-formulation-and-descriptor-model.md"
EU_FEED = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009R0767"
EU_PROCESS = "https://eur-lex.europa.eu/eli/reg/2013/68/oj/eng"
CDC_AUTOCLAVE = "https://www.cdc.gov/infection-control/hcp/disinfection-sterilization/steam-sterilization.html"
BREWHOUSE = "https://www.brewersassociation.org/resource-hub/brewhouse/"
MEGALAC = "https://www.megalac.com/products/2-megalac"
ELANCOBAN = "https://efsa.onlinelibrary.wiley.com/doi/10.2903/j.efsa.2026.10123"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def fields(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return csv.DictReader(handle).fieldnames


def write(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def upsert(path, key, additions):
    rows = read(path)
    addition_keys = {row[key] for row in additions}
    assert len(addition_keys) == len(additions)
    rows = [row for row in rows if row[key] not in addition_keys]
    write(path, fields(path), rows + additions)


formulation_ids = {
    "AOM_000798", "AOM_002110", "AOM_000799", "AOM_000800",
    "AOM_000801", "AOM_001494", "AOM_002097", "AOM_001493",
    "AOM_001495", "AOM_003495", "AOM_000805", "AOM_003995",
    "AOM_000803", "AOM_002109", "AOM_002098", "AOM_001492",
    "AOM_003870", "AOM_003991", "AOM_001498", "AOM_001496",
    "AOM_001502", "AOM_000804", "AOM_001501",
}
formulation_labels = {
    "AOM_000798": "Beef Survival Meal",
    "AOM_002110": "Chick Mash",
    "AOM_000799": "Commercial Feed",
    "AOM_000800": "Concentrate",
    "AOM_000801": "Dairy Meal",
    "AOM_001494": "Finisher Diet",
    "AOM_002097": "Fish Mix",
    "AOM_001493": "Growers Concentrate",
    "AOM_001495": "Growers Diet",
    "AOM_003495": "Growers Premix",
    "AOM_000805": "Imported Concentrate",
    "AOM_003995": "Lamb and Ewe Pellet",
    "AOM_000803": "Layer Concentrate",
    "AOM_002109": "Layer's Meal",
    "AOM_002098": "Poultry Feed",
    "AOM_001492": "Protein-Mineral Concentrate",
    "AOM_003870": "Rabbit Pellet",
    "AOM_003991": "Ruminant Premix",
    "AOM_001498": "Sheep Meal",
    "AOM_001496": "Starter Diet",
    "AOM_001502": "Swine Mix",
    "AOM_000804": "Total Mixed Ration",
    "AOM_001501": "AquaNutro Abalone Grower",
}
assert formulation_ids == set(formulation_labels)
formulation_parents = {
    "AOM_001493": "AOM_000800",
    "AOM_000805": "AOM_000800",
    "AOM_000803": "AOM_000800",
    "AOM_001492": "AOM_000800",
}

classification_rows = [{
    "concept_id": "AOM_001491",
    "preferred_label": "Formulated feeds",
    "disposition": "category",
    "semantic_class": "",
    "target_parent_id": "AOM_000328",
    "status": "approved",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": f"{EU_FEED};{ADR}",
    "rationale": "Feed-material ingredients and formulated or compound feeds require separate browse roots and semantic classes.",
}]
classification_rows += [{
    "concept_id": concept_id,
    "preferred_label": formulation_labels[concept_id],
    "disposition": "feed_formulation",
    "semantic_class": "aom:FeedFormulation",
    "target_parent_id": formulation_parents.get(concept_id, "AOM_001491"),
    "status": "approved",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": f"era_master_sheet.xlsx#AOM;{EU_FEED};{ADR}",
    "rationale": "Workbook identity denotes a diet, ration, compound feed, premix, concentrate, mash, mix, meal, or feed product rather than one feed material.",
} for concept_id in sorted(formulation_ids)]
classification_rows += [
    {
        "concept_id": "AOM_001497", "preferred_label": "Megalac",
        "disposition": "feed_material", "semantic_class": "aom:FeedMaterial",
        "target_parent_id": "AOM_006334", "status": "approved",
        "reviewer": REVIEWER, "review_date": DATE, "evidence": MEGALAC,
        "rationale": "Manufacturer identifies Megalac as rumen-protected fat supplement, not a complete diet.",
    },
    {
        "concept_id": "AOM_001579", "preferred_label": "Elancoban",
        "disposition": "feed_additive", "semantic_class": "aom:FeedAdditive",
        "target_parent_id": "AOM_004433", "status": "approved",
        "reviewer": REVIEWER, "review_date": DATE, "evidence": ELANCOBAN,
        "rationale": "EFSA identifies Elancoban G200 as feed additive containing monensin sodium.",
    },
    {
        "concept_id": "AOM_001870", "preferred_label": "Prime Gluten 60",
        "disposition": "feed_material", "semantic_class": "aom:FeedMaterial",
        "target_parent_id": "AOM_001571", "status": "approved",
        "reviewer": REVIEWER, "review_date": DATE, "evidence": f"era_master_sheet.xlsx#AOM;{ADR}",
        "rationale": "Named protein feed product remains a material; formulation composition is not established.",
    },
    {
        "concept_id": "AOM_006154", "preferred_label": "Prime Gluten 60 Ground",
        "disposition": "feed_material", "semantic_class": "aom:FeedMaterial",
        "target_parent_id": "AOM_001870", "status": "approved",
        "reviewer": REVIEWER, "review_date": DATE, "evidence": f"era_master_sheet.xlsx#AOM;{ADR}",
        "rationale": "Ground presentation narrows material identity and does not create a formulated feed.",
    },
    {
        "concept_id": "AOM_001500", "preferred_label": "ACTIPAL HP 1",
        "disposition": "hold_product_class", "semantic_class": "",
        "target_parent_id": "AOM_000781", "status": "hold",
        "reviewer": REVIEWER, "review_date": DATE, "evidence": f"era_master_sheet.xlsx#AOM;{ADR}",
        "rationale": "Workbook preserves product identity but does not establish feed-material, additive, or formulation class.",
    },
]
assert len(classification_rows) == 29
assert Counter(row["disposition"] for row in classification_rows) == {
    "feed_formulation": 23, "feed_material": 3, "category": 1,
    "feed_additive": 1, "hold_product_class": 1,
}
write(
    DATA / "approved_feed_formulation_classifications.csv",
    list(classification_rows[0]), classification_rows,
)

new_concept_path = DATA / "approved_new_concepts.csv"
new_concepts = read(new_concept_path)
feed_material_root = next(row for row in new_concepts if row["concept_id"] == "AOM_100850")
feed_material_root.update({
    "preferred_label": "Feed materials",
    "scope_note": "Products or substances used directly as feed or as materials in formulated feeds; formulations and additives remain separately classified.",
    "derived_path": "Management/Livestock Management/Feed Characteristic/Feed materials",
    "evidence": f"{EU_FEED};{ADR}",
    "rationale": "Separates feed materials from formulated feeds while retaining explicit source, component, process, form, composition, and role facets.",
})
write(new_concept_path, fields(new_concept_path), new_concepts)

label_correction_path = DATA / "approved_label_corrections.csv"
label_corrections = [
    {
        "case_id": "FEED-MODEL-FORMULATED-ROOT", "concept_id": "AOM_001491",
        "old_label": "Preformulated Feed", "new_label": "Formulated feeds", "language": "en",
        "reviewer": REVIEWER, "review_date": DATE, "evidence": f"{EU_FEED};{ADR}",
        "rationale": "Names formulation class without implying timing or treating diets as feed-material ingredients.",
    },
    {
        "case_id": "FEED-PROCESS-SPROUTING", "concept_id": "AOM_003098",
        "old_label": "Sprouted", "new_label": "Sprouting", "language": "en",
        "reviewer": REVIEWER, "review_date": DATE, "evidence": f"{EU_PROCESS};{ADR}",
        "rationale": "Uses process noun for existing process identity before retiring duplicate generated concept.",
    },
]
existing_label_corrections = read(label_correction_path)
correction_ids = {row["concept_id"] for row in label_corrections}
existing_label_corrections = [
    row for row in existing_label_corrections if row["concept_id"] not in correction_ids
]
write(label_correction_path, fields(label_correction_path), existing_label_corrections + label_corrections)

label_additions = [
    ("AOM_100850", "Feed ingredient"),
    ("AOM_101019", "Ingredient anatomical parts"),
    ("AOM_101020", "Ingredient presentation forms"),
    ("AOM_101022", "Ingredient product roles"),
    ("AOM_101023", "Ingredient constituents"),
    ("AOM_101068", "Brewing"),
    ("AOM_101076", "Whole form"),
    ("AOM_101099", "Steeping"),
    ("AOM_101109", "Material integrity values"),
    ("AOM_101110", "Whole grain"),
    ("AOM_101130", "Feed separation and fractionation processes"),
    ("AOM_101132", "Ingredient bulk consistencies"),
    ("AOM_101133", "Ingredient moisture conditions"),
]
label_addition_rows = [{
    "case_id": f"FEED-MODEL-ALIAS-{concept_id}",
    "concept_id": concept_id, "language": "en", "label_type": "alt",
    "label": label, "status": "approved", "reviewer": REVIEWER,
    "review_date": DATE, "evidence": ADR,
    "rationale": "Preserves prior public-facing generated label after structural relabeling.",
} for concept_id, label in label_additions]
write(DATA / "approved_label_additions.csv", list(label_addition_rows[0]), label_addition_rows)

hierarchy_specs = [
    ("FEED-MODEL-FORMULATED-ROOT", "AOM_001491", "AOM_100850", "AOM_000328", "Separate formulations from feed materials."),
    ("FEED-MODEL-ACTIPAL-HOLD", "AOM_001500", "AOM_001491", "AOM_000781", "Remove unverified branded product from formulation branch while product class remains held."),
    ("FEED-MODEL-ELANCOBAN", "AOM_001579", "AOM_001491", "AOM_004433", "Place feed additive with anti-coccidia category."),
    ("FEED-MODEL-MEGALAC", "AOM_001497", "AOM_001491", "AOM_006334", "Place rumen-protected fat supplement with protected fat materials."),
    ("FEED-MODEL-PRIME-GLUTEN", "AOM_001870", "AOM_001491", "AOM_001571", "Place named protein material with protein supplements."),
    ("FEED-MODEL-DEPRECATED-WHOLE-SILAGE", "AOM_006072", "AOM_001313", "AOM_000648", "Deprecated whole-crop silage duplicate must not remain under whole-grain maize."),
    ("PROCESS-HEATING-THERMAL", "AOM_101096", "AOM_000845", "AOM_000826", "Heating is thermal processing."),
    ("PROCESS-AUTOCLAVING-HEATING", "AOM_101088", "AOM_000845", "AOM_101096", "Autoclaving uses steam, pressure, temperature, and time and is a heating process."),
    ("PROCESS-DEFATTING-SEPARATION", "AOM_101069", "AOM_000845", "AOM_101130", "Defatting removes a fat fraction from retained material."),
    ("PROCESS-EXTRACTION-SEPARATION", "AOM_101072", "AOM_000845", "AOM_101130", "Solvent extraction removes a selected fraction."),
    ("PROCESS-DISTILLATION-SEPARATION", "AOM_101124", "AOM_000845", "AOM_101130", "Distillation fractionates liquids."),
    ("PROCESS-DISTILLATION-THERMAL", "AOM_101124", "", "AOM_000826", "Distillation uses boiling and condensation."),
    ("PROCESS-BREWHOUSE-SEPARATION", "AOM_101068", "AOM_000845", "AOM_101130", "Lautering and related brewhouse operations separate wort and spent grain."),
    ("PROCESS-BREWHOUSE-THERMAL", "AOM_101068", "", "AOM_000826", "Mashing and wort boiling include governed thermal operations; fermentation remains separate."),
]
hierarchy_rows = [{
    "case_id": case_id, "child_id": child_id,
    "remove_parent_id": remove_parent_id, "add_parent_id": add_parent_id,
    "status": "approved", "reviewer": REVIEWER, "review_date": DATE,
    "evidence": (
        CDC_AUTOCLAVE if child_id == "AOM_101088" else
        BREWHOUSE if child_id == "AOM_101068" else
        EU_PROCESS if child_id.startswith("AOM_101") else ADR
    ),
    "rationale": rationale,
} for case_id, child_id, remove_parent_id, add_parent_id, rationale in hierarchy_specs]
hierarchy_path = DATA / "approved_hierarchy_revisions.csv"
existing_hierarchy = [
    row for row in read(hierarchy_path)
    if not row["case_id"].startswith(("FEED-MODEL-", "PROCESS-HEATING-", "PROCESS-AUTOCLAVING-", "PROCESS-DEFATTING-", "PROCESS-EXTRACTION-", "PROCESS-DISTILLATION-", "PROCESS-BREWHOUSE-"))
]
write(hierarchy_path, fields(hierarchy_path), existing_hierarchy + hierarchy_rows)
assert len(existing_hierarchy + hierarchy_rows) == 32

facet_path = DATA / "approved_ingredient_facet_concepts.csv"
facet_rows = read(facet_path)
for row in facet_rows:
    if row["target_property"] == "aom:ingredientConstituent":
        row["target_property"] = "aom:primaryConstituent"
        row["value_class"] = "aom:ChemicalConstituent"
write(facet_path, fields(facet_path), facet_rows)

material_tables = [
    "approved_feed_material_facets.csv",
    "approved_generated_feed_material_facets.csv",
    "approved_hard_tail_feed_material_facets.csv",
    "approved_structural_feed_material_facets.csv",
]
relabelled_targets = {
    "AOM_101068": "Brewhouse processing",
    "AOM_101076": "Intact presentation",
    "AOM_101110": "Whole-grain integrity",
    "AOM_101130": "Feed separation processes",
}
constituent_review = []
for name in material_tables:
    path = DATA / name
    rows = read(path)
    for row in rows:
        if row["target_concept_id"] in relabelled_targets:
            row["target_label"] = relabelled_targets[row["target_concept_id"]]
        is_full_fat = (
            row["feed_material_id"] in {"AOM_000611", "AOM_001317"}
            and row["target_property"] == "aom:compositionState"
            and row["target_concept_id"] == "AOM_101134"
        )
        if row["target_property"] not in {
            "aom:ingredientConstituent", "aom:primaryConstituent"
        } and not is_full_fat:
            continue
        before_target = "AOM_101066" if is_full_fat else row["target_concept_id"]
        if before_target == "AOM_101066" and row["feed_material_id"] in {"AOM_000611", "AOM_001317"}:
            row["target_property"] = "aom:compositionState"
            row["target_concept_id"] = "AOM_101134"
            row["target_label"] = "Full-fat composition"
            disposition = "composition_state"
            rationale = "Full-fat denotes retained native fat, not identity as fat constituent or measured concentration."
        else:
            row["target_property"] = "aom:primaryConstituent"
            disposition = "primary_chemical_constituent"
            rationale = "Oil, starch, ash, or protein is identity-bearing chemical constituent, not formulation ingredient."
        constituent_review.append({
            "feed_id": row["feed_material_id"], "source_table": name,
            "prior_property": "aom:ingredientConstituent",
            "prior_target_id": before_target, "disposition": disposition,
            "approved_property": row["target_property"],
            "approved_target_id": row["target_concept_id"],
            "status": "approved", "evidence": ADR, "rationale": rationale,
        })
    write(path, fields(path), rows)
assert len(constituent_review) == 25
assert Counter(row["disposition"] for row in constituent_review) == {
    "primary_chemical_constituent": 23, "composition_state": 2,
}

definition_path = DATA / "approved_definition_overrides.csv"
definition_rows = []


def definition(identifier, text, evidence=ADR):
    definition_rows.append({
        "concept_id": identifier, "language": "en", "definition": text,
        "definition_method": "feed_structure_definition_replacement",
        "status": "approved", "reviewer": REVIEWER, "review_date": DATE,
        "evidence": evidence,
        "rationale": "Definition aligned with reviewed feed/formulation and independent descriptor model.",
    })


definition("AOM_100850", "A category for feed materials used directly for oral animal feeding or as materials in formulated feeds; source, component, process, form, integrity, composition, and product role require explicit assertions.", EU_FEED)
definition("AOM_001491", "A category for formulated feeds, including diets, rations, compound feeds, premixes, concentrates, mashes, and mixes; component feed materials and their proportions require separate assertions.", EU_FEED)
for concept_id in sorted(formulation_ids):
    definition(concept_id, f"A formulated feed represented in AOM as “{formulation_labels[concept_id]}”. Ingredient composition, proportions, target species or stage, completeness, and nutritional properties are unspecified unless separately asserted.", f"era_master_sheet.xlsx#AOM;{EU_FEED}")
definition("AOM_001500", "A named feed-related product represented in the source workbook as “ACTIPAL HP 1”; available evidence does not establish whether it is a feed material, formulation, or additive.")
definition("AOM_001497", "A named rumen-protected fat supplement represented as a feed material; formulation use and feeding rate do not make it a complete diet.", MEGALAC)
definition("AOM_001579", "A feed additive containing monensin sodium and used for coccidiosis control under authorized conditions.", ELANCOBAN)
definition("AOM_001870", "A named protein feed material represented as “Prime Gluten 60”; detailed composition and manufacturing process are unspecified.")
definition("AOM_006154", "Prime Gluten 60 feed material with governed grinding process and comminuted-particle presentation; moisture condition and particle-size threshold are unspecified.")
definition("AOM_003098", "A process in which grains or seeds are moistened and germinated under controlled conditions to initiate sprouting.", EU_PROCESS)
definition("AOM_101068", "Mashing, lautering, boiling, or related brewhouse operations represented separately from microbial fermentation.", BREWHOUSE)
definition("AOM_101099", "Moistening and softening feed materials, also called steeping, to facilitate water uptake, coat removal, cooking, germination, or reduction of some antinutritional factors.", EU_PROCESS)
definition("AOM_101130", "Feed processes whose objective includes separating components or fractions of a source material.", EU_PROCESS)
definition("AOM_101019", "Biological structures represented as components of feed materials.")
definition("AOM_101020", "Shapes and particle presentations applicable to feed materials or formulated feeds independently of moisture and bulk consistency.")
definition("AOM_101022", "Economic or production roles of feed materials, including product and by-product roles.")
definition("AOM_101023", "Chemical substances or chemically defined fractions that primarily characterize feed materials; these are not ingredient components of formulated feeds.")
definition("AOM_101076", "Presentation in which a feed item remains visibly intact; whole-crop or whole-grain integrity is not implied.")
definition("AOM_101109", "Compositional or anatomical integrity retained by a feed material independently of particle presentation and processing.")
definition("AOM_101110", "Retention of characteristic anatomical fractions of a cereal grain independently of particle-size reduction.")
definition("AOM_101120", "Protein represented as a primary chemical constituent of a feed material, not as an ingredient component of a formulated feed.")
definition("AOM_101132", "Bulk flow and dispersion consistencies applicable to feed materials or formulated feeds independently of particle presentation and moisture condition.")
definition("AOM_101133", "Qualitative moisture conditions applicable to feed materials or formulated feeds independently of particle presentation and bulk consistency.")
upsert(definition_path, "concept_id", definition_rows)

raw_labels = read(DATA / "labels.csv")
preferred = {
    row["concept_id"]: row["label"] for row in raw_labels
    if row["language"] == "en" and row["label_type"] == "pref"
}
preferred.update({row["concept_id"]: row["preferred_label"] for row in new_concepts})
preferred.update({row["concept_id"]: row["new_label"] for row in label_corrections})
assertion_counts = Counter()
for name in material_tables:
    for row in read(DATA / name):
        assertion_counts[row["target_concept_id"]] += 1
descriptor_rows = [{
    "concept_id": row["concept_id"], "preferred_label": row["preferred_label"],
    "facet": row["facet"], "target_property": row["target_property"],
    "value_class": row["value_class"], "concept_role": row["concept_role"],
    "material_assertion_count": assertion_counts[row["concept_id"]],
    "disposition": (
        "renamed_or_rescoped" if row["concept_id"] in {
            "AOM_101019", "AOM_101020", "AOM_101022", "AOM_101023",
            "AOM_101068", "AOM_101076", "AOM_101109", "AOM_101110",
            "AOM_101130", "AOM_101132", "AOM_101133",
        } else "new_composition_state" if row["concept_id"] == "AOM_101134"
        else "retained"
    ),
    "status": "approved", "evidence": row["evidence"],
} for row in facet_rows]

approved_parents = defaultdict(list)
for row in hierarchy_rows:
    approved_parents[row["child_id"]].append(row["add_parent_id"])
process_rows = [{
    "concept_id": row["concept_id"], "preferred_label": row["preferred_label"],
    "material_assertion_count": assertion_counts[row["concept_id"]],
    "approved_parent_additions": ";".join(sorted(approved_parents[row["concept_id"]])),
    "disposition": (
        "canonical_reuse_target" if row["concept_id"] in {"AOM_003098", "AOM_101099"}
        else "renamed_or_reparented" if row["concept_id"] in approved_parents or row["concept_id"] in {"AOM_101068", "AOM_101130"}
        else "retained"
    ),
    "status": "approved", "evidence": ADR,
} for row in facet_rows if row["facet"] == "processing_method"]

whole_ids = sorted({
    row["concept_id"] for row in raw_labels if "whole" in row["label"].casefold()
})
whole_rows = [{
    "concept_id": concept_id, "preferred_label": preferred[concept_id],
    "disposition": {
        "AOM_101076": "rename_intact_presentation",
        "AOM_101110": "rename_whole_grain_integrity",
        "AOM_006072": "deprecated_duplicate_reparented_from_whole_grain",
    }.get(concept_id, "retained_distinct_scope"),
    "status": "approved", "evidence": ADR,
    "rationale": "Whole-crop, whole-grain integrity, intact presentation, whole-milk composition, and lexical aliases remain separate reviewed scopes.",
} for concept_id in whole_ids]
assert len(whole_rows) == 12

write(REVIEW / "feed_formulation_review.csv", list(classification_rows[0]), classification_rows)
write(REVIEW / "chemical_constituent_assertion_review.csv", list(constituent_review[0]), constituent_review)
write(REVIEW / "feed_descriptor_review.csv", list(descriptor_rows[0]), descriptor_rows)
write(REVIEW / "feed_process_review.csv", list(process_rows[0]), process_rows)
write(REVIEW / "whole_term_review.csv", list(whole_rows[0]), whole_rows)
summary = {
    "formulation_cohort": len(classification_rows),
    "formulation_dispositions": dict(sorted(Counter(row["disposition"] for row in classification_rows).items())),
    "constituent_assertions": len(constituent_review),
    "constituent_dispositions": dict(sorted(Counter(row["disposition"] for row in constituent_review).items())),
    "descriptor_concepts": len(descriptor_rows),
    "process_concepts": len(process_rows),
    "whole_term_concepts": len(whole_rows),
    "hierarchy_revisions": len(existing_hierarchy + hierarchy_rows),
    "explicit_holds": ["AOM_001500"],
}
REVIEW.mkdir(parents=True, exist_ok=True)
(REVIEW / "feed_structure_summary.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps(summary, indent=2, sort_keys=True))
