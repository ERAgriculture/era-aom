#!/usr/bin/env python3
"""Implement accepted feed product-kind and source-navigation dispositions."""

import csv
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "livestock-staging"
REVIEW = ROOT / "review" / "livestock-v31"
OUTPUT = ROOT / "review" / "livestock-v34"
DATE = "2026-08-16"
REVIEWER = "Pete Steward"
ADR = "docs/decisions/0045-feed-product-kind-and-source-navigation.md"
METHOD = "docs/methods/feed-taxonomy-governance.md"
PREFIX = "FEED-PRODUCT-KIND-"


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


def normalize(value):
    text = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


review_rows = read(REVIEW / "feed_product_kind_review.csv")
review_by_id = {row["concept_id"]: row for row in review_rows}
assert len(review_rows) == len(review_by_id) == 32
assert sum(row["status"] == "approved" for row in review_rows) == 21
assert sum(row["status"] == "held" for row in review_rows) == 11

reserved_specs = [
    ("AOM_101156", "Ingredient descriptors", "Rejected pre-revert Cohort B branch"),
    ("AOM_101157", "Unclassified feed materials", "Rejected pre-revert Cohort A branch"),
    ("AOM_101158", "Other feed processes", "Rejected pre-revert Cohort C branch"),
]
new_specs = [
    (
        "AOM_101159",
        "Plant products and by-products",
        "Editorial navigation for plant-derived feed materials, including primary products and secondary outputs; source taxon and product role remain explicit independent assertions.",
        "AOM_100850",
    ),
    (
        "AOM_101160",
        "Other feeds",
        "Editorial navigation for evidenced feed materials outside forage, plant-product, and animal-origin branches; membership does not replace source, product-role, or regulatory assertions.",
        "AOM_100850",
    ),
    (
        "AOM_101161",
        "Other biological feed materials",
        "Biologically derived feed materials not yet placed under forage, plant-product, or animal-origin navigation; exact source taxon remains explicit when known.",
        "AOM_101160",
    ),
    (
        "AOM_101162",
        "Unclassified feed materials",
        "Temporary navigation for evidenced feed materials lacking durable placement; each member requires a recorded evidence gap, owner, target cohort, review date, and resolution within one release cycle.",
        "AOM_101160",
    ),
]
new_ids = {spec[0] for spec in new_specs}
reserved_ids = {spec[0] for spec in reserved_specs}
assert new_ids == {f"AOM_{number}" for number in range(101159, 101163)}

renames = {
    "AOM_000559": "Feeds of animal origin",
    "AOM_000735": "Forage materials",
    "AOM_101147": "Chemical substances",
}
proposed_labels = {
    **renames,
    **{concept_id: label for concept_id, label, _, _ in new_specs},
}
label_index = {}
for row in read(DATA / "labels.csv"):
    label_index.setdefault(normalize(row["label"]), set()).add(row["concept_id"])
for row in read(DATA / "approved_new_concepts.csv"):
    label_index.setdefault(normalize(row["preferred_label"]), set()).add(row["concept_id"])
for row in read(DATA / "approved_label_additions.csv"):
    label_index.setdefault(normalize(row["label"]), set()).add(row["concept_id"])
for row in read(DATA / "approved_concept_retirements.csv"):
    label_index.setdefault(normalize(row["preferred_label"]), set()).add(row["concept_id"])
external_labels = {normalize(row["target_label"]) for row in read(DATA / "approved_external_resource_labels.csv")}

collision_rows = []
for concept_id, label in proposed_labels.items():
    normalized = normalize(label)
    concept_matches = sorted(label_index.get(normalized, set()) - {concept_id})
    external_match = normalized in external_labels
    assert not concept_matches and not external_match, (concept_id, label, concept_matches, external_match)
    collision_rows.append({
        "concept_id": concept_id,
        "proposed_label": label,
        "normalized_label": normalized,
        "matched_concept_ids": "",
        "external_label_match": "false",
        "decision": "approved-no-collision",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"data/livestock-staging/labels.csv;data/livestock-staging/approved_label_additions.csv;data/livestock-staging/approved_external_resource_labels.csv;{ADR}",
    })
write(OUTPUT / "identity_collision_audit.csv", list(collision_rows[0]), collision_rows)

