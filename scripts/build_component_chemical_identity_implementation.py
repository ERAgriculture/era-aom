#!/usr/bin/env python3
"""Implement accepted component, chemical-identity, and composition boundaries."""

import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "livestock-staging"
REVIEW = ROOT / "review" / "livestock-v37"
OUTPUT = ROOT / "review" / "livestock-v38"
ADR = "docs/decisions/0048-chemical-identity-composition-and-component-model.md"
METHOD = "docs/methods/component-chemical-identity-governance.md"
DATE = "2026-08-20"
REVIEWER = "Pete Steward"
PREFIX = "COMPONENT-CHEMICAL-"


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
    value = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def upsert(path, key, replacements):
    current = [row for row in read(path) if row[key] not in replacements]
    current.extend(replacements.values())
    write(path, fields(path), current)


review_path = REVIEW / "component_chemical_review.csv"
review_rows = read(review_path)
assert len(review_rows) == 164
for row in review_rows:
    if row["status"] == "proposed":
        row["status"] = "approved"
assert Counter(row["status"] for row in review_rows) == {"approved": 145, "held": 19}
write(review_path, fields(review_path), review_rows)

overlap_path = REVIEW / "identity_overlap_review.csv"
overlap_rows = read(overlap_path)
for row in overlap_rows:
    if row["status"] == "proposed":
        row["status"] = "approved"
assert Counter(row["status"] for row in overlap_rows) == {"approved": 4, "held": 5}
write(overlap_path, fields(overlap_path), overlap_rows)

adr_path = ROOT / ADR
adr_text = adr_path.read_text(encoding="utf-8")
adr_text = adr_text.replace("- Status: Proposed", "- Status: Accepted")
adr_text = adr_text.replace(
    "Pending Pete Steward review.",
    "Accepted by Pete Steward on 2026-08-20. Proposed dispositions are approved; held rows remain explicit implementation holds.",
)
adr_path.write_text(adr_text, encoding="utf-8")

new_specs = {
    "AOM_101180": {
        "label": "Plant anatomical components",
        "definition": "Plant structures used as material-component values after source-aware anatomical review; processed fractions and unresolved vernacular parts remain outside this group.",
        "parent": "AOM_101019",
        "level": "6",
    },
    "AOM_101181": {
        "label": "Animal anatomical components",
        "definition": "Animal structures used as material-component values after source-aware anatomical review; body substances and unresolved collective terms remain outside this group.",
        "parent": "AOM_101019",
        "level": "6",
    },
}
new_ids = set(new_specs)
assert new_ids == {"AOM_101180", "AOM_101181"}

plant_ids = {
    "AOM_101024", "AOM_101025", "AOM_101026", "AOM_101027", "AOM_101028",
    "AOM_101029", "AOM_101033", "AOM_101035", "AOM_101036", "AOM_101037",
    "AOM_101038", "AOM_101039", "AOM_101042", "AOM_101043", "AOM_101045",
    "AOM_101046", "AOM_101047", "AOM_101107", "AOM_101117", "AOM_101121",
    "AOM_101153",
}
assert len(plant_ids) == 21

definition_updates = {
    "AOM_000196": "Measurable or observable characteristics describing chemical composition of feed; chemical identity, component retention, material use, and analytical result values require separate assertions.",
    "AOM_101146": "Chemical entities encountered in feed data independently of measured composition, feed-product kind, functional role, or additive authorization.",
    "AOM_101023": "Chemical-entity categories used as targets of constituent relations; primary role is supplied by relation from feed material.",
    "AOM_101147": "Chemically identified substances or substance groups represented independently of feed-material, formulation, or additive product kind.",
    "AOM_000809": "Chemical-entity category for fatty acids regarded as essential in relevant animal context; species, requirement, measured content, and feed use require separate assertions.",
    "AOM_001571": "Chemical-entity category for proteins represented as constituents of feed materials; measured protein content and feed-material use require separate assertions.",
    "AOM_001577": "Chemical-entity category for carbohydrates represented as constituents of feed materials; measured carbohydrate content and feed-material use require separate assertions.",
    "AOM_001865": "Chemical-entity category for non-bound or extractable gossypol represented independently of measured concentration and feed-product use.",
    "AOM_001578": "Chemical-entity category for dextrins represented independently of measured concentration and feed-product use.",
    "AOM_101085": "Anatomical structures, body substances, and process-defined fractions represented as components of feed materials; crop-residue product identity and component retention remain separate.",
    "AOM_101019": "Biological anatomical structures represented as feed-material components, grouped by plant or animal source where exact scope is established.",
    "AOM_101143": "Material fractions produced or recovered through processing rather than one anatomical structure, including bran and other reviewed fractions.",
    "AOM_101145": "Animal-derived body substances represented as feed-material components without treating them as connected anatomical structures or economic product roles.",
    "AOM_101104": "Cereal outer-layer milling fraction containing variable attached tissues and recovered during milling; not one exact anatomical structure.",
    "AOM_101115": "Positive native-component retention or integrity states represented independently of measured chemical composition.",
    "AOM_101086": "Component-retention state indicating retention of harvested whole-crop scope rather than one selected component.",
    "AOM_101110": "Component-retention state in which bran, plant embryo, and endosperm remain in characteristic proportions independently of particle-size reduction.",
    "AOM_001616": "Animal blood represented as one stable body-substance identity; feed-material use, source taxon, processing, and by-product role require separate assertions.",
    "AOM_101024": "Short enlarged plant shoot system with condensed stem and fleshy leaves or leaf bases.",
    "AOM_101025": "Flattened and expanded plant shoot axis.",
    "AOM_101027": "Plant shoot system containing a short enlarged stem with condensed internodes and one or more buds.",
    "AOM_101028": "Plant multi-tissue structure developing from gynoecium or carpel and potentially containing seed.",
    "AOM_101029": "Whole plant participating in plant embryo stage; commercial germ fractions require separate feed-material identity.",
    "AOM_101033": "Plant phyllome not associated with reproductive structure.",
    "AOM_101036": "Collective plant organ-part structure forming false stem from concentric leaf sheaths.",
    "AOM_101037": "Plant axis lacking shoot-axis nodes and usually growing indeterminately.",
    "AOM_101038": "Plant multi-tissue structure developing from ovule and containing plant embryo enclosed by seed coat.",
    "AOM_101042": "Elongated cylindrical plant organ part supporting another organ part.",
    "AOM_101043": "Radially enlarged plant axis.",
    "AOM_101046": "Plant tissue outside vascular cambium or xylem, including living inner and dead outer bark where present.",
    "AOM_101047": "Primary shoot axis of plant.",
    "AOM_101117": "Determinate reproductive shoot system containing at least one carpel or stamen and no nested determinate shoot system.",
    "AOM_101121": "Swollen horizontal shoot axis growing at or below substrate and producing shoots above and roots or rhizoids below.",
    "AOM_101122": "Animal exocrine gland that secretes bile and performs central metabolic, storage, synthesis, and detoxification functions.",
    "AOM_101153": "Maximal portion of nutritive plant tissue within seed.",
    **{concept_id: spec["definition"] for concept_id, spec in new_specs.items()},
}

