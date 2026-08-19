#!/usr/bin/env python3
"""Implement accepted feed-process mechanism, objective, benefit, and provenance axes."""

import csv
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "livestock-staging"
REVIEW = ROOT / "review" / "livestock-v35"
OUTPUT = ROOT / "review" / "livestock-v36"
DATE = "2026-08-18"
REVIEWER = "Pete Steward"
ADR = "docs/decisions/0047-feed-process-objective-benefit-and-effect-model.md"
METHOD = "docs/methods/feed-process-axis-governance.md"
PREFIX = "PROCESS-AXIS-"


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


def normalize(value):
    text = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


review_path = REVIEW / "process_axis_review.csv"
review_rows = read(review_path)
assert len(review_rows) == 54
for row in review_rows:
    if row["status"] == "proposed":
        row["status"] = "approved"
assert Counter(row["status"] for row in review_rows) == {"approved": 51, "held": 3}
write(review_path, fieldnames(review_path), review_rows)
review_summary_path = REVIEW / "process_purpose_summary.json"
review_summary = json.loads(review_summary_path.read_text())
review_summary.update({
    "status": "accepted-recommendation",
    "decision_status": "row-dispositions-approved-with-explicit-holds",
    "row_disposition_reviewer": REVIEWER,
    "row_disposition_review_date": DATE,
})
review_summary_path.write_text(json.dumps(review_summary, indent=2) + "\n")

new_specs = [
    (
        "AOM_101163",
        "Enzymatic or biochemical feed processes",
        "Feed-process mechanism category for operations driven primarily by enzyme catalysis or comparable biochemical action; process objective and intended benefit require separate assertions.",
        "AOM_000845",
        "AOM_000820;AOM_100848",
        "aom:ProcessMechanism",
    ),
    (
        "AOM_101164",
        "Feed constituent transformation processes",
        "Technical-objective category for feed operations intended to convert or degrade constituents without implying a nutritional benefit or measured effect.",
        "AOM_000845",
        "AOM_000817;AOM_000818;AOM_000819;AOM_000820;AOM_000827;AOM_000830;AOM_000832;AOM_003098;AOM_100848;AOM_101083;AOM_101088",
        "aom:ProcessTechnicalObjective",
    ),
    (
        "AOM_101165",
        "Feed preservation and stabilisation processes",
        "Technical-objective category for feed operations intended to preserve material or improve storage stability without asserting that the intended outcome was achieved.",
        "AOM_000845",
        "AOM_000830;AOM_101128",
        "aom:ProcessTechnicalObjective",
    ),
    (
        "AOM_101166",
        "Feed component addition and application processes",
        "Technical-objective category for feed operations intended to add or apply a component to material independently of application mechanism or downstream benefit.",
        "AOM_000845",
        "AOM_000817;AOM_003202;AOM_100848",
        "aom:ProcessTechnicalObjective",
    ),
    (
        "AOM_101167",
        "Feed moisture addition and conditioning processes",
        "Technical-objective category for feed operations intended to add moisture or condition material through water uptake without asserting a resulting form or benefit.",
        "AOM_000845",
        "AOM_101099",
        "aom:ProcessTechnicalObjective",
    ),
    (
        "AOM_101168",
        "Feed-process benefits",
        "Controlled vocabulary of contextual benefits that a feed process may be intended to support; membership never asserts an achieved or measured effect.",
        "AOM_000328",
        "",
        "aom:FeedBenefit",
    ),
    (
        "AOM_101169",
        "Digestibility improvement",
        "Possible feed benefit in which process application is intended to improve digestibility; achievement requires application-specific evidence.",
        "AOM_101168",
        "",
        "aom:FeedBenefit",
    ),
    (
        "AOM_101170",
        "Nutrient availability improvement",
        "Possible feed benefit in which process application is intended to improve nutrient availability; achievement requires application-specific evidence.",
        "AOM_101168",
        "",
        "aom:FeedBenefit",
    ),
    (
        "AOM_101171",
        "Antinutritional-factor reduction",
        "Possible feed benefit in which process application is intended to reduce one or more antinutritional factors; achievement requires application-specific evidence.",
        "AOM_101168",
        "",
        "aom:FeedBenefit",
    ),
    (
        "AOM_101172",
        "Feed safety improvement",
        "Possible feed benefit in which process application is intended to improve feed safety; achievement requires application-specific evidence.",
        "AOM_101168",
        "",
        "aom:FeedBenefit",
    ),
    (
        "AOM_101173",
        "Palatability or intake improvement",
        "Possible feed benefit in which process application is intended to improve palatability or voluntary intake; achievement requires application-specific evidence.",
        "AOM_101168",
        "",
        "aom:FeedBenefit",
    ),
    (
        "AOM_101174",
        "Preservation or storage-stability improvement",
        "Possible feed benefit in which process application is intended to improve preservation or storage stability; achievement requires application-specific evidence.",
        "AOM_101168",
        "",
        "aom:FeedBenefit",
    ),
    (
        "AOM_101175",
        "Handling or mixing improvement",
        "Possible feed benefit in which process application is intended to improve handling, mixing, or physical manageability; achievement requires application-specific evidence.",
        "AOM_101168",
        "",
        "aom:FeedBenefit",
    ),
    (
        "AOM_101176",
        "Composition tailoring",
        "Possible feed benefit in which process application is intended to obtain a material with a selected composition; achieved composition requires application-specific evidence.",
        "AOM_101168",
        "",
        "aom:FeedBenefit",
    ),
    (
        "AOM_101177",
        "Process-output recovery",
        "Possible production benefit in which process application is intended to recover a selected output or fraction; achieved recovery requires application-specific evidence.",
        "AOM_101168",
        "",
        "aom:FeedBenefit",
    ),
    (
        "AOM_101178",
        "Dust control",
        "Possible feed benefit in which process application is intended to reduce airborne or fugitive dust; achievement requires application-specific evidence.",
        "AOM_101168",
        "",
        "aom:FeedBenefit",
    ),
    (
        "AOM_101179",
        "Downstream-process facilitation",
        "Possible production benefit in which process application is intended to facilitate a later operation such as fermentation, ensiling, cooking, or fraction recovery.",
        "AOM_101168",
        "",
        "aom:FeedBenefit",
    ),
]
new_ids = {spec[0] for spec in new_specs}
assert new_ids == {f"AOM_{number}" for number in range(101163, 101180)}

