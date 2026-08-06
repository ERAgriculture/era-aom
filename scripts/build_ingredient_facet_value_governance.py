#!/usr/bin/env python3
"""Build approved high-confidence ingredient facet concepts and value contracts."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW = "review/livestock-v3/ingredient_component_value_candidates.csv"
DATE = "2026-08-05"
REVIEWER = "Pete Steward"
FACET_MODEL = {
    "material_component": ("aom:materialComponent", "aom:FeedMaterialComponent"),
    "anatomical_part": ("aom:ingredientPart", "aom:IngredientPartCategory"),
    "physical_form": ("aom:physicalForm", "aom:IngredientPhysicalForm"),
    "material_integrity": ("aom:materialIntegrity", "aom:MaterialIntegrity"),
    "feed_product_type": ("aom:feedProductType", "aom:FeedProductType"),
    "composition_state": ("aom:compositionState", "aom:CompositionState"),
    "processing_method": ("aom:processingMethod", "aom:ProcessingMethod"),
    "product_role": ("aom:productRole", "aom:ProductRole"),
    "chemical_constituent": ("aom:ingredientConstituent", "aom:IngredientConstituent"),
}

ROOTS = [
    ("part_root", "Ingredient anatomical parts", "Biological structures from which feed materials derive.", "anatomical_part"),
    ("form_root", "Ingredient physical forms", "Physical presentations of feed materials.", "physical_form"),
    ("process_root", "Ingredient processing methods", "Transformations used to produce or prepare feed materials.", "processing_method"),
    ("role_root", "Ingredient product roles", "Economic or production roles of feed materials.", "product_role"),
    ("constituent_root", "Ingredient constituents", "Chemical substances or fractions identified in feed materials.", "chemical_constituent"),
]

VALUES = [
    ("part_bulb", "Bulb", "part_root", "anatomical_part"),
    ("part_cladode", "Cladode", "part_root", "anatomical_part"),
    ("part_cob", "Cob", "part_root", "anatomical_part"),
    ("part_corm", "Corm", "part_root", "anatomical_part"),
    ("part_fruit", "Fruit", "part_root", "anatomical_part"),
    ("part_germ", "Germ", "part_root", "anatomical_part"),
    ("part_hull", "Hull", "part_root", "anatomical_part"),
    ("part_husk", "Husk", "part_root", "anatomical_part"),
    ("part_kernel", "Kernel", "part_root", "anatomical_part"),
    ("part_leaf", "Leaf", "part_root", "anatomical_part"),
    ("part_peel", "Peel", "part_root", "anatomical_part"),
    ("part_pod", "Pod", "part_root", "anatomical_part"),
    ("part_pseudostem", "Pseudostem", "part_root", "anatomical_part"),
    ("part_root_value", "Root", "part_root", "anatomical_part"),
    ("part_seed", "Seed", "part_root", "anatomical_part"),
    ("part_sheath", "Sheath", "part_root", "anatomical_part"),
    ("part_shell", "Shell", "part_root", "anatomical_part"),
    ("part_sprout", "Sprout", "part_root", "anatomical_part"),
    ("part_stalk", "Stalk", "part_root", "anatomical_part"),
    ("part_tuber", "Tuber", "part_root", "anatomical_part"),
    ("part_viscera", "Viscera", "part_root", "anatomical_part"),
    ("part_twig", "Twig", "part_root", "anatomical_part"),
    ("part_bark", "Bark", "part_root", "anatomical_part"),
    ("part_stem", "Stem", "part_root", "anatomical_part"),
    ("part_top", "Plant top", "part_root", "anatomical_part"),
    ("form_block", "Block form", "form_root", "physical_form"),
    ("form_lick", "Lick form", "form_root", "physical_form"),
    ("form_powder", "Powder form", "form_root", "physical_form"),
    ("form_cake", "Cake form", "form_root", "physical_form"),
    ("form_flake", "Flake form", "form_root", "physical_form"),
    ("form_dried", "Dried form", "form_root", "physical_form"),
    ("role_discard", "Discard role", "role_root", "product_role"),
    ("role_market_waste", "Market-waste role", "role_root", "product_role"),
    ("role_offal", "Offal role", "role_root", "product_role"),
    ("role_processing_waste", "Processing-waste role", "role_root", "product_role"),
    ("role_residue", "Residue role", "role_root", "product_role"),
    ("role_shorts", "Milling-shorts role", "role_root", "product_role"),
    ("role_waste", "Waste role", "role_root", "product_role"),
    ("role_byproduct", "By-product role", "role_root", "product_role"),
    ("role_crop_residue", "Crop-residue role", "role_root", "product_role"),
    ("const_gluten", "Gluten constituent", "constituent_root", "chemical_constituent"),
    ("const_starch", "Starch constituent", "constituent_root", "chemical_constituent"),
    ("const_fat", "Fat constituent", "constituent_root", "chemical_constituent"),
    ("const_essential_oil", "Essential-oil constituent", "constituent_root", "chemical_constituent"),
    ("process_brewing", "Brewing", "process_root", "processing_method"),
    ("process_defatting", "Defatting", "process_root", "processing_method"),
    ("process_pressing", "Pressing", "process_root", "processing_method"),
    ("process_drying", "Drying", "process_root", "processing_method"),
    ("process_extraction", "Extraction", "process_root", "processing_method"),
    ("process_threshing", "Threshing", "process_root", "processing_method"),
    ("part_grain", "Grain", "part_root", "anatomical_part"),
    ("form_mixture", "Mixture form", "form_root", "physical_form"),
    ("form_whole", "Whole form", "form_root", "physical_form"),
    ("form_liquid", "Liquid form", "form_root", "physical_form"),
    ("form_pulp", "Pulp form", "form_root", "physical_form"),
    ("role_binder", "Binder role", "role_root", "product_role"),
    ("const_ash", "Ash constituent", "constituent_root", "chemical_constituent"),
    ("const_oil", "Oil constituent", "constituent_root", "chemical_constituent"),
    ("process_milling", "Milling", "process_root", "processing_method"),
    ("process_hydrolysis", "Hydrolysis", "process_root", "processing_method"),
    ("process_sugar", "Sugar processing", "process_root", "processing_method"),
]

# Extensions append after established allocations so existing persistent IDs do
# not shift when new facet families are introduced.
EXTENSION_ROOTS = [
    ("material_component_root", "Feed material components", "Reviewed material scopes and components that are not limited to anatomical parts.", "material_component"),
]
EXTENSION_VALUES = [
    ("component_whole_crop", "Whole crop", "material_component_root", "material_component"),
    # ADR 0016 bulk-rule targets. Append only: existing allocations never shift.
    ("process_alkali_treatment", "Alkali treatment", "process_root", "processing_method"),
    ("process_autoclaving", "Autoclaving", "process_root", "processing_method"),
    ("process_boiling", "Boiling", "process_root", "processing_method"),
    ("process_cracking", "Cracking", "process_root", "processing_method"),
    ("process_crushing", "Crushing", "process_root", "processing_method"),
    ("process_enzyme_treatment", "Enzyme treatment", "process_root", "processing_method"),
    ("process_extrusion", "Extrusion", "process_root", "processing_method"),
    ("process_fermentation", "Fermentation", "process_root", "processing_method"),
    ("process_grinding", "Grinding", "process_root", "processing_method"),
    ("process_heating", "Heating", "process_root", "processing_method"),
    ("process_molasses_treatment", "Molasses treatment", "process_root", "processing_method"),
    ("process_roasting", "Roasting", "process_root", "processing_method"),
    ("process_soaking", "Soaking", "process_root", "processing_method"),
    ("process_sprouting", "Sprouting", "process_root", "processing_method"),
    ("process_urea_treatment", "Urea treatment", "process_root", "processing_method"),
    ("process_wilting", "Wilting", "process_root", "processing_method"),
    ("part_blood", "Blood", "part_root", "anatomical_part"),
    ("part_bran", "Bran", "part_root", "anatomical_part"),
    ("part_stover", "Stover", "part_root", "anatomical_part"),
    ("part_straw", "Straw", "part_root", "anatomical_part"),
    ("part_vine", "Vine", "part_root", "anatomical_part"),
    ("form_pellet", "Pellet form", "form_root", "physical_form"),
    ("integrity_root", "Material integrity values", None, "material_integrity"),
    ("integrity_whole_grain", "Whole grain", "integrity_root", "material_integrity"),
    # ADR 0020 closes ambiguous pulp, hay, formulated-meal, and whole-milk cases.
    ("product_type_root", "Feed product types", None, "feed_product_type"),
    ("product_processing_pulp", "Processing pulp", "product_type_root", "feed_product_type"),
    ("product_hay", "Hay", "product_type_root", "feed_product_type"),
    ("product_compound_feed", "Compound feed", "product_type_root", "feed_product_type"),
    ("composition_state_root", "Composition states", None, "composition_state"),
    ("composition_whole_milk", "Whole-milk composition", "composition_state_root", "composition_state"),
    # ADR 0029 hard-tail model extensions. Append only: existing IDs remain stable.
    ("part_flower", "Flower", "part_root", "anatomical_part"),
    ("form_slurry", "Slurry form", "form_root", "physical_form"),
    ("process_steeping", "Steeping", "process_root", "processing_method"),
    ("const_protein", "Protein constituent", "constituent_root", "chemical_constituent"),
    ("part_rhizome", "Rhizome", "part_root", "anatomical_part"),
    ("part_liver", "Liver", "part_root", "anatomical_part"),
    ("process_stacking", "Stacking", "process_root", "processing_method"),
    ("process_distillation", "Distillation", "process_root", "processing_method"),
]
RULE_EXTENSION_KEYS = {key for key, *_ in EXTENSION_VALUES[1:]}


def evidence_for(key):
    if key in {"part_flower", "form_slurry", "process_steeping", "const_protein", "part_rhizome", "part_liver", "process_stacking", "process_distillation"}:
        return "docs/decisions/0029-semantic-model-hard-tail-extension.md"
    if key.startswith("product_") or key.startswith("composition_"):
        return "docs/decisions/0020-ingredient-semantic-closure.md"
    if key in {"integrity_root", "integrity_whole_grain"}:
        return "docs/decisions/0018-whole-grain-integrity.md"
    if key in RULE_EXTENSION_KEYS:
        return "review/livestock-v6/ingredient_rule_quality_assessment.csv"
    if key in {"material_component_root", "component_whole_crop"}:
        return "review/livestock-v4/MAIZE_IDENTITY_REVIEW.md"
    return REVIEW

# Existing AOM concepts that also serve as governed facet values. Reuse their
# persistent identifiers rather than minting duplicate concepts.
EXISTING_VALUES = [
    ("AOM_000831", "Ensiling", "processing_method"),
]

ATOMIC = {
    "Block": "form_block", "Bulb": "part_bulb", "Cladode": "part_cladode",
    "Cob": "part_cob", "Corm": "part_corm", "Discards": "role_discard",
    "Fruits": "part_fruit", "Germ": "part_germ", "Gluten": "const_gluten",
    "Hull": "part_hull", "Husk": "part_husk", "Kernel": "part_kernel",
    "Leaves": "part_leaf", "Lick": "form_lick", "Market Waste": "role_market_waste",
    "Offal": "role_offal", "Peel": "part_peel", "Peels": "part_peel",
    "Pods": "part_pod", "Powder": "form_powder", "Processing Waste": "role_processing_waste",
    "Pseudo-stem": "part_pseudostem", "Residue": "role_residue", "Root": "part_root_value",
    "Seed": "part_seed", "Seeds": "part_seed", "Sheath": "part_sheath",
    "Shorts": "role_shorts", "Sprout": "part_sprout", "Stalk": "part_stalk",
    "Stalks": "part_stalk", "Starch": "const_starch", "Tuber": "part_tuber",
    "Viscera": "part_viscera", "Waste": "role_waste",
    "Ash": "const_ash", "Binder": "role_binder", "Grain": "part_grain",
    "Manure": "role_waste", "Mix": "form_mixture", "Oil": "const_oil",
    "Shell": "part_shell", "Shells": "part_shell", "Sludge": "role_processing_waste",
    "Tops": "part_top",
}

DECOMPOSITIONS = {
    "Bean Cake": ["form_cake", "role_byproduct"],
    "Bean Shell": ["part_shell"],
    "Brewers Grain": ["process_brewing", "role_byproduct"],
    "Flakes Defatted": ["form_flake", "process_defatting"],
    "Full Fat Cake": ["const_fat", "form_cake", "process_pressing"],
    "Hay": ["form_dried", "process_drying"],
    "Kernel Cake": ["part_kernel", "form_cake", "process_pressing"],
    "Leaves and Soft Twig": ["part_leaf", "part_twig"],
    "Leaves and Twigs": ["part_leaf", "part_twig"],
    "Leaves Cake": ["part_leaf", "form_cake", "process_pressing"],
    "Leaves Extract": ["part_leaf", "process_extraction"],
    "Peel Essential Oil": ["part_peel", "const_essential_oil", "process_extraction"],
    "Root Bark": ["part_root_value", "part_bark"],
    "Seed Cake": ["part_seed", "form_cake", "process_pressing"],
    "Seed Hull": ["part_seed", "part_hull"],
    "Stover": ["part_stem", "part_leaf", "role_crop_residue"],
    "Threshed Top": ["part_top", "process_threshing"],
    "Bran": ["process_milling", "role_byproduct"],
    "Cake": ["form_cake", "process_pressing", "role_byproduct"],
    "Haulm": ["part_stem", "part_leaf", "role_crop_residue"],
    "Hydrolysate": ["process_hydrolysis"],
    "Juice": ["form_liquid", "process_extraction"],
    "Molasses": ["form_liquid", "process_sugar", "role_byproduct"],
    "Pods Husk": ["part_pod", "part_husk"],
    "Pulp": ["form_pulp", "role_byproduct"],
    "Seed Kernel": ["part_seed", "part_kernel"],
    "Straw": ["part_stem", "part_leaf", "form_dried", "role_crop_residue"],
    "Hash": ["form_mixture", "role_byproduct"],
}

HOLDS = {
    "Beans": "May denote whole material identity or seed; no audited occurrence resolves scope.",
    "Full Fat": "Compositional state cannot be represented truthfully as mere fat-constituent identity.",
    "Heads": "Source-only mapping cannot distinguish audited shrimp heads from possible plant reproductive heads.",
    "Litter": "May denote bedding, poultry excreta mixture, or material identity; no audited occurrence resolves scope.",
    "Meal": "Audited value is a named complete ration, not evidence for ground physical form or extraction residue.",
    "Oil Crude": "Crude is processing state or grade, not a processing method; current facet model lacks that distinction.",
    "Shaft": "Cassava usage may be typo or local synonym for stem; no authoritative identity found.",
    "Vine": "Feed usage may mean stem alone or collective aerial biomass including leaves.",
    "Weeds": "Names source-material class, not anatomical part, form, process, role, or constituent.",
    "Whole": "May mean whole crop, whole organism, whole grain, or absence of a component; source context must resolve scope.",
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    concepts_path = DATA / "approved_new_concepts.csv"
    registry_path = DATA / "livestock_id_registry.csv"
    concepts = read(concepts_path)
    registry = read(registry_path)
    concepts = [row for row in concepts if not row["case_id"].startswith("FACETVAL-")]
    registry = [row for row in registry if not row["case_id"].startswith("FACETVAL-")]
    assert registry[-1]["concept_id"] == "AOM_101018"
    definitions = [(key, label, None, facet, note) for key, label, note, facet in ROOTS]
    definitions += [(key, label, parent, facet, f"Governed {facet.replace('_', ' ')} value used for ingredient-component semantics.") for key, label, parent, facet in VALUES]
    definitions += [(key, label, None, facet, note) for key, label, note, facet in EXTENSION_ROOTS]
    definitions += [
        (
            key, label, parent, facet,
            f"Governed {facet.replace('_', ' ')} "
            f"{'vocabulary' if parent is None else 'value'} used for feed-material semantics.",
        )
        for key, label, parent, facet in EXTENSION_VALUES
    ]
    ids = {key: f"AOM_{101019 + i:06d}" for i, (key, *_rest) in enumerate(definitions)}
    root_paths = {key: f"Management/Livestock Management/Feed Characteristic/{label}" for key, label, parent, *_ in definitions if parent is None}
    new_concepts = []
    for key, label, parent, facet, note in definitions:
        parent_id = "AOM_000328" if parent is None else ids[parent]
        level = "4" if parent is None else "5"
        path = root_paths[key] if parent is None else f"{root_paths[parent]}/{label}"
        new_concepts.append({
            "case_id": "FACETVAL-" + key.upper(), "concept_id": ids[key],
            "preferred_label": label, "scope_note": note, "broader_id": parent_id,
            "hierarchy_level": level, "derived_path": path, "child_ids": "",
            "reviewer": REVIEWER, "review_date": DATE, "evidence": evidence_for(key),
            "rationale": "Dedicated facet value prevents reuse of equal labels from incompatible AOM branches.",
        })
    new_registry = [{
        "concept_id": ids[key], "allocated_on": DATE, "status": "allocated",
        "preferred_label": label, "case_id": "FACETVAL-" + key.upper(), "allocator": REVIEWER,
        "allocation_basis": "Sequential governed allocation above AOM_101018 for ingredient facet value vocabulary; verified unused.",
    } for key, label, *_ in definitions]
    write(concepts_path, list(concepts[0]), concepts + new_concepts)
    write(registry_path, list(registry[0]), registry + new_registry)

    facet_fields = ["concept_id", "preferred_label", "facet", "target_property", "value_class", "concept_role", "status", "reviewer", "review_date", "evidence"]
    facet_concepts = []
    for key, label, parent, facet, _note in definitions:
        target_property, value_class = FACET_MODEL[facet]
        facet_concepts.append({
            "concept_id": ids[key], "preferred_label": label, "facet": facet,
            "target_property": target_property, "value_class": value_class,
            "concept_role": "facet_root" if parent is None else "facet_value",
            "status": "approved", "reviewer": REVIEWER, "review_date": DATE,
            "evidence": evidence_for(key),
        })
    for concept_id, label, facet in EXISTING_VALUES:
        target_property, value_class = FACET_MODEL[facet]
        facet_concepts.append({
            "concept_id": concept_id, "preferred_label": label, "facet": facet,
            "target_property": target_property, "value_class": value_class,
            "concept_role": "facet_value", "status": "approved",
            "reviewer": REVIEWER, "review_date": DATE,
            "evidence": "data/livestock-staging/definitions.csv",
        })
    write(DATA / "approved_ingredient_facet_concepts.csv", facet_fields, facet_concepts)

    facets = {key: facet for key, _label, _parent, facet, _note in definitions}
    labels = {key: label for key, label, *_ in definitions}
    mapping_fields = ["source_value", "facet", "target_concept_id", "target_label", "status", "reviewer", "review_date", "evidence", "rationale"]
    mappings = [{
        "source_value": source, "facet": facets[key], "target_concept_id": ids[key],
        "target_label": labels[key], "status": "approved", "reviewer": REVIEWER,
        "review_date": DATE, "evidence": REVIEW,
        "rationale": "High-confidence atomic descriptor mapped to dedicated facet value concept.",
    } for source, key in ATOMIC.items()]
    write(DATA / "approved_ingredient_component_value_mappings.csv", mapping_fields, mappings)

    decomposition_fields = ["source_value", "assertion_order", "facet", "target_concept_id", "target_label", "status", "reviewer", "review_date", "evidence", "rationale"]
    decompositions = []
    for source, keys in DECOMPOSITIONS.items():
        for order, key in enumerate(keys, 1):
            decompositions.append({
                "source_value": source, "assertion_order": order, "facet": facets[key],
                "target_concept_id": ids[key], "target_label": labels[key],
                "status": "approved", "reviewer": REVIEWER, "review_date": DATE,
                "evidence": REVIEW,
                "rationale": "High-confidence compound descriptor decomposed into independently typed facet assertion.",
            })
    write(DATA / "approved_ingredient_component_decompositions.csv", decomposition_fields, decompositions)
    hold_fields = ["source_value", "target_property", "value_class", "binding_action", "status", "reviewer", "review_date", "evidence", "rationale"]
    holds = [{
        "source_value": source, "target_property": "aom:legacyComponentDescriptor",
        "value_class": "xsd:string", "binding_action": "hold_ambiguous", "status": "approved",
        "reviewer": REVIEWER, "review_date": DATE,
        "evidence": "review/livestock-v3/INGREDIENT_FACET_CLOSURE.md",
        "rationale": rationale,
    } for source, rationale in HOLDS.items()]
    write(DATA / "approved_ingredient_component_value_holds.csv", hold_fields, holds)
    governed = set(ATOMIC) | set(DECOMPOSITIONS) | set(HOLDS)
    assert len(governed) == 83 and not (set(ATOMIC) & set(DECOMPOSITIONS))
    assert not (set(ATOMIC) & set(HOLDS)) and not (set(DECOMPOSITIONS) & set(HOLDS))
    print(f"Allocated {len(definitions)} facet concepts; approved {len(mappings)} atomic mappings, {len(decompositions)} decomposition assertions, and {len(holds)} holds")


if __name__ == "__main__":
    main()