new_path = DATA / "approved_new_concepts.csv"
new_rows = [
    row for row in read(new_path)
    if row["concept_id"] not in new_ids | reserved_ids
]
new_by_id = {row["concept_id"]: row for row in new_rows}
generated_updates = {
    "AOM_100921": ("Crop product", "AOM_101159"),
    "AOM_100976": ("Animal by-products", "AOM_000559"),
    "AOM_100987": ("Processed food by-products", "AOM_101160"),
    "AOM_100989": ("Microalgal feed materials", "AOM_101161"),
    "AOM_101139": ("Mineral feed materials", "AOM_101160"),
}
for concept_id, (label, parent_id) in generated_updates.items():
    row = new_by_id[concept_id]
    row.update({
        "broader_id": parent_id,
        "derived_path": f"Governed feed navigation/{label}",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": "Placed beneath accepted Feedipedia-aligned editorial navigation while source and product role remain independent.",
    })
chemical_row = new_by_id["AOM_101147"]
chemical_row.update({
    "preferred_label": renames["AOM_101147"],
    "scope_note": "Chemically identified substances or substance groups represented independently of feed-material, formulation, or additive product kind; intended use and authorization require separate assertions.",
    "derived_path": "Governed feed taxonomy/Chemical substances",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": f"{ADR};{METHOD}",
    "rationale": "Removes feed-product implication from independent chemical identity axis.",
})
for concept_id, label, scope_note, parent_id in new_specs:
    new_rows.append({
        "case_id": f"{PREFIX}NEW-{concept_id}",
        "concept_id": concept_id,
        "preferred_label": label,
        "scope_note": scope_note,
        "broader_id": parent_id,
        "hierarchy_level": "5",
        "derived_path": f"Governed feed navigation/{label}",
        "child_ids": "",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": "Collision-audited navigation concept required by accepted ADR 0045 implementation.",
    })
write(new_path, fieldnames(new_path), new_rows)

registry_path = DATA / "livestock_id_registry.csv"
registry_rows = [
    row for row in read(registry_path)
    if row["concept_id"] not in new_ids | reserved_ids
]
for concept_id, label, case_id in reserved_specs:
    registry_rows.append({
        "concept_id": concept_id,
        "allocated_on": "2026-08-13",
        "status": "retired-before-publication",
        "preferred_label": label,
        "case_id": f"REJECTED-PRE-REVERT-{case_id.upper().replace(' ', '-')}",
        "allocator": "ERA governance audit",
        "allocation_basis": "Observed only in reverted unapproved work and stale local graph; rejected, never published, and identifier must not be reassigned.",
    })
for concept_id, label, _, _ in new_specs:
    registry_rows.append({
        "concept_id": concept_id,
        "allocated_on": DATE,
        "status": "allocated",
        "preferred_label": label,
        "case_id": f"{PREFIX}NEW-{concept_id}",
        "allocator": REVIEWER,
        "allocation_basis": f"Sequential allocation above three reserved rejected IDs after global preferred, alternative, hidden, deprecated, and external-label collision audit; accepted under ADR 0045.",
    })
registry_rows.sort(key=lambda row: int(row["concept_id"].split("_")[1]))
write(registry_path, fieldnames(registry_path), registry_rows)

baseline_path = ROOT / "config" / "identity-integrity-baseline.json"
baseline = json.loads(baseline_path.read_text())
baseline["captured"] = DATE
baseline["frozen_generated_identifier_frontier"] = 101162
baseline["new_identifier_allocation_frozen"] = True
baseline_path.write_text(json.dumps(baseline, indent=2) + "\n")

label_corrections = [
    {
        "case_id": f"{PREFIX}LABEL-{concept_id}",
        "concept_id": concept_id,
        "old_label": old_label,
        "new_label": renames[concept_id],
        "language": "en",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": ADR,
        "rationale": rationale,
    }
    for concept_id, old_label, rationale in [
        ("AOM_000559", "Animal", "Uses animal origin as editorial feed-material navigation rather than an animal taxon identity."),
        ("AOM_000735", "Forage Plants", "Uses forage material scope without implying forage and crop are disjoint biological classes."),
    ]
]
upsert(DATA / "approved_label_corrections.csv", "concept_id", label_corrections)

