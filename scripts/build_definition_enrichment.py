#!/usr/bin/env python3
"""Build reviewed definitions from approved concept and facet governance."""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
OUT = DATA / "approved_definition_enrichments.csv"
QUEUE = ROOT / "review/livestock-v8/definition_gap_queue.csv"


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


existing = {
    row["concept_id"] for row in read("definitions.csv")
    if row["source_column"] != "approved_definition_enrichment"
}
concepts = {row["concept_id"]: row for row in read("concepts.csv")}
labels = {
    row["concept_id"]: row["label"] for row in read("labels.csv")
    if row["language"] == "en" and row["label_type"] == "pref"
}
mappings = defaultdict(list)
for row in read("mappings.csv"):
    if row["target_scheme"] != "ilri-code":
        mappings[row["subject_id"]].append(row)
new_concepts = read("approved_new_concepts.csv")
inventory = {row["concept_id"]: row for row in csv.DictReader(
    (ROOT / "review/livestock-v5/ingredient_harmonization_inventory.csv").open(encoding="utf-8", newline="")
)}
material_facets = read("approved_feed_material_facets.csv") + read("approved_generated_feed_material_facets.csv")
feedipedia_scope_reviews = list(csv.DictReader(
    (ROOT / "review/livestock-v11/feedipedia_source_scope_review.csv").open(encoding="utf-8", newline="")
))
public_authority_reviews = list(csv.DictReader(
    (ROOT / "review/livestock-v12/public_authority_source_scope_review.csv").open(encoding="utf-8", newline="")
))

rows = []
for row in new_concepts:
    if row["concept_id"] in existing:
        continue
    rows.append({
        "concept_id": row["concept_id"], "language": "en",
        "definition": row["scope_note"], "definition_method": "promoted_reviewed_scope_note",
        "status": "approved", "reviewer": "Pete Steward", "review_date": "2026-08-06",
        "evidence": row["evidence"],
        "rationale": "Reviewed concept scope text is definition-grade and promoted without semantic expansion.",
    })

by_material = defaultdict(list)
for row in material_facets:
    by_material[row["feed_material_id"]].append(row)
property_label = {
    "aom:ingredientPart": "ingredient part",
    "aom:processingMethod": "processing method",
    "aom:physicalForm": "physical form",
    "aom:productRole": "product role",
    "aom:feedProductType": "feed product type",
    "aom:materialIntegrity": "material integrity",
    "aom:materialComponent": "material component",
    "aom:compositionState": "composition state",
    "aom:ingredientConstituent": "ingredient constituent",
}
for concept_id, facets in sorted(by_material.items()):
    if concept_id in existing or concepts[concept_id]["status"] == "deprecated":
        continue
    source = inventory[concept_id]["source_identity_candidate"].strip()
    if not source:
        raise ValueError(f"Approved facet material lacks governed source identity: {concept_id}")
    grouped = defaultdict(list)
    for facet in facets:
        grouped[facet["target_property"]].append(facet["target_label"])
    characteristics = []
    for prop in sorted(grouped):
        values = ", ".join(sorted(set(grouped[prop])))
        characteristics.append(f"{property_label[prop]} — {values}")
    rows.append({
        "concept_id": concept_id, "language": "en",
        "definition": f"A feed material with governed source identity “{source}” and characteristics: " + "; ".join(characteristics) + ".",
        "definition_method": "composed_from_approved_semantic_facets",
        "status": "approved", "reviewer": "Pete Steward", "review_date": "2026-08-06",
        "evidence": "data/livestock-staging/approved_feed_material_facets.csv;data/livestock-staging/approved_generated_feed_material_facets.csv",
        "rationale": "Definition states only governed source identity and approved semantic assertions; no biological or nutritional claim is inferred.",
    })

base_ids = {row["concept_id"] for row in rows}

family_label = {
    "Animal": "animal-derived",
    "Animal Byproduct": "animal by-product",
    "Animal Manures": "animal-manure",
    "Crop Byproduct": "crop by-product",
    "Crop Product": "crop-product",
    "Forage Plants": "forage-plant",
    "Other Ingredients": "other-ingredient",
    "Probiotic": "probiotic",
}

for review in public_authority_reviews:
    concept_id = review["concept_id"]
    if (review["decision"] != "approve_direct_source_scope" or review["status"] != "approved"
            or concept_id in existing or concept_id in base_ids):
        continue
    identity = review["governed_identity"].strip()
    if not identity or not review["authority_uri"]:
        raise ValueError(f"Approved public-authority scope lacks identity/evidence: {concept_id}")
    rows.append({
        "concept_id": concept_id, "language": "en",
        "definition": (
            f"A {family_label[review['ingredient_family']]} feed material with governed source identity “{identity}”. "
            "Component, processing method, physical form, product role, integrity, composition, and constituent "
            "are unspecified at this concept level unless separately asserted."
        ),
        "definition_method": "composed_from_reviewed_public_authority_source_scope",
        "status": "approved", "reviewer": review["reviewer"], "review_date": review["review_date"],
        "evidence": review["authority_uri"], "rationale": review["rationale"],
    })