proposed_labels = {concept_id: label for concept_id, label, *_ in new_specs}
proposed_labels["AOM_101069"] = "Fat removal"
label_index = {}
for source, label_field in [
    (DATA / "labels.csv", "label"),
    (DATA / "approved_new_concepts.csv", "preferred_label"),
    (DATA / "approved_label_additions.csv", "label"),
    (DATA / "approved_concept_retirements.csv", "preferred_label"),
]:
    for row in read(source):
        label_index.setdefault(normalize(row[label_field]), set()).add(row["concept_id"])
external_labels = {
    normalize(row["target_label"])
    for row in read(DATA / "approved_external_resource_labels.csv")
}
collision_rows = []
for concept_id, label in proposed_labels.items():
    normalized = normalize(label)
    concept_matches = sorted(label_index.get(normalized, set()) - {concept_id})
    external_match = normalized in external_labels
    assert not concept_matches and not external_match, (
        concept_id,
        label,
        concept_matches,
        external_match,
    )
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
new_rows = [row for row in read(new_path) if row["concept_id"] not in new_ids]
new_by_id = {row["concept_id"]: row for row in new_rows}
new_by_id["AOM_100990"]["child_ids"] = ";".join(
    child
    for child in new_by_id["AOM_100990"]["child_ids"].split(";")
    if child != "AOM_000820"
)
new_by_id["AOM_100991"]["child_ids"] = ";".join(
    child
    for child in new_by_id["AOM_100991"]["child_ids"].split(";")
    if child != "AOM_003202"
)
new_by_id["AOM_101069"].update({
    "preferred_label": "Fat removal",
    "scope_note": "Technical process objective of removing or reducing a fat fraction; exact operation, resulting composition, and degree of removal require separate assertions.",
    "derived_path": "Governed feed taxonomy/Feed component separation processes/Fat removal",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": f"{ADR};{METHOD}",
    "rationale": "Reclassified from an underspecified operation to a technical objective; eight material migrations remain explicit holds.",
})
new_by_id["AOM_101084"].update({
    "scope_note": "Upstream production workflow in which sugar-bearing raw material is processed and one or more feed materials arise; direct treatment operations require separate assertions.",
    "derived_path": "Governed feed taxonomy/Feed processes/Sugar processing",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": f"{ADR};{METHOD}",
    "rationale": "Reclassified from direct processing method to production-process provenance.",
})
for concept_id, label, definition, parent_id, child_ids, _ in new_specs:
    new_rows.append({
        "case_id": f"{PREFIX}NEW-{concept_id}",
        "concept_id": concept_id,
        "preferred_label": label,
        "scope_note": definition,
        "broader_id": parent_id,
        "hierarchy_level": "5",
        "derived_path": f"Governed feed process axes/{label}",
        "child_ids": child_ids,
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": "Collision-audited concept required by accepted process-axis implementation.",
    })