proposed_labels = {
    "AOM_101180": "Plant anatomical components",
    "AOM_101181": "Animal anatomical components",
    "AOM_101146": "Feed-related chemical entities",
    "AOM_101023": "Chemical constituent categories",
    "AOM_000196": "Feed composition characteristics",
    "AOM_101029": "Plant embryo",
}

mapping_specs = [
    ("AOM_101146", "broadMatch", "CHEBI_24431", "chemical entity", "https://www.ebi.ac.uk/chebi/CHEBI%3A24431", "ChEBI record accessed 2026-08-20"),
    ("AOM_101147", "closeMatch", "CHEBI_59999", "chemical substance", "https://www.ebi.ac.uk/chebi/CHEBI%3A59999", "ChEBI record accessed 2026-08-20"),
    ("AOM_101104", "closeMatch", "FOODON_03420288", "seed bran", "http://purl.obolibrary.org/obo/FOODON_03420288", "FoodOn commit c5035015de540ba4f4210fd0e24d3909d6fb2037"),
    ("AOM_101046", "exactMatch", "PO_0004518", "bark", "http://purl.obolibrary.org/obo/PO_0004518", "Plant Ontology commit 94750e01c897da6955c2fef97379f4d99cb333a8"),
    ("AOM_101024", "exactMatch", "PO_0025356", "bulb", "http://purl.obolibrary.org/obo/PO_0025356", "Plant Ontology commit 94750e01c897da6955c2fef97379f4d99cb333a8"),
    ("AOM_101025", "exactMatch", "PO_0025354", "cladode", "http://purl.obolibrary.org/obo/PO_0025354", "Plant Ontology commit 94750e01c897da6955c2fef97379f4d99cb333a8"),
    ("AOM_101027", "exactMatch", "PO_0025355", "corm", "http://purl.obolibrary.org/obo/PO_0025355", "Plant Ontology commit 94750e01c897da6955c2fef97379f4d99cb333a8"),
    ("AOM_101153", "exactMatch", "PO_0009089", "endosperm", "http://purl.obolibrary.org/obo/PO_0009089", "Plant Ontology commit 94750e01c897da6955c2fef97379f4d99cb333a8"),
    ("AOM_101117", "exactMatch", "PO_0009046", "flower", "http://purl.obolibrary.org/obo/PO_0009046", "Plant Ontology commit 94750e01c897da6955c2fef97379f4d99cb333a8"),
    ("AOM_101028", "exactMatch", "PO_0009001", "fruit", "http://purl.obolibrary.org/obo/PO_0009001", "Plant Ontology commit 94750e01c897da6955c2fef97379f4d99cb333a8"),
    ("AOM_101029", "relatedMatch", "PO_0009009", "plant embryo", "http://purl.obolibrary.org/obo/PO_0009009", "Plant Ontology commit 94750e01c897da6955c2fef97379f4d99cb333a8"),
    ("AOM_101033", "exactMatch", "PO_0025034", "leaf", "http://purl.obolibrary.org/obo/PO_0025034", "Plant Ontology commit 94750e01c897da6955c2fef97379f4d99cb333a8"),
    ("AOM_101036", "exactMatch", "PO_0025248", "pseudostem", "http://purl.obolibrary.org/obo/PO_0025248", "Plant Ontology commit 94750e01c897da6955c2fef97379f4d99cb333a8"),
    ("AOM_101121", "exactMatch", "PO_0004542", "rhizome", "http://purl.obolibrary.org/obo/PO_0004542", "Plant Ontology commit 94750e01c897da6955c2fef97379f4d99cb333a8"),
    ("AOM_101037", "exactMatch", "PO_0009005", "root", "http://purl.obolibrary.org/obo/PO_0009005", "Plant Ontology commit 94750e01c897da6955c2fef97379f4d99cb333a8"),
    ("AOM_101038", "exactMatch", "PO_0009010", "seed", "http://purl.obolibrary.org/obo/PO_0009010", "Plant Ontology commit 94750e01c897da6955c2fef97379f4d99cb333a8"),
    ("AOM_101042", "exactMatch", "PO_0025066", "stalk", "http://purl.obolibrary.org/obo/PO_0025066", "Plant Ontology commit 94750e01c897da6955c2fef97379f4d99cb333a8"),
    ("AOM_101047", "exactMatch", "PO_0009047", "stem", "http://purl.obolibrary.org/obo/PO_0009047", "Plant Ontology commit 94750e01c897da6955c2fef97379f4d99cb333a8"),
    ("AOM_101043", "exactMatch", "PO_0025522", "tuber", "http://purl.obolibrary.org/obo/PO_0025522", "Plant Ontology commit 94750e01c897da6955c2fef97379f4d99cb333a8"),
    ("AOM_101122", "exactMatch", "UBERON_0002107", "liver", "http://purl.obolibrary.org/obo/UBERON_0002107", "Uberon commit 1d91869610a93335203dc931a224302f42e8c530"),
]
assert len(mapping_specs) == 20

