#!/usr/bin/env python3
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "livestock-staging"
REVIEW = ROOT / "review" / "livestock-v39"
OUTPUT = ROOT / "review" / "livestock-v40"
ADR = "docs/decisions/0049-composition-form-and-component-retention-model.md"
METHOD = "docs/methods/composition-form-and-retention-governance.md"
PREFIX = "COMPOSITION-FORM-"
DATE = "2026-08-21"
REVIEWER = "Pete Steward"
NEW_ID = "AOM_101182"


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


def normalize(value):
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.casefold()).split())


OUTPUT.mkdir(parents=True, exist_ok=True)
review_rows = read(REVIEW / "composition_form_review.csv")
assert len(review_rows) == 40
assert Counter(row["status"] for row in review_rows) == {"approved": 38, "held": 2}
review_by_id = {row["concept_id"]: row for row in review_rows}
assert {row["concept_id"] for row in review_rows if row["status"] == "held"} == {
    "AOM_101050", "AOM_101064",
}

renamed_labels = {
    "AOM_000326": "Feed physical characteristics",
    "AOM_101115": "Feed component-retention states",
    "AOM_101086": "Whole-crop component retention",
    "AOM_101110": "Whole-grain component retention",
    "AOM_101134": "Native-fat retention",
    "AOM_101067": "Essential oil constituent",
}
old_labels = {
    "AOM_000326": "Feed Physical Characteristic",
    "AOM_101115": "Native-component retention states",
    "AOM_101086": "Whole-crop composition",
    "AOM_101110": "Whole-grain composition",
    "AOM_101134": "Native-fat-retained composition",
    "AOM_101067": "Essential-oil constituent",
}
proposed_labels = {NEW_ID: "Feed physical descriptors", **renamed_labels}

mapping_specs = [
    ("AOM_001577", "exactMatch", "CHEBI_16646", "carbohydrate", "https://www.ebi.ac.uk/chebi/CHEBI%3A16646"),
    ("AOM_001571", "exactMatch", "CHEBI_36080", "protein", "https://www.ebi.ac.uk/chebi/CHEBI%3A36080"),
    ("AOM_101065", "exactMatch", "CHEBI_28017", "starch", "https://www.ebi.ac.uk/chebi/CHEBI%3A28017"),
    ("AOM_101067", "exactMatch", "CHEBI_83630", "essential oil", "https://www.ebi.ac.uk/chebi/CHEBI%3A83630"),
    ("AOM_101066", "broadMatch", "CHEBI_18059", "lipid", "https://www.ebi.ac.uk/chebi/CHEBI%3A18059"),
    ("AOM_101081", "broadMatch", "CHEBI_18059", "lipid", "https://www.ebi.ac.uk/chebi/CHEBI%3A18059"),
]

label_index = defaultdict(set)
for source, id_field, label_field in [
    (DATA / "labels.csv", "concept_id", "label"),
    (DATA / "approved_new_concepts.csv", "concept_id", "preferred_label"),
    (DATA / "approved_label_additions.csv", "concept_id", "label"),
    (DATA / "approved_concept_retirements.csv", "concept_id", "preferred_label"),
]:
    for row in read(source):
        label_index[normalize(row[label_field])].add(row[id_field])
external_labels = read(DATA / "approved_external_resource_labels.csv")
collision_rows = []
for case_id, concept_id, label in [
    ("LABEL-001", "AOM_000326", "Feed physical characteristics"),
    ("LABEL-002", NEW_ID, "Feed physical descriptors"),
    ("LABEL-003", "AOM_101115", "Feed component-retention states"),
    ("LABEL-004", "AOM_101086", "Whole-crop component retention"),
    ("LABEL-005", "AOM_101110", "Whole-grain component retention"),
    ("LABEL-006", "AOM_101134", "Native-fat retention"),
    ("LABEL-007", "AOM_101067", "Essential oil constituent"),
]:
    normalized = normalize(label)
    matches = sorted(label_index[normalized] - {concept_id})
    external_matches = sorted({
        row["target_uri"] for row in external_labels
        if normalize(row["target_label"]) == normalized
    })
    assert not matches, (concept_id, label, matches)
    assert not external_matches, (concept_id, label, external_matches)
    collision_rows.append({
        "case_id": case_id,
        "candidate_concept_id": concept_id,
        "candidate_label": label,
        "normalized_label": normalized,
        "matched_identity": "",
        "decision": "implemented-no-collision",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"data/livestock-staging/labels.csv;data/livestock-staging/approved_label_additions.csv;data/livestock-staging/approved_external_resource_labels.csv;{ADR}",
        "rationale": "Global preferred, alternative, hidden, deprecated, and external-label audit found no unexplained collision.",
    })