write(new_path, fieldnames(new_path), new_rows)

registry_path = DATA / "livestock_id_registry.csv"
registry_rows = [row for row in read(registry_path) if row["concept_id"] not in new_ids]
for concept_id, label, *_ in new_specs:
    registry_rows.append({
        "concept_id": concept_id,
        "allocated_on": DATE,
        "status": "allocated",
        "preferred_label": label,
        "case_id": f"{PREFIX}NEW-{concept_id}",
        "allocator": REVIEWER,
        "allocation_basis": "Sequential allocation after global preferred, alternative, hidden, deprecated, and external-label collision audit; accepted under ADR 0047.",
    })
registry_rows.sort(key=lambda row: int(row["concept_id"].split("_")[1]))
write(registry_path, fieldnames(registry_path), registry_rows)

baseline_path = ROOT / "config" / "identity-integrity-baseline.json"
baseline = json.loads(baseline_path.read_text())
baseline["captured"] = DATE
baseline["frozen_generated_identifier_frontier"] = 101179
baseline["new_identifier_allocation_frozen"] = True
baseline_path.write_text(json.dumps(baseline, indent=2) + "\n")

correction_path = DATA / "approved_label_corrections.csv"
corrections = [row for row in read(correction_path) if row["concept_id"] != "AOM_101069"]
write(correction_path, fieldnames(correction_path), corrections)

addition_path = DATA / "approved_label_additions.csv"
additions = [row for row in read(addition_path) if row["case_id"] != f"{PREFIX}ALIAS-AOM_101069"]
additions.append({
    "case_id": f"{PREFIX}ALIAS-AOM_101069",
    "concept_id": "AOM_101069",
    "language": "en",
    "label_type": "alt",
    "label": "Defatting",
    "status": "approved",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": ADR,
    "rationale": "Preserves prior public label and searchability after objective-focused relabeling.",
})
write(addition_path, fieldnames(addition_path), additions)

definition_updates = {
    "AOM_000845": "Controlled operations and upstream production workflows relevant to feed materials; mechanism, technical objective, intended benefit, and observed effect are represented independently.",
    "AOM_100990": "Feed-process mechanism category for operations driven primarily by living organisms or biological activity; objective and intended benefit require separate assertions.",
    "AOM_100991": "Feed-process mechanism category for operations driven primarily by chemical agents or reactions; objective and intended benefit require separate assertions.",
    "AOM_000837": "Feed-process mechanism category for operations driven primarily by mechanical force; objective and intended benefit require separate assertions.",
    "AOM_000826": "Feed-process mechanism category for operations driven primarily by heat transfer or controlled temperature; objective and intended benefit require separate assertions.",
    "AOM_101129": "Technical-objective category for feed operations intended to reduce particle dimensions without implying one machine, mechanism, physical form, or nutritional benefit.",
    "AOM_101130": "Technical-objective category for feed operations intended to remove, separate, or recover a material component or fraction independently of mechanism.",
    "AOM_101131": "Technical-objective category for feed operations intended to shape or agglomerate material into a presentation such as pellets, flakes, or extrudates.",
    "AOM_000842": "Technical-objective category for feed operations intended to reduce moisture independently of mechanism, resulting moisture condition, or storage benefit.",
    "AOM_101069": "Technical process objective of removing or reducing a fat fraction; exact operation, resulting composition, and degree of removal require separate assertions.",
    "AOM_101084": "Upstream production workflow in which sugar-bearing raw material is processed and one or more feed materials arise; direct treatment operations require separate assertions.",
    "AOM_000817": "Application of ammonia or ammonium hydroxide to feed material as a chemical treatment; dose, conditions, constituent changes, and nutritional effects require separate evidence.",
    "AOM_000818": "Application of an acidic agent to feed material under controlled conditions; agent, dose, objective, and resulting effects require separate assertions.",
    "AOM_000819": "Application of an alkaline agent to feed material under controlled conditions; agent, dose, objective, and resulting effects require separate assertions.",
    "AOM_100848": "Application of urea to feed material under conditions that may involve urease-mediated ammonia formation and subsequent chemical action; resulting effects require separate evidence.",
    "AOM_003202": "Application of molasses to feed material by an unspecified generic application operation; mixing, coating, dose, and downstream effects require separate assertions.",
    "AOM_000820": "Treatment of feed material with one or more enzymes before feeding; enzyme identity, substrate, dose, conditions, and resulting effects require separate assertions.",
    "AOM_006824": "Treatment of feed material with one or more fibrolytic enzymes; enzyme identity, substrate, dose, conditions, and resulting effects require separate assertions.",
    "AOM_000830": "Controlled transformation of feed material through microbial activity; organism, conditions, preservation objective, and resulting effects require separate assertions.",
    "AOM_000831": "Controlled anaerobic conservation of moist feed material in which fermentation occurs; material, packing, conditions, and resulting effects require separate assertions.",
    "AOM_000827": "Heating feed material in boiling water or steam; medium, duration, objective, and resulting effects require separate assertions.",
    "AOM_000828": "Boiling operation in which feed material directly contacts boiling water; duration, objective, and resulting effects require separate assertions.",
    "AOM_000829": "Boiling operation in which feed material is heated indirectly by steam or a heated vessel; duration, objective, and resulting effects require separate assertions.",
    "AOM_000832": "Heating feed material by roasting under dry or low-moisture conditions; temperature, duration, objective, and resulting effects require separate assertions.",
    "AOM_101088": "Heating feed material with pressurized steam in an autoclave; pressure, temperature, duration, objective, and resulting effects require separate assertions.",
    "AOM_101096": "Application of heat to feed material without specifying heating equipment, medium, objective, or resulting effect.",
    "AOM_101083": "Cleavage of chemical bonds in feed constituents through reaction with water; catalytic route, conditions, objective, and resulting effects require separate assertions.",
    "AOM_101099": "Contacting feed material with water or aqueous liquid for uptake or conditioning; duration, subsequent operation, and resulting effects require separate assertions.",
    "AOM_101128": "Multi-stage thermal processing of animal-derived material that may include separation or stabilisation; drying, grinding, outputs, and effects require separate assertions.",
}
for concept_id, _, definition, *_ in new_specs:
    definition_updates[concept_id] = definition