label_index = {}
for source, label_field in [
    (DATA / "labels.csv", "label"),
    (DATA / "approved_new_concepts.csv", "preferred_label"),
    (DATA / "approved_label_additions.csv", "label"),
    (DATA / "approved_concept_retirements.csv", "preferred_label"),
]:
    for row in read(source):
        label_index.setdefault(normalize(row[label_field]), set()).add(row["concept_id"])
mapped_external = {
    (concept_id, normalize(label))
    for concept_id, _, _, label, _, _ in mapping_specs
}
external_labels = read(DATA / "approved_external_resource_labels.csv")
collision_rows = []
for concept_id, label in proposed_labels.items():
    normalized = normalize(label)
    concept_matches = sorted(label_index.get(normalized, set()) - {concept_id})
    external_matches = sorted({
        row["target_uri"]
        for row in external_labels
        if normalize(row["target_label"]) == normalized
    })
    allowed_external = (concept_id, normalized) in mapped_external
    assert not concept_matches, (concept_id, label, concept_matches)
    assert not external_matches or allowed_external, (concept_id, label, external_matches)
    collision_rows.append({
        "concept_id": concept_id,
        "proposed_label": label,
        "normalized_label": normalized,
        "matched_concept_ids": "",
        "external_label_matches": ";".join(external_matches),
        "decision": "approved-authority-mapped-label" if external_matches else "approved-no-collision",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"data/livestock-staging/labels.csv;data/livestock-staging/approved_label_additions.csv;data/livestock-staging/approved_external_resource_labels.csv;{ADR}",
        "rationale": "Global preferred, alternative, hidden, deprecated, and external-label audit found no unexplained identity collision.",
    })
write(OUTPUT / "identity_collision_audit.csv", list(collision_rows[0]), collision_rows)

new_path = DATA / "approved_new_concepts.csv"
new_rows = [row for row in read(new_path) if row["concept_id"] not in new_ids]
new_by_id = {row["concept_id"]: row for row in new_rows}
for concept_id, label in {
    "AOM_101146": "Feed-related chemical entities",
    "AOM_101023": "Chemical constituent categories",
    "AOM_101029": "Plant embryo",
}.items():
    new_by_id[concept_id]["preferred_label"] = label
for concept_id, definition in definition_updates.items():
    if concept_id in new_by_id:
        new_by_id[concept_id]["scope_note"] = definition
new_by_id["AOM_101146"].update({"broader_id": "AOM_000328", "hierarchy_level": "5", "derived_path": "Governed feed taxonomy/Feed-related chemical entities"})
new_by_id["AOM_101023"].update({"broader_id": "AOM_101146", "hierarchy_level": "6", "derived_path": "Governed feed taxonomy/Feed-related chemical entities/Chemical constituent categories"})
new_by_id["AOM_101019"].update({"broader_id": "AOM_101085", "hierarchy_level": "6", "derived_path": "Governed feed taxonomy/Feed material components/Anatomical components"})
new_by_id["AOM_101115"].update({"broader_id": "AOM_000328", "hierarchy_level": "5", "derived_path": "Governed feed taxonomy/Native-component retention states"})
for concept_id in {"AOM_101086", "AOM_101110", "AOM_101116", "AOM_101134"}:
    new_by_id[concept_id].update({"hierarchy_level": "6", "derived_path": f"Governed feed taxonomy/Native-component retention states/{new_by_id[concept_id]['preferred_label']}"})
for concept_id in plant_ids:
    new_by_id[concept_id].update({"broader_id": "AOM_101180", "hierarchy_level": "7", "derived_path": f"Governed feed taxonomy/Feed material components/Anatomical components/Plant anatomical components/{new_by_id[concept_id]['preferred_label']}"})
