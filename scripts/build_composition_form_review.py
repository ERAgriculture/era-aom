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
OUT = ROOT / "review" / "livestock-v39"
SOURCE_COMMIT = "dc36ae5bb3977e1f63074334f6b3ac90200ffb4c"
REVIEWER = "Codex"
REVIEW_DATE = "2026-08-21"

AXIS_ROOTS = {
    "physical-characteristic": "AOM_000326",
    "presentation-form": "AOM_101020",
    "bulk-consistency": "AOM_101132",
    "moisture-condition": "AOM_101133",
    "component-retention": "AOM_101115",
}
EXTRA_AXES = {
    "dual-use-constituent": {
        "AOM_101080", "AOM_001577", "AOM_101067", "AOM_101066",
        "AOM_101064", "AOM_101081", "AOM_001571", "AOM_101120",
        "AOM_101065",
    },
    "specific-material": {"AOM_000764", "AOM_000766", "AOM_001938"},
}


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_rows(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


OUT.mkdir(parents=True, exist_ok=True)
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
product_types = {
    row["concept_id"]: row["semantic_class"]
    for row in read_rows(DATA / "approved_feed_taxonomy_classifications.csv")
    if row["status"] == "approved"
}
parents = defaultdict(set)
children = defaultdict(set)
for row in read_rows(GRAPH / "edges.csv"):
    if row["edge_type"] == "broader":
        parents[row["source"]].add(row["target"])
        children[row["target"]].add(row["source"])


def label(concept_id):
    return nodes[concept_id]["label"]


def descendant_depths(root_id):
    found = {root_id: 0}
    pending = deque((concept_id, 1) for concept_id in children[root_id])
    while pending:
        concept_id, depth = pending.popleft()
        if concept_id in found and found[concept_id] <= depth:
            continue
        found[concept_id] = depth
        pending.extend((child_id, depth + 1) for child_id in children[concept_id])
    return found


scope = {}
for axis, root_id in AXIS_ROOTS.items():
    for concept_id, depth in descendant_depths(root_id).items():
        assert concept_id not in scope
        scope[concept_id] = (axis, depth)
for axis, concept_ids in EXTRA_AXES.items():
    for concept_id in concept_ids:
        assert concept_id not in scope
        scope[concept_id] = (axis, 0)
assert len(scope) == 40

facet_rows = read_rows(FACETS)
affected_rows = [row for row in facet_rows if row["target_concept_id"] in scope]
assert len(affected_rows) == 796
facet_counts = Counter(row["target_concept_id"] for row in affected_rows)
facet_materials = defaultdict(set)
for row in affected_rows:
    facet_materials[row["target_concept_id"]].add(row["feed_material_id"])

evidence_ids = {
    row["evidence_id"] for row in read_rows(OUT / "evidence_register.csv")
}


def recommendation(
    role,
    disposition,
    action,
    evidence,
    rationale,
    proposed_label="",
    proposed_parent="",
    mapping="",
    status="approved",
    blocking_question="",
):
    referenced = set(evidence.split(";"))
    assert referenced <= evidence_ids, sorted(referenced - evidence_ids)
    return {
        "review_role": role,
        "recommended_disposition": disposition,
        "proposed_label": proposed_label,
        "proposed_parent_or_axis": proposed_parent,
        "recommended_semantic_action": action,
        "mapping_candidate": mapping,
        "evidence_ids": evidence,
        "status": status,
        "blocking_question": blocking_question,
        "rationale": rationale,
    }


def reviewed(concept_id):
    if concept_id == "AOM_000326":
        return recommendation(
            "measured-physical-root", "retain-and-rename",
            "Keep measurable or observable physical characteristics distinct from categorical form, consistency, moisture, and process.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-PHYSICAL;FOODON-STRUCTURE",
            "Current singular label and legacy child blur measured qualities with descriptive states.",
            proposed_label="Feed physical characteristics",
            proposed_parent="AOM_000328 Feed Characteristic",
        )
    if concept_id == "AOM_000324":
        return recommendation(
            "legacy-conflated-characteristic", "deprecate-and-replace",
            "Replace legacy value with an unallocated Feed physical descriptors navigation concept above presentation, bulk-consistency, and moisture-condition axes.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-FACETS;FOODON-PHYSICAL",
            "Definition conflates dry, wet, pellet, and paste across independent moisture, presentation, and consistency axes.",
            proposed_parent="replace with unallocated Feed physical descriptors under AOM_000328",
        )
    if concept_id in {"AOM_000322", "AOM_000323", "AOM_000325"}:
        return recommendation(
            "measured-physical-characteristic", "retain-measured-characteristic",
            "Retain under Feed physical characteristics and keep categorical form or process assertions separate.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-PHYSICAL;FOODON-STRUCTURE",
            "Concept denotes measurable or observable physical quality rather than presentation category.",
            proposed_parent="AOM_000326 Feed physical characteristics",
        )
    if concept_id == "AOM_101020":
        return recommendation(
            "presentation-axis-root", "retain-and-reparent",
            "Place beneath proposed Feed physical descriptors navigation while preserving aom:presentationForm.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-FACETS;FOODON-PHYSICAL",
            "Presentation answers visible shape or particle presentation, not moisture, bulk flow, or processing method.",
            proposed_parent="unallocated Feed physical descriptors",
        )
    if concept_id == "AOM_101050":
        return recommendation(
            "delivery-mode-misclassified-as-form", "remove-from-presentation-hold-replacement",
            "Do not use Lick as presentation form; hold stable ID until a feed offering or consumption-mode axis is reviewed.",
            "LOCAL-GRAPH;FAO-BLOCKS;FEEDIPEDIA-MINERAL-BLOCK",
            "Animals may lick a coherent block, but licking describes consumption or delivery while block describes physical presentation.",
            proposed_parent="future feed offering or consumption-mode axis",
            status="held",
            blocking_question="Which governed relation should represent free-choice licking, and does it apply beyond mineral formulations?",
        )
    if concept_id in {"AOM_101051", "AOM_101126"}:
        return recommendation(
            "comminuted-presentation", "retain-under-comminuted-form",
            "Retain beneath Comminuted particle form; require separate particle-size and drying assertions when evidence supports them.",
            "LOCAL-GRAPH;AOM-SCHEMA;FEEDIPEDIA-GLOSSARY",
            "Meal and powder are useful presentation labels but do not establish one universal particle threshold or moisture condition.",
            proposed_parent="AOM_101125 Comminuted particle form",
        )
    if concept_id == "AOM_101125":
        return recommendation(
            "particle-presentation-grouping", "retain-grouping",
            "Retain as presentation grouping for size-reduced particles; keep Grinding and particle-size measurements independent.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-STRUCTURE",
            "Resulting presentation, process applied, and measured particle size answer different questions.",
            proposed_parent="AOM_101020 Feed presentation forms",
        )
    if scope[concept_id][0] == "presentation-form":
        return recommendation(
            "presentation-form-value", "retain-presentation-value",
            "Retain under Feed presentation forms with definition specific to visible presentation and no moisture or process inference.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-PHYSICAL",
            "Current value can remain useful when relation scope is explicit and independent.",
            proposed_parent="AOM_101020 Feed presentation forms",
        )
    if concept_id == "AOM_101132":
        return recommendation(
            "bulk-consistency-axis-root", "retain-and-reparent",
            "Place beneath proposed Feed physical descriptors navigation while preserving aom:bulkConsistency.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-PHYSICAL",
            "Bulk flow and dispersion are categorical physical descriptors independent of particle presentation and moisture condition.",
            proposed_parent="unallocated Feed physical descriptors",
        )
    if concept_id in {"AOM_101077", "AOM_101078", "AOM_101118"}:
        return recommendation(
            "bulk-consistency-value", "retain-distinct-consistency",
            "Retain current stable ID and sharpen definition without inferring moisture amount or processing method.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-PHYSICAL",
            "Liquid lacks a governed dispersed-solid requirement; slurry requires solids in a liquid phase; pulp denotes moist fibrous or cellular semisolid material.",
            proposed_parent="AOM_101132 Feed bulk consistencies",
        )
    if concept_id == "AOM_101133":
        return recommendation(
            "moisture-condition-axis-root", "retain-and-reparent",
            "Place beneath proposed Feed physical descriptors navigation while preserving aom:moistureCondition.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-PHYSICAL;FEEDIPEDIA-GLOSSARY",
            "Moisture condition is independent of solid shape, particle presentation, and bulk flow.",
            proposed_parent="unallocated Feed physical descriptors",
        )
    if concept_id in {"AOM_001510", "AOM_101054"}:
        return recommendation(
            "moisture-condition-value", "retain-moisture-value",
            "Retain under Feed moisture conditions; do not infer solid form from Dried or exact water content from Fresh.",
            "LOCAL-GRAPH;AOM-SCHEMA;FEEDIPEDIA-GLOSSARY",
            "Drying changes moisture condition while solids may exist without drying and dried materials may have many presentations.",
            proposed_parent="AOM_101133 Feed moisture conditions",
        )
    if concept_id == "AOM_101115":
        return recommendation(
            "component-retention-axis-root", "retain-and-rename",
            "Keep positive retained-component states independent of measured composition and negative absence-of-process categories.",
            "LOCAL-GRAPH;AOM-SCHEMA;ADR-0048",
            "Axis records what native component remains; it should not encode measured quantity or merely lack of defatting.",
            proposed_label="Feed component-retention states",
            proposed_parent="AOM_000328 Feed Characteristic",
        )
    if concept_id == "AOM_101086":
        return recommendation(
            "whole-crop-retention", "retain-and-rename",
            "Retain stable ID and current componentRetentionState assertion; make component-retention meaning explicit in label.",
            "LOCAL-GRAPH;AOM-SCHEMA;ADR-0048",
            "Whole-crop describes retained harvested scope, not measured chemical composition.",
            proposed_label="Whole-crop component retention",
            proposed_parent="AOM_101115 Feed component-retention states",
        )
    if concept_id == "AOM_101110":
        return recommendation(
            "whole-grain-retention", "retain-and-rename",
            "Retain stable ID and current componentRetentionState assertions; preserve positive retained Bran, plant embryo, and Endosperm relations.",
            "LOCAL-GRAPH;AOM-SCHEMA;ADR-0048",
            "Whole-grain integrity remains true after grinding and must not be treated as presentation or measured composition.",
            proposed_label="Whole-grain component retention",
            proposed_parent="AOM_101115 Feed component-retention states",
        )
    if concept_id == "AOM_101116":
        return recommendation(
            "whole-milk-state", "deprecate-after-migration",
            "Move current Whole Milk assertion to Native-fat retention when purpose is retained milk fat, then publish replacement history and retire product-specific state.",
            "LOCAL-GRAPH;AOM-SCHEMA;ADR-0048;EU-CATALOGUE",
            "Whole Milk product identity already conveys whole product; current state has one use and its only governed retained-component relation is fat.",
            proposed_parent="replace with AOM_101134 Native-fat retention",
        )
    if concept_id == "AOM_101134":
        return recommendation(
            "native-fat-retention", "retain-rename-and-repredicate",
            "Rename and migrate three relevant materials to aom:componentRetentionState while retaining positive aom:retainsChemicalConstituent fat relation.",
            "LOCAL-GRAPH;AOM-SCHEMA;ADR-0048",
            "Positive native-fat retention is component retention; it is not measured fat content and does not merely assert absence of defatting.",
            proposed_label="Native-fat retention",
            proposed_parent="AOM_101115 Feed component-retention states",
        )
    if concept_id == "AOM_101080":
        return recommendation(
            "analytical-residue-misclassified-as-constituent", "deprecate-category-error",
            "Remove Bone Ash primaryConstituent assertion; use AOM_000226 Ash for measured ash characteristic and explicit mineral identities when known.",
            "LOCAL-GRAPH;AOM-SCHEMA;FAO-ASH;FEEDIPEDIA-GLOSSARY",
            "Ash is analytical residue after incineration, not one chemical constituent; Bone Ash to Ash constituent is also identity-tautological.",
            proposed_parent="replace analytical use with AOM_000226 Ash",
        )
    if concept_id == "AOM_001577":
        return recommendation(
            "chemical-identity", "retain-and-map",
            "Retain chemical identity and map to ChEBI; keep measured carbohydrate composition and feed-material use separate.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-CHEMICAL;CHEBI-CARBOHYDRATE",
            "One reusable chemical identity can support constituent relations without becoming a concentration characteristic or feed product.",
            mapping="CHEBI:16646 exactMatch candidate",
        )
    if concept_id == "AOM_001571":
        return recommendation(
            "chemical-identity", "retain-and-map",
            "Retain chemical identity and map to ChEBI; keep measured protein composition and feed-material use separate.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-CHEMICAL;CHEBI-PROTEIN",
            "Existing identity replaces deprecated Protein constituent while relation supplies constituent role.",
            mapping="CHEBI:36080 exactMatch candidate",
        )
    if concept_id == "AOM_101120":
        return recommendation(
            "deprecated-duplicate", "retain-deprecation",
            "Keep deprecated with replacement AOM_001571 and no hierarchy or material assertions.",
            "LOCAL-GRAPH;ADR-0048;CHEBI-PROTEIN",
            "ADR 0048 implementation already removed duplicate active identity.",
            proposed_parent="replaced by AOM_001571 Protein",
            mapping="AOM_001571 replacement",
        )
    if concept_id == "AOM_101065":
        return recommendation(
            "chemical-mixture-identity", "retain-label-and-map",
            "Retain Starch constituent label because bare Starch collides with feed-material label; map chemical scope to ChEBI and retain four primaryConstituent assertions.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-CHEMICAL;CHEBI-STARCH",
            "Qualified label distinguishes chemical constituent identity from AOM_001832 Starch feed material while preserving one semantic target.",
            mapping="CHEBI:28017 exactMatch candidate",
        )
    if concept_id == "AOM_101067":
        return recommendation(
            "chemical-mixture-identity", "retain-rename-and-map",
            "Use readable Essential oil constituent label and map to ChEBI mixture identity; keep product or additive use separate.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-CHEMICAL;CHEBI-ESSENTIAL-OIL",
            "Essential oil is a chemical mixture identity; constituent role comes from relation and product use remains independent.",
            proposed_label="Essential oil constituent",
            mapping="CHEBI:83630 exactMatch candidate",
        )
    if concept_id in {"AOM_101066", "AOM_101081"}:
        return recommendation(
            "contextual-lipid-constituent", "retain-qualified-label-broad-map",
            "Retain qualified constituent label and current assertions; use only broad lipid mapping until fat-versus-oil scope is externally aligned.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-CHEMICAL;CHEBI-LIPID",
            "Fat and oil are context-sensitive mixtures; bare Oil also collides with existing AOM_001333 feed-material identity.",
            mapping="CHEBI:18059 broadMatch candidate",
        )
    if concept_id == "AOM_101064":
        return recommendation(
            "heterogeneous-protein-fraction", "hold-identity-boundary",
            "Retain stable ID without new assertion or mapping until gluten chemical-mixture versus processed-material scope is reviewed.",
            "LOCAL-GRAPH;AOM-SCHEMA;FOODON-CHEMICAL",
            "Gluten can denote heterogeneous protein fraction or commercial material; current definition does not resolve identity.",
            status="held",
            blocking_question="Does AOM require one gluten chemical-mixture identity, one processed feed-material identity, or linked concepts for both?",
        )
    if concept_id == "AOM_000764":
        return recommendation(
            "mineral-formulation-block", "retain-distinct-formulation",
            "Retain FeedFormulation classification and Block form assertion; do not merge with Mineral Lick.",
            "LOCAL-GRAPH;AOM-SCHEMA;FAO-BLOCKS;FEEDIPEDIA-MINERAL-BLOCK",
            "Block is coherent physical presentation; formulation remains distinct from consumption mode.",
            proposed_parent="AOM_101140 Mineral complementary feeds",
        )
    if concept_id == "AOM_000766":
        return recommendation(
            "mineral-formulation-lick", "retain-distinct-formulation",
            "Retain FeedFormulation classification; do not infer Block form and clarify lick as intended gradual or free-choice consumption.",
            "LOCAL-GRAPH;AOM-SCHEMA;FAO-BLOCKS;FEEDIPEDIA-MINERAL-BLOCK",
            "Mineral lick may be block or another presentation; current lack of form assertion is safer than treating lick as shape.",
            proposed_parent="AOM_101140 Mineral complementary feeds",
        )
    if concept_id == "AOM_001938":
        return recommendation(
            "processed-poultry-offal-material", "retain-and-add-product-role",
            "Retain Chicken source/offal identity plus Dried, Meal, Drying, and Grinding assertions; add aom:productRole AOM_101062 By-product role.",
            "LOCAL-GRAPH;AOM-SCHEMA;FEEDIPEDIA-POULTRY-OFFAL;FEEDIPEDIA-POULTRY-BYPRODUCT",
            "Mapped Feedipedia material is poultry offal meal within animal by-products; economic role is independent of source, process, form, and moisture.",
            proposed_parent="AOM_100983 Chicken feed materials",
        )
    raise AssertionError(concept_id)


review_rows = []
inventory_rows = []
for concept_id in sorted(scope, key=lambda item: (scope[item][0], scope[item][1], label(item), item)):
    axis, depth = scope[concept_id]
    rec = reviewed(concept_id)
    parent_ids = sorted(parents[concept_id])
    descendants = descendant_depths(concept_id)
    descendants.pop(concept_id)
    inventory_rows.append({
        "concept_id": concept_id,
        "preferred_label": label(concept_id),
        "review_axis": axis,
        "depth_from_axis_root": depth,
        "current_parent_ids": ";".join(parent_ids),
        "current_parent_labels": ";".join(label(item) for item in parent_ids),
        "direct_child_count": len(children[concept_id]),
        "descendant_count": len(descendants),
        "semantic_type": semantic_types.get(concept_id, product_types.get(concept_id, "")),
        "affected_assertion_count": facet_counts[concept_id],
        "distinct_material_count": len(facet_materials[concept_id]),
        "review_role": rec["review_role"],
        "review_status": rec["status"],
        "current_definition": definitions.get(concept_id, ""),
    })
    review_rows.append({
        "concept_id": concept_id,
        "preferred_label": label(concept_id),
        "review_axis": axis,
        "review_role": rec["review_role"],
        "current_parent_ids": ";".join(parent_ids),
        **rec,
        "reviewer": REVIEWER,
        "review_date": REVIEW_DATE,
    })

inventory_fields = list(inventory_rows[0])
review_fields = list(review_rows[0])
write_rows(OUT / "composition_form_inventory.csv", inventory_fields, inventory_rows)
write_rows(OUT / "composition_form_review.csv", review_fields, review_rows)


def assertion_action(target_id):
    if target_id == "AOM_101116":
        return "migrate target to AOM_101134 and property to aom:componentRetentionState"
    if target_id == "AOM_101134":
        return "migrate property to aom:componentRetentionState"
    if target_id == "AOM_101080":
        return "remove tautological primaryConstituent assertion"
    return "retain assertion; apply approved target label or hierarchy changes only"


review_by_id = {row["concept_id"]: row for row in review_rows}
material_labels = {row["node_id"]: row["label"] for row in read_rows(GRAPH / "nodes.csv")}
assertion_rows = []
for row in sorted(affected_rows, key=lambda item: (item["target_property"], item["target_concept_id"], item["feed_material_id"])):
    target_review = review_by_id[row["target_concept_id"]]
    assertion_rows.append({
        "feed_material_id": row["feed_material_id"],
        "feed_material_label": material_labels[row["feed_material_id"]],
        "target_property": row["target_property"],
        "target_concept_id": row["target_concept_id"],
        "target_label": row["target_label"],
        "review_axis": target_review["review_axis"],
        "recommended_assertion_action": assertion_action(row["target_concept_id"]),
        "review_status": target_review["status"],
        "current_status": row["status"],
        "current_evidence": row["evidence"],
        "current_rationale": row["rationale"],
        "reviewer": REVIEWER,
        "review_date": REVIEW_DATE,
    })
write_rows(OUT / "affected_material_assertions.csv", list(assertion_rows[0]), assertion_rows)

specific_ids = {"AOM_000764", "AOM_000766", "AOM_001938"}
specific_facets = defaultdict(list)
for row in facet_rows:
    if row["feed_material_id"] in specific_ids:
        target = row["target_concept_id"] or row["target_uri"]
        specific_facets[row["feed_material_id"]].append(
            f'{row["target_property"]}={target} {row["target_label"]}'.strip()
        )
specific_rows = []
for concept_id in sorted(specific_ids):
    rec = reviewed(concept_id)
    proposed_relation = ""
    proposed_target = ""
    if concept_id == "AOM_001938":
        proposed_relation = "aom:productRole"
        proposed_target = "AOM_101062 By-product role"
    specific_rows.append({
        "concept_id": concept_id,
        "preferred_label": label(concept_id),
        "current_product_type": product_types.get(concept_id, "aom:FeedMaterial"),
        "current_parent_ids": ";".join(sorted(parents[concept_id])),
        "current_facets": "; ".join(sorted(specific_facets[concept_id])),
        "recommended_disposition": rec["recommended_disposition"],
        "proposed_relation": proposed_relation,
        "proposed_target": proposed_target,
        "evidence_ids": rec["evidence_ids"],
        "status": rec["status"],
        "rationale": rec["rationale"],
        "reviewer": REVIEWER,
        "review_date": REVIEW_DATE,
    })
write_rows(OUT / "specific_material_review.csv", list(specific_rows[0]), specific_rows)

overlap_rows = [
    {
        "case_id": "FORM-001", "concepts": "AOM_000324;AOM_101020;AOM_101132;AOM_101133",
        "overlap_basis": "Legacy physical form definition combines presentation, consistency, and moisture examples.",
        "recommended_boundary": "Deprecate AOM_000324; add unallocated Feed physical descriptors navigation above three independent relation ranges.",
        "evidence_ids": "LOCAL-GRAPH;AOM-SCHEMA;FOODON-FACETS;FOODON-PHYSICAL", "status": "proposed",
    },
    {
        "case_id": "FORM-002", "concepts": "AOM_101125;AOM_101126;AOM_101051;AOM_000323",
        "overlap_basis": "Meal and powder are size-reduced presentations but do not establish one measured particle threshold.",
        "recommended_boundary": "Keep presentation hierarchy and measured particle-size characteristic separate.",
        "evidence_ids": "LOCAL-GRAPH;AOM-SCHEMA;FOODON-STRUCTURE", "status": "proposed",
    },
    {
        "case_id": "FORM-003", "concepts": "AOM_101054;AOM_101020",
        "overlap_basis": "Dried is sometimes used conversationally as form although it denotes moisture removal.",
        "recommended_boundary": "Keep Dried under moisture condition; never infer one presentation or solid state.",
        "evidence_ids": "AOM-SCHEMA;FEEDIPEDIA-GLOSSARY", "status": "proposed",
    },
    {
        "case_id": "FORM-004", "concepts": "AOM_101077;AOM_101118;AOM_101078",
        "overlap_basis": "Liquid, slurry, and pulp overlap in ordinary language.",
        "recommended_boundary": "Liquid has no dispersed-solid requirement; slurry requires dispersed solids; pulp is moist fibrous or cellular semisolid.",
        "evidence_ids": "LOCAL-GRAPH;FOODON-PHYSICAL", "status": "proposed",
    },
    {
        "case_id": "FORM-005", "concepts": "AOM_101050;AOM_101049;AOM_000764;AOM_000766",
        "overlap_basis": "Block is presentation while lick is consumption or delivery mode; a block may be licked.",
        "recommended_boundary": "Retain Mineral Block and Mineral Lick as distinct formulations; remove Lick form from presentation and hold replacement axis.",
        "evidence_ids": "LOCAL-GRAPH;FAO-BLOCKS;FEEDIPEDIA-MINERAL-BLOCK", "status": "held",
    },
    {
        "case_id": "RETENTION-001", "concepts": "AOM_101116;AOM_101134",
        "overlap_basis": "Whole-milk state has one use and retained-fat relation duplicates generic native-fat retention intent.",
        "recommended_boundary": "Migrate relevant Whole Milk assertion to Native-fat retention and deprecate product-specific state.",
        "evidence_ids": "LOCAL-GRAPH;AOM-SCHEMA;ADR-0048;EU-CATALOGUE", "status": "proposed",
    },
    {
        "case_id": "CHEMICAL-001", "concepts": "AOM_101080;AOM_000226",
        "overlap_basis": "Ash constituent treats analytical incineration residue as chemical identity.",
        "recommended_boundary": "Deprecate Ash constituent; use measured Ash characteristic and explicit mineral identities.",
        "evidence_ids": "LOCAL-GRAPH;FAO-ASH;FEEDIPEDIA-GLOSSARY", "status": "proposed",
    },
    {
        "case_id": "ROLE-001", "concepts": "AOM_001938;AOM_101062",
        "overlap_basis": "Processed chicken offal material lacks explicit economic product role.",
        "recommended_boundary": "Add independent By-product role without changing chicken source, offal identity, process, moisture, or meal presentation.",
        "evidence_ids": "FEEDIPEDIA-POULTRY-OFFAL;FEEDIPEDIA-POULTRY-BYPRODUCT", "status": "proposed",
    },
]
write_rows(OUT / "axis_overlap_review.csv", list(overlap_rows[0]), overlap_rows)

collision_rows = [
    ("LABEL-001", "AOM_000326", "Feed physical characteristics", "", "approved-no-collision", "Rename existing stable ID."),
    ("LABEL-002", "UNALLOCATED", "Feed physical descriptors", "", "approved-no-collision", "Allocate only after ADR acceptance and full ID audit."),
    ("LABEL-003", "AOM_101115", "Feed component-retention states", "", "approved-no-collision", "Rename existing stable ID."),
    ("LABEL-004", "AOM_101086", "Whole-crop component retention", "", "approved-no-collision", "Rename existing stable ID."),
    ("LABEL-005", "AOM_101110", "Whole-grain component retention", "", "approved-no-collision", "Rename existing stable ID."),
    ("LABEL-006", "AOM_101134", "Native-fat retention", "", "approved-no-collision", "Rename existing stable ID."),
    ("LABEL-007", "AOM_101067", "Essential oil constituent", "", "approved-no-collision", "Rename existing stable ID while retaining constituent-qualified identity."),
    ("LABEL-008", "AOM_101065", "Starch", "AOM_001832 alt label Starch", "blocked-collision", "Retain Starch constituent label."),
    ("LABEL-009", "AOM_101081", "Oil", "AOM_001333 preferred label Oil", "blocked-collision", "Retain Oil constituent label."),
]
label_rows = [
    {
        "case_id": case_id,
        "candidate_concept_id": concept_id,
        "candidate_label": candidate,
        "normalized_label": " ".join(candidate.lower().replace("-", " ").split()),
        "matched_identity": match,
        "decision": decision,
        "reviewer": REVIEWER,
        "review_date": REVIEW_DATE,
        "evidence": "data/livestock-staging/labels.csv;data/livestock-staging/approved_label_additions.csv;data/livestock-staging/approved_external_resource_labels.csv;data/livestock-staging/approved_deprecated_concepts.csv",
        "rationale": rationale,
    }
    for case_id, concept_id, candidate, match, decision, rationale in collision_rows
]
write_rows(OUT / "label_collision_audit.csv", list(label_rows[0]), label_rows)

status_counts = Counter(row["status"] for row in review_rows)
summary = {
    "review": "livestock-v39-composition-form-component-retention",
    "source_commit": SOURCE_COMMIT,
    "review_date": REVIEW_DATE,
    "status": "accepted-recommendation",
    "decision_status": "row-dispositions-approved-with-explicit-holds",
    "reviewed_concepts": len(review_rows),
    "affected_material_assertions": len(assertion_rows),
    "specific_materials_reviewed": len(specific_rows),
    "axis_overlap_cases": len(overlap_rows),
    "label_collision_cases": len(label_rows),
    "review_status_counts": dict(sorted(status_counts.items())),
    "implementation_changes": 0,
    "allocated_identifiers": 0,
    "proposed_navigation_concepts_without_ids": ["Feed physical descriptors"],
    "outputs": {
        "inventory_sha256": sha256(OUT / "composition_form_inventory.csv"),
        "review_sha256": sha256(OUT / "composition_form_review.csv"),
        "assertions_sha256": sha256(OUT / "affected_material_assertions.csv"),
        "specific_materials_sha256": sha256(OUT / "specific_material_review.csv"),
        "overlap_sha256": sha256(OUT / "axis_overlap_review.csv"),
        "collision_sha256": sha256(OUT / "label_collision_audit.csv"),
        "evidence_sha256": sha256(OUT / "evidence_register.csv"),
        "authority_sha256": sha256(OUT / "authority_comparison.csv"),
    },
}
(OUT / "composition_form_summary.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps(summary, indent=2, sort_keys=True))