for case_id, concept_id, label, match, rationale in [
    ("LABEL-008", "AOM_101065", "Starch", "AOM_001832 alt label Starch", "Bare label rejected; retain Starch constituent."),
    ("LABEL-009", "AOM_101081", "Oil", "AOM_001333 preferred label Oil", "Bare label rejected; retain Oil constituent."),
]:
    collision_rows.append({
        "case_id": case_id,
        "candidate_concept_id": concept_id,
        "candidate_label": label,
        "normalized_label": normalize(label),
        "matched_identity": match,
        "decision": "rejected-collision",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"data/livestock-staging/labels.csv;{ADR}",
        "rationale": rationale,
    })
write(OUTPUT / "identity_collision_audit.csv", list(collision_rows[0]), collision_rows)

definition_updates = {
    "AOM_000326": "Measurable or observable characteristics describing physical properties of a feed or diet, such as floatability, particle size, or water-retention capacity; categorical presentation, bulk consistency, moisture condition, and processing method are represented separately.",
    NEW_ID: "Navigation grouping for categorical physical descriptors of feed presentation, bulk consistency, and moisture condition; measured physical characteristics and processing methods are represented separately.",
    "AOM_101115": "Positive states indicating retention of native material or chemical components, represented independently of measured composition, presentation, moisture, and processing method.",
    "AOM_101086": "Component-retention state indicating retention of harvested whole-crop scope rather than one selected component.",
    "AOM_101110": "Component-retention state in which bran, plant embryo, and endosperm remain in characteristic proportions independently of particle-size reduction.",
    "AOM_101134": "Component-retention state indicating positive retention of native fat; no measured concentration or inference from absence of defatting is asserted.",
    "AOM_101065": "Starch chemical identity represented as a primary constituent of feed materials; measured starch content and starch feed-material use require separate assertions.",
    "AOM_101066": "Contextual fat or lipid-mixture category represented as a primary constituent of feed materials; measured fat content and feed-product use require separate assertions.",
    "AOM_101067": "Essential-oil chemical mixture represented as a primary constituent of feed materials; additive or feed-material use requires a separate assertion.",
    "AOM_101081": "Contextual oil or lipid-mixture category represented as a primary constituent of feed materials; measured oil content and feed-product use require separate assertions.",
    "AOM_000764": "A mineral complementary feed formulation presented as a coherent block; consumption method, exact composition, and production process remain unspecified unless separately asserted.",
    "AOM_000766": "A mineral complementary feed formulation intended for gradual or free-choice consumption by licking; physical presentation, exact composition, and production process remain unspecified unless separately asserted.",
}

new_path = DATA / "approved_new_concepts.csv"
new_rows = [row for row in read(new_path) if row["concept_id"] != NEW_ID]
new_by_id = {row["concept_id"]: row for row in new_rows}
for concept_id in {"AOM_101115", "AOM_101086", "AOM_101110", "AOM_101134", "AOM_101067"}:
    new_by_id[concept_id]["preferred_label"] = renamed_labels[concept_id]
for concept_id, definition in definition_updates.items():
    if concept_id in new_by_id:
        new_by_id[concept_id]["scope_note"] = definition

physical_roots = {"AOM_101020", "AOM_101132", "AOM_101133"}
presentation_children = {
    "AOM_101049", "AOM_101050", "AOM_101052", "AOM_101053",
    "AOM_101075", "AOM_101076", "AOM_101108", "AOM_101125",
}
presentation_grandchildren = {"AOM_101051", "AOM_101126"}
bulk_children = {"AOM_101077", "AOM_101078", "AOM_101118"}
moisture_children = {"AOM_101054"}
for concept_id in physical_roots:
    row = new_by_id[concept_id]
    row.update({
        "broader_id": "AOM_000328",
        "hierarchy_level": "6",
        "derived_path": f"Governed feed taxonomy/Feed physical descriptors/{row['preferred_label']}",
    })
for concept_id in presentation_children:
    row = new_by_id[concept_id]
    row.update({
        "hierarchy_level": "7",
        "derived_path": f"Governed feed taxonomy/Feed physical descriptors/Feed presentation forms/{row['preferred_label']}",
    })
for concept_id in presentation_grandchildren:
    row = new_by_id[concept_id]
    row.update({
        "hierarchy_level": "8",
        "derived_path": f"Governed feed taxonomy/Feed physical descriptors/Feed presentation forms/Comminuted particle form/{row['preferred_label']}",
    })
for concept_id in bulk_children:
    row = new_by_id[concept_id]
    row.update({
        "hierarchy_level": "7",
        "derived_path": f"Governed feed taxonomy/Feed physical descriptors/Feed bulk consistencies/{row['preferred_label']}",
    })