new_by_id["AOM_101122"].update({"broader_id": "AOM_101181", "hierarchy_level": "7", "derived_path": "Governed feed taxonomy/Feed material components/Anatomical components/Animal anatomical components/Liver"})
new_by_id["AOM_101104"].update({"broader_id": "AOM_101143", "hierarchy_level": "6", "derived_path": "Governed feed taxonomy/Feed material components/Processed material fractions/Bran"})
for concept_id, spec in new_specs.items():
    new_rows.append({
        "case_id": f"{PREFIX}NEW-{concept_id}",
        "concept_id": concept_id,
        "preferred_label": spec["label"],
        "scope_note": spec["definition"],
        "broader_id": spec["parent"],
        "hierarchy_level": spec["level"],
        "derived_path": f"Governed feed taxonomy/Feed material components/Anatomical components/{spec['label']}",
        "child_ids": "",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": "Collision-audited navigation concept approved under ADR 0048.",
    })
write(new_path, fields(new_path), new_rows)

registry_path = DATA / "livestock_id_registry.csv"
registry_rows = [row for row in read(registry_path) if row["concept_id"] not in new_ids]
for concept_id, spec in new_specs.items():
    registry_rows.append({
        "concept_id": concept_id,
        "allocated_on": DATE,
        "status": "allocated",
        "preferred_label": spec["label"],
        "case_id": f"{PREFIX}NEW-{concept_id}",
        "allocator": REVIEWER,
        "allocation_basis": "Sequential allocation after global preferred, alternative, hidden, deprecated, and external-label collision audit; accepted under ADR 0048.",
    })
registry_rows.sort(key=lambda row: int(row["concept_id"].split("_")[1]))
write(registry_path, fields(registry_path), registry_rows)

baseline_path = ROOT / "config" / "identity-integrity-baseline.json"
baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
baseline.update({"captured": DATE, "frozen_generated_identifier_frontier": 101181, "new_identifier_allocation_frozen": True})
baseline_path.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")

correction_path = DATA / "approved_label_corrections.csv"
corrections = {row["concept_id"]: row for row in read(correction_path)}
corrections["AOM_000196"] = {
    "case_id": f"{PREFIX}LABEL-AOM_000196",
    "concept_id": "AOM_000196",
    "old_label": "Feed Chemical Composition",
    "new_label": "Feed composition characteristics",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": ADR,
    "rationale": "Label distinguishes measured composition characteristics from chemical identity.",
}
write(correction_path, fields(correction_path), list(corrections.values()))

addition_path = DATA / "approved_label_additions.csv"
alias_specs = {
    "AOM_101146": "Feed chemical entities",
    "AOM_101023": "Primary chemical constituents",
    "AOM_101029": "Germ",
}
additions = [row for row in read(addition_path) if row["case_id"] not in {f"{PREFIX}ALIAS-{concept_id}" for concept_id in alias_specs}]
for concept_id, label in alias_specs.items():
    additions.append({
        "case_id": f"{PREFIX}ALIAS-{concept_id}",
        "concept_id": concept_id,
        "language": "en",
        "label_type": "alt",
        "label": label,
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": ADR,
        "rationale": "Preserves prior public label after accepted semantic clarification.",
    })
write(addition_path, fields(addition_path), additions)

override_path = DATA / "approved_definition_overrides.csv"
overrides = {row["concept_id"]: row for row in read(override_path)}
for concept_id, definition in definition_updates.items():
    overrides[concept_id] = {
        "concept_id": concept_id,
        "language": "en",
        "definition": definition,
        "definition_method": "component_chemical_identity_definition_replacement",
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": "Definition enforces accepted identity, composition, component, anatomy, or component-retention boundary.",
    }
write(override_path, fields(override_path), list(overrides.values()))

definition_path = DATA / "approved_definition_enrichments.csv"
definition_rows = [row for row in read(definition_path) if row["concept_id"] not in definition_updates]
for concept_id, definition in definition_updates.items():
    definition_rows.append({
        "concept_id": concept_id,
        "language": "en",
        "definition": definition,
        "definition_method": "component_chemical_identity_definition_replacement",
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": "Definition enforces accepted identity, composition, component, anatomy, or component-retention boundary.",
    })

semantic_types = {
    "AOM_001578": "aom:ChemicalConstituent",
    "AOM_101180": "aom:FeedMaterialPartCategory",
    "AOM_101181": "aom:FeedMaterialPartCategory",
}
type_path = DATA / "approved_concept_semantic_types.csv"
type_rows = [row for row in read(type_path) if row["concept_id"] not in semantic_types]
for concept_id, semantic_class in semantic_types.items():
    type_rows.append({
        "case_id": f"{PREFIX}TYPE-{concept_id}",
        "concept_id": concept_id,
        "semantic_class": semantic_class,
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": "Accepted semantic class supports independent identity or anatomy navigation.",
    })
write(type_path, fields(type_path), type_rows)

facet_path = DATA / "approved_ingredient_facet_concepts.csv"
retired_facet_ids = {
    "AOM_001571", "AOM_001616", "AOM_101103", "AOM_101105",
    "AOM_101106", "AOM_101120", "AOM_101144", "AOM_101154",
}
facet_rows = [row for row in read(facet_path) if row["concept_id"] not in retired_facet_ids]
facet_by_id = {row["concept_id"]: row for row in facet_rows}
for concept_id in {"AOM_101086", "AOM_101110", "AOM_101115"}:
    facet_by_id[concept_id].update({
        "facet": "component_retention_state",
        "target_property": "aom:componentRetentionState",
        "value_class": "aom:ComponentRetentionState",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": ADR,
    })