base_ids = {row["concept_id"] for row in rows}
for review in feedipedia_scope_reviews:
    concept_id = review["concept_id"]
    if review["status"] != "approved" or concept_id in existing or concept_id in base_ids:
        continue
    source = review["source_identity"].strip()
    if not source:
        raise ValueError(f"Approved Feedipedia scope lacks governed identity: {concept_id}")
    rows.append({
        "concept_id": concept_id, "language": "en",
        "definition": (
            f"A {family_label[review['ingredient_family']]} feed material with governed identity “{source}”. "
            "Component, processing method, physical form, product role, integrity, composition, and constituent "
            "are unspecified at this concept level unless separately asserted."
        ),
        "definition_method": "composed_from_reviewed_feedipedia_source_scope",
        "status": "approved", "reviewer": review["reviewer"], "review_date": review["review_date"],
        "evidence": review["feedipedia_url"],
        "rationale": review["rationale"],
    })

base_ids = {row["concept_id"] for row in rows}


def domain_for(path):
    folded = path.casefold()
    if "/feed ingredient/" in folded:
        return "feed_material"
    if "/rearing stage/" in folded:
        return "rearing_stage"
    if path.startswith("Species/"):
        return "taxon"
    if path.startswith("Outcomes/"):
        return "outcome"
    if path.startswith("Farming System/"):
        return "farming_system"
    if path.startswith("Management/"):
        return "management"
    return "core_root"


def context_text(path, domain):
    parts = path.split("/")
    label = parts[-1]
    parent = parts[-2] if len(parts) > 1 else "AOM"
    if domain == "rearing_stage":
        context = next((item for item in parts if item in {"Cattle;Buffalo", "Sheep", "Goat", "Pig", "Chicken", "Fish"}), "livestock system")
        return f"A controlled rearing-stage category scoped to {context}; used for records classified as “{label}”."
    if domain == "taxon":
        return f"A taxonomic concept used in AOM to identify {label} within the {parent} classification."
    if domain == "outcome":
        return f"An AOM outcome concept for recording {label} within {parent}."
    if domain == "management":
        return f"A livestock-management concept concerning {label} within {parent}."
    if domain == "farming_system":
        system = "aquatic" if "aquatic system" in path else "terrestrial" if "terrestrial system" in path else "livestock"
        if label.casefold() == f"{system} system":
            return f"A farming-system classification identifying the {system} livestock-system context."
        return f"A farming-system classification for {label} within the {system} system context."
    raise ValueError(domain)


gap_rows = []
eligible_domains = {"rearing_stage", "taxon", "outcome", "management", "farming_system"}
for concept_id, concept in sorted(concepts.items()):
    if concept["status"] == "deprecated" or concept_id in existing or concept_id in base_ids:
        continue
    path = concept["derived_path"]
    domain = domain_for(path)
    public = mappings[concept_id]
    schemes = sorted({row["target_scheme"] for row in public})
    targets = sorted({row["target_uri"] or row["target_id"] for row in public if row["target_uri"] or row["target_id"]})
    if domain in eligible_domains:
        definition = context_text(path, domain)
        rows.append({
            "concept_id": concept_id, "language": "en", "definition": definition,
            "definition_method": "composed_from_governed_hierarchy_role",
            "status": "approved", "reviewer": "Pete Steward", "review_date": "2026-08-06",
            "evidence": "data/livestock-staging/concepts.csv",
            "rationale": "Definition states only approved hierarchy context and model role; no domain fact is inferred.",
        })
        route, status = "approved_structural_definition", "approved"
    elif domain == "feed_material" and "feedipedia" in schemes:
        route, status = "research_feedipedia", "research-required"
    elif domain == "feed_material" and ({"agrovoc", "ontology"} & set(schemes)):
        route, status = "research_public_ontology", "research-required"
    elif domain == "feed_material" and ({"ncbi-taxonomy", "world-flora-online"} & set(schemes)):
        route, status = "research_taxon_insufficient_for_material", "research-required"
    elif domain == "feed_material":
        route, status = "research_source_workbook", "research-required"
    else:
        route, status = "manual_core_definition", "expert-review-required"
    gap_rows.append({
        "concept_id": concept_id, "preferred_label": labels[concept_id],
        "hierarchy_path": path, "domain": domain,
        "public_mapping_schemes": ";".join(schemes),
        "public_mapping_targets": ";".join(targets),
        "recommended_route": route, "status": status,
    })

rows.sort(key=lambda row: row["concept_id"])
fields = ["concept_id", "language", "definition", "definition_method", "status", "reviewer", "review_date", "evidence", "rationale"]
with OUT.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
QUEUE.parent.mkdir(parents=True, exist_ok=True)
queue_fields = ["concept_id", "preferred_label", "hierarchy_path", "domain", "public_mapping_schemes", "public_mapping_targets", "recommended_route", "status"]
with QUEUE.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=queue_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(gap_rows)
(QUEUE.parent / "definition_gap_summary.json").write_text(json.dumps({
    "prior_active_gaps": len(gap_rows),
    "approved_structural_definitions": sum(row["status"] == "approved" for row in gap_rows),
    "research_required": sum(row["status"] == "research-required" for row in gap_rows),
    "expert_review_required": sum(row["status"] == "expert-review-required" for row in gap_rows),
    "remaining_after_approval": sum(row["status"] != "approved" for row in gap_rows),
    "routes": dict(sorted(Counter(row["recommended_route"] for row in gap_rows).items())),
    "closed_identifiers_used_for_routing": False,
}, indent=2) + "\n", encoding="utf-8")
print(f"Approved {len(rows)} definition enrichments; classified {len(gap_rows)} prior gaps")