for concept_id in moisture_children:
    row = new_by_id[concept_id]
    row.update({
        "hierarchy_level": "7",
        "derived_path": f"Governed feed taxonomy/Feed physical descriptors/Feed moisture conditions/{row['preferred_label']}",
    })
new_by_id["AOM_101115"].update({
    "hierarchy_level": "5",
    "derived_path": "Governed feed taxonomy/Feed component-retention states",
})
for concept_id in {"AOM_101086", "AOM_101110", "AOM_101134"}:
    new_by_id[concept_id].update({
        "hierarchy_level": "6",
        "derived_path": f"Governed feed taxonomy/Feed component-retention states/{new_by_id[concept_id]['preferred_label']}",
    })
new_rows.append({
    "case_id": f"{PREFIX}NEW-{NEW_ID}",
    "concept_id": NEW_ID,
    "preferred_label": "Feed physical descriptors",
    "scope_note": definition_updates[NEW_ID],
    "broader_id": "AOM_000328",
    "hierarchy_level": "5",
    "derived_path": "Governed feed taxonomy/Feed physical descriptors",
    "child_ids": "",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": f"{ADR};{METHOD}",
    "rationale": "Collision-audited navigation concept approved under ADR 0049.",
})
write(new_path, fields(new_path), new_rows)

registry_path = DATA / "livestock_id_registry.csv"
registry_rows = [row for row in read(registry_path) if row["concept_id"] != NEW_ID]
registry_rows.append({
    "concept_id": NEW_ID,
    "allocated_on": DATE,
    "status": "allocated",
    "preferred_label": "Feed physical descriptors",
    "case_id": f"{PREFIX}NEW-{NEW_ID}",
    "allocator": REVIEWER,
    "allocation_basis": "Sequential allocation after global preferred, alternative, hidden, deprecated, and external-label collision audit; accepted under ADR 0049.",
})
registry_rows.sort(key=lambda row: int(row["concept_id"].split("_")[1]))
write(registry_path, fields(registry_path), registry_rows)

baseline_path = ROOT / "config" / "identity-integrity-baseline.json"
baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
baseline.update({
    "captured": DATE,
    "frozen_generated_identifier_frontier": 101182,
    "new_identifier_allocation_frozen": True,
})
baseline_path.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")

correction_path = DATA / "approved_label_corrections.csv"
corrections = {row["concept_id"]: row for row in read(correction_path)}
corrections["AOM_000326"] = {
    "case_id": f"{PREFIX}LABEL-AOM_000326",
    "concept_id": "AOM_000326",
    "old_label": old_labels["AOM_000326"],
    "new_label": renamed_labels["AOM_000326"],
    "language": "en",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": ADR,
    "rationale": "Plural label scopes branch to measurable or observable physical characteristics and separates categorical descriptors.",
}
write(correction_path, fields(correction_path), list(corrections.values()))

addition_path = DATA / "approved_label_additions.csv"
alias_specs = {
    concept_id: old_labels[concept_id]
    for concept_id in (
        "AOM_101067", "AOM_101086", "AOM_101110", "AOM_101115", "AOM_101134",
    )
}
owned_alias_cases = {f"{PREFIX}ALIAS-{concept_id}" for concept_id in alias_specs}
additions = [row for row in read(addition_path) if row["case_id"] not in owned_alias_cases]
for concept_id, alias in alias_specs.items():
    additions.append({
        "case_id": f"{PREFIX}ALIAS-{concept_id}",
        "concept_id": concept_id,
        "language": "en",
        "label_type": "alt",
        "label": alias,
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": ADR,
        "rationale": "Preserves prior public label after accepted semantic clarification.",
    })
write(addition_path, fields(addition_path), additions)

facet_path = DATA / "approved_ingredient_facet_concepts.csv"
facet_rows = [
    row for row in read(facet_path)
    if row["concept_id"] not in {"AOM_101080", "AOM_101116"}
]
for row in facet_rows:
    concept_id = row["concept_id"]
    if concept_id in renamed_labels:
        row["preferred_label"] = renamed_labels[concept_id]
        row["reviewer"] = REVIEWER
        row["review_date"] = DATE
        row["evidence"] = ADR
    if concept_id == "AOM_101134":
        row["facet"] = "component_retention_state"
        row["target_property"] = "aom:componentRetentionState"
        row["value_class"] = "aom:ComponentRetentionState"
write(facet_path, fields(facet_path), facet_rows)