addition_path = DATA / "approved_label_additions.csv"
addition_rows = [
    row for row in read(addition_path)
    if not row["case_id"].startswith(PREFIX)
]
addition_rows.extend([
    {
        "case_id": f"{PREFIX}ALIAS-AOM_101147",
        "concept_id": "AOM_101147",
        "language": "en",
        "label_type": "alt",
        "label": "Feed chemical substances",
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": ADR,
        "rationale": "Preserves prior generated label after product-neutral relabeling.",
    },
    {
        "case_id": f"{PREFIX}ALIAS-AOM_101159",
        "concept_id": "AOM_101159",
        "language": "en",
        "label_type": "alt",
        "label": "Plant products/by-products",
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": ADR,
        "rationale": "Preserves accepted Feedipedia-style navigation wording as a searchable alias.",
    },
])
write(addition_path, fieldnames(addition_path), addition_rows)

definition_updates = {
    "AOM_000559": "Editorial navigation for feed materials of animal origin; exact animal source, material identity, and product role require explicit assertions.",
    "AOM_000561": "Classification hold for animal-manure source terms whose intentional oral-feed use, safety, and feed-product status remain unresolved; membership asserts no feed eligibility.",
    "AOM_000735": "Editorial navigation for plant materials used as forage, fresh, dried, ensiled, or grazed; crop cultivation status and source taxon remain independent and may overlap.",
    "AOM_001068": "Classification hold for the source term Pseudovitamin; exact chemical identity, product kind, and intended function remain unresolved.",
    "AOM_001866": "Generic glycerol or glycerine feed-material concept retained temporarily under Unclassified feed materials while crude, refined, and chemical scope are reconciled; additive status is not asserted.",
    "AOM_001922": "Classification hold for water represented as a feed or diet input; exact product-kind scope and distinction between drinking and incorporated water remain unresolved.",
    "AOM_002072": "Classification hold for a ground chromium-oxide source term; chemical identity, prepared-product status, grinding assertion, and presentation form require separate confirmation.",
    "AOM_006241": "Biological feed material with unresolved yeast organism and product scope; no exact source taxon or preparation is inferred.",
    "AOM_006349": "Classification hold for a Pleurotus ostreatus source term whose exact material identity and FeedMaterial status remain unresolved; no fruiting body, powder, mycelium, or treated substrate is inferred.",
    "AOM_101147": chemical_row["scope_note"],
    **{concept_id: scope_note for concept_id, _, scope_note, _ in new_specs},
}
definition_rows = [{
    "concept_id": concept_id,
    "language": "en",
    "definition": definition,
    "definition_method": "feed_product_kind_definition_replacement",
    "status": "approved",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": f"{ADR};{METHOD}",
    "rationale": "Definition records accepted navigation scope, independent axes, and evidence boundary.",
} for concept_id, definition in definition_updates.items()]
upsert(DATA / "approved_definition_overrides.csv", "concept_id", definition_rows)

desired_parent = {
    "AOM_000561": "AOM_101142",
    "AOM_001068": "AOM_101142",
    "AOM_001832": "AOM_101159",
    "AOM_001865": "AOM_101023",
    "AOM_001866": "AOM_101162",
    "AOM_001916": "AOM_101159",
    "AOM_001922": "AOM_101142",
    "AOM_002072": "AOM_101142",
    "AOM_006241": "AOM_101161",
    "AOM_006334": "AOM_101160",
    "AOM_006349": "AOM_101142",
    "AOM_000809": "AOM_101023",
}
superseded_parent = {
    "AOM_000561": "AOM_100850",
    "AOM_001068": "AOM_101147",
    "AOM_001832": "AOM_100850",
    "AOM_001865": "AOM_101147",
    "AOM_001866": "AOM_100850",
    "AOM_001916": "AOM_100850",
    "AOM_001922": "AOM_100850",
    "AOM_002072": "AOM_000746",
    "AOM_006241": "AOM_100850",
    "AOM_006334": "AOM_100850",
    "AOM_006349": "AOM_100850",
    "AOM_000809": "AOM_101147",
}
assert set(superseded_parent) == set(desired_parent)
hierarchy_path = DATA / "approved_hierarchy_revisions.csv"
hierarchy_rows = [
    row for row in read(hierarchy_path)
    if not row["case_id"].startswith(PREFIX)
]
for concept_id, target_parent in desired_parent.items():
    hierarchy_rows.append({
        "case_id": f"{PREFIX}MOVE-{concept_id}",
        "child_id": concept_id,
        "remove_parent_id": superseded_parent[concept_id],
        "add_parent_id": target_parent,
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": ADR,
        "rationale": "Implements accepted Feedipedia-aligned navigation or explicit classification hold without inferring source, role, or product eligibility.",
    })