definition_path = DATA / "approved_definition_enrichments.csv"
definition_rows = [row for row in read(definition_path) if row["concept_id"] not in definition_updates]
for concept_id, definition in definition_updates.items():
    definition_rows.append({
        "concept_id": concept_id,
        "language": "en",
        "definition": definition,
        "definition_method": "process_axis_definition_replacement",
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};{METHOD}",
        "rationale": "Definition separates operation, mechanism, objective, modal benefit, and observed effect.",
    })
write(definition_path, fieldnames(definition_path), definition_rows)

semantic_types = {
    "AOM_100990": "aom:ProcessMechanism",
    "AOM_100991": "aom:ProcessMechanism",
    "AOM_000837": "aom:ProcessMechanism",
    "AOM_000826": "aom:ProcessMechanism",
    "AOM_101129": "aom:ProcessTechnicalObjective",
    "AOM_101130": "aom:ProcessTechnicalObjective",
    "AOM_101131": "aom:ProcessTechnicalObjective",
    "AOM_000842": "aom:ProcessTechnicalObjective",
    "AOM_101069": "aom:ProcessTechnicalObjective",
    "AOM_101084": "aom:ProductionProcess",
    **{concept_id: semantic_class for concept_id, *_, semantic_class in new_specs},
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
        "rationale": "Accepted process-axis class separates this concept from direct processing-method values.",
    })
write(type_path, fieldnames(type_path), type_rows)

facet_path = DATA / "approved_ingredient_facet_concepts.csv"
facet_rows = [
    row for row in read(facet_path)
    if row["concept_id"] not in {"AOM_101069", "AOM_101129", "AOM_101130", "AOM_101131"}
]
facet_by_id = {row["concept_id"]: row for row in facet_rows}
facet_by_id["AOM_101084"].update({
    "facet": "production_process_provenance",
    "target_property": "aom:productionProcessProvenance",
    "value_class": "aom:ProductionProcess",
    "status": "approved",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": ADR,
})
write(facet_path, fieldnames(facet_path), facet_rows)

decomposition_path = DATA / "approved_ingredient_component_decompositions.csv"
decompositions = [row for row in read(decomposition_path) if row["target_concept_id"] != "AOM_101069"]
write(decomposition_path, fieldnames(decomposition_path), decompositions)