component_mapping_path = DATA / "approved_ingredient_component_value_mappings.csv"
component_mappings = [
    row for row in read(component_mapping_path)
    if not (row["source_value"] == "Ash" and row["target_concept_id"] == "AOM_101080")
]
write(component_mapping_path, fields(component_mapping_path), component_mappings)

component_hold_path = DATA / "approved_ingredient_component_value_holds.csv"
component_holds = [row for row in read(component_hold_path) if row["source_value"] != "Ash"]
component_holds.append({
    "source_value": "Ash",
    "target_property": "aom:legacyComponentDescriptor",
    "value_class": "xsd:string",
    "binding_action": "hold_ambiguous",
    "status": "approved",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": f"{ADR};{METHOD}",
    "rationale": "Raw Ash descriptor may denote analytical ash measurement, residue material, or mineral content; do not map it to deprecated chemical constituent.",
})
write(component_hold_path, fields(component_hold_path), component_holds)

deprecation_path = DATA / "approved_deprecations.csv"
deprecations = {row["deprecated_id"]: row for row in read(deprecation_path)}
for deprecated_id, replacement_id, preferred_label, rationale in [
    ("AOM_000324", NEW_ID, "Feed physical descriptors", "Legacy physical form conflates presentation, consistency, and moisture axes; replacement is explicit navigation grouping."),
    ("AOM_101116", "AOM_101134", "Native-fat retention", "Product-specific whole-milk state duplicates current retained-fat meaning; Whole Milk identity remains separate."),
    ("AOM_101080", "AOM_000226", "Ash", "Ash is analytical incineration residue, not one chemical constituent; measured Ash characteristic is appropriate replacement route."),
]:
    deprecations[deprecated_id] = {
        "case_id": f"{PREFIX}DEPRECATE-{deprecated_id}",
        "deprecated_id": deprecated_id,
        "replacement_id": replacement_id,
        "preferred_label": preferred_label,
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": rationale,
    }
write(deprecation_path, fields(deprecation_path), list(deprecations.values()))

revision_path = DATA / "approved_hierarchy_revisions.csv"
revision_specs = [
    (f"{PREFIX}MOVE-AOM_101020-{NEW_ID}", "AOM_101020", "AOM_000328", NEW_ID),
    (f"{PREFIX}MOVE-AOM_101132-{NEW_ID}", "AOM_101132", "AOM_000328", NEW_ID),
    (f"{PREFIX}MOVE-AOM_101133-{NEW_ID}", "AOM_101133", "AOM_000328", NEW_ID),
    (f"{PREFIX}REMOVE-AOM_000324-AOM_000326", "AOM_000324", "AOM_000326", ""),
]
owned_revision_cases = {case_id for case_id, _, _, _ in revision_specs}
revisions = [row for row in read(revision_path) if row["case_id"] not in owned_revision_cases]
for case_id, child_id, old_parent, new_parent in revision_specs:
    revisions.append({
        "case_id": case_id,
        "child_id": child_id,
        "remove_parent_id": old_parent,
        "add_parent_id": new_parent,
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": (
            "Removes deprecated physical-form wrapper from active browse hierarchy."
            if not new_parent else
            "Places independent categorical physical axis beneath accepted physical-descriptor navigation without changing governed relation property."
        ),
    })
write(revision_path, fields(revision_path), revisions)

mapping_path = DATA / "approved_mapping_additions.csv"
owned_mapping_cases = {
    f"{PREFIX}MAP-{concept_id}-{target_id}"
    for concept_id, _, target_id, _, _ in mapping_specs
}
mapping_rows = [row for row in read(mapping_path) if row["case_id"] not in owned_mapping_cases]
for concept_id, relation, target_id, target_label, target_uri in mapping_specs:
    mapping_rows.append({
        "case_id": f"{PREFIX}MAP-{concept_id}-{target_id}",
        "subject_id": concept_id,
        "mapping_relation": relation,
        "target_scheme": "ontology",
        "target_id": target_id,
        "target_uri": target_uri,
        "original_value": target_uri,
        "status": "approved",
        "source_release": "ChEBI record accessed 2026-08-21",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": "Accepted concept-level chemical-identity comparison; broad relation retained for contextual fat and oil mixtures.",
    })
write(mapping_path, fields(mapping_path), mapping_rows)

external_path = DATA / "approved_external_resource_labels.csv"
external_by_uri = {row["target_uri"]: row for row in read(external_path)}
for _, _, _, target_label, target_uri in mapping_specs:
    external_by_uri[target_uri] = {
        "target_uri": target_uri,
        "target_label": target_label,
        "language": "en",
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": "ChEBI record accessed 2026-08-21",
        "rationale": "Pinned authority label recorded for browser display and mapping audit.",
    }
write(external_path, fields(external_path), list(external_by_uri.values()))