for concept_id, label, facet, prop, value_class in [
    ("AOM_001571", "Protein", "chemical_constituent", "aom:primaryConstituent", "aom:ChemicalConstituent"),
    ("AOM_001616", "Blood", "material_component", "aom:materialComponent", "aom:FeedMaterialComponent"),
]:
    facet_rows.append({
        "concept_id": concept_id,
        "preferred_label": label,
        "facet": facet,
        "target_property": prop,
        "value_class": value_class,
        "concept_role": "facet_value",
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": ADR,
    })
write(facet_path, fields(facet_path), facet_rows)

deprecation_path = DATA / "approved_deprecations.csv"
deprecations = {row["deprecated_id"]: row for row in read(deprecation_path)}
for deprecated_id, replacement_id, label, rationale in [
    ("AOM_101103", "AOM_001616", "Blood", "Property context does not justify duplicate Blood identity; replacement remains usable as body substance and feed material."),
    ("AOM_101120", "AOM_001571", "Protein", "Constituent relation supplies role; duplicate Protein constituent identity is unnecessary."),
    ("AOM_101144", "AOM_101143", "Processed material fractions", "One-child Cereal milling fractions wrapper adds no stable semantic distinction."),
]:
    deprecations[deprecated_id] = {
        "case_id": f"{PREFIX}DEPRECATE-{deprecated_id}",
        "deprecated_id": deprecated_id,
        "replacement_id": replacement_id,
        "preferred_label": label,
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": rationale,
    }
write(deprecation_path, fields(deprecation_path), list(deprecations.values()))

retirement_path = DATA / "approved_concept_retirements.csv"
retirements = {row["concept_id"]: row for row in read(retirement_path)}
for concept_id, label, rationale, history in [
    ("AOM_101154", "Composite crop-residue components", "Crop-residue material identity is not one material-component category.", "Retired as erroneous component wrapper. Model Straw and Stover through reviewed feed-material identity and product role; unresolved generic identities remain held."),
    ("AOM_101105", "Stover", "Published component ID must not be repurposed as generic material identity without collision review.", "Retired as material-component value without replacement. Generic Stover feed-material identity remains an explicit hold."),
    ("AOM_101106", "Straw", "Published component ID must not be repurposed as generic material identity without collision review.", "Retired as material-component value without replacement. Reuse of AOM_000582 or another generic Straw identity remains an explicit hold."),
]:
    retirements[concept_id] = {
        "case_id": f"{PREFIX}RETIRE-{concept_id}",
        "concept_id": concept_id,
        "preferred_label": label,
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": rationale,
        "history_note": history,
    }
write(retirement_path, fields(retirement_path), list(retirements.values()))

revision_path = DATA / "approved_hierarchy_revisions.csv"
revision_specs = [
    ("AOM_000809", "AOM_101023", "AOM_101146"),
    ("AOM_001571", "AOM_101023", "AOM_101146"),
    ("AOM_001577", "AOM_101023", "AOM_101146"),
    ("AOM_001578", "AOM_001577", "AOM_101146"),
    ("AOM_001865", "AOM_101023", "AOM_101146"),
    ("AOM_001616", "", "AOM_101145"),
]
revision_cases = {f"{PREFIX}MOVE-{child_id}-{parent_id}" for child_id, _, parent_id in revision_specs}
revisions = [row for row in read(revision_path) if row["case_id"] not in revision_cases]
for child_id, old_parent, new_parent in revision_specs:
    revisions.append({
        "case_id": f"{PREFIX}MOVE-{child_id}-{new_parent}",
        "child_id": child_id,
        "remove_parent_id": old_parent,
        "add_parent_id": new_parent,
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": "Accepted hierarchy separates chemical identity or body-substance identity from relation-specific role.",
    })
write(revision_path, fields(revision_path), revisions)

mapping_path = DATA / "approved_mapping_additions.csv"
mapping_cases = {f"{PREFIX}MAP-{concept_id}-{target_id}" for concept_id, _, target_id, _, _, _ in mapping_specs}
mapping_rows = [row for row in read(mapping_path) if row["case_id"] not in mapping_cases]
for concept_id, relation, target_id, label, uri, release in mapping_specs:
    mapping_rows.append({
        "case_id": f"{PREFIX}MAP-{concept_id}-{target_id}",
        "subject_id": concept_id,
        "mapping_relation": relation,
        "target_scheme": "ontology",
        "target_id": target_id,
        "target_uri": uri,
        "original_value": uri,
        "status": "approved",
        "source_release": release,
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": "Concept-level definition comparison supports governed mapping relation.",
    })
write(mapping_path, fields(mapping_path), mapping_rows)

external_path = DATA / "approved_external_resource_labels.csv"
external_by_uri = {row["target_uri"]: row for row in read(external_path)}
for _, _, _, label, uri, release in mapping_specs:
    external_by_uri[uri] = {
        "target_uri": uri,
        "target_label": label,
        "language": "en",
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": release,
        "rationale": "Pinned authority label recorded for browser display and mapping audit.",
    }
