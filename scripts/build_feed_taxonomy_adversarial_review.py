#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "livestock-staging"
OUT = ROOT / "review" / "livestock-v29"

FEED_MATERIALS = "AOM_100850"
SUPPLEMENT = "AOM_000736"
OTHER_INGREDIENTS = "AOM_000781"
ORGANIC_ACID = "AOM_006389"
STRUCTURAL_ROOTS = {
    "AOM_101019",
    "AOM_101068",
    "AOM_101085",
    "AOM_101109",
    "AOM_101110",
    "AOM_101115",
    "AOM_101130",
}


@dataclass(frozen=True)
class Recommendation:
    problem: str
    action: str
    axis: str
    target: str
    evidence_state: str
    rationale: str


def rows(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


labels = {
    row["concept_id"]: row["label"]
    for row in rows(DATA / "labels.csv")
    if row["language"] == "en" and row["label_type"] == "pref"
}
definitions = {
    row["concept_id"]: row["definition"]
    for row in rows(DATA / "definitions.csv")
    if row["language"] == "en"
}
parents = defaultdict(set)
children = defaultdict(set)
for row in rows(DATA / "relations.csv"):
    if row["relation_type"] == "broader":
        parents[row["subject_id"]].add(row["object_id"])
        children[row["object_id"]].add(row["subject_id"])


def descendants(root):
    found = set()
    pending = list(children[root])
    while pending:
        concept_id = pending.pop()
        if concept_id in found:
            continue
        found.add(concept_id)
        pending.extend(children[concept_id])
    return found


def top_groups(concept_id, root):
    groups = []
    for candidate in children[root]:
        if concept_id == candidate or concept_id in descendants(candidate):
            groups.append(candidate)
    return sorted(groups)


governed_types = defaultdict(set)
for row in rows(DATA / "approved_feed_formulation_classifications.csv"):
    if row["semantic_class"]:
        governed_types[row["concept_id"]].add(row["semantic_class"])
for row in rows(DATA / "approved_ingredient_facet_concepts.csv"):
    if row["value_class"]:
        governed_types[row["concept_id"]].add(row["value_class"])


schema_replacements = {
    "AOM_000531": "aom:ingredientName literal property",
    "AOM_000532": "aom:materialComponent / aom:hasAnatomicalComponent relation",
    "AOM_000533": "aom:sourceTaxon relation",
    "AOM_000534": "aom:ingredientProportion quantity",
    "AOM_000535": "aom:materialSource relation",
}

direct_anomalies = {
    "AOM_000809": Recommendation(
        "chemical class used as feed-material category",
        "move",
        "chemical constituent",
        "Primary chemical constituents",
        "authority-supported",
        "Essential fatty acid denotes chemical composition, not one feed material.",
    ),
    "AOM_003100": Recommendation(
        "management activity used as feed material",
        "move",
        "feeding practice",
        "grazing or feed-access practice",
        "model-supported",
        "Grazing is an animal-management process, not a material entity.",
    ),
    "AOM_000811": Recommendation(
        "compound category mixes source material and extraction state",
        "split",
        "feed material plus process",
        "herb feed materials; extracts linked to Extraction",
        "requires-concept-review",
        "Herbs and extracts require separate material identity and processing assertions.",
    ),
    "AOM_000807": Recommendation(
        "functional use class asserted as feed material",
        "move",
        "feed additive function",
        "zootechnical additives / gut-flora function",
        "authority-supported",
        "Prebiotic describes intended physiological function and may apply to different substances.",
    ),
    "AOM_003076": Recommendation(
        "functional use class asserted as feed material",
        "move",
        "feed additive or microbial preparation",
        "zootechnical additives / gut-flora stabilisers",
        "authority-supported",
        "Probiotic identity depends on microbial preparation and intended additive use.",
    ),
    ORGANIC_ACID: Recommendation(
        "chemical class used as feed-material category",
        "move",
        "chemical substance",
        "chemical substances; additive function asserted separately",
        "authority-supported",
        "Organic acid is a chemical class; feed-additive status depends on use and authorization.",
    ),
    SUPPLEMENT: Recommendation(
        "meaningless mixed material superclass",
        "retire-and-replace",
        "supplemental feeding role",
        "feeding role or complementary-feed formulation",
        "authority-supported",
        "Supplement denotes use with another feed, not a material identity. Descendants require independent classification.",
    ),
    OTHER_INGREDIENTS: Recommendation(
        "meaningless residual material superclass",
        "retire-after-disposition",
        "none",
        "independent evidence-backed branches",
        "model-supported",
        "Other Ingredients provides no reusable semantics and hides unresolved identity decisions.",
    ),
}

supplement_defaults = {
    "AOM_000737": Recommendation("additive category under material catch-all", "move", "feed additive", "nutritional additives / amino acids", "authority-supported", "EU feed-additive categories place amino acids, salts, and analogues under nutritional additives."),
    "AOM_000751": Recommendation("additive category under material catch-all", "move", "feed additive", "zootechnical additives / digestibility enhancers", "authority-supported", "Ingested feed enzymes are additive preparations; processing enzymes require a separate process model."),
    "AOM_000779": Recommendation("branch mixes substances, materials, additives, and formulations", "split", "multiple feed axes", "mineral feed materials; trace-element additives; mineral complementary feeds; chemical constituents", "authority-supported", "Mineral identity alone does not determine material, additive, formulation, or constituent role."),
    "AOM_000793": Recommendation("additive category under material catch-all", "split", "feed additive and formulation", "nutritional additives; vitamin premixtures", "authority-supported", "Vitamin substances are nutritional additives; vitamin mixes are premixtures or formulations."),
    "AOM_000795": Recommendation("generic mixture used as feed material", "move", "feed formulation", "mineral or vitamin complementary feeds", "authority-supported", "Mixtures are formulations, not single feed materials."),
    "AOM_001068": Recommendation("chemical class under material catch-all", "move", "chemical substance or feed additive", "chemical substances; intended additive use separately", "requires-substance-evidence", "Pseudovitamin is not a material product class."),
    "AOM_001091": Recommendation("functional category under material catch-all", "move", "feed additive function", "technological additives / mycotoxin reduction", "authority-supported", "EU feed-additive functional groups explicitly represent substances reducing mycotoxin contamination."),
    "AOM_001571": Recommendation("chemical constituent used as material superclass", "split", "chemical constituent and feed material", "Protein constituent; separately evidenced protein feed materials", "model-supported", "Casein and gluten products are materials; Protein is a constituent class."),
    "AOM_001577": Recommendation("chemical constituent used as material superclass", "split", "chemical substance and feed material", "Carbohydrate constituents; separately evidenced carbohydrate materials", "model-supported", "Carbohydrate is a constituent class; dextrin requires a substance/use decision."),
    "AOM_001749": Recommendation("nutritional additive under material catch-all", "move", "feed additive", "nutritional additives / urea and derivatives", "authority-supported", "EU Regulation 1831/2003 places urea and derivatives under nutritional additives."),
    "AOM_003577": Recommendation("formulated product typed through material branch", "move", "feed formulation", "complementary or protein feed formulations", "authority-supported", "Commercial protein supplement denotes a formulated complementary feed."),
    "AOM_003889": Recommendation("poorly evidenced local material", "hold-and-research", "unresolved feed material", "mineral or soil-derived feed materials", "requires-product-evidence", "Bole Soil needs source, composition, safety, and intended-use evidence."),
    "AOM_004433": Recommendation("feed-additive category under material catch-all", "move-and-rename", "feed additive", "coccidiostats and histomonostats", "authority-supported", "Coccidiostats are a distinct feed-additive category, not generic supplements."),
    "AOM_006334": Recommendation("functional product class under material catch-all", "move-and-rename", "feed material", "rumen-protected fat feed materials", "product-evidence-supported", "Rumen-protected fat is a feed-material product class; protection method and composition require explicit assertions."),
    "AOM_006339": Recommendation("functional category under material catch-all", "move", "feed additive function", "technological additives / preservatives or hygiene enhancers", "authority-supported", "Antifungal function does not identify one material and needs product-specific classification."),
    "AOM_100989": Recommendation("source-material group named by supplemental use", "rename-and-move", "feed material", "microalgal feed materials", "model-supported", "Microalgal biomass remains a source-based feed material regardless of supplemental use."),
}

mineral_formulations = {
    "AOM_000764", "AOM_000765", "AOM_000766", "AOM_001415", "AOM_001773",
    "AOM_003084", "AOM_003201",
}
mineral_constituents = {
    "AOM_000754", "AOM_001066", "AOM_000756", "AOM_000759", "AOM_000763",
    "AOM_000770", "AOM_000774", "AOM_000776", "AOM_000778",
}
mineral_materials = {
    "AOM_001367", "AOM_001368", "AOM_001369", "AOM_001370", "AOM_006124",
    "AOM_001371", "AOM_001372", "AOM_000755", "AOM_000757", "AOM_001746",
    "AOM_002074", "AOM_000758", "AOM_000760", "AOM_003760", "AOM_001378",
    "AOM_006125", "AOM_000768", "AOM_001427", "AOM_000772", "AOM_001487",
    "AOM_000777",
}
mineral_additive_candidates = {"AOM_001067", "AOM_001417", "AOM_001418"}

vitamin_formulations = {"AOM_001505", "AOM_001839", "AOM_000791"}

other_defaults = {
    "AOM_000745": Recommendation("role category used as material superclass", "split", "material plus functional role", "independent materials linked to Binder role", "model-supported", "Binder already has a governed product-role value; substances require independent material/additive classification."),
    "AOM_000747": Recommendation("experimental role used as material superclass", "split", "material plus experimental role", "marker substances linked to Digestibility-marker role", "model-supported", "Digestibility marker is a study role, while chromium oxide is a substance."),
    "AOM_100987": Recommendation("valid materials hidden under residual category", "move", "feed material and product role", "processed food by-products", "authority-supported", "Former foodstuffs are feed materials with by-product or waste roles, not Other Ingredients."),
    "AOM_100988": Recommendation("valid material scope hidden under residual category", "move-or-hold", "feed material and waste role", "organic-waste feed materials", "requires-safety-evidence", "Waste identity and regulatory acceptability require explicit evidence; Other Ingredients adds no meaning."),
}

other_overrides = {
    "AOM_000753": Recommendation("mineral material hidden under residual category", "move", "feed material", "mineral feed materials", "catalogue-supported", "Sodium bicarbonate identity should be classified with mineral feed materials."),
    "AOM_000780": Recommendation("substance classified without intended function", "move-or-hold", "feed additive or feed material", "emulsifier additive when intended; material otherwise", "requires-use-evidence", "Lecithin status depends on product identity and intended technological function."),
    "AOM_000782": Recommendation("functional class used as material", "move", "feed additive function", "toxin-binding or decontamination functions", "requires-product-evidence", "Antitoxin does not identify one substance or product."),
    "AOM_000783": Recommendation("multi-component product under residual material category", "move", "feed formulation", "complementary feeds / blocks", "model-supported", "Molasses and urea block is a formulation."),
    "AOM_001500": Recommendation("unresolved commercial product", "hold-and-research", "unresolved", "no type until manufacturer evidence", "requires-product-evidence", "ACTIPAL HP 1 remains an explicit product-class hold."),
    "AOM_001507": Recommendation("placeholder represented as domain concept", "retire", "missing-data code", "source-data unknown value", "model-supported", "Unspecified is a data-quality state, not a feed material."),
    "AOM_001824": Recommendation("material hidden under residual category", "move-or-hold", "feed material", "carbonized plant-derived materials", "requires-use-and-safety-evidence", "Wood charcoal needs source, processing, and intended-feed-use evidence."),
    "AOM_001825": Recommendation("regulated product under residual category", "hold-and-research", "feed additive or medicinal product", "regulatory product classification", "requires-current-regulatory-evidence", "Olaquindox classification and permitted use are jurisdiction- and date-sensitive."),
    "AOM_001832": Recommendation("substance/material ambiguity", "rename-and-move", "feed material", "Starch feed material; keep Starch constituent separate", "catalogue-supported", "Generic Starch must be disambiguated from chemical-constituent use."),
    "AOM_001865": Recommendation("analytical/toxic constituent used as material", "move", "chemical constituent", "undesirable or toxic constituents", "model-supported", "Free gossypol is a constituent measurement target, not a feed ingredient."),
    "AOM_001866": Recommendation("valid feed material hidden under residual category", "move", "feed material", "products from oils and fats", "catalogue-supported", "Glycerol/glycerine is represented in EU feed-material catalogue."),
    "AOM_001867": Recommendation("poorly evidenced inert material", "hold-and-research", "unresolved", "marker, contaminant, or material role", "requires-use-evidence", "Sand label alone does not establish intended feed use."),
    "AOM_001868": Recommendation("unresolved commercial product", "hold-and-research", "unresolved", "no type until product evidence", "requires-product-evidence", "Toxynil identity and function require stable manufacturer evidence."),
    "AOM_001869": Recommendation("waste material with regulatory risk", "hold-and-research", "feed material candidate", "waste-derived materials", "requires-safety-and-regulatory-evidence", "Activated sludge cannot be normalized as feed material from label alone."),
    "AOM_001917": Recommendation("role/placeholder represented as material", "move", "product role", "Filler role", "model-supported", "Unspecified filler is a role with unknown bearer, not a material identity."),
    "AOM_001921": Recommendation("unresolved possible duplicate commercial product", "hold-and-identity-review", "unresolved", "compare with AOM_001831 Vitalite", "requires-product-evidence", "Vitalyte and Vitalite require product and spelling identity review."),
    "AOM_001922": Recommendation("valid material hidden under residual category", "move", "feed material", "water and liquid feed materials", "model-supported", "Water is a material, not an Other Ingredient residue class."),
    "AOM_002191": Recommendation("mineral material hidden under residual category", "move", "feed material", "calcareous shell mineral materials", "catalogue-supported", "Ground fossil shell belongs with mineral feed materials if identity is confirmed."),
    "AOM_003172": Recommendation("waste material hidden under residual category", "move", "feed material and waste role", "food-waste feed materials", "requires-safety-evidence", "Food waste needs explicit source and product-role modelling."),
    "AOM_003203": Recommendation("mineral/waste material hidden under residual category", "move-or-hold", "feed material", "ash-derived mineral materials", "requires-composition-and-safety-evidence", "Wood ash needs composition and feed-use evidence."),
    "AOM_006241": Recommendation("source material hidden under residual category", "move", "feed material", "fungal or yeast feed materials", "model-supported", "Unspecified yeast is a material with unresolved taxon, not an Other Ingredient class."),
    "AOM_006349": Recommendation("source material hidden under residual category", "move", "feed material", "fungal feed materials with source taxon", "model-supported", "Pleurotus ostreatus should be classified by biological source."),
}

structural_overrides = {
    "AOM_101019": Recommendation("anatomical and manufactured component roots exposed in parallel", "rename-and-reparent", "material component", "Anatomical components under Feed material components", "ontology-supported", "FoodOn separates organism anatomy from manufactured fractions while relating both as product facets."),
    "AOM_101085": Recommendation("under-specified root with unrelated Bran and Whole crop children", "retain-and-restructure", "material component", "Feed material components with typed subbranches", "ontology-supported", "One component root should contain explicit anatomical-component and processed-fraction subbranches; Whole crop belongs elsewhere."),
    "AOM_101104": Recommendation("processed milling fraction lacks typed component branch", "move", "processed material fraction", "Cereal milling fractions under Feed material components", "ontology-supported", "Bran may denote cereal outer tissues but feed bran is commonly a milling fraction; it is not a simple universal anatomy value."),
    "AOM_101086": Recommendation("whole-crop scope represented as component", "move-and-rename", "component-retention state", "Whole-crop composition under component-retention states", "model-supported", "Whole crop describes retained harvested scope, not one component part."),
    "AOM_101105": Recommendation("composite crop residue represented as anatomy", "move", "feed material and product role", "crop-residue feed materials / Stover role", "model-supported", "Stover is a composite post-harvest residue, not one anatomical structure."),
    "AOM_101106": Recommendation("composite crop residue represented as anatomy", "move", "feed material and product role", "crop-residue feed materials / Straw role", "model-supported", "Straw is a composite crop residue, not one anatomical structure."),
    "AOM_101103": Recommendation("body substance represented as connected anatomy", "move", "material component", "animal body substances under Feed material components", "ontology-supported", "Blood is a body substance rather than a connected anatomical structure."),
    "AOM_101109": Recommendation("misnamed integrity root duplicates composition semantics", "retire", "none", "replace with component-retention states", "authority-supported", "Whole grain can remain compositionally whole after grinding; integrity is misleading."),
    "AOM_101110": Recommendation("whole-grain composition represented as integrity", "rename-and-move", "component-retention state", "Whole-grain composition under component-retention states", "authority-supported", "Whole grain means bran, germ, and endosperm retained in original proportions, including after grinding."),
    "AOM_101115": Recommendation("orphan top-level fragment with negative-sounding values", "rename-and-reparent", "component-retention state", "Native-component retention states under Feed Chemical Composition", "authority-supported", "Positive retention assertions are clearer than absence-of-process assertions and work under open-world semantics."),
    "AOM_101116": Recommendation("generic composition value lacks positive retained-component semantics", "retain-and-strengthen", "component-retention state", "Whole-milk composition plus retains native milk fat", "requires-definition-evidence", "Whole milk should use positive composition evidence, not merely absence of skimming."),
    "AOM_101134": Recommendation("negative-sounding state lacks explicit retained constituent", "rename-or-strengthen", "component-retention state", "Native-fat-retained composition plus retains native fat", "model-supported", "Not-defatted is unsafe as an inferred negative; assert retained native fat positively when source says full-fat."),
    "AOM_101068": Recommendation("upstream beverage-manufacturing bundle placed among feed treatments", "retire-from-feed-processes", "source production process", "future Beer brewing process linked with derivedFromProcess", "ontology-supported", "Brewhouse operations are not intentionally applied to feed material; by-products are outputs of brewing stages."),
    "AOM_101130": Recommendation("ambiguous objective branch includes non-separation process bundles", "rename-and-prune", "process objective", "Feed component separation processes", "ontology-supported", "FoodOn uses component separation process for processes removing a component; Brewhouse processing does not satisfy that definition."),
    "AOM_101128": Recommendation("broad thermal conversion treated universally as separation", "remove-separation-parent", "thermal source processing", "Thermal feed processes; separation only for explicit rendering outputs", "requires-process-specific-evidence", "Rendering can include separation but generic rendering does not always assert component recovery."),
}


def recommendation(concept_id):
    if concept_id in schema_replacements:
        return Recommendation(
            "schema field exposed as feed material",
            "deprecate-and-remove-from-browse",
            "schema property",
            schema_replacements[concept_id],
            "model-supported",
            "Legacy field identity should remain searchable but no longer appear as a feed material.",
        )
    if concept_id in structural_overrides:
        return structural_overrides[concept_id]
    if concept_id in direct_anomalies:
        return direct_anomalies[concept_id]

    supplement_groups = top_groups(concept_id, SUPPLEMENT)
    if supplement_groups:
        top = supplement_groups[0]
        if concept_id in mineral_formulations:
            return Recommendation("formulation under mineral material catch-all", "move", "feed formulation", "mineral complementary feeds", "model-supported", "Blocks, licks, and mixes are multi-component formulations.")
        if concept_id in mineral_constituents:
            return Recommendation("element identity used as feed material", "move-or-hold", "chemical constituent or feed additive", "chemical elements; authorized trace-element compounds separately", "requires-compound-and-use-evidence", "Element label alone does not identify a feed material or authorized additive preparation.")
        if concept_id in mineral_materials:
            return Recommendation("mineral material under supplement catch-all", "move", "feed material", "mineral feed materials", "catalogue-supported", "Substance is a candidate mineral feed material; exact composition and synonym identity still require verification.")
        if concept_id in mineral_additive_candidates:
            return Recommendation("trace-element compound under supplement catch-all", "move-or-hold", "feed additive", "nutritional additives / trace-element compounds", "requires-authorization-evidence", "Trace-element compound use requires product and authorization evidence.")
        if top == "AOM_000779" and concept_id != top:
            return Recommendation("uncertain mineral product under mixed branch", "hold-and-research", "unresolved", "no target until product/substance evidence", "requires-product-evidence", "Current Mineral parent cannot establish material, additive, formulation, or constituent role.")
        if concept_id in vitamin_formulations:
            return Recommendation("vitamin mixture under additive substance branch", "move", "feed formulation", "premixtures or complementary feeds", "model-supported", "Vitamin mixtures are multi-component preparations, not single material substances.")
        if top == "AOM_000793" and concept_id != top:
            return Recommendation("vitamin substance under supplement catch-all", "move-or-hold", "feed additive", "nutritional additives / vitamins and provitamins", "requires-substance-evidence", "Specific vitamin identity supports additive review; product formulation must remain explicit.")
        if top == "AOM_006334" and concept_id == "AOM_001497":
            return Recommendation("branded product under generic supplement catch-all", "retain-product-and-reparent", "feed material", "Megalac under rumen-protected fat feed materials", "product-evidence-supported", "Manufacturer identifies Megalac as calcium-salt rumen-protected fat made from PFAD.")
        if top == "AOM_004433" and concept_id == "AOM_001579":
            return Recommendation("coccidiostat product under supplement catch-all", "reparent", "feed additive", "coccidiostats and histomonostats", "authority-supported", "Elancoban is monensin-sodium feed additive used for coccidiosis control.")
        if top == "AOM_001571" and concept_id != top:
            return Recommendation("feed material under chemical constituent superclass", "reparent", "feed material", "evidence-backed protein-rich feed materials", "requires-product-evidence", "Material identity must not be inferred from Protein constituent parent alone.")
        if top == "AOM_001577" and concept_id != top:
            return Recommendation("substance under chemical constituent superclass", "move-or-hold", "chemical substance or feed material", "Dextrin substance with explicit feed role", "requires-use-evidence", "Dextrin needs explicit material/additive use evidence.")
        if top == "AOM_001068" and concept_id != top:
            return Recommendation("substance under ambiguous pseudovitamin material branch", "move-or-hold", "chemical substance or feed additive", "Inositol with explicit feed role", "requires-use-evidence", "Inositol identity does not by itself establish material or additive use.")
        if top == "AOM_100989" and concept_id != top:
            return Recommendation("biological source material named by use", "reparent", "feed material", "microalgal feed materials with source taxon", "ontology-supported", "Chlorella vulgaris should be represented by material plus source taxon.")
        return supplement_defaults[top]

    other_groups = top_groups(concept_id, OTHER_INGREDIENTS)
    if other_groups:
        top = other_groups[0]
        if concept_id in other_overrides:
            return other_overrides[concept_id]
        if top == "AOM_000745" and concept_id != top:
            return Recommendation("material or additive hidden beneath Binder role category", "reparent-and-link-role", "feed material or feed additive", "independent identity plus Binder role", "requires-item-evidence", "Binder function must be an explicit role; bearer classification requires substance/product evidence.")
        if top == "AOM_000747" and concept_id != top:
            return Recommendation("marker substance hidden beneath experimental role", "reparent-and-link-role", "chemical substance", "Chromium oxide plus Digestibility-marker role", "model-supported", "Ground form remains separate presentation/process evidence; marker function is a role.")
        if top == "AOM_100987" and concept_id == "AOM_001831":
            return Recommendation("possible misspelled commercial product under by-product branch", "hold-and-identity-review", "unresolved", "compare with AOM_001921 Vitalyte", "requires-product-evidence", "Vitalite lacks evidence that it is a processed food by-product.")
        if top in other_overrides:
            return other_overrides[top]
        return other_defaults[top]

    if concept_id == "AOM_000808":
        return Recommendation("chemical substance classified as feed material by superclass", "move-or-hold", "chemical substance or feed additive", "Fumaric acid; acidity-regulator function separately", "requires-use-evidence", "Fumaric acid is an organic acid and may be used as an additive; use does not alter chemical identity.")

    if concept_id in descendants("AOM_101019"):
        return Recommendation("anatomical value in flat generated branch", "retain-and-reparent", "anatomical component", "Anatomical components under Feed material components", "ontology-supported", "Retain reusable anatomy value but place it under one component architecture.")
    if concept_id in descendants("AOM_101085"):
        return Recommendation("under-specified material component value", "hold-and-restructure", "material component", "typed component subbranch", "requires-component-review", "Component value needs explicit anatomical, processed-fraction, body-substance, or retained-scope type.")
    if concept_id in descendants("AOM_101115"):
        return Recommendation("composition shorthand lacks positive retained-component relation", "retain-and-strengthen", "component-retention state", "Native-component retention states", "requires-definition-evidence", "Retain searchable shorthand only with positive retained-component semantics.")
    if concept_id in descendants("AOM_101130"):
        return Recommendation("process grouped by broad separation objective", "retain-with-reviewed-parent", "process objective", "Feed component separation processes", "process-definition-supported", "Retain separation parent only when process definition removes or recovers a component or fraction.")

    return Recommendation(
        "direct feed-material category outside disputed branches",
        "retain-pending-later-review",
        "feed material",
        labels.get(concept_id, concept_id),
        "outside-current-defect",
        "Included to prove complete direct-branch coverage; no new defect asserted in this review.",
    )


direct_feed = set(children[FEED_MATERIALS])
supplement_cohort = descendants(SUPPLEMENT)
other_cohort = descendants(OTHER_INGREDIENTS)
organic_acid_cohort = descendants(ORGANIC_ACID)
structural_cohort = set(STRUCTURAL_ROOTS)
for root in STRUCTURAL_ROOTS:
    structural_cohort.update(descendants(root))

cohort = direct_feed | supplement_cohort | other_cohort | organic_acid_cohort | structural_cohort


def scopes(concept_id):
    found = []
    if concept_id in direct_feed:
        found.append("feed_material_direct_child")
    if concept_id in supplement_cohort:
        found.append("supplement_descendant")
    if concept_id in other_cohort:
        found.append("other_ingredients_descendant")
    if concept_id in organic_acid_cohort:
        found.append("organic_acid_descendant")
    if concept_id in structural_cohort:
        found.append("component_composition_process_structure")
    return ";".join(found)


OUT.mkdir(parents=True, exist_ok=True)
fieldnames = [
    "concept_id",
    "preferred_label",
    "review_scope",
    "current_parent_ids",
    "current_parent_labels",
    "current_top_group_ids",
    "current_top_group_labels",
    "current_descendant_count",
    "current_governed_types",
    "current_definition",
    "problem_category",
    "recommended_action",
    "recommended_axis",
    "recommended_target",
    "evidence_state",
    "rationale",
]
output_rows = []
for concept_id in sorted(cohort):
    rec = recommendation(concept_id)
    top_ids = sorted(set(top_groups(concept_id, SUPPLEMENT) + top_groups(concept_id, OTHER_INGREDIENTS)))
    parent_ids = sorted(parents[concept_id])
    output_rows.append({
        "concept_id": concept_id,
        "preferred_label": labels.get(concept_id, ""),
        "review_scope": scopes(concept_id),
        "current_parent_ids": ";".join(parent_ids),
        "current_parent_labels": ";".join(labels.get(item, item) for item in parent_ids),
        "current_top_group_ids": ";".join(top_ids),
        "current_top_group_labels": ";".join(labels.get(item, item) for item in top_ids),
        "current_descendant_count": len(descendants(concept_id)),
        "current_governed_types": ";".join(sorted(governed_types[concept_id])),
        "current_definition": definitions.get(concept_id, ""),
        "problem_category": rec.problem,
        "recommended_action": rec.action,
        "recommended_axis": rec.axis,
        "recommended_target": rec.target,
        "evidence_state": rec.evidence_state,
        "rationale": rec.rationale,
    })

with (OUT / "feed_taxonomy_adversarial_review.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(output_rows)

summary = {
    "reviewed_concepts": len(output_rows),
    "feed_material_direct_children": len(direct_feed),
    "supplement_descendants": len(supplement_cohort),
    "other_ingredients_descendants": len(other_cohort),
    "organic_acid_descendants": len(organic_acid_cohort),
    "structural_root_and_descendants": len(structural_cohort),
    "recommended_actions": dict(sorted(Counter(row["recommended_action"] for row in output_rows).items())),
    "recommended_axes": dict(sorted(Counter(row["recommended_axis"] for row in output_rows).items())),
    "evidence_states": dict(sorted(Counter(row["evidence_state"] for row in output_rows).items())),
    "explicit_holds": sum("hold" in row["recommended_action"] for row in output_rows),
}
(OUT / "feed_taxonomy_adversarial_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

print(json.dumps(summary, indent=2))