feed_facet_path = DATA / "approved_feed_material_facets.csv"
feed_facets = read(feed_facet_path)
whole_milk_rows = 0
for row in feed_facets:
    if row["feed_material_id"] == "AOM_000555" and row["target_concept_id"] in {"AOM_101116", "AOM_101134"}:
        row.update({
            "target_property": "aom:componentRetentionState",
            "target_concept_id": "AOM_101134",
            "target_label": "Native-fat retention",
            "reviewer": REVIEWER,
            "review_date": DATE,
            "evidence": f"{row['evidence']};{ADR}" if ADR not in row["evidence"] else row["evidence"],
            "rationale": "Whole Milk identity remains separate; accepted state records positive native-fat retention.",
        })
        whole_milk_rows += 1
    elif row["target_concept_id"] in renamed_labels:
        row["target_label"] = renamed_labels[row["target_concept_id"]]
assert whole_milk_rows == 1
feed_facets = [
    row for row in feed_facets
    if not (
        row["feed_material_id"] == "AOM_001938"
        and row["target_property"] == "aom:productRole"
        and row["target_concept_id"] == "AOM_101062"
    )
]
feed_facets.append({
    "feed_material_id": "AOM_001938",
    "target_property": "aom:productRole",
    "target_concept_id": "AOM_101062",
    "target_label": "By-product role",
    "status": "approved",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": f"https://www.feedipedia.org/node/12474;https://www.feedipedia.org/node/214;{ADR}",
    "rationale": "Mapped poultry offal meal is an animal by-product; role remains independent of source, process, moisture, and presentation.",
})
write(feed_facet_path, fields(feed_facet_path), feed_facets)

hard_tail_path = DATA / "approved_hard_tail_feed_material_facets.csv"
hard_tail_rows = []
native_fat_rows = 0
for row in read(hard_tail_path):
    if row["target_concept_id"] == "AOM_101080":
        continue
    if row["target_concept_id"] == "AOM_101134":
        row.update({
            "target_property": "aom:componentRetentionState",
            "target_label": "Native-fat retention",
            "reviewer": REVIEWER,
            "review_date": DATE,
            "evidence": f"{row['evidence']};{ADR}" if ADR not in row["evidence"] else row["evidence"],
            "rationale": "Explicit full-fat descriptor supports positive native-fat retention independently of measured fat content.",
        })
        native_fat_rows += 1
    elif row["target_concept_id"] in renamed_labels:
        row["target_label"] = renamed_labels[row["target_concept_id"]]
    hard_tail_rows.append(row)
assert native_fat_rows == 2
write(hard_tail_path, fields(hard_tail_path), hard_tail_rows)

retention_path = DATA / "approved_component_retention_relations.csv"
retention_rows = []
for row in read(retention_path):
    if row["state_concept_id"] == "AOM_101116":
        continue
    if row["state_concept_id"] in {"AOM_101110", "AOM_101134"}:
        row["reviewer"] = REVIEWER
        row["review_date"] = DATE
        if ADR not in row["evidence"]:
            row["evidence"] = f"{row['evidence']};{ADR}"
        row["rationale"] = row["rationale"].replace("Whole-grain composition", "Whole-grain component retention").replace("Native-fat-retained composition", "Native-fat retention")
    retention_rows.append(row)
write(retention_path, fields(retention_path), retention_rows)

classification_path = DATA / "approved_feed_taxonomy_classifications.csv"
classification_rows = read(classification_path)
classification_updates = {
    "AOM_101115": ("Feed component-retention states", "implemented-cohort-e", "", "AOM_000328", "Positive component-retention root retained outside measured composition."),
    "AOM_101086": ("Whole-crop component retention", "implemented-cohort-e", "", "AOM_101115", "Whole-crop label now exposes positive retention meaning."),
    "AOM_101110": ("Whole-grain component retention", "implemented-cohort-e", "", "AOM_101115", "Whole-grain label now exposes positive retention meaning independent of grinding."),
    "AOM_101116": ("Whole-milk composition", "deprecated-cohort-e", "", "", "Product-specific state replaced by reusable Native-fat retention."),
    "AOM_101134": ("Native-fat retention", "implemented-cohort-e", "", "AOM_101115", "Positive native-fat retention replaces legacy composition-state use."),
    "AOM_000764": ("Mineral Block", "implemented-cohort-e", "aom:FeedFormulation", "AOM_101140", "Distinct mineral formulation with explicit Block presentation."),
    "AOM_000766": ("Mineral Lick", "implemented-cohort-e", "aom:FeedFormulation", "AOM_101140", "Distinct lick formulation; physical presentation remains unspecified."),
}
for row in classification_rows:
    if row["concept_id"] in classification_updates:
        label, implementation_status, semantic_class, parent, rationale = classification_updates[row["concept_id"]]
        row.update({
            "preferred_label": label,
            "implementation_status": implementation_status,
            "semantic_class": semantic_class,
            "target_parent_id": parent,
            "status": "approved",
            "reviewer": REVIEWER,
            "review_date": DATE,
            "evidence": f"{ADR};{METHOD}",
            "rationale": rationale,
        })