write(external_path, fields(external_path), list(external_by_uri.values()))

feed_facet_path = DATA / "approved_feed_material_facets.csv"
feed_facets = read(feed_facet_path)
integrity_materials = set()
for row in feed_facets:
    if row["target_concept_id"] in {"AOM_101086", "AOM_101110"}:
        row.update({
            "target_property": "aom:componentRetentionState",
            "reviewer": REVIEWER,
            "review_date": DATE,
            "evidence": f"{row['evidence']};{ADR}" if ADR not in row["evidence"] else row["evidence"],
            "rationale": "Positive component retention is independent of measured chemical composition.",
        })
        integrity_materials.add(row["feed_material_id"])
assert len(integrity_materials) == 5
write(feed_facet_path, fields(feed_facet_path), feed_facets)

hard_tail_path = DATA / "approved_hard_tail_feed_material_facets.csv"
hard_tail_rows = read(hard_tail_path)
protein_migrations = 0
protein_material_ids = set()
for row in hard_tail_rows:
    if row["target_concept_id"] == "AOM_101120":
        row.update({
            "target_concept_id": "AOM_001571",
            "target_label": "Protein",
            "reviewer": REVIEWER,
            "review_date": DATE,
            "evidence": f"{row['evidence']};{ADR}",
            "rationale": "Reuses stable Protein identity; primary constituent role is supplied by relation.",
        })
        protein_migrations += 1
        protein_material_ids.add(row["feed_material_id"])
assert protein_migrations in {0, 1}
write(hard_tail_path, fields(hard_tail_path), hard_tail_rows)

generated_path = DATA / "approved_generated_feed_material_facets.csv"
generated_rows = read(generated_path)
removed_residue_rows = [row for row in generated_rows if row["target_concept_id"] in {"AOM_101105", "AOM_101106"}]
removed_residue_counts = Counter(row["target_concept_id"] for row in removed_residue_rows)
assert not removed_residue_counts or removed_residue_counts == Counter({
    "AOM_101106": 62,
    "AOM_101105": 4,
})
generated_rows = [row for row in generated_rows if row["target_concept_id"] not in {"AOM_101105", "AOM_101106"}]
write(generated_path, fields(generated_path), generated_rows)

changed_material_ids = (
    {row["feed_material_id"] for row in removed_residue_rows}
    | integrity_materials
    | protein_material_ids
)
all_facets = (
    feed_facets
    + generated_rows
    + hard_tail_rows
    + read(DATA / "approved_structural_feed_material_facets.csv")
)
facets_by_material = {}
for row in all_facets:
    facets_by_material.setdefault(row["feed_material_id"], []).append(row)
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
    "aom:ingredientPart": "ingredient part",
    "aom:processingMethod": "processing method",
    "aom:productionProcessProvenance": "production-process provenance",
    "aom:physicalForm": "legacy physical form",
    "aom:presentationForm": "presentation form",
    "aom:bulkConsistency": "bulk consistency",
    "aom:moistureCondition": "moisture condition",
    "aom:productRole": "product role",
    "aom:feedProductType": "feed product type",
    "aom:materialIntegrity": "material integrity",
    "aom:materialComponent": "material component",
    "aom:compositionState": "composition state",
    "aom:componentRetentionState": "component-retention state",
    "aom:primaryConstituent": "primary chemical constituent",
    "aom:ingredientConstituent": "legacy ingredient constituent",
}
definition_rows = [row for row in definition_rows if row["concept_id"] not in changed_material_ids]
for concept_id in sorted(changed_material_ids):
    source = hard_tail_sources.get(concept_id, inventory.get(concept_id, "")).strip()
    assert source, concept_id
    grouped = {}
    for facet in facets_by_material.get(concept_id, []):
        grouped.setdefault(facet["target_property"], set()).add(facet["target_label"])
    characteristics = [
        f"{property_labels[prop]} — {', '.join(sorted(values))}"
        for prop, values in sorted(grouped.items())
    ]
    definition_rows.append({
        "concept_id": concept_id,
        "language": "en",
        "definition": (
            f"A feed material with governed source identity “{source}” and characteristics: "
            + "; ".join(characteristics)
            + "."
        ),
        "definition_method": "composed_from_approved_semantic_facets",
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": "data/livestock-staging/approved_feed_material_facets.csv;data/livestock-staging/approved_generated_feed_material_facets.csv;data/livestock-staging/approved_hard_tail_feed_material_facets.csv;data/livestock-staging/approved_structural_feed_material_facets.csv",
        "rationale": "Definition regenerated after accepted component, constituent, or retention-state migration.",
    })
definition_rows.sort(key=lambda row: row["concept_id"])
write(definition_path, fields(definition_path), definition_rows)

rule_path = DATA / "approved_ingredient_harmonization_rules.csv"
rule_rows = [row for row in read(rule_path) if row["rule_id"] not in {"COMPONENT-STOVER", "COMPONENT-STRAW"}]
assert len(rule_rows) == 37
write(rule_path, fields(rule_path), rule_rows)

manifest_path = DATA / "ingredient_rule_promotion_manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest.update({"rule_version": "1.1.0", "approved_rules": 37, "generated_assertions": len(generated_rows), "review_date": DATE})
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

