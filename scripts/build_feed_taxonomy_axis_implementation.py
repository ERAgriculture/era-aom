#!/usr/bin/env python3
"""Implement approved feed-taxonomy axes while preserving evidence holds."""

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "livestock-staging"
REVIEW = ROOT / "review" / "livestock-v30"
V29 = ROOT / "review" / "livestock-v29" / "feed_taxonomy_adversarial_review.csv"
DATE = "2026-08-12"
REVIEWER = "Pete Steward"
ADR = "docs/decisions/0044-feed-taxonomy-axis-reclassification.md"
METHOD = "docs/methods/feed-taxonomy-governance.md"
EU_FEED = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009R0767"
EU_ADDITIVES = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32003R1831"
EU_CATALOGUE = "https://eur-lex.europa.eu/eli/reg/2013/68/oj/eng"
EU_WASTE = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32008L0098"
EU_ANIMAL_BYPRODUCTS = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009R1069"
AGROVOC_ADDITIVES = "https://agrovoc.fao.org/browse/agrovoc/en/page/c_2827"
AGROVOC_SUPPLEMENTS = "https://agrovoc.fao.org/browse/agrovoc/en/page/c_33996"
AGROVOC_ORGANIC_ACIDS = "https://agrovoc.fao.org/browse/agrovoc/en/page/c_5383"
FOODON_FACETS = "https://foodon.org/food-facets/"
FOODON_PROCESSES = "https://foodon.org/food-facets/food-transformation-process/"
FOODON_RELATIONS = "https://foodon.org/design/foodon-relations/"
MEGALAC = "https://www.megalac.com/resources-advice/fats-advice/64-rumenprotected-fats-calcium-salt-supplements"
ELANCOBAN = "https://efsa.onlinelibrary.wiley.com/doi/10.2903/j.efsa.2026.10123"
WHOLE_GRAIN = "https://wholegrainscouncil.org/definition-whole-grain"
OWL_NEGATIVE = "https://www.w3.org/TR/owl-syntax/#Negative_Object_Property_Assertions"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def fieldnames(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return csv.DictReader(handle).fieldnames


def write(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def upsert(path, key, additions):
    rows = read(path)
    keys = {row[key] for row in additions}
    assert len(keys) == len(additions)
    write(path, fieldnames(path), [row for row in rows if row[key] not in keys] + additions)


review_rows = read(V29)
assert len(review_rows) == 220
review_by_id = {row["concept_id"]: row for row in review_rows}
assert len(review_by_id) == len(review_rows)

supported_states = {
    "authority-supported", "catalogue-supported", "model-supported",
    "ontology-supported", "process-definition-supported",
    "product-evidence-supported",
}

new_specs = [
    ("FEED-TAXONOMY-ADDITIVES", "AOM_101135", "Feed additives", "Feed products intentionally added for a technological, sensory, nutritional, zootechnical, coccidiostatic, or histomonostatic function; authorization conditions require dated regulatory evidence.", "AOM_000328"),
    ("FEED-TAXONOMY-ADDITIVE-NUTRITIONAL", "AOM_101136", "Nutritional feed additives", "Feed-additive category for vitamins, trace-element compounds, amino acids, urea, and related authorized nutritional additive groups.", "AOM_101135"),
    ("FEED-TAXONOMY-ADDITIVE-ZOOTECHNICAL", "AOM_101137", "Zootechnical feed additives", "Feed-additive category for substances or preparations used to affect animal performance, digestibility, or gut flora under authorized conditions.", "AOM_101135"),
    ("FEED-TAXONOMY-ADDITIVE-TECHNOLOGICAL", "AOM_101138", "Technological feed additives", "Feed-additive category for substances or preparations used for technological functions in feed, including preservation and contaminant reduction where authorized.", "AOM_101135"),
    ("FEED-TAXONOMY-MINERAL-MATERIALS", "AOM_101139", "Mineral feed materials", "Mineral substances or products represented as feed materials; chemical composition and authorization as an additive require separate assertions.", "AOM_100850"),
    ("FEED-TAXONOMY-MINERAL-FORMULATIONS", "AOM_101140", "Mineral complementary feeds", "Formulated complementary feeds whose governed identity is a mineral block, lick, salt lick, or mineral mixture.", "AOM_001491"),
    ("FEED-TAXONOMY-VITAMIN-FORMULATIONS", "AOM_101141", "Vitamin premixtures and complementary feeds", "Multi-component vitamin preparations represented as premixtures or complementary feeds rather than single vitamin substances.", "AOM_001491"),
    ("FEED-TAXONOMY-HOLDS", "AOM_101142", "Feed classification holds", "Editorial grouping for active source terms whose feed product kind, chemical identity, intended use, safety, or regulatory class remains unresolved; membership asserts no feed-material, formulation, or additive class.", "AOM_000328"),
    ("FEED-TAXONOMY-COMPONENT-FRACTIONS", "AOM_101143", "Processed material fractions", "Material components or fractions produced or recovered through processing rather than one anatomical structure.", "AOM_101085"),
    ("FEED-TAXONOMY-CEREAL-FRACTIONS", "AOM_101144", "Cereal milling fractions", "Cereal-grain material fractions separated or recovered during milling, including bran and related fractions.", "AOM_101143"),
    ("FEED-TAXONOMY-BODY-SUBSTANCES", "AOM_101145", "Animal body substances", "Animal-derived body substances represented as feed-material components without treating them as connected anatomical structures.", "AOM_101085"),
    ("FEED-TAXONOMY-CHEMICAL-ROOT", "AOM_101146", "Feed chemical entities", "Chemical substances and constituent categories used to describe feed identity or composition independently of feed product kind or additive function.", "AOM_000328"),
    ("FEED-TAXONOMY-CHEMICAL-SUBSTANCES", "AOM_101147", "Feed chemical substances", "Chemically identified substances or substance groups encountered in feed data; intended feed use and additive authorization require separate assertions.", "AOM_101146"),
    ("FEED-TAXONOMY-ROLE-PRODUCT", "AOM_101148", "Feed product roles", "Economic or production-status roles borne by feed materials. By-product and waste roles are sibling categories; material identity, component, process, and legal eligibility for feed remain separate.", "AOM_101022"),
    ("FEED-TAXONOMY-ROLE-FUNCTIONAL", "AOM_101149", "Feed functional roles", "Functions borne by substances or products in feed, represented independently of their material, formulation, additive, or chemical identity.", "AOM_101022"),
    ("FEED-TAXONOMY-ROLE-EXPERIMENTAL", "AOM_101150", "Feed experimental roles", "Roles borne by substances or products because of their use in an experimental design or measurement method.", "AOM_101022"),
    ("FEED-TAXONOMY-ROLE-MARKER", "AOM_101151", "Digestibility-marker role", "Experimental role borne by a marker substance used to estimate digestibility or passage without making marker function its chemical identity.", "AOM_101150"),
    ("FEED-TAXONOMY-ROLE-FILLER", "AOM_101152", "Filler role", "Functional role borne by a material or product used to add bulk or carrier mass; bearer identity requires a separate assertion.", "AOM_101149"),
    ("FEED-TAXONOMY-COMPONENT-ENDOSPERM", "AOM_101153", "Endosperm", "Seed tissue that stores nutrient reserves and forms a retained component of whole cereal grain.", "AOM_101019"),
    ("FEED-TAXONOMY-COMPONENT-CROP-RESIDUE", "AOM_101154", "Composite crop-residue components", "Collective crop-residue components such as straw or stover that contain multiple anatomical structures.", "AOM_101085"),
    ("FEED-TAXONOMY-FORMULATION-MINERAL-VITAMIN", "AOM_101155", "Mineral and vitamin complementary feeds", "Formulated complementary feeds or mixtures containing governed mineral, vitamin, salt, or urea components.", "AOM_001491"),
]

assert [spec[1] for spec in new_specs] == [f"AOM_{number}" for number in range(101135, 101156)]
allocated_ids = {spec[1] for spec in new_specs}

all_labels = {}
for row in read(DATA / "labels.csv"):
    all_labels.setdefault(row["label"].casefold(), set()).add(row["concept_id"])
for row in read(DATA / "approved_new_concepts.csv"):
    all_labels.setdefault(row["preferred_label"].casefold(), set()).add(row["concept_id"])
for _, concept_id, label, _, _ in new_specs:
    collisions = all_labels.get(label.casefold(), set()) - {concept_id}
    assert not collisions, (concept_id, label, collisions)

new_path = DATA / "approved_new_concepts.csv"
new_rows = [
    row for row in read(new_path)
    if row["concept_id"] not in {"AOM_101068", "AOM_101109"} | allocated_ids
]
new_by_id = {row["concept_id"]: row for row in new_rows}

generated_updates = {
    "AOM_100987": ("Processed food by-products", "Feed-material category for former foodstuffs and processed-food production residues used as feed; product or waste role remains explicit.", "AOM_100850"),
    "AOM_100988": ("Untreated organic-waste feed classification holds", "Editorial grouping for untreated organic-waste source terms whose safety and regulatory suitability as feed remain unresolved.", "AOM_101142"),
    "AOM_100989": ("Microalgal feed materials", "Feed materials derived from microalgal biomass; source taxon and processing remain explicit.", "AOM_100850"),
    "AOM_101019": ("Anatomical components", "Biological anatomical structures represented as components of feed materials.", "AOM_101085"),
    "AOM_101022": ("Feed roles", "Product, functional, or experimental roles borne by feed-related materials, products, or substances independently of identity.", "AOM_000328"),
    "AOM_101055": ("Discarded-material waste role", "Waste role borne by material described as discarded or culled; lawful recovery or eligibility for feed requires separate evidence.", "AOM_101061"),
    "AOM_101056": ("Market-waste role", "Waste role borne by material removed from a market or retail stream; material identity, safety, and eligibility for feed remain separate.", "AOM_101061"),
    "AOM_101057": ("Offal by-product role", "By-product role borne by material described in source terminology as offal; exact animal or crop-derived material identity and component require separate assertions.", "AOM_101062"),
    "AOM_101058": ("Processing-waste role", "Waste role borne by material identified as waste from a processing operation; processing origin alone does not establish lawful feed use.", "AOM_101061"),
    "AOM_101059": ("Production-residue by-product role", "By-product role borne by a secondary residue retained from production or processing for another use; exact residue identity requires a separate assertion.", "AOM_101062"),
    "AOM_101060": ("Milling by-product role", "By-product role borne by a secondary milling output such as shorts; milling fraction identity and processing method remain separate.", "AOM_101062"),
    "AOM_101061": ("Waste role", "Product-status role borne by material identified as waste or discarded. Waste remains distinct from by-product status and does not establish eligibility for feed.", "AOM_101148"),
    "AOM_101062": ("By-product role", "Product role borne by a secondary output obtained alongside or remaining after production or processing of a principal product and retained for another use. Material identity and lawful feed use require separate assertions.", "AOM_101148"),
    "AOM_101063": ("Crop-residue by-product role", "By-product role borne by crop residue retained after harvest or processing for another use; anatomical or composite component identity remains separate.", "AOM_101062"),
    "AOM_101023": ("Primary chemical constituents", "Chemical substances or chemically defined fractions asserted as primary constituents of feed materials.", "AOM_101146"),
    "AOM_101085": ("Feed material components", "Anatomical structures, processed fractions, body substances, or collective material scopes represented as components of feed materials.", "AOM_000328"),
    "AOM_101086": ("Whole-crop composition", "Composition state indicating retention of the harvested whole-crop scope rather than one component part.", "AOM_101115"),
    "AOM_101103": ("Blood component", "Animal body substance represented as a feed-material component; distinct from Blood feed material.", "AOM_101145"),
    "AOM_101104": ("Bran", "Cereal outer-layer milling fraction with variable attached endosperm; represented as a processed material fraction.", "AOM_101144"),
    "AOM_101105": ("Stover", "Composite crop-residue component remaining after grain or seed harvest; not one anatomical structure.", "AOM_101154"),
    "AOM_101106": ("Straw", "Composite crop-residue component consisting mainly of dried cereal or legume stems and leaves after harvest; not one anatomical structure.", "AOM_101154"),
    "AOM_101110": ("Whole-grain composition", "Component-retention state in which bran, germ, and endosperm remain in characteristic proportions independently of particle-size reduction.", "AOM_101115"),
    "AOM_101115": ("Native-component retention states", "Composition states defined by positive retention of native material components or chemical constituents.", "AOM_000196"),
    "AOM_101130": ("Feed component separation processes", "Feed processes whose objective includes removing, separating, or recovering a material component or fraction.", "AOM_000845"),
    "AOM_101134": ("Native-fat-retained composition", "Component-retention state indicating positive retention of native fat; no measured concentration or inferred absence of defatting is asserted.", "AOM_101115"),
}
for concept_id, (label, _, _) in generated_updates.items():
    collisions = all_labels.get(label.casefold(), set()) - {concept_id}
    assert not collisions, (concept_id, label, collisions)
for concept_id, (label, scope, parent) in generated_updates.items():
    row = new_by_id[concept_id]
    row.update({
        "preferred_label": label,
        "scope_note": scope,
        "broader_id": parent,
        "derived_path": f"Governed feed taxonomy/{label}",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": "Reclassified through complete feed-taxonomy axis review.",
    })

product_role_ids = {
    row["concept_id"] for row in read(DATA / "approved_ingredient_facet_concepts.csv")
    if row["facet"] == "product_role"
} - {"AOM_101022", "AOM_101079"} - allocated_ids
for concept_id in product_role_ids:
    row = new_by_id[concept_id]
    row["derived_path"] = f"Governed feed taxonomy/Feed roles/Feed product roles/{row['preferred_label']}"
for concept_id in {"AOM_101079"}:
    row = new_by_id[concept_id]
    row["broader_id"] = "AOM_101149"
    row["derived_path"] = f"Governed feed taxonomy/Feed roles/Feed functional roles/{row['preferred_label']}"

for case_id, concept_id, label, scope, parent in new_specs:
    new_rows.append({
        "case_id": case_id,
        "concept_id": concept_id,
        "preferred_label": label,
        "scope_note": scope,
        "broader_id": parent,
        "hierarchy_level": "5",
        "derived_path": f"Governed feed taxonomy/{label}",
        "child_ids": "",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": "Collision-audited concept required by approved feed-taxonomy axis implementation.",
    })
write(new_path, fieldnames(new_path), new_rows)

registry_path = DATA / "livestock_id_registry.csv"
registry_rows = [
    row for row in read(registry_path)
    if row["concept_id"] not in allocated_ids
]
registry_by_id = {row["concept_id"]: row for row in registry_rows}
for retired_id, rationale in {
    "AOM_101068": "Retired before publication: brewhouse processing is an upstream source-production bundle, not a governed feed treatment.",
    "AOM_101109": "Retired before publication: material integrity replaced by positive native-component retention states.",
}.items():
    registry_by_id[retired_id].update({
        "status": "retired-before-publication",
        "allocation_basis": rationale + " Identifier must not be reassigned.",
    })
for concept_id, (label, _, _) in generated_updates.items():
    if concept_id in registry_by_id:
        registry_by_id[concept_id]["preferred_label"] = label
for case_id, concept_id, label, _, _ in new_specs:
    registry_rows.append({
        "concept_id": concept_id,
        "allocated_on": DATE,
        "status": "allocated",
        "preferred_label": label,
        "case_id": case_id,
        "allocator": REVIEWER,
        "allocation_basis": "Sequential allocation after global preferred, alternative, hidden, deprecated, and external-label collision audit; approved under ADR 0044.",
    })
write(registry_path, fieldnames(registry_path), registry_rows)

label_corrections = [
    ("FEED-TAXONOMY-HOLD-SUPPLEMENT", "AOM_000736", "Supplement", "Unresolved supplement classifications"),
    ("FEED-TAXONOMY-HOLD-OTHER", "AOM_000781", "Other Ingredients", "Unresolved other-ingredient classifications"),
    ("FEED-TAXONOMY-HOLD-MINERAL", "AOM_000779", "Mineral", "Unresolved mineral classifications"),
    ("FEED-TAXONOMY-RUMEN-FAT", "AOM_006334", "Protected Fat", "Rumen-protected fat feed materials"),
    ("FEED-TAXONOMY-COCCIDIOSTATS", "AOM_004433", "Anti-coccidia", "Coccidiostats and histomonostats"),
    ("FEED-TAXONOMY-STARCH-MATERIAL", "AOM_001832", "Starch", "Starch feed material"),
    ("FEED-TAXONOMY-MIXTURE", "AOM_000795", "Mixture", "Mineral and vitamin feed mixtures"),
]
approved_label_by_id = {
    concept_id: new_label
    for _, concept_id, _, new_label in label_corrections
}
approved_label_by_id.update({
    concept_id: label
    for concept_id, (label, _, _) in generated_updates.items()
})
correction_rows = [{
    "case_id": case_id,
    "concept_id": concept_id,
    "old_label": old_label,
    "new_label": new_label,
    "language": "en",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": ADR,
    "rationale": "Label exposes approved axis or unresolved-hold status without changing stable identity.",
} for case_id, concept_id, old_label, new_label in label_corrections]
upsert(DATA / "approved_label_corrections.csv", "concept_id", correction_rows)

aliases = [
    ("AOM_100988", "Untreated organic-waste feed materials"),
    ("AOM_100989", "Microalgae supplements"),
    ("AOM_101019", "Feed-material anatomical parts"),
    ("AOM_101022", "Feed-material product roles"),
    ("AOM_101055", "Discard role"),
    ("AOM_101057", "Offal role"),
    ("AOM_101059", "Residue role"),
    ("AOM_101060", "Milling-shorts role"),
    ("AOM_101063", "Crop-residue role"),
    ("AOM_101086", "Whole crop"),
    ("AOM_101110", "Whole-grain integrity"),
    ("AOM_101115", "Composition states"),
    ("AOM_101130", "Feed separation processes"),
    ("AOM_101134", "Full-fat composition"),
]
label_addition_path = DATA / "approved_label_additions.csv"
existing_additions = [
    row for row in read(label_addition_path)
    if not row["case_id"].startswith("FEED-TAXONOMY-ALIAS-")
    and row["concept_id"] not in {"AOM_101068", "AOM_101109"}
]
alias_rows = [{
    "case_id": f"FEED-TAXONOMY-ALIAS-{concept_id}",
    "concept_id": concept_id,
    "language": "en",
    "label_type": "alt",
    "label": label,
    "status": "approved",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": ADR,
    "rationale": "Preserves prior public-facing label after approved axis reclassification.",
} for concept_id, label in aliases]
write(label_addition_path, fieldnames(label_addition_path), existing_additions + alias_rows)

retirement_rows = [{
    "case_id": f"FEED-TAXONOMY-RETIRE-{concept_id}",
    "concept_id": concept_id,
    "preferred_label": review_by_id[concept_id]["preferred_label"],
    "status": "approved",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": f"{ADR};{METHOD}",
    "rationale": rationale,
} for concept_id, rationale in {
    "AOM_000531": "Legacy schema field replaced by aom:ingredientName.",
    "AOM_000532": "Legacy schema field replaced by reviewed material-component relations.",
    "AOM_000533": "Legacy schema field replaced by aom:sourceTaxon.",
    "AOM_000534": "Legacy schema field replaced by quantified ingredient-component proportion.",
    "AOM_000535": "Legacy schema field replaced by explicit source relations.",
    "AOM_000736": "Catch-all Supplement branch emptied through approved migrations and explicit hold routing.",
    "AOM_000781": "Catch-all Other Ingredients branch emptied through approved migrations and explicit hold routing.",
    "AOM_001507": "Source-data unknown value is not an ontology concept.",
}.items()]
write(DATA / "approved_concept_retirements.csv", list(retirement_rows[0]), retirement_rows)

deprecation_path = DATA / "approved_deprecations.csv"
existing_deprecations = [
    row for row in read(deprecation_path)
    if row["deprecated_id"] not in {"AOM_000745", "AOM_000747", "AOM_001917"}
]
role_deprecations = [
    ("FEED-TAXONOMY-BINDER-ROLE", "AOM_000745", "AOM_101079", "Binder"),
    ("FEED-TAXONOMY-MARKER-ROLE", "AOM_000747", "AOM_101151", "Digestibility Marker"),
    ("FEED-TAXONOMY-FILLER-ROLE", "AOM_001917", "AOM_101152", "Unspecified Filler"),
]
existing_deprecations += [{
    "case_id": case_id,
    "deprecated_id": deprecated_id,
    "replacement_id": replacement_id,
    "preferred_label": preferred_label,
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": ADR,
    "rationale": "Legacy material-like category denotes a role now represented on an independent role axis.",
} for case_id, deprecated_id, replacement_id, preferred_label in role_deprecations]
write(deprecation_path, fieldnames(deprecation_path), existing_deprecations)

desired_parent = {
    "AOM_000736": "AOM_101142",
    "AOM_000781": "AOM_101142",
    "AOM_000779": "AOM_101142",
    "AOM_000737": "AOM_101136",
    "AOM_000751": "AOM_101137",
    "AOM_000793": "AOM_101136",
    "AOM_001091": "AOM_101138",
    "AOM_001749": "AOM_101136",
    "AOM_003577": "AOM_001491",
    "AOM_003889": "AOM_101142",
    "AOM_004433": "AOM_101135",
    "AOM_006334": "AOM_100850",
    "AOM_006339": "AOM_101138",
    "AOM_001068": "AOM_101147",
    "AOM_001571": "AOM_101023",
    "AOM_001577": "AOM_101023",
    "AOM_000807": "AOM_101137",
    "AOM_000809": "AOM_101147",
    "AOM_000811": "AOM_101142",
    "AOM_003076": "AOM_101137",
    "AOM_003100": "AOM_100853",
    "AOM_006389": "AOM_101147",
    "AOM_000780": "AOM_101142",
    "AOM_000782": "AOM_101142",
    "AOM_000783": "AOM_001491",
    "AOM_001500": "AOM_101142",
    "AOM_001824": "AOM_101142",
    "AOM_001825": "AOM_101142",
    "AOM_001832": "AOM_100850",
    "AOM_001865": "AOM_101147",
    "AOM_001866": "AOM_100850",
    "AOM_001867": "AOM_101142",
    "AOM_001868": "AOM_101142",
    "AOM_001869": "AOM_101142",
    "AOM_001921": "AOM_101142",
    "AOM_001922": "AOM_100850",
    "AOM_002191": "AOM_101139",
    "AOM_003172": "AOM_101142",
    "AOM_003203": "AOM_101142",
    "AOM_006241": "AOM_100850",
    "AOM_006349": "AOM_100850",
    "AOM_000753": "AOM_101139",
    "AOM_000795": "AOM_101155",
    "AOM_001831": "AOM_101142",
}

mineral_materials = {
    "AOM_000755", "AOM_000757", "AOM_000758", "AOM_000760", "AOM_000768",
    "AOM_000772", "AOM_000777", "AOM_001367", "AOM_001368", "AOM_001369",
    "AOM_001370", "AOM_001371", "AOM_001372", "AOM_001378", "AOM_001427",
    "AOM_001487", "AOM_001746", "AOM_002074", "AOM_003760", "AOM_006124",
    "AOM_006125",
}
mineral_formulations = {
    "AOM_000764", "AOM_000765", "AOM_000766", "AOM_001415", "AOM_001773",
    "AOM_003084", "AOM_003201",
}
vitamin_formulations = {"AOM_000791", "AOM_001505", "AOM_001839"}
mineral_vitamin_formulations = {"AOM_000794", "AOM_001428", "AOM_001431"}
for concept_id in mineral_materials:
    if concept_id in review_by_id:
        desired_parent[concept_id] = "AOM_101139"
for concept_id in mineral_formulations:
    desired_parent[concept_id] = "AOM_101140"
for concept_id in vitamin_formulations:
    desired_parent[concept_id] = "AOM_101141"
for concept_id in mineral_vitamin_formulations:
    desired_parent[concept_id] = "AOM_101155"

mineral_holds = {
    "AOM_000754", "AOM_000756", "AOM_000759", "AOM_000763", "AOM_000770",
    "AOM_000774", "AOM_000776", "AOM_000778", "AOM_001066", "AOM_001067",
    "AOM_001417", "AOM_001418", "AOM_001506", "AOM_001509", "AOM_001872",
    "AOM_006331",
}
for concept_id in mineral_holds:
    desired_parent[concept_id] = "AOM_000779"

vitamin_holds = {
    "AOM_000787", "AOM_000788", "AOM_000789", "AOM_000790", "AOM_001376",
    "AOM_001834",
}
for concept_id in vitamin_holds:
    desired_parent[concept_id] = "AOM_101142"

protein_holds = {"AOM_001572", "AOM_001870"}
for concept_id in protein_holds:
    desired_parent[concept_id] = "AOM_101142"

binder_direct = {
    row["concept_id"] for row in review_rows
    if row["current_parent_ids"] == "AOM_000745"
}
for concept_id in binder_direct:
    desired_parent[concept_id] = "AOM_101142"
desired_parent["AOM_000746"] = "AOM_101147"

hierarchy_path = DATA / "approved_hierarchy_revisions.csv"
superseded_prefixes = (
    "FEED-TAXONOMY-", "PROCESS-BREWHOUSE-", "PROCESS-RENDERING-SEPARATION",
)
hierarchy_rows = [
    row for row in read(hierarchy_path)
    if not row["case_id"].startswith(superseded_prefixes)
]
generated_direct_updates = set(generated_updates)
for concept_id, target_parent in sorted(desired_parent.items()):
    if concept_id in generated_direct_updates:
        continue
    current_parents = review_by_id[concept_id]["current_parent_ids"].split(";")
    if target_parent in current_parents:
        continue
    assert len(current_parents) == 1, (concept_id, current_parents, target_parent)
    hierarchy_rows.append({
        "case_id": f"FEED-TAXONOMY-MOVE-{concept_id}",
        "child_id": concept_id,
        "remove_parent_id": current_parents[0],
        "add_parent_id": target_parent,
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": ADR,
        "rationale": "Move from mixed catch-all or incorrect axis to approved independent taxonomy axis.",
    })
write(hierarchy_path, fieldnames(hierarchy_path), hierarchy_rows)

facet_path = DATA / "approved_ingredient_facet_concepts.csv"
facet_rows = [
    row for row in read(facet_path)
    if row["concept_id"] not in {"AOM_101068", "AOM_101109"} | {
        "AOM_101143", "AOM_101144", "AOM_101145", "AOM_101148", "AOM_101149",
        "AOM_101150", "AOM_101151", "AOM_101152", "AOM_101153", "AOM_101154",
    }
]
facet_by_id = {row["concept_id"]: row for row in facet_rows}
facet_updates = {
    "AOM_101019": ("Anatomical components", "anatomical_component", "aom:materialComponent", "aom:FeedMaterialPartCategory", "facet_root"),
    "AOM_101022": ("Feed roles", "feed_role", "aom:role", "aom:FeedRole", "facet_root"),
    "AOM_101023": ("Primary chemical constituents", "chemical_constituent", "aom:primaryConstituent", "aom:ChemicalConstituent", "facet_root"),
    "AOM_101086": ("Whole-crop composition", "component_retention_state", "aom:compositionState", "aom:ComponentRetentionState", "facet_value"),
    "AOM_101103": ("Blood component", "material_component", "aom:materialComponent", "aom:FeedMaterialComponent", "facet_value"),
    "AOM_101104": ("Bran", "material_component", "aom:materialComponent", "aom:FeedMaterialComponent", "facet_value"),
    "AOM_101105": ("Stover", "material_component", "aom:materialComponent", "aom:FeedMaterialComponent", "facet_value"),
    "AOM_101106": ("Straw", "material_component", "aom:materialComponent", "aom:FeedMaterialComponent", "facet_value"),
    "AOM_101110": ("Whole-grain composition", "component_retention_state", "aom:compositionState", "aom:ComponentRetentionState", "facet_value"),
    "AOM_101115": ("Native-component retention states", "component_retention_state", "aom:compositionState", "aom:ComponentRetentionState", "facet_root"),
    "AOM_101116": ("Whole-milk composition", "component_retention_state", "aom:compositionState", "aom:ComponentRetentionState", "facet_value"),
    "AOM_101130": ("Feed component separation processes", "processing_method", "aom:processingMethod", "aom:ProcessingMethod", "facet_value"),
    "AOM_101134": ("Native-fat-retained composition", "component_retention_state", "aom:compositionState", "aom:ComponentRetentionState", "facet_value"),
    "AOM_101079": ("Binder role", "functional_role", "aom:functionalRole", "aom:FeedFunctionalRole", "facet_value"),
}
for concept_id, values in facet_updates.items():
    row = facet_by_id[concept_id]
    row.update(dict(zip(
        ["preferred_label", "facet", "target_property", "value_class", "concept_role"], values
    )))
    row.update({"review_date": DATE, "evidence": ADR})
for row in facet_rows:
    if row["concept_id"] in product_role_ids:
        row.update({
            "preferred_label": generated_updates[row["concept_id"]][0],
            "facet": "product_role",
            "target_property": "aom:productRole",
            "value_class": "aom:ProductRole",
            "review_date": DATE,
            "evidence": ADR,
        })

new_facet_rows = [
    ("AOM_101143", "Processed material fractions", "material_component", "aom:materialComponent", "aom:FeedMaterialComponent", "facet_root"),
    ("AOM_101144", "Cereal milling fractions", "material_component", "aom:materialComponent", "aom:FeedMaterialComponent", "facet_root"),
    ("AOM_101145", "Animal body substances", "material_component", "aom:materialComponent", "aom:FeedMaterialComponent", "facet_root"),
    ("AOM_101148", "Feed product roles", "product_role", "aom:productRole", "aom:ProductRole", "facet_root"),
    ("AOM_101149", "Feed functional roles", "functional_role", "aom:functionalRole", "aom:FeedFunctionalRole", "facet_root"),
    ("AOM_101150", "Feed experimental roles", "experimental_role", "aom:experimentalRole", "aom:ExperimentalFeedRole", "facet_root"),
    ("AOM_101151", "Digestibility-marker role", "experimental_role", "aom:experimentalRole", "aom:ExperimentalFeedRole", "facet_value"),
    ("AOM_101152", "Filler role", "functional_role", "aom:functionalRole", "aom:FeedFunctionalRole", "facet_value"),
    ("AOM_101153", "Endosperm", "anatomical_component", "aom:materialComponent", "aom:FeedMaterialPartCategory", "facet_value"),
    ("AOM_101154", "Composite crop-residue components", "material_component", "aom:materialComponent", "aom:FeedMaterialComponent", "facet_root"),
]
facet_rows += [{
    "concept_id": concept_id,
    "preferred_label": label,
    "facet": facet,
    "target_property": prop,
    "value_class": value_class,
    "concept_role": role,
    "status": "approved",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": ADR,
} for concept_id, label, facet, prop, value_class, role in new_facet_rows]
write(facet_path, fieldnames(facet_path), facet_rows)

decomposition_path = DATA / "approved_ingredient_component_decompositions.csv"
decomposition_rows = [
    row for row in read(decomposition_path)
    if row["target_concept_id"] not in {"AOM_101068", "AOM_101109"}
]
for row in decomposition_rows:
    if row["target_concept_id"] in generated_updates:
        row["target_label"] = generated_updates[row["target_concept_id"]][0]
write(decomposition_path, fieldnames(decomposition_path), decomposition_rows)

mapping_path = DATA / "approved_ingredient_component_value_mappings.csv"
mapping_rows = read(mapping_path)
for row in mapping_rows:
    if row["target_concept_id"] in generated_updates:
        row["target_label"] = generated_updates[row["target_concept_id"]][0]
write(mapping_path, fieldnames(mapping_path), mapping_rows)

material_tables = [
    "approved_feed_material_facets.csv",
    "approved_generated_feed_material_facets.csv",
    "approved_hard_tail_feed_material_facets.csv",
    "approved_structural_feed_material_facets.csv",
]
target_updates = {
    "AOM_101086": ("aom:compositionState", "Whole-crop composition"),
    "AOM_101103": ("aom:materialComponent", "Blood component"),
    "AOM_101105": ("aom:materialComponent", "Stover"),
    "AOM_101106": ("aom:materialComponent", "Straw"),
    "AOM_101110": ("aom:compositionState", "Whole-grain composition"),
    "AOM_101134": ("aom:compositionState", "Native-fat-retained composition"),
    **{
        concept_id: ("aom:productRole", label)
        for concept_id, (label, _, _) in generated_updates.items()
        if concept_id in product_role_ids
    },
}
for name in material_tables:
    path = DATA / name
    rows = read(path)
    for row in rows:
        if row["target_concept_id"] in target_updates:
            row["target_property"], row["target_label"] = target_updates[row["target_concept_id"]]
    write(path, fieldnames(path), rows)

role_assertions = []
binder_ids = {
    row["concept_id"] for row in review_rows
    if row["current_top_group_ids"] == "AOM_000745" and row["concept_id"] != "AOM_000745"
}
for concept_id in sorted(binder_ids):
    role_assertions.append({
        "case_id": f"FEED-TAXONOMY-BINDER-{concept_id}",
        "subject_id": concept_id,
        "relation_property": "aom:functionalRole",
        "role_concept_id": "AOM_101079",
        "role_class": "aom:FeedFunctionalRole",
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": "era_master_sheet.xlsx#AOM;" + ADR,
        "rationale": "Legacy Binder placement supports functional role while bearer product kind remains held where item evidence is insufficient.",
    })
for concept_id in ["AOM_000746", "AOM_002072"]:
    role_assertions.append({
        "case_id": f"FEED-TAXONOMY-MARKER-{concept_id}",
        "subject_id": concept_id,
        "relation_property": "aom:experimentalRole",
        "role_concept_id": "AOM_101151",
        "role_class": "aom:ExperimentalFeedRole",
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": "era_master_sheet.xlsx#AOM;" + ADR,
        "rationale": "Digestibility-marker use is experimental role independent of chromium-oxide chemical identity and processing state.",
    })
write(DATA / "approved_feed_role_assertions.csv", list(role_assertions[0]), role_assertions)

role_review_specs = [
    ("AOM_101148", "Feed product roles", "Feed product roles", "AOM_101022", f"{EU_WASTE};{ADR};{METHOD}", "Separate product-status roles from material, component, process, functional, and experimental axes."),
    ("AOM_101062", "By-product role", "By-product role", "AOM_101148", f"{EU_WASTE};{EU_CATALOGUE};{ADR};{METHOD}", "Keep by-product and waste as sibling roles; secondary role does not replace material identity."),
    ("AOM_101061", "Waste role", "Waste role", "AOM_101148", f"{EU_WASTE};{ADR};{METHOD}", "Waste status is not a subtype of by-product status and does not establish feed eligibility."),
    ("AOM_101055", "Discard role", "Discarded-material waste role", "AOM_101061", f"{EU_WASTE};era_master_sheet.xlsx#AOM;{ADR};{METHOD}", "Discard terminology belongs beneath waste role; source material identity remains separate."),
    ("AOM_101056", "Market-waste role", "Market-waste role", "AOM_101061", f"{EU_WASTE};era_master_sheet.xlsx#AOM;{ADR};{METHOD}", "Market waste is a source-specific waste specialization, not a by-product subtype."),
    ("AOM_101058", "Processing-waste role", "Processing-waste role", "AOM_101061", f"{EU_WASTE};era_master_sheet.xlsx#AOM;{ADR};{METHOD}", "Processing waste remains under waste unless evidence supports by-product status."),
    ("AOM_101057", "Offal role", "Offal by-product role", "AOM_101062", f"{EU_ANIMAL_BYPRODUCTS};era_master_sheet.xlsx#AOM;{ADR};{METHOD}", "Offal wording identifies secondary-output role; exact animal or crop material identity must remain separate."),
    ("AOM_101059", "Residue role", "Production-residue by-product role", "AOM_101062", f"{EU_CATALOGUE};era_master_sheet.xlsx#AOM;{ADR};{METHOD}", "Residues retained as feed are modeled as by-product roles while residue identity and process provenance remain separate."),
    ("AOM_101060", "Milling-shorts role", "Milling by-product role", "AOM_101062", f"{EU_CATALOGUE};era_master_sheet.xlsx#AOM;{ADR};{METHOD}", "Shorts is a milling-fraction identity; role assertion records only secondary-output status."),
    ("AOM_101063", "Crop-residue role", "Crop-residue by-product role", "AOM_101062", f"{EU_CATALOGUE};era_master_sheet.xlsx#AOM;{ADR};{METHOD}", "Crop-residue component identity remains independent from secondary-output role."),
]
role_review_rows = [{
    "concept_id": concept_id,
    "previous_label": previous_label,
    "approved_label": approved_label,
    "semantic_axis": "product_role",
    "target_parent_id": parent_id,
    "status": "approved",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": evidence,
    "rationale": rationale,
} for concept_id, previous_label, approved_label, parent_id, evidence, rationale in role_review_specs]
write(REVIEW / "feed_product_role_review.csv", list(role_review_rows[0]), role_review_rows)

retention_relations = [
    ("FEED-TAXONOMY-WHOLE-GRAIN-BRAN", "AOM_101110", "aom:retainsMaterialComponent", "AOM_101104", "aom:FeedMaterialComponent", "Whole-grain composition positively retains bran."),
    ("FEED-TAXONOMY-WHOLE-GRAIN-GERM", "AOM_101110", "aom:retainsMaterialComponent", "AOM_101029", "aom:FeedMaterialPartCategory", "Whole-grain composition positively retains germ."),
    ("FEED-TAXONOMY-WHOLE-GRAIN-ENDOSPERM", "AOM_101110", "aom:retainsMaterialComponent", "AOM_101153", "aom:FeedMaterialPartCategory", "Whole-grain composition positively retains endosperm."),
    ("FEED-TAXONOMY-WHOLE-MILK-FAT", "AOM_101116", "aom:retainsChemicalConstituent", "AOM_101066", "aom:ChemicalConstituent", "Whole-milk composition positively retains native milk fat."),
    ("FEED-TAXONOMY-NATIVE-FAT", "AOM_101134", "aom:retainsChemicalConstituent", "AOM_101066", "aom:ChemicalConstituent", "Native-fat-retained composition positively retains native fat."),
]
retention_rows = [{
    "case_id": case_id,
    "state_concept_id": state_id,
    "relation_property": prop,
    "retained_concept_id": target_id,
    "retained_class": target_class,
    "status": "approved",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": f"{WHOLE_GRAIN};{OWL_NEGATIVE};{ADR}",
    "rationale": rationale,
} for case_id, state_id, prop, target_id, target_class, rationale in retention_relations]
write(DATA / "approved_component_retention_relations.csv", list(retention_rows[0]), retention_rows)

feed_material_ids = mineral_materials | {
    "AOM_000753", "AOM_001497", "AOM_001827", "AOM_001829", "AOM_001830",
    "AOM_001832", "AOM_001838", "AOM_001866", "AOM_001922", "AOM_002191",
    "AOM_002200", "AOM_003829", "AOM_006241", "AOM_006349", "AOM_006364",
}
feed_formulation_ids = mineral_formulations | vitamin_formulations | mineral_vitamin_formulations | {
    "AOM_000783", "AOM_000794", "AOM_000795", "AOM_003577",
}
feed_additive_ids = {
    "AOM_000738", "AOM_000739", "AOM_000740", "AOM_000748", "AOM_000749",
    "AOM_000750", "AOM_001377", "AOM_001433", "AOM_001579", "AOM_001749",
    "AOM_003747", "AOM_003749", "AOM_003878", "AOM_003994", "AOM_006114",
}

classification_rows = []
for row in review_rows:
    concept_id = row["concept_id"]
    evidence_state = row["evidence_state"]
    if evidence_state == "outside-current-defect":
        implementation_status = "outside-scope"
        status = "reviewed"
        semantic_class = "aom:FeedMaterial"
    elif concept_id in feed_material_ids:
        implementation_status = "implemented"
        status = "approved"
        semantic_class = "aom:FeedMaterial"
    elif concept_id in feed_formulation_ids:
        implementation_status = "implemented"
        status = "approved"
        semantic_class = "aom:FeedFormulation"
    elif concept_id in feed_additive_ids:
        implementation_status = "implemented"
        status = "approved"
        semantic_class = "aom:FeedAdditive"
    elif evidence_state not in supported_states:
        implementation_status = "hold"
        status = "hold"
        semantic_class = "aom:Feed" if row["review_scope"] in {"supplement_descendant", "other_ingredients_descendant"} else ""
    else:
        implementation_status = "implemented-structural"
        status = "approved"
        semantic_class = ""
    classification_rows.append({
        "concept_id": concept_id,
        "preferred_label": approved_label_by_id.get(concept_id, row["preferred_label"]),
        "implementation_status": implementation_status,
        "semantic_class": semantic_class,
        "target_parent_id": desired_parent.get(concept_id, generated_updates.get(concept_id, ("", "", ""))[2]),
        "status": status,
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{row['evidence_state']};{ADR};{METHOD}",
        "rationale": row["rationale"],
    })
write(DATA / "approved_feed_taxonomy_classifications.csv", list(classification_rows[0]), classification_rows)

chemical_substance_ids = {
    "AOM_000737", "AOM_000738", "AOM_000739", "AOM_000740", "AOM_000746",
    "AOM_000808", "AOM_000809", "AOM_001068", "AOM_001069", "AOM_001377",
    "AOM_001433", "AOM_001749", "AOM_001865", "AOM_002072", "AOM_003878",
    "AOM_006389", "AOM_101147",
}
chemical_constituent_ids = {"AOM_001571", "AOM_001577", "AOM_101023"}
semantic_type_rows = [{
    "case_id": f"FEED-TAXONOMY-TYPE-{concept_id}",
    "concept_id": concept_id,
    "semantic_class": (
        "aom:FeedChemicalEntity" if concept_id == "AOM_101146"
        else "aom:ChemicalConstituent" if concept_id in chemical_constituent_ids
        else "aom:ChemicalSubstance"
    ),
    "status": "approved",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": f"{ADR};{METHOD}",
    "rationale": "Chemical identity is represented independently of feed product kind and additive function.",
} for concept_id in sorted({"AOM_101146"} | chemical_substance_ids | chemical_constituent_ids)]
write(DATA / "approved_concept_semantic_types.csv", list(semantic_type_rows[0]), semantic_type_rows)

definition_path = DATA / "approved_definition_overrides.csv"
write(
    definition_path,
    fieldnames(definition_path),
    [
        row for row in read(definition_path)
        if row["concept_id"] not in {"AOM_101068", "AOM_101109"}
    ],
)
definition_rows = [{
    "concept_id": concept_id,
    "language": "en",
    "definition": definition,
    "definition_method": "feed_taxonomy_axis_definition_replacement",
    "status": "approved",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": f"{ADR};{METHOD}",
    "rationale": "Definition records approved axis, evidence boundary, and non-entailments.",
} for concept_id, definition in {
    **{concept_id: scope for _, concept_id, _, scope, _ in new_specs},
    **{concept_id: scope for concept_id, (_, scope, _) in generated_updates.items()},
    "AOM_000736": "Deprecated legacy Supplement catch-all; resolved descendants moved to feed-material, formulation, additive, or chemical axes and unresolved descendants routed to explicit holds.",
    "AOM_000781": "Deprecated legacy Other Ingredients catch-all; resolved descendants moved to evidence-backed axes and unresolved descendants routed to explicit holds.",
    "AOM_000779": "Editorial grouping for former mineral-supplement terms whose chemical identity, product kind, or additive authorization remains unresolved.",
    "AOM_006334": "Feed-material category for fat products whose rumen protection is supported by product or process evidence; drying, physical form, and feeding rate require separate assertions.",
    "AOM_004433": "Feed-additive category for coccidiostats and histomonostats under applicable authorization conditions.",
    "AOM_001832": "Starch represented as a feed material; Starch constituent remains a separate chemical-constituent concept.",
    "AOM_000795": "Formulated mineral and vitamin feed mixtures; individual components and proportions require separate assertions.",
}.items()]
upsert(definition_path, "concept_id", definition_rows)

evidence_rows = [
    ("EV-FEED-PRODUCT-KINDS", "Regulation (EC) No 767/2009", "regulation", EU_FEED, "Separates feed materials, compound feeds, complete feeds, and complementary feeds.", "Does not classify every legacy AOM product label."),
    ("EV-FEED-ADDITIVE-CATEGORIES", "Regulation (EC) No 1831/2003", "regulation", EU_ADDITIVES, "Defines technological, sensory, nutritional, zootechnical, coccidiostat, and histomonostat additive categories.", "Authorization remains substance, preparation, use, species, and date specific."),
    ("EV-FEED-MATERIAL-CATALOGUE", "Commission Regulation (EU) No 68/2013", "regulation", EU_CATALOGUE, "Supports mineral feed materials, glycerine, former foodstuffs, and processing definitions.", "Catalogue inclusion does not prove identity for ambiguous brands or waste streams."),
    ("EV-WASTE-BYPRODUCT-DISTINCTION", "Directive 2008/98/EC on waste", "regulation", EU_WASTE, "Distinguishes qualifying by-products from waste and defines waste around discard status.", "Legal status is jurisdictional and fact-specific; a source label alone cannot establish compliance."),
    ("EV-ANIMAL-BYPRODUCTS", "Regulation (EC) No 1069/2009", "regulation", EU_ANIMAL_BYPRODUCTS, "Defines animal by-products and derived products separately from generic waste and material identity.", "Does not cover plant offal terminology or authorize a material for feed."),
    ("EV-AGROVOC-ADDITIVES", "AGROVOC feed additives", "authority vocabulary", AGROVOC_ADDITIVES, "Separates feed-additive use from ordinary feed consumption.", "Broad vocabulary scope does not replace regulatory authorization."),
    ("EV-AGROVOC-SUPPLEMENTS", "AGROVOC supplements", "authority vocabulary", AGROVOC_SUPPLEMENTS, "Defines supplement by use with another feed, supporting role/formulation treatment rather than material identity.", "Does not classify every product called supplement."),
    ("EV-AGROVOC-ORGANIC-ACIDS", "AGROVOC organic acids", "authority vocabulary", AGROVOC_ORGANIC_ACIDS, "Places organic acids on a chemical identity axis.", "Intended additive function requires separate evidence."),
    ("EV-FOODON-FACETS", "FoodOn food facets", "ontology", FOODON_FACETS, "Supports separation of material, anatomy, chemical, quality, and process axes.", "FoodOn scope is food-system wide and requires AOM-specific adaptation."),
    ("EV-FOODON-PROCESSES", "FoodOn transformation processes", "ontology", FOODON_PROCESSES, "Supports process objective and component-separation modelling.", "Does not prove a process was applied to a specific AOM material."),
    ("EV-FOODON-RELATIONS", "FoodOn relations", "ontology", FOODON_RELATIONS, "Supports output/provenance relations distinct from processing applied to a feed.", "AOM does not yet publish upstream brewing provenance assertions."),
    ("EV-MEGALAC", "Megalac product evidence", "manufacturer", MEGALAC, "Supports calcium-salt rumen-protected fat product identity.", "Manufacturer evidence applies to named product, not every protected-fat term."),
    ("EV-ELANCOBAN", "EFSA Elancoban assessment", "regulatory assessment", ELANCOBAN, "Supports monensin-sodium coccidiostatic feed-additive identity.", "Authorization conditions remain dated and jurisdiction specific."),
    ("EV-WHOLE-GRAIN", "Whole Grains Council definition", "industry definition", WHOLE_GRAIN, "Supports bran, germ, and endosperm retention despite grinding.", "Industry definition is used for component-retention semantics, not regulatory feed claims."),
    ("EV-OWL-OPEN-WORLD", "OWL 2 structural specification", "standard", OWL_NEGATIVE, "Supports explicit negative assertions and prevents treating missing process assertions as negative facts.", "Positive retained-component statements still require source evidence."),
]
evidence_register = [{
    "evidence_id": evidence_id,
    "title": title,
    "source_type": source_type,
    "uri": uri,
    "accessed_on": DATE,
    "supports": supports,
    "limitations": limitations,
} for evidence_id, title, source_type, uri, supports, limitations in evidence_rows]
write(REVIEW / "evidence_register.csv", list(evidence_register[0]), evidence_register)

implementation_rows = []
classification_by_id = {row["concept_id"]: row for row in classification_rows}
for row in review_rows:
    implementation = classification_by_id[row["concept_id"]]
    implementation_rows.append({
        "concept_id": row["concept_id"],
        "preferred_label": implementation["preferred_label"],
        "v29_action": row["recommended_action"],
        "v29_evidence_state": row["evidence_state"],
        "implementation_status": implementation["implementation_status"],
        "semantic_class": implementation["semantic_class"],
        "target_parent_id": implementation["target_parent_id"],
        "decision_record": ADR,
        "method_record": METHOD,
        "reviewer": REVIEWER,
        "review_date": DATE,
        "rationale": row["rationale"],
    })
write(REVIEW / "feed_taxonomy_implementation_register.csv", list(implementation_rows[0]), implementation_rows)

summary = {
    "reviewed_concepts": len(implementation_rows),
    "implementation_statuses": dict(sorted(Counter(row["implementation_status"] for row in implementation_rows).items())),
    "semantic_classes": dict(sorted(Counter(row["semantic_class"] or "none" for row in implementation_rows).items())),
    "new_concepts": len(new_specs),
    "source_concept_retirements": len(retirement_rows),
    "generated_ids_retired_before_publication": ["AOM_101068", "AOM_101109"],
    "role_assertions": len(role_assertions),
    "product_role_concepts_reviewed": len(role_review_rows),
    "component_retention_relations": len(retention_rows),
    "concept_semantic_types": len(semantic_type_rows),
    "evidence_sources": len(evidence_register),
}
REVIEW.mkdir(parents=True, exist_ok=True)
(REVIEW / "feed_taxonomy_implementation_summary.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps(summary, indent=2, sort_keys=True))