write(hierarchy_path, fieldnames(hierarchy_path), hierarchy_rows)

semantic_type_path = DATA / "approved_concept_semantic_types.csv"
semantic_type_rows = [
    row for row in read(semantic_type_path)
    if row["concept_id"] not in {"AOM_000809", "AOM_001068", "AOM_001865"}
]
for concept_id in ["AOM_000809", "AOM_001865"]:
    semantic_type_rows.append({
        "case_id": f"{PREFIX}TYPE-{concept_id}",
        "concept_id": concept_id,
        "semantic_class": "aom:ChemicalConstituent",
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": ADR,
        "rationale": "Accepted Cohort A disposition treats constituent identity independently of feed-product kind.",
    })
write(semantic_type_path, fieldnames(semantic_type_path), semantic_type_rows)

descriptor_ids = {f"AOM_00053{number}" for number in range(1, 6)}
held_ids = {row["concept_id"] for row in review_rows if row["status"] == "held"} - descriptor_ids
feed_material_ids = {
    "AOM_100850", "AOM_000559", "AOM_100976", "AOM_001916", "AOM_100921",
    "AOM_000735", "AOM_001866", "AOM_100989", "AOM_101139", "AOM_100987",
    "AOM_006334", "AOM_001832", "AOM_006241",
} | new_ids
final_parent = {
    "AOM_100850": "AOM_000328",
    "AOM_101135": "AOM_000328",
    "AOM_101146": "AOM_000328",
    "AOM_101147": "AOM_101146",
    "AOM_000559": "AOM_100850",
    "AOM_100976": "AOM_000559",
    "AOM_000561": "AOM_101142",
    "AOM_001916": "AOM_101159",
    "AOM_100921": "AOM_101159",
    "AOM_000735": "AOM_100850",
    "AOM_001866": "AOM_101162",
    "AOM_100989": "AOM_101161",
    "AOM_101139": "AOM_101160",
    "AOM_006349": "AOM_101142",
    "AOM_100987": "AOM_101160",
    "AOM_006334": "AOM_101160",
    "AOM_001832": "AOM_101159",
    "AOM_006241": "AOM_101161",
    "AOM_001922": "AOM_101142",
    "AOM_000746": "AOM_101147",
    "AOM_002072": "AOM_101142",
    "AOM_000809": "AOM_101023",
    "AOM_001865": "AOM_101023",
    "AOM_006389": "AOM_101147",
    "AOM_000808": "AOM_006389",
    "AOM_001068": "AOM_101142",
    "AOM_001069": "AOM_101147",
    "AOM_101159": "AOM_100850",
    "AOM_101160": "AOM_100850",
    "AOM_101161": "AOM_101160",
    "AOM_101162": "AOM_101160",
}

classification_path = DATA / "approved_feed_taxonomy_classifications.csv"
classification_rows = [
    row for row in read(classification_path)
    if row["concept_id"] not in new_ids
]
classified_ids = {row["concept_id"] for row in classification_rows}
for row in review_rows:
    if row["concept_id"] not in classified_ids:
        classification_rows.append({
            "concept_id": row["concept_id"],
            "preferred_label": row["preferred_label"],
            "implementation_status": "",
            "semantic_class": "",
            "target_parent_id": "",
            "status": "",
            "reviewer": "",
            "review_date": "",
            "evidence": "",
            "rationale": "",
        })
classification_by_id = {row["concept_id"]: row for row in classification_rows}
assert set(review_by_id) <= set(classification_by_id)
for row in review_rows:
    concept_id = row["concept_id"]
    target = classification_by_id[concept_id]
    target.update({
        "preferred_label": proposed_labels.get(concept_id, row["preferred_label"]),
        "implementation_status": (
            "implemented-cohort-b" if concept_id in descriptor_ids
            else "hold" if concept_id in held_ids
            else "implemented"
        ),
        "semantic_class": (
            "aom:FeedAdditive" if concept_id == "AOM_101135"
            else "aom:FeedMaterial" if concept_id in feed_material_ids
            else ""
        ),
        "target_parent_id": final_parent.get(concept_id, ""),
        "status": "hold" if concept_id in held_ids else "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{row['evidence_ids']};{ADR};{METHOD}",
        "rationale": row["rationale"],
    })
