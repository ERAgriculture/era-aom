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
OUT = ROOT / "review" / "livestock-v35"
REVIEW = OUT / "process_axis_review.csv"
INVENTORY = OUT / "process_hierarchy_inventory.csv"
OVERLAP = OUT / "process_axis_overlap_matrix.csv"
SUMMARY = OUT / "process_purpose_summary.json"

PROCESS_ROOT = "AOM_000845"
RETIRED_PRECEDENT = "AOM_101068"


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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


process_depths = depths(PROCESS_ROOT)
process_ids = {PROCESS_ROOT, *process_depths}
direct_branches = {
    child_id: {child_id, *depths(child_id)}
    for child_id in children[PROCESS_ROOT]
}

review_rows = read_rows(REVIEW)
review_by_id = {row["concept_id"]: row for row in review_rows}
evidence_ids = {
    row["evidence_id"] for row in read_rows(OUT / "evidence_register.csv")
}
assert len(review_by_id) == len(review_rows), "Duplicate concept IDs in process review"
assert nodes[PROCESS_ROOT]["label"] == "Feed processes"
assert len(process_ids) == 53
assert len(process_depths) == 52
assert len(children[PROCESS_ROOT]) == 12
assert set(review_by_id) == process_ids | {RETIRED_PRECEDENT}

for concept_id in process_ids:
    assert review_by_id[concept_id]["preferred_label"] == nodes[concept_id]["label"]

for row in review_rows:
    assert row["status"] in {"proposed", "held"}
    assert row["recommended_semantic_action"]
    assert row["rationale"]
    row_evidence = set(row["evidence_ids"].split(";"))
    assert row_evidence <= evidence_ids, (
        row["concept_id"], sorted(row_evidence - evidence_ids)
    )

registry_by_id = {
    row["concept_id"]: row
    for row in read_rows(DATA / "livestock_id_registry.csv")
}
assert RETIRED_PRECEDENT not in nodes
assert registry_by_id[RETIRED_PRECEDENT]["status"] == "retired-before-publication"

usage_assertions = Counter()
usage_materials = defaultdict(set)
for row in read_rows(FACETS):
    if row["target_property"] != "aom:processingMethod":
        continue
    target_id = row["target_concept_id"]
    assert target_id in process_ids
    usage_assertions[target_id] += 1
    usage_materials[target_id].add(row["feed_material_id"])

for concept_id in process_ids:
    if review_by_id[concept_id]["review_role"] in {
        "root",
        "mechanism-grouping",
        "technical-objective-grouping",
        "deprecated-duplicate",
    }:
        assert usage_assertions[concept_id] == 0, concept_id
assert usage_assertions["AOM_101069"] == 8
assert usage_assertions["AOM_101084"] == 3

inventory_fields = [
    "concept_id",
    "preferred_label",
    "node_status",
    "depth_from_process_root",
    "current_parent_ids",
    "current_parent_labels",
    "current_parent_review_roles",
    "root_direct_branch_ids",
    "root_direct_branch_labels",
    "direct_child_count",
    "descendant_count",
    "processing_method_assertion_count",
    "processing_method_material_count",
    "review_role",
    "review_status",
    "current_definition",
]
inventory_rows = []
for concept_id in sorted(process_ids):
    current_parents = sorted(parents[concept_id] & process_ids)
    branch_ids = sorted(
        branch_id
        for branch_id, branch_members in direct_branches.items()
        if concept_id in branch_members
    )
    inventory_rows.append(
        {
            "concept_id": concept_id,
            "preferred_label": nodes[concept_id]["label"],
            "node_status": nodes[concept_id]["status"],
            "depth_from_process_root": 0 if concept_id == PROCESS_ROOT else process_depths[concept_id],
            "current_parent_ids": ";".join(current_parents),
            "current_parent_labels": ";".join(nodes[parent_id]["label"] for parent_id in current_parents),
            "current_parent_review_roles": ";".join(
                review_by_id[parent_id]["review_role"] for parent_id in current_parents
            ),
            "root_direct_branch_ids": ";".join(branch_ids),
            "root_direct_branch_labels": ";".join(nodes[branch_id]["label"] for branch_id in branch_ids),
            "direct_child_count": len(children[concept_id] & process_ids),
            "descendant_count": len(depths(concept_id)),
            "processing_method_assertion_count": usage_assertions[concept_id],
            "processing_method_material_count": len(usage_materials[concept_id]),
            "review_role": review_by_id[concept_id]["review_role"],
            "review_status": review_by_id[concept_id]["status"],
            "current_definition": definitions.get(concept_id, ""),
        }
    )

