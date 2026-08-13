#!/usr/bin/env python3
import csv
import hashlib
import json
import re
from collections import defaultdict, deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "dist" / "livestock-staging"
OUT = ROOT / "review" / "livestock-v31"
INVENTORY_PATH = OUT / "feed_product_kind_inventory.csv"
SUMMARY_PATH = OUT / "feed_product_kind_summary.json"

FEED_MATERIALS = "AOM_100850"
FEED_ADDITIVES = "AOM_101135"
FEED_CHEMICAL_ENTITIES = "AOM_101146"
FEED_CHEMICAL_SUBSTANCES = "AOM_101147"
FORAGE_PLANTS = "AOM_000735"
CROP_PRODUCTS = "AOM_100921"
CROP_BYPRODUCTS = "AOM_001916"
REPORTED = {
    "AOM_100850",
    "AOM_101135",
    "AOM_101146",
    "AOM_101147",
    "AOM_001866",
    "AOM_006349",
    "AOM_000735",
    "AOM_100921",
    "AOM_001916",
}


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_label(value):
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


labels = {
    row["node_id"]: row["label"]
    for row in read_rows(GRAPH / "nodes.csv")
}
parents = defaultdict(set)
children = defaultdict(set)
for row in read_rows(GRAPH / "edges.csv"):
    if row["edge_type"] == "broader":
        parents[row["source"]].add(row["target"])
        children[row["target"]].add(row["source"])


def depths(root):
    found = {}
    pending = deque((concept_id, 1) for concept_id in children[root])
    while pending:
        concept_id, depth = pending.popleft()
        if concept_id in found and found[concept_id] <= depth:
            continue
        found[concept_id] = depth
        pending.extend((child_id, depth + 1) for child_id in children[concept_id])
    return found


feed_material_depths = depths(FEED_MATERIALS)
feed_additive_depths = depths(FEED_ADDITIVES)
chemical_substance_depths = depths(FEED_CHEMICAL_SUBSTANCES)
forage_depths = depths(FORAGE_PLANTS)
crop_product_depths = depths(CROP_PRODUCTS)
crop_byproduct_depths = depths(CROP_BYPRODUCTS)
feed_material_branches = {
    child_id: {child_id, *depths(child_id)}
    for child_id in children[FEED_MATERIALS]
}

assert labels[FEED_MATERIALS] == "Feed materials"
assert labels[FEED_ADDITIVES] == "Feed additives"
assert labels[FEED_CHEMICAL_SUBSTANCES] == "Feed chemical substances"
assert len(children[FEED_MATERIALS]) == 20
assert len(feed_material_depths) == 1625
assert len(feed_additive_depths) == 33
assert len(chemical_substance_depths) == 8
assert len(forage_depths) == 768
assert len(crop_product_depths) == 185
assert len(crop_byproduct_depths) == 504

inventory_ids = {
    FEED_MATERIALS,
    FEED_ADDITIVES,
    FEED_CHEMICAL_ENTITIES,
    FEED_CHEMICAL_SUBSTANCES,
    *feed_material_depths,
    *feed_additive_depths,
    *chemical_substance_depths,
}

fieldnames = [
    "concept_id",
    "preferred_label",
    "cohort_scope",
    "feed_material_direct_branch_ids",
    "feed_material_direct_branch_labels",
    "depth_from_feed_materials",
    "depth_from_feed_additives",
    "depth_from_feed_chemical_substances",
    "current_parent_ids",
    "current_parent_labels",
    "direct_child_count",
    "descendant_count",
    "review_requirement",
]