hold_path = DATA / "approved_ingredient_component_value_holds.csv"
holds = [row for row in read(hold_path) if row["source_value"] != "Flakes Defatted"]
holds.append({
    "source_value": "Flakes Defatted",
    "target_property": "aom:compositionState",
    "value_class": "aom:CompositionState",
    "binding_action": "hold_ambiguous",
    "status": "approved",
    "reviewer": REVIEWER,
    "review_date": DATE,
    "evidence": ADR,
    "rationale": "Defatted denotes a composition state but does not identify the extraction or separation operation; state vocabulary and material migrations remain held for Cohort D/E review.",
})
write(hold_path, fieldnames(hold_path), holds)

semantic_relation_path = DATA / "approved_semantic_relations.csv"
semantic_relations = [row for row in read(semantic_relation_path) if row["case_id"] != "COLLISION-ENZYME-TREATMENT"]
write(semantic_relation_path, fieldnames(semantic_relation_path), semantic_relations)

for filename in ["approved_feed_material_facets.csv", "approved_hard_tail_feed_material_facets.csv"]:
    path = DATA / filename
    rows = read(path)
    for row in rows:
        if row["target_concept_id"] == "AOM_101084":
            row["target_property"] = "aom:productionProcessProvenance"
            row["rationale"] = "Feed material arises from upstream sugar-processing provenance; direct treatment operation remains unspecified."
            evidence = list(dict.fromkeys(filter(None, row["evidence"].split(";"))))
            if ADR not in evidence:
                evidence.append(ADR)
            row["evidence"] = ";".join(evidence)
            row["reviewer"] = REVIEWER
            row["review_date"] = DATE
    write(path, fieldnames(path), rows)

generated_rows = read(DATA / "approved_generated_feed_material_facets.csv")
assert not [row for row in generated_rows if row["target_concept_id"] == "AOM_101069"]

mechanism_ids = {
    "Biological": "AOM_100990",
    "Chemical": "AOM_100991",
    "Mechanical": "AOM_000837",
    "Thermal": "AOM_000826",
    "Enzymatic or biochemical": "AOM_101163",
}
objective_ids = {
    "Particle-size reduction": "AOM_101129",
    "Component separation or fraction recovery": "AOM_101130",
    "Shaping or agglomeration": "AOM_101131",
    "Moisture reduction": "AOM_000842",
    "Constituent transformation": "AOM_101164",
    "Preservation or stabilisation": "AOM_101165",
    "Component addition or application": "AOM_101166",
    "Moisture addition or conditioning": "AOM_101167",
}
benefit_ids = {
    "Digestibility improvement": "AOM_101169",
    "Nutrient availability improvement": "AOM_101170",
    "Antinutritional-factor reduction": "AOM_101171",
    "Safety improvement": "AOM_101172",
    "Palatability or intake improvement": "AOM_101173",
    "Palatability improvement": "AOM_101173",
    "Preservation or storage-stability improvement": "AOM_101174",
    "Handling or mixing improvement": "AOM_101175",
    "Handling improvement": "AOM_101175",
    "Softening": "AOM_101175",
    "Composition tailoring": "AOM_101176",
    "Process-output recovery": "AOM_101177",
    "Dust reduction": "AOM_101178",
    "Fermentation support": "AOM_101179",
    "Ensiling preparation": "AOM_101179",
    "Process preparation": "AOM_101179",
}
axis_rows = []
for row in review_rows:
    if row["status"] != "approved" or row["review_role"] != "process-operation":
        continue
    process_id = row["concept_id"]
    for mechanism in filter(None, row["recommended_mechanisms"].split(";")):
        if mechanism not in mechanism_ids:
            assert mechanism == "Unspecified at generic level"
            continue
        axis_rows.append((process_id, "aom:processMechanism", mechanism_ids[mechanism], "aom:ProcessMechanism", mechanism))
    for objective in filter(None, row["recommended_technical_objectives"].split(";")):
        if objective not in objective_ids:
            assert objective == "Context-dependent"
            continue
        axis_rows.append((process_id, "aom:technicalProcessObjective", objective_ids[objective], "aom:ProcessTechnicalObjective", objective))
    for benefit in filter(None, row["possible_intended_feed_benefits"].split(";")):
        assert benefit in benefit_ids, benefit
        axis_rows.append((process_id, "aom:maySupportFeedBenefit", benefit_ids[benefit], "aom:FeedBenefit", benefit))