write(classification_path, fields(classification_path), classification_rows)

changed_material_ids = {
    "AOM_000538", "AOM_000555", "AOM_000611", "AOM_000656", "AOM_000660",
    "AOM_001313", "AOM_001317", "AOM_001324", "AOM_001326", "AOM_001938",
}
facet_files = [
    feed_facet_path,
    DATA / "approved_generated_feed_material_facets.csv",
    hard_tail_path,
    DATA / "approved_structural_feed_material_facets.csv",
]
all_facets = [row for path in facet_files for row in read(path)]
facets_by_material = defaultdict(list)
for row in all_facets:
    facets_by_material[row["feed_material_id"]].append(row)
inventory = {
    row["concept_id"]: row["source_identity_candidate"]
    for row in read(ROOT / "review" / "livestock-v5" / "ingredient_harmonization_inventory.csv")
}
hard_tail_sources = {
    row["concept_id"]: row["governed_source_identity"]
    for row in read(ROOT / "review" / "livestock-v14" / "definition_hard_tail_review.csv")
    if row["status"] == "approved"
}
property_labels = {
    "aom:processingMethod": "processing method",
    "aom:ingredientPart": "ingredient part",
    "aom:materialComponent": "material component",
    "aom:presentationForm": "presentation form",
    "aom:bulkConsistency": "bulk consistency",
    "aom:moistureCondition": "moisture condition",
    "aom:productRole": "product role",
    "aom:componentRetentionState": "component-retention state",
    "aom:compositionState": "composition state",
    "aom:primaryConstituent": "primary constituent",
}
property_order = {name: index for index, name in enumerate(property_labels)}
for concept_id in sorted(changed_material_ids):
    source = hard_tail_sources.get(concept_id, inventory.get(concept_id, "")).strip()
    assert source, concept_id
    grouped = defaultdict(set)
    for facet in facets_by_material.get(concept_id, []):
        if facet["target_property"] in property_labels:
            grouped[facet["target_property"]].add(facet["target_label"])
    if grouped:
        descriptions = [
            f"{property_labels[prop]} — {', '.join(sorted(grouped[prop]))}"
            for prop in sorted(grouped, key=lambda item: property_order[item])
        ]
        definition_updates[concept_id] = (
            f"A feed material with governed source identity “{source}” and characteristics: "
            f"{'; '.join(descriptions)}."
        )
    else:
        definition_updates[concept_id] = (
            f"A feed material with governed source identity “{source}”; material component, processing method, "
            "presentation form, bulk consistency, moisture condition, product role, component retention, and "
            "chemical constituent remain unspecified unless separately asserted."
        )

override_path = DATA / "approved_definition_overrides.csv"
overrides = {row["concept_id"]: row for row in read(override_path)}
for concept_id, definition in definition_updates.items():
    overrides[concept_id] = {
        "concept_id": concept_id,
        "language": "en",
        "definition": definition,
        "definition_method": "composition_form_definition_replacement",
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": "Definition enforces accepted physical, retention, chemical-identity, formulation, or product-role boundary.",
    }
write(override_path, fields(override_path), list(overrides.values()))

definition_path = DATA / "approved_definition_enrichments.csv"
definition_rows = [row for row in read(definition_path) if row["concept_id"] not in definition_updates]
for concept_id, definition in definition_updates.items():
    definition_rows.append({
        "concept_id": concept_id,
        "language": "en",
        "definition": definition,
        "definition_method": "composition_form_definition_replacement",
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": "Definition enforces accepted physical, retention, chemical-identity, formulation, or product-role boundary.",
    })
definition_rows.sort(key=lambda row: row["concept_id"])
write(definition_path, fields(definition_path), definition_rows)