inventory = []
for concept_id in sorted(inventory_ids):
    scopes = []
    requirements = []
    if concept_id == FEED_MATERIALS:
        scopes.append("feed-material-root")
        requirements.append("product-kind-root-review")
    if concept_id in feed_material_depths:
        scopes.append("feed-material-descendant")
        requirements.append("affected-descendant-inventory")
    if feed_material_depths.get(concept_id) == 1:
        scopes.append("direct-feed-material-child")
        requirements.append("row-level-disposition")
    if concept_id == FEED_ADDITIVES or concept_id in feed_additive_depths:
        scopes.append("feed-additive-branch")
        requirements.append("authority-boundary-comparison")
    if concept_id in {FEED_CHEMICAL_ENTITIES, FEED_CHEMICAL_SUBSTANCES} or concept_id in chemical_substance_depths:
        scopes.append("chemical-identity-branch")
        requirements.append("identity-product-boundary-review")
    if concept_id in {FORAGE_PLANTS, CROP_PRODUCTS, CROP_BYPRODUCTS} or concept_id in forage_depths or concept_id in crop_product_depths or concept_id in crop_byproduct_depths:
        scopes.append("crop-forage-navigation")
        requirements.append("source-navigation-impact-review")
    if concept_id in REPORTED:
        scopes.append("reported-concept")
    branch_ids = sorted(
        branch_id
        for branch_id, branch_members in feed_material_branches.items()
        if concept_id in branch_members
    )
    concept_descendants = depths(concept_id)
    inventory.append(
        {
            "concept_id": concept_id,
            "preferred_label": labels[concept_id],
            "cohort_scope": ";".join(scopes),
            "feed_material_direct_branch_ids": ";".join(branch_ids),
            "feed_material_direct_branch_labels": ";".join(labels[branch_id] for branch_id in branch_ids),
            "depth_from_feed_materials": feed_material_depths.get(concept_id, ""),
            "depth_from_feed_additives": feed_additive_depths.get(concept_id, ""),
            "depth_from_feed_chemical_substances": chemical_substance_depths.get(concept_id, ""),
            "current_parent_ids": ";".join(sorted(parents[concept_id])),
            "current_parent_labels": ";".join(labels[parent_id] for parent_id in sorted(parents[concept_id])),
            "direct_child_count": len(children[concept_id]),
            "descendant_count": len(concept_descendants),
            "review_requirement": ";".join(dict.fromkeys(requirements)),
        }
    )

OUT.mkdir(parents=True, exist_ok=True)
with INVENTORY_PATH.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(inventory)


def normalized_intersection(first, second):
    first_labels = defaultdict(set)
    second_labels = defaultdict(set)
    for concept_id in first:
        first_labels[normalized_label(labels[concept_id])].add(concept_id)
    for concept_id in second:
        second_labels[normalized_label(labels[concept_id])].add(concept_id)
    return sorted(label for label in first_labels if label and label in second_labels)


summary = {
    "status": "recommendation-only",
    "decision_status": "accepted-for-implementation-planning",
    "reviewer": "Pete Steward",
    "review_date": "2026-08-13",
    "review_issue": "https://github.com/ERAgriculture/era-program/issues/52",
    "graph_inputs": {
        "nodes": "dist/livestock-staging/nodes.csv",
        "nodes_sha256": file_sha256(GRAPH / "nodes.csv"),
        "edges": "dist/livestock-staging/edges.csv",
        "edges_sha256": file_sha256(GRAPH / "edges.csv"),
    },
    "inventory_concepts": len(inventory),
    "feed_material_direct_children": len(children[FEED_MATERIALS]),
    "feed_material_descendants": len(feed_material_depths),
    "feed_additive_descendants": len(feed_additive_depths),
    "chemical_substance_descendants": len(chemical_substance_depths),
    "forage_descendants": len(forage_depths),
    "crop_product_descendants": len(crop_product_depths),
    "crop_byproduct_descendants": len(crop_byproduct_depths),
    "crop_forage_id_intersections": {
        "forage_and_crop_product": len(set(forage_depths) & set(crop_product_depths)),
        "forage_and_crop_byproduct": len(set(forage_depths) & set(crop_byproduct_depths)),
        "crop_product_and_crop_byproduct": len(set(crop_product_depths) & set(crop_byproduct_depths)),
    },
    "crop_forage_normalized_label_intersections": {
        "forage_and_crop_product": normalized_intersection(forage_depths, crop_product_depths),
        "forage_and_crop_byproduct": normalized_intersection(forage_depths, crop_byproduct_depths),
        "crop_product_and_crop_byproduct": normalized_intersection(crop_product_depths, crop_byproduct_depths),
    },
    "implementation_changes": 0,
    "allocated_identifiers": 0,
}
SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