retention_path = DATA / "approved_component_retention_relations.csv"
retention_rows = read(retention_path)
for row in retention_rows:
    if row["retained_concept_id"] == "AOM_101029":
        evidence = list(dict.fromkeys(filter(None, row["evidence"].split(";") + [ADR])))
        row.update({
            "reviewer": REVIEWER,
            "review_date": DATE,
            "evidence": ";".join(evidence),
            "rationale": "Whole-grain retention includes plant embryo; commercial germ fractions remain separate feed-material identities.",
        })
write(retention_path, fields(retention_path), retention_rows)

classification_path = DATA / "approved_feed_taxonomy_classifications.csv"
classification_rows = read(classification_path)
classification_updates = {
    "AOM_101019": ("implemented-cohort-d", "AOM_101085", "Plant and Animal navigation added; unresolved anatomy remains held at root."),
    "AOM_101029": ("implemented-cohort-d", "AOM_101180", "Anatomical meaning clarified as Plant embryo; commercial germ remains separate material identity."),
    "AOM_101103": ("deprecated-cohort-d", "AOM_001616", "Duplicate Blood component identity replaced by stable Blood identity."),
    "AOM_101104": ("implemented-cohort-d", "AOM_101143", "Bran placed directly under process-defined material fractions."),
    "AOM_101105": ("retired-component-identity-held", "", "Component use retired; generic Stover material identity remains held."),
    "AOM_101106": ("retired-component-identity-held", "", "Component use retired; generic Straw material identity remains held."),
    "AOM_101115": ("implemented-cohort-d", "AOM_000328", "Component retention moved outside measured chemical-composition browse branch."),
    "AOM_101120": ("deprecated-cohort-d", "AOM_001571", "Duplicate Protein constituent identity replaced by Protein."),
    "AOM_101144": ("deprecated-cohort-d", "AOM_101143", "One-child structural wrapper replaced by broader processed-fraction root."),
    "AOM_101146": ("implemented-cohort-d", "AOM_000328", "Chemical identity retained independently and renamed for clarity."),
    "AOM_101154": ("retired-cohort-d", "", "Erroneous crop-residue component wrapper retired."),
}
for row in classification_rows:
    if row["concept_id"] in classification_updates:
        implementation_status, target_parent, rationale = classification_updates[row["concept_id"]]
        row.update({
            "preferred_label": proposed_labels.get(row["concept_id"], row["preferred_label"]),
            "implementation_status": implementation_status,
            "target_parent_id": target_parent,
            "status": "approved",
            "reviewer": REVIEWER,
            "review_date": DATE,
            "evidence": f"{ADR};{METHOD}",
            "rationale": rationale,
        })
write(classification_path, fields(classification_path), classification_rows)

usage_rows = read(REVIEW / "material_usage_inventory.csv")
migration_rows = []
for row in usage_rows:
    if row["recommended_disposition"] == "remove-component-use-hold-identity":
        action = "removed-tautological-component-assertion"
        new_property = ""
        new_target = ""
    elif row["recommended_disposition"] == "deprecate-after-migration":
        action = "migrated-to-canonical-identity"
        new_property = row["target_property"]
        new_target = "AOM_001571"
    elif row["recommended_disposition"] == "move-to-component-integrity":
        action = "migrated-to-component-retention-property"
        new_property = "aom:componentRetentionState"
        new_target = row["target_concept_id"]
    elif row["status"] == "approved-generated":
        action = "retained-generated-assertion"
        new_property = row["target_property"]
        new_target = row["target_concept_id"]
    else:
        action = "retained-reviewed-assertion"
        new_property = row["target_property"]
        new_target = row["target_concept_id"]
    migration_rows.append({
        "feed_material_id": row["feed_material_id"],
        "old_property": row["target_property"],
        "old_target_id": row["target_concept_id"],
        "implementation_action": action,
        "new_property": new_property,
        "new_target_id": new_target,
        "review_status": "held" if row["recommended_disposition"].startswith("hold-") else "approved",
        "reviewer": REVIEWER,
        "implementation_date": DATE,
        "decision_record": ADR,
        "rationale": row["rationale"],
    })
write(OUTPUT / "material_assertion_migration_register.csv", list(migration_rows[0]), migration_rows)

anatomy_rows = read(REVIEW / "anatomical_authority_mapping.csv")
mapping_by_id = {concept_id: (relation, target_id, uri) for concept_id, relation, target_id, _, uri, _ in mapping_specs}
anatomy_implementation = []
for row in anatomy_rows:
    mapping = mapping_by_id.get(row["concept_id"])
    if mapping:
        relation, target_id, _ = mapping
        action = f"published-{relation}"
        target = target_id
        rationale = (
            f"Pinned authority definition reviewed against governed AOM definition; "
            f"{relation} scope accepted under ADR 0048."
        )
    else:
        action = "mapping-held"
        target = ""
        rationale = row["rationale"]
    if row["concept_id"] in plant_ids:
        hierarchy_action = "moved-under-AOM_101180"
    elif row["concept_id"] == "AOM_101122":
        hierarchy_action = "moved-under-AOM_101181"
    else:
        hierarchy_action = "retained-under-AOM_101019-hold"
    anatomy_implementation.append({
        "concept_id": row["concept_id"],
        "preferred_label": proposed_labels.get(row["concept_id"], row["preferred_label"]),
        "hierarchy_action": hierarchy_action,
        "mapping_action": action,
        "mapping_target": target,
        "status": "approved" if mapping else "held",
        "reviewer": REVIEWER,
        "implementation_date": DATE,
        "evidence_ids": row["evidence_ids"],
        "rationale": rationale,
    })
