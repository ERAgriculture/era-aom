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
definition_grade_mappings = defaultdict(list)
for row in read("mappings.csv"):
    if row["target_scheme"] != "ilri-code":
        mappings[row["subject_id"]].append(row)
        if row["status"] not in {"reviewed-related", "review-held"}:
            definition_grade_mappings[row["subject_id"]].append(row)
new_concepts = read("approved_new_concepts.csv")
inventory = {row["concept_id"]: row for row in csv.DictReader(
    (ROOT / "review/livestock-v5/ingredient_harmonization_inventory.csv").open(encoding="utf-8", newline="")
)}
hard_tail_reviews = list(csv.DictReader(
    (ROOT / "review/livestock-v14/definition_hard_tail_review.csv").open(encoding="utf-8", newline="")
))
hard_tail_by_id = {row["concept_id"]: row for row in hard_tail_reviews if row["status"] == "approved"}
material_facets = (
    read("approved_feed_material_facets.csv")
    + read("approved_generated_feed_material_facets.csv")
    + read("approved_hard_tail_feed_material_facets.csv")
    + read("approved_structural_feed_material_facets.csv")
)
feedipedia_scope_reviews = list(csv.DictReader(
    (ROOT / "review/livestock-v11/feedipedia_source_scope_review.csv").open(encoding="utf-8", newline="")
))
public_authority_reviews = list(csv.DictReader(
    (ROOT / "review/livestock-v12/public_authority_source_scope_review.csv").open(encoding="utf-8", newline="")
))
workbook_source_reviews = list(csv.DictReader(
    (ROOT / "review/livestock-v13/workbook_source_scope_review.csv").open(encoding="utf-8", newline="")
))
approved_definition_overrides = read("approved_definition_overrides.csv")

rows = []
generated_definition_overrides = {
    "AOM_101062": (
        "A product role for material obtained alongside or remaining after production or "
        "processing of a principal product and retained for another use, including as feed.",
        "data/livestock-staging/legacy_records.csv;https://www.feedipedia.org/node/712",
    ),
    "AOM_101104": (
        "Outer protective tissues of a cereal grain, principally pericarp and seed coat, "
        "commonly separated as a by-product during grinding or milling.",
        "data/livestock-staging/legacy_records.csv;https://www.feedipedia.org/node/712",
    ),
}
for row in new_concepts:
    if row["concept_id"] in existing:
        continue
    definition, evidence = generated_definition_overrides.get(
        row["concept_id"], (row["scope_note"], row["evidence"])
    )
    rows.append({
        "concept_id": row["concept_id"], "language": "en",
        "definition": definition, "definition_method": "promoted_reviewed_scope_note",
        "status": "approved", "reviewer": "Pete Steward", "review_date": "2026-08-06",
        "evidence": evidence,
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
new_concept_ids = {row["concept_id"] for row in new_concepts}
for concept_id, facets in sorted(by_material.items()):
    if (
        concept_id in existing or concept_id in new_concept_ids
        or concepts[concept_id]["status"] == "deprecated"
    ):
        continue
    source = hard_tail_by_id.get(concept_id, {}).get(
        "governed_source_identity", inventory[concept_id]["source_identity_candidate"]
    ).strip()
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
        "evidence": (
            "data/livestock-staging/approved_hard_tail_feed_material_facets.csv"
            if concept_id in hard_tail_by_id else
            "data/livestock-staging/approved_feed_material_facets.csv;data/livestock-staging/approved_generated_feed_material_facets.csv;data/livestock-staging/approved_structural_feed_material_facets.csv"
        ),
        "rationale": "Definition states only governed source identity and approved semantic assertions; no biological or nutritional claim is inferred.",
    })

base_ids = {row["concept_id"] for row in rows}