changed_ids = {
    "AOM_000326", "AOM_000324", "AOM_101020", "AOM_101132", "AOM_101133",
    "AOM_101115", "AOM_101086", "AOM_101110", "AOM_101116", "AOM_101134",
    "AOM_101080", "AOM_001577", "AOM_101067", "AOM_101066", "AOM_101081",
    "AOM_001571", "AOM_101065", "AOM_000764", "AOM_000766", "AOM_001938",
}
implementation_rows = []
for row in review_rows:
    concept_id = row["concept_id"]
    if row["status"] == "held":
        implementation_status = "held-no-semantic-change"
    elif row["recommended_disposition"].startswith("deprecate"):
        implementation_status = "deprecated-with-replacement"
    elif row["recommended_disposition"] == "retain-deprecation":
        implementation_status = "verified-existing-deprecation"
    elif concept_id in changed_ids:
        implementation_status = "implemented"
    else:
        implementation_status = "confirmed-no-change"
    implementation_rows.append({
        "concept_id": concept_id,
        "preferred_label": row["preferred_label"],
        "review_status": row["status"],
        "implementation_status": implementation_status,
        "review_axis": row["review_axis"],
        "recommended_disposition": row["recommended_disposition"],
        "decision_record": ADR,
        "method": METHOD,
        "reviewer": REVIEWER,
        "implementation_date": DATE,
        "evidence_ids": row["evidence_ids"],
        "rationale": row["rationale"],
    })
write(OUTPUT / "composition_form_implementation_register.csv", list(implementation_rows[0]), implementation_rows)

holds = []
for row in review_rows:
    if row["status"] != "held":
        continue
    holds.append({
        "concept_id": row["concept_id"],
        "preferred_label": row["preferred_label"],
        "hold_scope": row["recommended_disposition"],
        "blocking_question": row["blocking_question"],
        "owner": REVIEWER,
        "review_date": DATE,
        "status": "held",
        "evidence": f"{ADR};{METHOD}",
    })
write(OUTPUT / "implementation_holds.csv", list(holds[0]), holds)

migration_rows = [
    {
        "feed_material_id": "AOM_000555", "old_property": "aom:compositionState", "old_target_id": "AOM_101116",
        "implementation_action": "migrated-property-and-target", "new_property": "aom:componentRetentionState", "new_target_id": "AOM_101134",
        "status": "approved", "reviewer": REVIEWER, "implementation_date": DATE, "decision_record": ADR,
        "rationale": "Whole Milk identity remains separate while native-fat retention uses reusable positive state.",
    },
    {
        "feed_material_id": "AOM_000611", "old_property": "aom:compositionState", "old_target_id": "AOM_101134",
        "implementation_action": "migrated-property", "new_property": "aom:componentRetentionState", "new_target_id": "AOM_101134",
        "status": "approved", "reviewer": REVIEWER, "implementation_date": DATE, "decision_record": ADR,
        "rationale": "Explicit full-fat evidence supports positive native-fat retention, not measured composition.",
    },
    {
        "feed_material_id": "AOM_001317", "old_property": "aom:compositionState", "old_target_id": "AOM_101134",
        "implementation_action": "migrated-property", "new_property": "aom:componentRetentionState", "new_target_id": "AOM_101134",
        "status": "approved", "reviewer": REVIEWER, "implementation_date": DATE, "decision_record": ADR,
        "rationale": "Explicit full-fat evidence supports positive native-fat retention, not measured composition.",
    },
    {
        "feed_material_id": "AOM_000538", "old_property": "aom:primaryConstituent", "old_target_id": "AOM_101080",
        "implementation_action": "removed-category-error", "new_property": "", "new_target_id": "",
        "status": "approved", "reviewer": REVIEWER, "implementation_date": DATE, "decision_record": ADR,
        "rationale": "Ash is analytical residue and Bone Ash to Ash constituent was tautological.",
    },
    {
        "feed_material_id": "AOM_001938", "old_property": "", "old_target_id": "",
        "implementation_action": "added-product-role", "new_property": "aom:productRole", "new_target_id": "AOM_101062",
        "status": "approved", "reviewer": REVIEWER, "implementation_date": DATE, "decision_record": ADR,
        "rationale": "Feedipedia identifies poultry offal meal as animal by-product independently of source and processing facets.",
    },
]
write(OUTPUT / "material_assertion_migration_register.csv", list(migration_rows[0]), migration_rows)

mapping_implementation = []
for concept_id, relation, target_id, target_label, target_uri in mapping_specs:
    mapping_implementation.append({
        "concept_id": concept_id,
        "preferred_label": proposed_labels.get(concept_id, review_by_id[concept_id]["preferred_label"]),
        "mapping_relation": relation,
        "target_id": target_id,
        "target_label": target_label,
        "target_uri": target_uri,
        "status": "approved",
        "reviewer": REVIEWER,
        "implementation_date": DATE,
        "evidence_ids": review_by_id[concept_id]["evidence_ids"],
        "rationale": "Accepted chemical-identity mapping; broad mapping preserves contextual fat/oil scope.",
    })
write(OUTPUT / "chemical_mapping_implementation.csv", list(mapping_implementation[0]), mapping_implementation)

