#!/usr/bin/env python3
import csv
import hashlib
import json
from collections import Counter, defaultdict, deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "dist" / "livestock-staging"
DATA = ROOT / "data" / "livestock-staging"
FACETS = ROOT / "dist" / "releases" / "2026.1-rc.1" / "feed-material-facets.csv"
OUT = ROOT / "review" / "livestock-v37"
REVIEW = OUT / "component_chemical_review.csv"
INVENTORY = OUT / "component_chemical_inventory.csv"
USAGE = OUT / "material_usage_inventory.csv"
ANATOMY = OUT / "anatomical_authority_mapping.csv"
COLLISIONS = OUT / "identity_overlap_review.csv"
SUMMARY = OUT / "component_chemical_summary.json"

SOURCE_COMMIT = "5a6d0be7eab56a192522fc4c2b2556a2be2bbbba"
CHEMICAL_ROOT = "AOM_101146"
COMPOSITION_ROOT = "AOM_000196"
COMPONENT_ROOT = "AOM_101085"
ANATOMY_ROOT = "AOM_101019"
AXIS_ROOTS = {
    "chemical-identity": CHEMICAL_ROOT,
    "composition": COMPOSITION_ROOT,
    "material-component": COMPONENT_ROOT,
}
REVIEW_DATE = "2026-08-19"
REVIEWER = "Codex"


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_rows(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


nodes = {row["node_id"]: row for row in read_rows(GRAPH / "nodes.csv")}
definitions = {
    row["concept_id"]: row["definition"]
    for row in read_rows(DATA / "definitions.csv")
    if row["language"] == "en"
}
semantic_types = {
    row["concept_id"]: row["semantic_class"]
    for row in read_rows(DATA / "approved_concept_semantic_types.csv")
    if row["status"] == "approved"
}
parents = defaultdict(set)
children = defaultdict(set)
for row in read_rows(GRAPH / "edges.csv"):
    if row["edge_type"] == "broader":
        parents[row["source"]].add(row["target"])
        children[row["target"]].add(row["source"])


def descendant_depths(root_id):
    found = {}
    pending = deque((concept_id, 1) for concept_id in children[root_id])
    while pending:
        concept_id, depth = pending.popleft()
        if concept_id in found and found[concept_id] <= depth:
            continue
        found[concept_id] = depth
        pending.extend((child_id, depth + 1) for child_id in children[concept_id])
    return found


axis_depths = {
    axis: descendant_depths(root_id)
    for axis, root_id in AXIS_ROOTS.items()
}
axis_members = {
    axis: {root_id, *axis_depths[axis]}
    for axis, root_id in AXIS_ROOTS.items()
}
review_ids = set().union(*axis_members.values())
assert len(axis_members["chemical-identity"]) == 18
assert len(axis_members["composition"]) == 105
assert len(axis_members["material-component"]) == 41
assert sum(len(ids) for ids in axis_members.values()) == len(review_ids) == 164
assert len(children[ANATOMY_ROOT]) == 31

facet_rows = read_rows(FACETS)
facet_counts = Counter()
facet_materials = defaultdict(set)
for row in facet_rows:
    key = (row["target_property"], row["target_concept_id"])
    facet_counts[key] += 1
    facet_materials[key].add(row["feed_material_id"])

evidence_ids = {
    row["evidence_id"] for row in read_rows(OUT / "evidence_register.csv")
}

plant_ontology_mappings = {
    "AOM_101046": ("PO:0004518", "bark"),
    "AOM_101121": ("PO:0004542", "rhizome"),
    "AOM_101028": ("PO:0009001", "fruit"),
    "AOM_101037": ("PO:0009005", "root"),
    "AOM_101038": ("PO:0009010", "seed"),
    "AOM_101117": ("PO:0009046", "flower"),
    "AOM_101047": ("PO:0009047", "stem"),
    "AOM_101153": ("PO:0009089", "endosperm"),
    "AOM_101033": ("PO:0025034", "leaf"),
    "AOM_101042": ("PO:0025066", "stalk"),
    "AOM_101036": ("PO:0025248", "pseudostem"),
    "AOM_101025": ("PO:0025354", "cladode"),
    "AOM_101027": ("PO:0025355", "corm"),
    "AOM_101024": ("PO:0025356", "bulb"),
    "AOM_101043": ("PO:0025522", "tuber"),
}
animal_ontology_mappings = {
    "AOM_101122": ("UBERON:0002107", "liver"),
}
ambiguous_anatomy = {
    "AOM_101029",
    "AOM_101030",
    "AOM_101031",
    "AOM_101032",
    "AOM_101034",
    "AOM_101040",
    "AOM_101041",
    "AOM_101048",
    "AOM_101074",
}


def recommendation(
    review_role,
    disposition,
    semantic_action,
    evidence,
    rationale,
    proposed_label="",
    proposed_parent_or_axis="",
    mapping_candidate="",
    status="proposed",
    blocking_question="",
):
    referenced_evidence = set(evidence.split(";"))
    assert referenced_evidence <= evidence_ids, sorted(referenced_evidence - evidence_ids)
    return {
        "review_role": review_role,
        "recommended_disposition": disposition,
        "proposed_label": proposed_label,
        "proposed_parent_or_axis": proposed_parent_or_axis,
        "recommended_semantic_action": semantic_action,
        "mapping_candidate": mapping_candidate,
        "evidence_ids": evidence,
        "status": status,
        "blocking_question": blocking_question,
        "rationale": rationale,
    }


def chemical_recommendation(concept_id):
    if concept_id == CHEMICAL_ROOT:
        return recommendation(
            "identity-root",
            "retain-and-rename",
            "Keep as identity axis distinct from measured composition and feed-product use; map broadly to ChEBI chemical entity.",
            "LOCAL-GRAPH;CHEBI-ENTITY;CHEBI-SUBSTANCE;FOODON-REPO",
            "Chemical identity answers what entity is present; composition answers how much is present.",
            proposed_label="Feed-related chemical entities",
            proposed_parent_or_axis="AOM_000328 Feed Characteristic",
            mapping_candidate="CHEBI:24431 broad mapping candidate",
        )
    if concept_id == "AOM_101147":
        return recommendation(
            "chemical-substance-grouping",
            "retain-grouping",
            "Keep only chemically identified substances or substance groups here; require exact child mappings before implementation.",
            "LOCAL-GRAPH;CHEBI-ENTITY;CHEBI-SUBSTANCE",
            "Chemical substance is narrower than chemical entity but not every mixture or constituent category meets its ChEBI definition.",
            proposed_parent_or_axis=CHEMICAL_ROOT,
            mapping_candidate="CHEBI:59999 close or broad mapping candidate",
        )
    if concept_id == "AOM_101023":
        return recommendation(
            "constituent-category-grouping",
            "retain-and-rename",
            "Drop role word Primary from grouping; primary role remains supplied by aom:primaryConstituent.",
            "LOCAL-GRAPH;AOM-SCHEMA;CHEBI-ENTITY",
            "Role belongs to relation between material and entity, not intrinsically to target concept.",
            proposed_label="Chemical constituent categories",
            proposed_parent_or_axis=CHEMICAL_ROOT,
        )
    if concept_id == "AOM_101120":
        return recommendation(
            "duplicate-constituent-category",
            "deprecate-after-migration",
            "Migrate one primaryConstituent assertion to AOM_001571 Protein, correct retained definition, then publish replacement crosswalk.",
            "LOCAL-GRAPH;AOM-SCHEMA;CHEBI-ENTITY",
            "Existing Protein identity was retained and semantically typed as chemical constituent; property context does not justify duplicate identity.",
            proposed_parent_or_axis="replace with AOM_001571",
            mapping_candidate="AOM_001571",
        )
    if concept_id in {
        "AOM_101064",
        "AOM_101065",
        "AOM_101066",
        "AOM_101067",
        "AOM_101080",
        "AOM_101081",
    }:
        return recommendation(
            "role-suffixed-constituent-category",
            "hold-exact-identity-and-label",
            "Retain stable ID temporarily; decide chemical entity, mixture, processed material, or feed-material identity before removing Constituent suffix.",
            "LOCAL-GRAPH;AOM-SCHEMA;CHEBI-ENTITY;CHEBI-SUBSTANCE",
            "Current generic definition states only relation use and does not establish chemical identity; exact mapping and collision review remain necessary.",
            proposed_parent_or_axis="Feed-related chemical entities or Feed materials after concept-level review",
            status="held",
            blocking_question="Which external entity or material identity exactly matches this category, and do current material assertions remain non-tautological?",
        )
    if concept_id in {"AOM_000746", "AOM_006389", "AOM_000808"}:
        return recommendation(
            "chemical-substance-or-group",
            "retain-identity",
            "Keep in chemical-identity axis; represent feed-material or additive use separately.",
            "LOCAL-GRAPH;CHEBI-ENTITY;CHEBI-SUBSTANCE",
            "Current concept identifies chemical substance or substance group independently of product use.",
            proposed_parent_or_axis="AOM_101147 Chemical substances",
        )
    return recommendation(
        "chemical-entity-category",
        "retain-reclassify-identity",
        "Keep stable identity under Feed-related chemical entities; correct legacy feed-ingredient definition and review exact ChEBI mapping.",
        "LOCAL-GRAPH;CHEBI-ENTITY;CHEBI-SUBSTANCE;FOODON-REPO",
        "Legacy definition records former product branch while current semantic classification treats concept as chemical constituent.",
        proposed_parent_or_axis="Feed-related chemical entities",
    )


def composition_recommendation(concept_id):
    if concept_id == COMPOSITION_ROOT:
        return recommendation(
            "measured-composition-root",
            "retain-and-rename",
            "Keep separate from chemical identity; scope descendants to measurable or observable composition characteristics.",
            "LOCAL-GRAPH;AOM-SCHEMA;CHEBI-ENTITY",
            "Current definition already describes measurable proportions but label obscures characteristic-level semantics.",
            proposed_label="Feed composition characteristics",
            proposed_parent_or_axis="AOM_000328 Feed Characteristic",
        )
    if concept_id == "AOM_101115":
        return recommendation(
            "mixed-component-retention-root",
            "move-out-of-composition",
            "Move component-retention meanings toward component integrity; split composition states during Cohort E.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-LANGUAL",
            "Whole-component retention is not one chemical concentration characteristic and current children mix integrity with composition state.",
            proposed_parent_or_axis="component-integrity axis; Cohort E split",
        )
    if concept_id in {"AOM_101086", "AOM_101110"}:
        return recommendation(
            "component-integrity-state",
            "move-to-component-integrity",
            "Represent retained whole-crop or whole-grain structure through positive component-integrity semantics.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-LANGUAL;EU-FEED-CATALOGUE",
            "Whole-crop and whole-grain describe retained component structure, not measured chemical content.",
            proposed_parent_or_axis="component-integrity axis",
        )
    if concept_id in {"AOM_101116", "AOM_101134"}:
        return recommendation(
            "retention-or-composition-state",
            "hold-for-cohort-e",
            "Retain temporarily; decide retained-component integrity versus composition state in Cohort E.",
            "LOCAL-GRAPH;AOM-SCHEMA",
            "Whole-milk and Native-fat-retained may not share one semantic axis despite current common parent.",
            proposed_parent_or_axis="Cohort E Composition and Form review",
            status="held",
            blocking_question="Does concept assert retained physical components, measured composition, or both?",
        )
    if children[concept_id]:
        return recommendation(
            "composition-grouping",
            "retain-boundary-for-cohort-e",
            "Keep inside measured-composition closure for complete Cohort E hierarchy and label review; do not merge with chemical identity.",
            "LOCAL-GRAPH;AOM-SCHEMA;CHEBI-ENTITY",
            "Grouping organizes measured characteristics; exact internal hierarchy is deferred without weakening identity boundary.",
            proposed_parent_or_axis="Feed composition characteristics",
        )
    return recommendation(
        "composition-characteristic",
        "retain-boundary-for-cohort-e",
        "Keep as measurable or observable composition characteristic; Cohort E should disambiguate content labels and measurement semantics.",
        "LOCAL-GRAPH;AOM-SCHEMA;CHEBI-ENTITY",
        "Measured concentration or proportion is not identical to chemical entity carrying same lexical label.",
        proposed_parent_or_axis="Feed composition characteristics",
    )


def component_recommendation(concept_id):
    if concept_id == COMPONENT_ROOT:
        return recommendation(
            "component-root",
            "retain-root",
            "Use materialComponent as canonical component query across anatomical structures, body substances, and processed fractions.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-REPO;FOODON-LANGUAL",
            "One superproperty already spans component subtypes; duplicate relation semantics are unnecessary.",
            proposed_parent_or_axis="AOM_000328 Feed Characteristic",
        )
    if concept_id == ANATOMY_ROOT:
        return recommendation(
            "anatomy-root",
            "retain-and-restructure",
            "Add Plant and Animal anatomical navigation after exact mapping review; do not add permanent Other branch.",
            "LOCAL-GRAPH;FOODON-REPO;FOODON-LANGUAL;PLANT-ONTOLOGY;UBERON",
            "Current flat branch mixes 29 plant-oriented values with two animal values and several vernacular holds.",
            proposed_parent_or_axis=COMPONENT_ROOT,
        )
    if concept_id == "AOM_101145":
        return recommendation(
            "animal-body-substance-root",
            "retain-grouping",
            "Keep body substances separate from anatomy and from by-product role.",
            "LOCAL-GRAPH;UBERON",
            "Blood is body substance; whether feed material is by-product is independent economic role.",
            proposed_parent_or_axis=COMPONENT_ROOT,
        )
    if concept_id == "AOM_101103":
        return recommendation(
            "duplicate-animal-body-substance",
            "deprecate-after-reuse-review",
            "Reuse existing AOM_001616 Blood as body-substance identity if definition review confirms exact match; keep by-product role separate.",
            "LOCAL-GRAPH;UBERON;FOODON-REPO",
            "Property context does not justify duplicate Blood identity and current component concept has no material assertions.",
            proposed_parent_or_axis="replace with AOM_001616 after identity confirmation",
            mapping_candidate="AOM_001616",
        )
    if concept_id == "AOM_101143":
        return recommendation(
            "processed-fraction-root",
            "retain-grouping",
            "Keep process-defined material fractions separate from exact anatomy.",
            "LOCAL-GRAPH;FOODON-PINNED;EU-FEED-CATALOGUE",
            "Manufacturing fractions can contain several anatomical tissues and variable attached material.",
            proposed_parent_or_axis=COMPONENT_ROOT,
        )
    if concept_id == "AOM_101144":
        return recommendation(
            "one-child-milling-grouping",
            "retire-structural-wrapper",
            "Move Bran directly under Processed material fractions; retain wrapper only if later reviewed cohort adds multiple justified members.",
            "LOCAL-GRAPH;EU-FEED-CATALOGUE;FOODON-PINNED",
            "Current one-child branch adds Bran-specific complexity without additional distinction.",
            proposed_parent_or_axis="replace with AOM_101143",
        )
    if concept_id == "AOM_101104":
        return recommendation(
            "processed-milling-fraction",
            "retain-and-reparent",
            "Keep Bran as process-defined component/fraction and move directly under Processed material fractions.",
            "LOCAL-GRAPH;EU-FEED-CATALOGUE;FOODON-PINNED",
            "EU maize bran contains outer skins, germ fragments, and endosperm particles; it is not one anatomy structure.",
            proposed_parent_or_axis="AOM_101143 Processed material fractions",
            mapping_candidate="FOODON:03420288 close mapping candidate",
        )
    if concept_id == "AOM_101154":
        return recommendation(
            "crop-residue-component-root",
            "retire-category-error",
            "Move Straw and Stover to crop-residue material identity architecture and migrate tautological component assertions.",
            "LOCAL-GRAPH;AGROVOC-STRAW;NALT-CROP-RESIDUES;NALT-STOVER",
            "Agricultural authorities treat children as residue products/materials, not components of identically named feed materials.",
            proposed_parent_or_axis="replacement crop-residue material hierarchy",
        )
    if concept_id in {"AOM_101105", "AOM_101106"}:
        is_straw = concept_id == "AOM_101106"
        return recommendation(
            "crop-residue-material-type",
            "remove-component-use-hold-identity",
            "Remove tautological materialComponent assertions; reuse existing material identities and decide whether generic concept remains necessary outside component axis.",
            "LOCAL-GRAPH;AGROVOC-STRAW;NALT-CROP-RESIDUES;NALT-STOVER",
            "Current target repeats material identity for Straw/Stover records and does not identify a distinct component; Straw also overlaps existing AOM_000582 Unspecified Straw.",
            proposed_parent_or_axis="existing source-specific feed materials; AOM_000582 review for generic Straw" if is_straw else "existing source-specific feed materials; generic Stover need review",
            mapping_candidate="AOM_000582" if is_straw else "generic Stover material identity decision pending",
            status="held",
            blocking_question="Does existing AOM_000582 cover generic Straw identity?" if is_straw else "Is a generic Stover material concept required after source-specific hierarchy and role facets are complete?",
        )
    if concept_id == "AOM_101029":
        return recommendation(
            "ambiguous-plant-anatomy-or-fraction",
            "split-meaning",
            "Reserve anatomical meaning for Plant embryo mapping; represent commercial germ as process-defined feed material or fraction.",
            "LOCAL-GRAPH;PO-EMBRYO;EU-FEED-CATALOGUE;FOODON-PINNED",
            "Plant Ontology gives germ only related synonym status while EU maize germ is manufacturing product containing several tissues.",
            proposed_label="Plant embryo for anatomical meaning",
            proposed_parent_or_axis="Plant anatomical components; processed feed-material identity",
            mapping_candidate="PO:0009009 related mapping candidate",
        )
    if concept_id in {"AOM_101122", "AOM_101044"}:
        mapping = "UBERON:0002107" if concept_id == "AOM_101122" else "UBERON:0002075 close mapping candidate"
        return recommendation(
            "animal-anatomy",
            "move-under-animal-anatomy",
            "Place under proposed Animal anatomical components after exact collective-scope review.",
            "LOCAL-GRAPH;UBERON;FOODON-REPO",
            "Current flat anatomy branch obscures biological source; animal anatomy mapping is available or close.",
            proposed_parent_or_axis="Animal anatomical components",
            mapping_candidate=mapping,
            status="held" if concept_id == "AOM_101044" else "proposed",
            blocking_question="Does plural Viscera map to one viscus, a collection, or source-specific offal material?" if concept_id == "AOM_101044" else "",
        )
    if concept_id in ambiguous_anatomy:
        return recommendation(
            "vernacular-or-collective-plant-component",
            "hold-exact-anatomical-scope",
            "Keep stable component value visible but do not force under Plant anatomy until source- and taxon-aware identity is resolved.",
            "LOCAL-GRAPH;PLANT-ONTOLOGY;FOODON-PINNED",
            "Common feed label may denote anatomy, a whole material, a collective part, or processing fraction depending on source.",
            proposed_parent_or_axis="AOM_101085 pending exact mapping",
            status="held",
            blocking_question="What exact plant structure or material fraction does this label denote across current material assertions?",
        )
    mapping = plant_ontology_mappings.get(concept_id)
    return recommendation(
        "plant-anatomy",
        "move-under-plant-anatomy",
        "Place under proposed Plant anatomical components and publish exact external mapping only after definition comparison.",
        "LOCAL-GRAPH;PLANT-ONTOLOGY;FOODON-REPO",
        "Concept denotes plant structure; grouped navigation improves current flat mixed branch without changing source or product role.",
        proposed_parent_or_axis="Plant anatomical components",
        mapping_candidate=f"{mapping[0]} exact-label mapping candidate" if mapping else "Plant Ontology exact mapping pending",
    )


recommendation_functions = {
    "chemical-identity": chemical_recommendation,
    "composition": composition_recommendation,
    "material-component": component_recommendation,
}

review_fields = [
    "concept_id",
    "preferred_label",
    "review_axis",
    "review_role",
    "current_parent_ids",
    "recommended_disposition",
    "proposed_label",
    "proposed_parent_or_axis",
    "recommended_semantic_action",
    "mapping_candidate",
    "evidence_ids",
    "status",
    "blocking_question",
    "rationale",
    "reviewer",
    "review_date",
]
review_rows = []
review_by_id = {}
for axis, root_id in AXIS_ROOTS.items():
    ordered_ids = sorted(axis_members[axis], key=lambda concept_id: (0 if concept_id == root_id else axis_depths[axis][concept_id], concept_id))
    for concept_id in ordered_ids:
        decision = recommendation_functions[axis](concept_id)
        row = {
            "concept_id": concept_id,
            "preferred_label": nodes[concept_id]["label"],
            "review_axis": axis,
            "current_parent_ids": ";".join(sorted(parents[concept_id] & axis_members[axis])),
            **decision,
            "reviewer": REVIEWER,
            "review_date": REVIEW_DATE,
        }
        review_rows.append(row)
        review_by_id[concept_id] = row

assert len(review_rows) == len(review_by_id) == 164
write_rows(REVIEW, review_fields, review_rows)

counted_properties = [
    "aom:ingredientPart",
    "aom:materialComponent",
    "aom:primaryConstituent",
    "aom:compositionState",
]
inventory_fields = [
    "concept_id",
    "preferred_label",
    "review_axis",
    "depth_from_axis_root",
    "current_parent_ids",
    "current_parent_labels",
    "direct_child_count",
    "descendant_count",
    "semantic_type",
    "ingredient_part_assertions",
    "material_component_assertions",
    "primary_constituent_assertions",
    "composition_state_assertions",
    "distinct_material_count",
    "review_role",
    "review_status",
    "current_definition",
]
inventory_rows = []
for row in review_rows:
    concept_id = row["concept_id"]
    axis = row["review_axis"]
    root_id = AXIS_ROOTS[axis]
    current_parents = sorted(parents[concept_id] & axis_members[axis])
    material_ids = set().union(
        *(facet_materials[(target_property, concept_id)] for target_property in counted_properties)
    )
    inventory_rows.append(
        {
            "concept_id": concept_id,
            "preferred_label": nodes[concept_id]["label"],
            "review_axis": axis,
            "depth_from_axis_root": 0 if concept_id == root_id else axis_depths[axis][concept_id],
            "current_parent_ids": ";".join(current_parents),
            "current_parent_labels": ";".join(nodes[parent_id]["label"] for parent_id in current_parents),
            "direct_child_count": len(children[concept_id] & axis_members[axis]),
            "descendant_count": len(set(descendant_depths(concept_id)) & review_ids),
            "semantic_type": semantic_types.get(concept_id, ""),
            "ingredient_part_assertions": facet_counts[("aom:ingredientPart", concept_id)],
            "material_component_assertions": facet_counts[("aom:materialComponent", concept_id)],
            "primary_constituent_assertions": facet_counts[("aom:primaryConstituent", concept_id)],
            "composition_state_assertions": facet_counts[("aom:compositionState", concept_id)],
            "distinct_material_count": len(material_ids),
            "review_role": row["review_role"],
            "review_status": row["status"],
            "current_definition": definitions.get(concept_id, ""),
        }
    )
write_rows(INVENTORY, inventory_fields, inventory_rows)

usage_fields = [
    "feed_material_id",
    "feed_material_label",
    "target_property",
    "target_concept_id",
    "target_label",
    "review_axis",
    "recommended_disposition",
    "status",
    "reviewer",
    "review_date",
    "evidence",
    "rationale",
    "rule_id",
]
usage_rows = []
for row in facet_rows:
    target_id = row["target_concept_id"]
    if target_id not in review_ids:
        continue
    decision = review_by_id[target_id]
    usage_rows.append(
        {
            "feed_material_id": row["feed_material_id"],
            "feed_material_label": nodes[row["feed_material_id"]]["label"],
            "target_property": row["target_property"],
            "target_concept_id": target_id,
            "target_label": row["target_label"],
            "review_axis": decision["review_axis"],
            "recommended_disposition": decision["recommended_disposition"],
            "status": row["status"],
            "reviewer": row["reviewer"],
            "review_date": row["review_date"],
            "evidence": row["evidence"],
            "rationale": row["rationale"],
            "rule_id": row["rule_id"],
        }
    )
usage_rows.sort(key=lambda row: (row["target_property"], row["target_concept_id"], row["feed_material_id"], row["rule_id"]))
assert len(usage_rows) == 627
write_rows(USAGE, usage_fields, usage_rows)

anatomy_fields = [
    "concept_id",
    "preferred_label",
    "recommended_group",
    "mapping_status",
    "authority",
    "authority_id",
    "authority_label",
    "recommended_mapping_relation",
    "evidence_ids",
    "rationale",
    "blocking_question",
]
anatomy_rows = []
for concept_id in sorted(children[ANATOMY_ROOT], key=lambda item: nodes[item]["label"]):
    label = nodes[concept_id]["label"]
    if concept_id in plant_ontology_mappings:
        authority_id, authority_label = plant_ontology_mappings[concept_id]
        values = {
            "recommended_group": "Plant anatomical components",
            "mapping_status": "exact-label-candidate",
            "authority": "Plant Ontology",
            "authority_id": authority_id,
            "authority_label": authority_label,
            "recommended_mapping_relation": "review for skos:exactMatch",
            "evidence_ids": "PLANT-ONTOLOGY" + (";PO-ENDOSPERM" if concept_id == "AOM_101153" else ""),
            "rationale": "Pinned Plant Ontology contains same preferred label; definition comparison remains required before asserting exact mapping.",
            "blocking_question": "Does AOM definition and every current use match external anatomical scope across taxa?",
        }
    elif concept_id in animal_ontology_mappings:
        authority_id, authority_label = animal_ontology_mappings[concept_id]
        values = {
            "recommended_group": "Animal anatomical components",
            "mapping_status": "exact-label-candidate",
            "authority": "Uberon",
            "authority_id": authority_id,
            "authority_label": authority_label,
            "recommended_mapping_relation": "review for skos:exactMatch",
            "evidence_ids": "UBERON",
            "rationale": "Uberon contains same preferred label; definition and source-species scope remain implementation gates.",
            "blocking_question": "Does AOM definition match Uberon entity without feed-product meaning?",
        }
    elif concept_id == "AOM_101044":
        values = {
            "recommended_group": "Animal anatomical components",
            "mapping_status": "close-collective-candidate",
            "authority": "Uberon",
            "authority_id": "UBERON:0002075",
            "authority_label": "viscus",
            "recommended_mapping_relation": "review for skos:closeMatch",
            "evidence_ids": "UBERON",
            "rationale": "Current plural collective descriptor may be broader than singular Uberon viscus.",
            "blocking_question": "Is Viscera one anatomy collection, generic organ category, or offal material identity?",
        }
    elif concept_id == "AOM_101029":
        values = {
            "recommended_group": "semantic split required",
            "mapping_status": "related-only-semantic-split",
            "authority": "Plant Ontology;EU Catalogue",
            "authority_id": "PO:0009009",
            "authority_label": "plant embryo",
            "recommended_mapping_relation": "skos:relatedMatch only until split",
            "evidence_ids": "PO-EMBRYO;EU-FEED-CATALOGUE;FOODON-PINNED",
            "rationale": "Germ is only related synonym for embryo while commercial maize germ is process-defined mixed-tissue product.",
            "blocking_question": "Which stable ID retains anatomical meaning and how are commercial germ materials represented?",
        }
    elif concept_id == "AOM_101040":
        values = {
            "recommended_group": "source-specific split required",
            "mapping_status": "ambiguous-biological-source",
            "authority": "Plant Ontology;Uberon",
            "authority_id": "",
            "authority_label": "",
            "recommended_mapping_relation": "none pending source split",
            "evidence_ids": "PLANT-ONTOLOGY;UBERON",
            "rationale": "Shell can denote plant covering, animal shell, or processed material; one unqualified anatomy value is unsafe.",
            "blocking_question": "Which source-specific structures occur in current materials?",
        }
    else:
        values = {
            "recommended_group": "Plant anatomical components candidate" if concept_id not in ambiguous_anatomy else "hold outside exact anatomy",
            "mapping_status": "exact-mapping-pending" if concept_id not in ambiguous_anatomy else "vernacular-or-collective-hold",
            "authority": "Plant Ontology;FoodOn",
            "authority_id": "",
            "authority_label": "",
            "recommended_mapping_relation": "none pending concept-level review",
            "evidence_ids": "PLANT-ONTOLOGY;FOODON-PINNED",
            "rationale": "Label is plant-oriented but exact anatomical identity is not established by current generic definition.",
            "blocking_question": "What exact taxon-aware anatomy or material meaning matches current uses?",
        }
    anatomy_rows.append({"concept_id": concept_id, "preferred_label": label, **values})

assert len(anatomy_rows) == 31
write_rows(ANATOMY, anatomy_fields, anatomy_rows)

collision_fields = [
    "case_id",
    "candidate_a_id",
    "candidate_a_label",
    "candidate_b_id",
    "candidate_b_label",
    "overlap_basis",
    "recommended_disposition",
    "evidence_ids",
    "status",
    "blocking_question",
    "rationale",
]
collision_cases = [
    (
        "IDENTITY-001",
        "AOM_101103",
        "AOM_001616",
        "Blood component versus Blood; component property context may have created duplicate identity.",
        "deprecate AOM_101103 and reuse AOM_001616 if definitions confirm exact identity",
        "LOCAL-GRAPH;UBERON;FOODON-REPO",
        "proposed",
        "Does AOM_001616 Blood cover reusable body-substance identity without source-specific product meaning?",
        "AOM_101103 has zero uses and property context alone cannot justify duplicate identity.",
    ),
    (
        "IDENTITY-002",
        "AOM_101120",
        "AOM_001571",
        "Protein constituent versus Protein after AOM_001571 was reclassified as chemical constituent.",
        "deprecate AOM_101120 after one assertion migrates to corrected AOM_001571",
        "LOCAL-GRAPH;AOM-SCHEMA;CHEBI-ENTITY",
        "proposed",
        "Does corrected AOM_001571 definition cover every intended Protein constituent use?",
        "Primary relation supplies constituent role; duplicate target is unnecessary if identity matches.",
    ),
    (
        "IDENTITY-003",
        "AOM_101065",
        "AOM_001832",
        "Starch constituent versus Starch feed material.",
        "hold identity-versus-product-use reuse decision",
        "LOCAL-GRAPH;AOM-SCHEMA;CHEBI-ENTITY",
        "held",
        "Can one Starch identity bear feed-material use and constituent relations without duplicate SKOS concepts?",
        "Accepted product-kind separation does not by itself prove two starch identities.",
    ),
    (
        "IDENTITY-004",
        "AOM_101081",
        "AOM_001333",
        "Oil constituent versus Oil feed material.",
        "hold identity-versus-product-use reuse decision",
        "LOCAL-GRAPH;AOM-SCHEMA;CHEBI-SUBSTANCE",
        "held",
        "Is Oil one reusable material identity, a chemical mixture category, or distinct product and constituent scopes?",
        "Current relation and product branches distinguish use but definitions do not yet prove distinct entities.",
    ),
    (
        "IDENTITY-005",
        "AOM_101106",
        "AOM_000582",
        "Straw component versus Unspecified Straw feed material.",
        "remove tautological component use and review replacement by AOM_000582",
        "LOCAL-GRAPH;AGROVOC-STRAW;NALT-CROP-RESIDUES",
        "held",
        "Does Unspecified Straw mean generic Straw or only a source-unresolved feed record category?",
        "External authorities describe Straw as crop-residue material; component context alone does not prove separate identity.",
    ),
    (
        "IDENTITY-006",
        "AOM_101104",
        "AOM_000563",
        "Bran processed fraction versus Unspecified Bran feed material.",
        "retain as explicit hold pending generic-versus-source-unspecified scope review",
        "LOCAL-GRAPH;EU-FEED-CATALOGUE;FOODON-PINNED",
        "held",
        "Does Unspecified Bran denote same generic milling fraction or a feed material with unknown biological source?",
        "Bran is process-defined in both contexts; current definitions may distinguish scope but not identity conclusively.",
    ),
    (
        "IDENTITY-007",
        "AOM_101029",
        "AOM_001294",
        "Germ anatomical component versus Maize Germ manufacturing product.",
        "retain distinct meanings and rename anatomical concept after split",
        "LOCAL-GRAPH;PO-EMBRYO;EU-FEED-CATALOGUE",
        "proposed",
        "Which label and identifier should carry plant embryo meaning?",
        "Plant Ontology and EU Catalogue support distinct anatomy and process-product meanings.",
    ),
    (
        "IDENTITY-008",
        "AOM_001577",
        "AOM_000228",
        "Carbohydrate chemical entity category versus Carbohydrate measured composition characteristic.",
        "retain distinct IDs and relabel composition characteristic for clarity",
        "LOCAL-GRAPH;AOM-SCHEMA;CHEBI-ENTITY",
        "proposed",
        "",
        "Identity and measured concentration are different entities despite shared lexical label.",
    ),
    (
        "IDENTITY-009",
        "AOM_101080",
        "AOM_000226",
        "Ash constituent category versus Ash composition characteristic or incineration residue.",
        "hold until Cohort E distinguishes residue identity from measured ash content",
        "LOCAL-GRAPH;AOM-SCHEMA;CHEBI-SUBSTANCE",
        "held",
        "Is Ash target a processed residue material, a chemical-constituent category, or ash-content measurement?",
        "Current definitions and hierarchy encode different roles without enough evidence for merge or exact separation.",
    ),
]
collision_rows = []
for case_id, candidate_a_id, candidate_b_id, overlap_basis, disposition, evidence, status, question, rationale in collision_cases:
    assert candidate_a_id in nodes and candidate_b_id in nodes
    assert set(evidence.split(";")) <= evidence_ids
    collision_rows.append(
        {
            "case_id": case_id,
            "candidate_a_id": candidate_a_id,
            "candidate_a_label": nodes[candidate_a_id]["label"],
            "candidate_b_id": candidate_b_id,
            "candidate_b_label": nodes[candidate_b_id]["label"],
            "overlap_basis": overlap_basis,
            "recommended_disposition": disposition,
            "evidence_ids": evidence,
            "status": status,
            "blocking_question": question,
            "rationale": rationale,
        }
    )
write_rows(COLLISIONS, collision_fields, collision_rows)

status_counts = Counter(row["status"] for row in review_rows)
axis_counts = Counter(row["review_axis"] for row in review_rows)
usage_property_counts = Counter(row["target_property"] for row in usage_rows)
summary = {
    "status": "recommendation-only",
    "decision_status": "proposed-pending-human-review",
    "review_issue": "https://github.com/ERAgriculture/era-program/issues/55",
    "proposed_adr": "docs/decisions/0048-chemical-identity-composition-and-component-model.md",
    "source_commit": SOURCE_COMMIT,
    "review_author": REVIEWER,
    "review_date": REVIEW_DATE,
    "reviewed_concepts": len(review_rows),
    "axis_concept_counts": dict(sorted(axis_counts.items())),
    "review_status_counts": dict(sorted(status_counts.items())),
    "anatomical_children_reviewed": len(anatomy_rows),
    "exact_label_authority_candidates": sum(row["mapping_status"] == "exact-label-candidate" for row in anatomy_rows),
    "identity_overlap_cases": len(collision_rows),
    "affected_material_assertions": len(usage_rows),
    "affected_assertion_property_counts": dict(sorted(usage_property_counts.items())),
    "affected_materials": len({row["feed_material_id"] for row in usage_rows}),
    "proposed_navigation_concepts_without_ids": [
        "Plant anatomical components",
        "Animal anatomical components",
    ],
    "implementation_changes": 0,
    "allocated_identifiers": 0,
    "inputs": {
        "nodes_sha256": file_sha256(GRAPH / "nodes.csv"),
        "edges_sha256": file_sha256(GRAPH / "edges.csv"),
        "definitions_sha256": file_sha256(DATA / "definitions.csv"),
        "semantic_types_sha256": file_sha256(DATA / "approved_concept_semantic_types.csv"),
        "facets_sha256": file_sha256(FACETS),
        "evidence_register_sha256": file_sha256(OUT / "evidence_register.csv"),
        "authority_comparison_sha256": file_sha256(OUT / "authority_comparison.csv"),
    },
    "outputs": {
        "review_sha256": file_sha256(REVIEW),
        "inventory_sha256": file_sha256(INVENTORY),
        "usage_sha256": file_sha256(USAGE),
        "anatomy_sha256": file_sha256(ANATOMY),
        "identity_overlap_sha256": file_sha256(COLLISIONS),
    },
}
SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