for review in hard_tail_reviews:
    concept_id = review["concept_id"]
    if review["status"] != "approved" or concept_id in existing or concept_id in base_ids:
        continue
    if review["decision"] == "approve_core_hierarchy_scope":
        definition = f"An AOM top-level classification for “{review['preferred_label']}”, used to organize governed concepts in this domain."
        method = "composed_from_governed_core_hierarchy_scope"
    elif review["decision"] == "approve_feedipedia_category_scope":
        definition = (
            f"An AOM controlled feed category for “{review['preferred_label']}”. "
            "Used to organize narrower feed materials; it does not identify one material or assert inherited characteristics."
        )
        method = "composed_from_reviewed_feedipedia_category_scope"
    elif review["decision"] == "approve_bounded_workbook_material_scope":
        definition = (
            f"An AOM feed material with governed operational source identity “{review['governed_source_identity']}”. "
            "Component, whole-material integrity, processing method, physical form, product role, composition, "
            "constituent, and nutritional properties are unspecified unless separately asserted."
        )
        method = "composed_from_bounded_workbook_material_scope"
    else:
        raise ValueError(f"Approved hard-tail case lacks facets or category method: {concept_id}")
    rows.append({
        "concept_id": concept_id, "language": "en", "definition": definition,
        "definition_method": method, "status": "approved", "reviewer": review["reviewer"],
        "review_date": review["review_date"], "evidence": review["evidence"], "rationale": review["rationale"],
    })

base_ids = {row["concept_id"] for row in rows}

workbook_family_label = {
    "Animal": "animal-derived feed ingredient",
    "Animal Byproduct": "animal by-product feed ingredient",
    "Animal Manures": "animal-manure feed ingredient",
    "Crop Byproduct": "crop by-product feed ingredient",
    "Crop Product": "crop-product feed ingredient",
    "Essential Fatty Acid": "essential-fatty-acid feed ingredient",
    "Forage Plants": "forage feed material",
    "Grazing": "grazing feed-source",
    "Herb or Extract": "herb-or-extract feed ingredient",
    "Ingredient source": "feed-ingredient source",
    "Organic Acid": "organic-acid feed ingredient",
    "Other Ingredients": "feed ingredient",
    "Prebiotic": "prebiotic feed ingredient",
    "Preformulated Feed": "preformulated feed",
    "Probiotic": "probiotic feed ingredient",
    "Supplement": "feed-supplement ingredient",
}
for review in workbook_source_reviews:
    concept_id = review["concept_id"]
    if review["status"] != "approved" or concept_id in existing or concept_id in base_ids:
        continue
    if review["definition_scope"] == "category":
        definition = (
            f"An AOM controlled category for “{review['preferred_label']}” within “{review['parent_label']}”. "
            "Used to classify feed records at this scope; narrower material characteristics require separate assertions."
        )
        method = "composed_from_canonical_workbook_category_scope"
    else:
        definition = (
            f"A {workbook_family_label[review['ingredient_family']]} with governed workbook identity "
            f"“{review['preferred_label']}”, classified within “{review['parent_label']}”. Component, processing method, "
            "physical form, product role, integrity, composition, and constituent are unspecified unless separately asserted."
        )
        method = "composed_from_canonical_workbook_identity_scope"
    rows.append({
        "concept_id": concept_id, "language": "en", "definition": definition,
        "definition_method": method, "status": "approved", "reviewer": review["reviewer"],
        "review_date": review["review_date"], "evidence": review["evidence"], "rationale": review["rationale"],
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
    definition_grade_public = definition_grade_mappings[concept_id]
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
    elif domain == "feed_material" and public and not definition_grade_public:
        route, status = "research_related_mapping_insufficient", "research-required"
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

override_ids = {row["concept_id"] for row in approved_definition_overrides}
assert len(override_ids) == len(approved_definition_overrides)
assert override_ids <= set(concepts) and not override_ids & existing
rows = [row for row in rows if row["concept_id"] not in override_ids]
rows.extend(approved_definition_overrides)
gap_rows = [row for row in gap_rows if row["concept_id"] not in override_ids]
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