binding_rows = [{
    "source_value": "Ash",
    "old_binding_action": "map_to_existing",
    "old_target_id": "AOM_101080",
    "implementation_action": "migrated-to-ambiguity-hold",
    "new_binding_action": "hold_ambiguous",
    "new_target_property": "aom:legacyComponentDescriptor",
    "status": "approved",
    "reviewer": REVIEWER,
    "implementation_date": DATE,
    "decision_record": ADR,
    "rationale": "Analytical measurement, residue material, and mineral-content meanings cannot be resolved from raw Ash label alone.",
}]
write(OUTPUT / "component_binding_migration_register.csv", list(binding_rows[0]), binding_rows)

specific_rows = [
    {
        "concept_id": "AOM_000764", "preferred_label": "Mineral Block", "implementation_action": "retained-distinct-formulation-and-block-form",
        "status": "approved", "reviewer": REVIEWER, "implementation_date": DATE, "evidence": f"{ADR};{METHOD}",
        "rationale": "Block is presentation; formulation remains distinct from lick consumption mode.",
    },
    {
        "concept_id": "AOM_000766", "preferred_label": "Mineral Lick", "implementation_action": "retained-distinct-formulation-with-unspecified-form",
        "status": "approved", "reviewer": REVIEWER, "implementation_date": DATE, "evidence": f"{ADR};{METHOD}",
        "rationale": "Lick denotes intended consumption; no Block presentation is inferred.",
    },
    {
        "concept_id": "AOM_001938", "preferred_label": "Chicken Offal Dried Ground", "implementation_action": "added-by-product-role-without-rendering-inference",
        "status": "approved", "reviewer": REVIEWER, "implementation_date": DATE, "evidence": f"https://www.feedipedia.org/node/12474;https://www.feedipedia.org/node/214;{ADR}",
        "rationale": "By-product role is explicit; family-level rendering process remains unasserted.",
    },
]
write(OUTPUT / "specific_material_implementation.csv", list(specific_rows[0]), specific_rows)

implementation_counts = Counter(row["implementation_status"] for row in implementation_rows)
summary = {
    "status": "implemented-candidate",
    "decision": ADR,
    "reviewed_concepts": 40,
    "approved_dispositions": 38,
    "held_dispositions": 2,
    "implementation_status_counts": dict(sorted(implementation_counts.items())),
    "new_navigation_concepts": 1,
    "identifier_frontier": 101182,
    "deprecated_with_replacement": 3,
    "renamed_concepts": 6,
    "hierarchy_moves": 3,
    "browse_hierarchy_suppressions": 1,
    "external_mappings": 6,
    "exact_external_mappings": 4,
    "broad_external_mappings": 2,
    "material_assertions_reviewed": 796,
    "material_assertions_retained_unchanged": 792,
    "material_assertions_migrated": 3,
    "material_assertions_removed": 1,
    "material_assertions_added": 1,
    "raw_component_bindings_held": 1,
    "reviewer": REVIEWER,
    "implementation_date": DATE,
}
(OUTPUT / "composition_form_implementation_summary.json").write_text(
    json.dumps(summary, indent=2) + "\n", encoding="utf-8"
)
(OUTPUT / "README.md").write_text(
    "# Livestock v40 composition, form, and retention implementation\n\n"
    "Implements accepted [ADR 0049](../../docs/decisions/0049-composition-form-and-component-retention-model.md).\n\n"
    "## Contents\n\n"
    "- `composition_form_implementation_register.csv`: every reviewed concept disposition.\n"
    "- `material_assertion_migration_register.csv`: three migrations, one removal, and one added role.\n"
    "- `chemical_mapping_implementation.csv`: four exact and two broad ChEBI mappings.\n"
    "- `component_binding_migration_register.csv`: retired Ash constituent mapping converted to explicit raw-value hold.\n"
    "- `identity_collision_audit.csv`: seven applied labels and two rejected bare-label collisions.\n"
    "- Governed hierarchy revisions move three active axes and suppress deprecated Physical form from active browsing.\n"
    "- `specific_material_implementation.csv`: Mineral Block, Mineral Lick, and Chicken Offal decisions.\n"
    "- `implementation_holds.csv`: Lick delivery and Gluten identity preserved without inference.\n"
    "- `composition_form_implementation_summary.json`: machine-readable implementation counts.\n\n"
    "## Evidence trail\n\n"
    "Claim evidence remains in `review/livestock-v39/evidence_register.csv`; method is documented in "
    "`docs/methods/composition-form-and-retention-governance.md`.\n",
    encoding="utf-8",
)
print(json.dumps(summary, indent=2))