for concept_id, label, _, _ in new_specs:
    classification_rows.append({
        "concept_id": concept_id,
        "preferred_label": label,
        "implementation_status": "implemented",
        "semantic_class": "aom:FeedMaterial",
        "target_parent_id": final_parent[concept_id],
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"FEEDIPEDIA-CATEGORIES;{ADR};{METHOD}",
        "rationale": "Accepted editorial navigation category; source, product role, and legal status remain independent.",
    })
write(classification_path, fieldnames(classification_path), classification_rows)

temporary_rows = [{
    "concept_id": "AOM_001866",
    "preferred_label": "Glycerol",
    "reason": "FeedMaterial status is supported but generic concept scope does not distinguish crude glycerine, refined glycerine, or chemical glycerol.",
    "evidence_gap": "Align AOM scope to applicable catalogue entries and represented source records.",
    "owner": REVIEWER,
    "target_cohort": "Cohort A follow-up; era-program issue 52",
    "review_date": DATE,
    "resolution_deadline": "before next public livestock release",
    "status": "temporary-unclassified",
}]
write(OUTPUT / "temporary_unclassified_register.csv", list(temporary_rows[0]), temporary_rows)

implementation_rows = []
for row in review_rows:
    concept_id = row["concept_id"]
    classification = classification_by_id[concept_id]
    implementation_rows.append({
        "concept_id": concept_id,
        "preferred_label": classification["preferred_label"],
        "review_status": row["status"],
        "implementation_status": classification["implementation_status"],
        "semantic_class": classification["semantic_class"],
        "target_parent_id": classification["target_parent_id"],
        "decision_record": ADR,
        "method": METHOD,
        "reviewer": REVIEWER,
        "implementation_date": DATE,
        "evidence_ids": row["evidence_ids"],
        "rationale": row["rationale"],
    })
write(OUTPUT / "feed_product_kind_implementation_register.csv", list(implementation_rows[0]), implementation_rows)

evidence_rows = read(REVIEW / "evidence_register.csv")
evidence_rows.extend([
    {
        "evidence_id": "ADR-0045-ACCEPTANCE",
        "authority": "ERA-AOM governance",
        "title": "ADR 0045 accepted feed product-kind and source-navigation decision",
        "url": ADR,
        "evidence_class": "decision-record",
        "supported_claim": "Pete Steward accepted all Cohort A dispositions and authorized separate governed implementation.",
        "limitation": "Implementation does not authorize external publication or resolve recorded holds.",
        "access_date": DATE,
    },
    {
        "evidence_id": "GLOBAL-LABEL-AUDIT-V34",
        "authority": "ERA-AOM",
        "title": "Cohort A normalized-label and external-label collision audit",
        "url": "review/livestock-v34/identity_collision_audit.csv",
        "evidence_class": "governance-audit",
        "supported_claim": "All seven proposed preferred labels are collision-free across governed preferred, alternative, hidden, deprecated, and external-resource labels.",
        "limitation": "Lexical non-collision does not itself establish semantic identity or authority scope.",
        "access_date": DATE,
    },
    {
        "evidence_id": "REJECTED-ID-RESERVATION",
        "authority": "ERA governance audit",
        "title": "Reservation of rejected pre-revert identifiers",
        "url": "review/livestock-v32/README.md#browser-baseline-correction",
        "evidence_class": "identifier-governance",
        "supported_claim": "AOM_101156 through AOM_101158 were observed only in reverted unapproved work and remain absent from ontology output.",
        "limitation": "Reservation prevents reuse but does not validate rejected concepts or parentage.",
        "access_date": DATE,
    },
])
write(OUTPUT / "evidence_register.csv", list(evidence_rows[0]), evidence_rows)

summary = {
    "status": "implemented-candidate",
    "decision": ADR,
    "reviewed_rows": len(review_rows),
    "approved_rows": sum(row["status"] == "approved" for row in review_rows),
    "held_rows": sum(row["status"] == "held" for row in review_rows),
    "new_navigation_concepts": len(new_specs),
    "reserved_rejected_identifiers": sorted(reserved_ids),
    "label_changes": len(renames),
    "hierarchy_revisions": len(desired_parent),
    "temporary_unclassified_members": len(temporary_rows),
    "feed_material_direct_children": ["AOM_000559", "AOM_000735", "AOM_101159", "AOM_101160"],
    "reviewer": REVIEWER,
    "implementation_date": DATE,
}
(OUTPUT / "feed_product_kind_implementation_summary.json").write_text(
    json.dumps(summary, indent=2) + "\n"
)
print(json.dumps(summary, indent=2))