axis_relation_rows = []
for number, (process_id, relation, target_id, target_class, source_term) in enumerate(sorted(set(axis_rows)), start=1):
    axis_relation_rows.append({
        "case_id": f"{PREFIX}REL-{number:03d}",
        "subject_id": process_id,
        "subject_class": "aom:ProcessingMethod",
        "relation_property": relation,
        "object_id": target_id,
        "object_class": target_class,
        "status": "approved",
        "reviewer": REVIEWER,
        "review_date": DATE,
        "evidence": f"{ADR};review/livestock-v35/process_axis_review.csv",
        "rationale": f"Accepted row-level disposition: {source_term}.",
    })
write(DATA / "approved_process_axis_relations.csv", list(axis_relation_rows[0]), axis_relation_rows)

defatting_material_ids = {
    "AOM_001361", "AOM_001362", "AOM_001949", "AOM_001970",
    "AOM_001971", "AOM_002121", "AOM_002122", "AOM_002133",
}
overlap_row = next(row for row in read(REVIEW / "process_axis_overlap_matrix.csv") if row["concept_id"] == "AOM_101069")
assert overlap_row["processing_method_material_count"] == "8"
defatting_hold_rows = [{
    "feed_material_id": material_id,
    "legacy_assertion": "aom:processingMethod AOM_101069",
    "hold_reason": "Defatted states reduced fat content but does not identify extraction, pressing, solvent treatment, or another operation.",
    "required_resolution": "Select evidenced operation and composition state during Cohort D/E review.",
    "owner": REVIEWER,
    "review_date": DATE,
    "status": "held",
    "evidence": ADR,
} for material_id in sorted(defatting_material_ids)]
write(OUTPUT / "defatting_material_migration_holds.csv", list(defatting_hold_rows[0]), defatting_hold_rows)

implementation_rows = []
for row in review_rows:
    if row["status"] == "held":
        implementation_status = "hold"
    elif row["concept_id"] == "AOM_101069":
        implementation_status = "implemented-objective;material-migrations-held"
    elif row["concept_id"] == "AOM_101084":
        implementation_status = "implemented-production-provenance"
    else:
        implementation_status = "implemented"
    implementation_rows.append({
        "concept_id": row["concept_id"],
        "preferred_label": row["preferred_label"],
        "review_status": row["status"],
        "implementation_status": implementation_status,
        "review_role": row["review_role"],
        "mechanisms": row["recommended_mechanisms"],
        "technical_objectives": row["recommended_technical_objectives"],
        "possible_benefits": row["possible_intended_feed_benefits"],
        "decision_record": ADR,
        "method": METHOD,
        "reviewer": REVIEWER,
        "implementation_date": DATE,
        "evidence_ids": row["evidence_ids"],
        "rationale": row["rationale"],
    })
write(OUTPUT / "process_axis_implementation_register.csv", list(implementation_rows[0]), implementation_rows)

summary = {
    "status": "implemented-candidate",
    "decision": ADR,
    "reviewed_rows": len(review_rows),
    "approved_rows": sum(row["status"] == "approved" for row in review_rows),
    "held_rows": sum(row["status"] == "held" for row in review_rows),
    "new_axis_concepts": len(new_specs),
    "new_mechanism_concepts": 1,
    "new_objective_concepts": 4,
    "new_benefit_concepts_including_root": 12,
    "explicit_axis_relations": len(axis_relation_rows),
    "defatting_material_migration_holds": len(defatting_hold_rows),
    "sugar_provenance_migrations": 3,
    "observed_effect_assertions": 0,
    "identifier_frontier": 101179,
    "reviewer": REVIEWER,
    "implementation_date": DATE,
}
(OUTPUT / "process_axis_implementation_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
(OUTPUT / "README.md").write_text(
    "# Livestock v36 process-axis implementation\n\n"
    "Implements accepted [ADR 0047](../../docs/decisions/0047-feed-process-objective-benefit-and-effect-model.md).\n\n"
    "## Contents\n\n"
    "- `process_axis_implementation_register.csv`: every reviewed process disposition and implementation state.\n"
    "- `identity_collision_audit.csv`: global collision result for every allocated or relabelled concept.\n"
    "- `defatting_material_migration_holds.csv`: eight material assertions withheld until operation and composition evidence are reviewed.\n"
    "- `process_axis_implementation_summary.json`: machine-readable implementation counts.\n\n"
    "## Evidence trail\n\n"
    "Claim-level sources remain in `review/livestock-v35/evidence_register.csv`; row-level evidence IDs remain in `review/livestock-v35/process_axis_review.csv`. Implementation method is documented in `docs/methods/feed-process-axis-governance.md`.\n",
    encoding="utf-8",
)

print(json.dumps(summary, indent=2))