write(OUTPUT / "anatomical_mapping_implementation.csv", list(anatomy_implementation[0]), anatomy_implementation)

implementation_rows = []
for row in review_rows:
    if row["concept_id"] in {"AOM_101105", "AOM_101106"}:
        implementation_status = "retired-component-use;material-identity-held"
    elif row["status"] == "held":
        implementation_status = "held-no-semantic-change"
    elif row["concept_id"] in {"AOM_101103", "AOM_101120", "AOM_101144"}:
        implementation_status = "deprecated-with-replacement"
    elif row["concept_id"] == "AOM_101154":
        implementation_status = "retired"
    elif row["recommended_disposition"] == "retain-boundary-for-cohort-e":
        implementation_status = "retained-for-cohort-e"
    else:
        implementation_status = "implemented"
    implementation_rows.append({
        "concept_id": row["concept_id"],
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
write(OUTPUT / "component_chemical_implementation_register.csv", list(implementation_rows[0]), implementation_rows)

hold_rows = []
for row in review_rows:
    if row["status"] == "held":
        hold_rows.append({
            "concept_id": row["concept_id"],
            "preferred_label": row["preferred_label"],
            "hold_scope": row["recommended_disposition"],
            "blocking_question": row["blocking_question"],
            "owner": REVIEWER,
            "review_date": DATE,
            "status": "held",
            "evidence": f"{ADR};{METHOD}",
        })
write(OUTPUT / "implementation_holds.csv", list(hold_rows[0]), hold_rows)

summary = {
    "status": "implemented-candidate",
    "decision": ADR,
    "reviewed_concepts": len(review_rows),
    "approved_dispositions": sum(row["status"] == "approved" for row in review_rows),
    "held_dispositions": sum(row["status"] == "held" for row in review_rows),
    "new_navigation_concepts": len(new_specs),
    "identifier_frontier": 101181,
    "deprecated_with_replacement": 3,
    "retired_without_replacement": 3,
    "external_mappings": len(mapping_specs),
    "exact_external_mappings": sum(row[1] == "exactMatch" for row in mapping_specs),
    "related_external_mappings": sum(row[1] == "relatedMatch" for row in mapping_specs),
    "close_external_mappings": sum(row[1] == "closeMatch" for row in mapping_specs),
    "broad_external_mappings": sum(row[1] == "broadMatch" for row in mapping_specs),
    "material_assertions_reviewed": len(migration_rows),
    "material_assertions_removed": sum(row["implementation_action"] == "removed-tautological-component-assertion" for row in migration_rows),
    "material_assertions_retargeted": sum(row["implementation_action"] == "migrated-to-canonical-identity" for row in migration_rows),
    "material_assertions_repredicated": sum(row["implementation_action"] == "migrated-to-component-retention-property" for row in migration_rows),
    "ingredient_part_assertions_retained": sum(row["old_property"] == "aom:ingredientPart" for row in migration_rows),
    "anatomical_children_reviewed": len(anatomy_rows),
    "anatomical_mappings_held": sum(row["mapping_action"] == "mapping-held" for row in anatomy_implementation),
    "reviewer": REVIEWER,
    "implementation_date": DATE,
}
(OUTPUT / "component_chemical_implementation_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
(OUTPUT / "README.md").write_text(
    "# Livestock v38 component and chemical-identity implementation\n\n"
    "Implements accepted [ADR 0048](../../docs/decisions/0048-chemical-identity-composition-and-component-model.md).\n\n"
    "## Contents\n\n"
    "- `component_chemical_implementation_register.csv`: every reviewed concept disposition.\n"
    "- `material_assertion_migration_register.csv`: all 627 retained, removed, retargeted, or repredicated assertions.\n"
    "- `anatomical_mapping_implementation.csv`: all 31 anatomy hierarchy and authority-mapping decisions.\n"
    "- `identity_collision_audit.csv`: full label collision gate for new and renamed concepts.\n"
    "- `implementation_holds.csv`: 19 unresolved cases carried forward without inference.\n"
    "- `component_chemical_implementation_summary.json`: machine-readable implementation counts.\n\n"
    "## Evidence trail\n\n"
    "Claim evidence remains in `review/livestock-v37/evidence_register.csv`; method is documented in `docs/methods/component-chemical-identity-governance.md`.\n",
    encoding="utf-8",
)

review_summary_path = REVIEW / "component_chemical_summary.json"
review_summary = json.loads(review_summary_path.read_text(encoding="utf-8"))
review_summary.update({
    "status": "accepted-recommendation",
    "decision_status": "row-dispositions-approved-with-explicit-holds",
    "row_disposition_reviewer": REVIEWER,
    "row_disposition_review_date": DATE,
})
review_summary["review_status_counts"] = {"approved": 145, "held": 19}
review_summary["outputs"]["review_sha256"] = sha256(review_path)
review_summary["outputs"]["identity_overlap_sha256"] = sha256(overlap_path)
review_summary_path.write_text(json.dumps(review_summary, indent=2) + "\n", encoding="utf-8")

print(json.dumps(summary, indent=2))