with INVENTORY.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=inventory_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(inventory_rows)

overlap_fields = [
    "concept_id",
    "preferred_label",
    "current_status",
    "review_role",
    "recommended_disposition",
    "recommended_mechanisms",
    "recommended_technical_objectives",
    "possible_intended_feed_benefits",
    "processing_method_material_count",
    "recommended_semantic_action",
    "evidence_ids",
    "status",
    "blocking_question",
]
overlap_rows = []
for row in review_rows:
    concept_id = row["concept_id"]
    current_status = (
        nodes[concept_id]["status"]
        if concept_id in nodes
        else registry_by_id[concept_id]["status"]
    )
    overlap_rows.append(
        {
            "concept_id": concept_id,
            "preferred_label": row["preferred_label"],
            "current_status": current_status,
            "review_role": row["review_role"],
            "recommended_disposition": row["recommended_disposition"],
            "recommended_mechanisms": row["recommended_mechanisms"],
            "recommended_technical_objectives": row["recommended_technical_objectives"],
            "possible_intended_feed_benefits": row["possible_intended_feed_benefits"],
            "processing_method_material_count": len(usage_materials[concept_id]),
            "recommended_semantic_action": row["recommended_semantic_action"],
            "evidence_ids": row["evidence_ids"],
            "status": row["status"],
            "blocking_question": row["blocking_question"],
        }
    )

with OVERLAP.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=overlap_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(overlap_rows)

role_counts = Counter(row["review_role"] for row in review_rows if row["concept_id"] in process_ids)
status_counts = Counter(row["status"] for row in review_rows)
summary = {
    "status": "recommendation-only",
    "decision_status": "axis-architecture-approved-row-dispositions-pending",
    "architecture_reviewer": "Pete Steward",
    "architecture_review_date": "2026-08-18",
    "row_review_author": "Codex",
    "review_issue": "https://github.com/ERAgriculture/era-program/issues/54",
    "source_commit": "ce9f5da",
    "current_process_concepts_including_root": len(process_ids),
    "current_process_descendants": len(process_depths),
    "current_direct_children": len(children[PROCESS_ROOT]),
    "current_review_roles": dict(sorted(role_counts.items())),
    "review_statuses": dict(sorted(status_counts.items())),
    "retired_provenance_precedents": 1,
    "processing_methods_used_by_materials": sum(
        1 for material_ids in usage_materials.values() if material_ids
    ),
    "processing_method_assertions": sum(usage_assertions.values()),
    "materials_with_processing_method": len(set().union(*usage_materials.values())),
    "proposed_relations": [
        "aom:processMechanism",
        "aom:technicalProcessObjective",
        "aom:maySupportFeedBenefit",
        "aom:productionProcessProvenance",
        "aom:observedProcessEffect",
    ],
    "implementation_changes": 0,
    "allocated_identifiers": 0,
    "inputs": {
        "nodes_sha256": file_sha256(GRAPH / "nodes.csv"),
        "edges_sha256": file_sha256(GRAPH / "edges.csv"),
        "definitions_sha256": file_sha256(DATA / "definitions.csv"),
        "facets_sha256": file_sha256(FACETS),
        "review_sha256": file_sha256(REVIEW),
    },
}
SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
