#!/usr/bin/env python3
"""Build ADR 0053 guided-review recommendation artifacts."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "review/crop-foundation-v1"
OUTPUT = ROOT / "review/crop-foundation-v2"


def read_csv(name: str) -> list[dict[str, str]]:
    with (SOURCE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with (OUTPUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


GUIDED_DECISIONS = {
    "GR-01": {
        "recommended_decision": "accept",
        "decision_detail": "Govern prac, out, and out_econ as cross-domain source registries and route approved identities row by row.",
        "conditions_or_holds": "Energy and cookstove rows remain on module hold.",
    },
    "GR-02": {
        "recommended_decision": "accept-with-revision",
        "decision_detail": "Govern source codes as lexical identifiers and preserve displayed notation without automatic numeric formatting.",
        "conditions_or_holds": "Replace the question's inaccurate reference to eight corrections with the audited 58 pilot notation mutations and 65 placeholder economic identifiers.",
    },
    "GR-03": {
        "recommended_decision": "accept-with-revision",
        "decision_detail": "Model theme, pillar, subpillar, and indicator navigation as collections by default.",
        "conditions_or_holds": "Use scoped collection labels where a collection and member property or practice otherwise share a preferred label; require evidence for every semantic broader relation.",
    },
    "GR-04": {
        "recommended_decision": "accept-with-conditions",
        "decision_detail": "Give stable AOM identifiers priority only after compatible identity, entity type, lifecycle, module, label, and definition are confirmed.",
        "conditions_or_holds": "Exact labels, definitions, source codes, legacy mappings, and hierarchy remain evidence signals rather than automatic equivalence.",
    },
    "GR-05": {
        "recommended_decision": "accept",
        "decision_detail": "Separate practice identity, practice application, baseline or condition, and experimental treatment, comparator, or control role.",
        "conditions_or_holds": "Do not encode study role or unspecified state in preferred practice identity.",
    },
    "GR-06": {
        "recommended_decision": "accept",
        "decision_detail": "Model reviewed outcomes as sosa:Property specifications with explicit feature, procedure, quantity, unit or basis, and derivation where applicable.",
        "conditions_or_holds": "Trait-method-scale and QUDT bindings require domain and claim-level evidence.",
    },
    "GR-07": {
        "recommended_decision": "accept-policy-with-holds",
        "decision_detail": "Convert 43 editorial nodes to collections, collapse 13 duplicate group-and-leaf nodes, and hold 53 candidate practice groups for extensional review.",
        "conditions_or_holds": "No generated practice parent is promoted as a concept solely from worksheet structure.",
    },
    "GR-08": {
        "recommended_decision": "revise-and-decompose",
        "decision_detail": "Replace same-label distinct-context minting with explicit practice, material, trait or variety, and missing-value decomposition.",
        "conditions_or_holds": "Urea and ash rows are application practices linked to materials; heat tolerance is crop-variety use plus trait; Unspecified is field-scoped missing information, not a public global identity.",
    },
    "GR-09": {
        "recommended_decision": "accept-source-correction-gate",
        "decision_detail": "Correct or explicitly hold economic definition, label, placeholder identifier, and contextual-category defects before identifier allocation.",
        "conditions_or_holds": "Correction proposals require source-owner approval and canonical workbook update before regeneration.",
    },
    "GR-10": {
        "recommended_decision": "accept",
        "decision_detail": "Decompose economic measure, cost or benefit category, object, activity, actor, transaction, time, currency, denominator, allocation basis, and valuation method.",
        "conditions_or_holds": "Fixed or variable classification remains contextual unless evidence proves it intrinsic.",
    },
    "GR-11": {
        "recommended_decision": "accept-individual-review",
        "decision_detail": "Review every external candidate by definition, scope, and entity type; retain four strong close-match candidates and one conditional close-match candidate.",
        "conditions_or_holds": "No external mapping is approved. One practice candidate remains definition-overlap hold; 20 exact-label candidates are non-identity facet or relation evidence.",
    },
    "GR-12": {
        "recommended_decision": "hold-module-boundary",
        "decision_detail": "Keep all 14 energy and cookstove rows in an unassigned agricultural or household energy boundary.",
        "conditions_or_holds": "Do not force them into core, crop, or livestock and do not mint a new module until a later architecture decision establishes sufficient scope.",
    },
}


ISSUE_ACTIONS = {
    "literal-na-sentinel": ("generator-fix", "Normalize semantic value to null while retaining raw cell provenance.", "proposed", "no"),
    "placeholder-identifier": ("source-correction", "Replace placeholder only through governed identifier allocation after row approval.", "held", "yes"),
    "pilot-notation-mutation": ("generator-fix", "Preserve governed lexical notation; prohibit automatic .0 suffixes.", "proposed", "no"),
    "deprecated-source-record": ("lifecycle-hold", "Retain provenance but exclude from active identity promotion.", "held", "no"),
    "indicator-label-code-collision": ("navigation-model-fix", "Use collection membership and scoped collection labels instead of duplicate public identity.", "proposed", "no"),
    "non-boolean-not-percentage": ("source-correction", "Resolve field value against approved boolean or controlled-value contract.", "held", "yes"),
    "duplicate-subpractice-code": ("source-correction", "Resolve duplicate lexical code before identifier or mapping allocation.", "held", "yes"),
    "definition-content-defect": ("source-correction", "Approve corrected definition before identifier allocation.", "held", "yes"),
    "missing-definition": ("source-correction", "Supply approved definition or retain lifecycle hold.", "held", "yes"),
    "duplicate-contextual-variable-label": ("semantic-decomposition", "Use scoped measure identity plus explicit accounting context.", "held", "yes"),
    "unknown-lifecycle-status": ("source-owner-decision", "Resolve lifecycle value before promotion.", "held", "yes"),
    "invalid-sign-code": ("source-correction", "Normalize only after source owner confirms intended controlled value.", "held", "yes"),
}


SAME_LABEL_DECOMPOSITIONS = [
    {
        "source_id": "prac:b23",
        "source_label": "Urea",
        "source_meaning": "Field application of urea.",
        "conflicting_aom_ids": "AOM_001749",
        "recommended_identity": "Urea application",
        "recommended_model": "agricultural practice linked to governed urea material or chemical identity",
        "public_identity_action": "do-not-mint-another-urea-material",
        "status": "proposed",
    },
    {
        "source_id": "prac:b74",
        "source_label": "Ash",
        "source_meaning": "Field application of plant ash.",
        "conflicting_aom_ids": "AOM_000226",
        "recommended_identity": "Plant-ash application",
        "recommended_model": "agricultural practice linked to governed plant-ash material identity",
        "public_identity_action": "do-not-mint-another-ash-material",
        "status": "proposed",
    },
    {
        "source_id": "prac:b5",
        "source_label": "Heat Tolerance",
        "source_meaning": "Use of an improved crop variety bred for heat resistance.",
        "conflicting_aom_ids": "AOM_000156",
        "recommended_identity": "Use of heat-tolerant crop variety",
        "recommended_model": "agricultural practice linked to crop-variety and heat-tolerance trait facets",
        "public_identity_action": "do-not-reuse-animal-breed-practice",
        "status": "proposed",
    },
    {
        "source_id": "prac:h55.2",
        "source_label": "Unspecified",
        "source_meaning": "Breed practice not specified as improved or unimproved.",
        "conflicting_aom_ids": "AOM_001507;AOM_003050;AOM_003051;AOM_003052",
        "recommended_identity": "",
        "recommended_model": "field-scoped missing or unspecified value with raw provenance",
        "public_identity_action": "do-not-mint-global-unspecified-concept",
        "status": "proposed",
    },
]


ECONOMIC_CORRECTIONS = [
    {
        "source_row": "3",
        "source_id": "out_econ:row:3",
        "category": "Fixed Costs",
        "current_label": "Equipment",
        "current_definition": "Fixed cost of machinery or equipment. This can be depreciation over time or the initial cost of purchasing.",
        "proposed_label": "Equipment acquisition or depreciation cost",
        "proposed_definition": "Cost attributed to acquiring owned machinery or equipment, or depreciation allocated to it over a stated period and basis.",
        "action": "source-owner-approval-required",
    },
    {
        "source_row": "5",
        "source_id": "out_econ:row:5",
        "category": "Fixed Costs",
        "current_label": "Loans",
        "current_definition": "Cost of loans, e.g., interest payments.",
        "proposed_label": "Loan interest cost",
        "proposed_definition": "Interest and other explicitly included financing charges on borrowed capital over a stated period; principal repayment is excluded unless separately specified.",
        "action": "source-owner-approval-required",
    },
    {
        "source_row": "25",
        "source_id": "out_econ:row:25",
        "category": "Variable Costs",
        "current_label": "Equipment",
        "current_definition": "Cost of renting or maintainance of machinery or equipment",
        "proposed_label": "Equipment rental or maintenance cost",
        "proposed_definition": "Cost of renting machinery or equipment, or maintaining it, over a stated period and allocation basis.",
        "action": "source-owner-approval-required",
    },
    {
        "source_row": "32",
        "source_id": "out_econ:row:32",
        "category": "Variable Costs",
        "current_label": "Family Labor Cost (Female)",
        "current_definition": "Family labor costs for men are considered. Family labor comes from the farming household and is often unpaid in smallholder systems. If costs are disaggregated by gende, please use the gendered categories instead of this one.",
        "proposed_label": "Female family labour cost",
        "proposed_definition": "Reported or imputed cost of labour supplied by female members of the farming household; record the valuation method when labour is unpaid.",
        "action": "source-owner-approval-required",
    },
    {
        "source_row": "33",
        "source_id": "out_econ:row:33",
        "category": "Variable Costs",
        "current_label": "Hired Labor Cost",
        "current_definition": "Family labor costs for women are considered. Family labor comes from the farming household and is often unpaid in smallholder systems. If costs are disaggregated by gende, please use the gendered categories instead of this one.",
        "proposed_label": "Hired labour cost",
        "proposed_definition": "Cost of labour supplied by workers outside the farming household over a stated period and allocation basis.",
        "action": "source-owner-approval-required",
    },
    {
        "source_row": "47",
        "source_id": "out_econ:row:47",
        "category": "Private Benefits",
        "current_label": "Nutrient/Soil management",
        "current_definition": "E.g. compost or manure",
        "proposed_label": "",
        "proposed_definition": "",
        "action": "hold-for-source-owner-clarification-of-measure-versus-input",
    },
    {
        "source_row": "49",
        "source_id": "out_econ:row:49",
        "category": "Societal Benefits",
        "current_label": "Monetary Societal Benefits",
        "current_definition": "",
        "proposed_label": "Monetary societal benefit value",
        "proposed_definition": "Monetary value assigned to benefits accruing beyond the private operator or household, with beneficiary scope, valuation method, currency, time, and denominator basis stated.",
        "action": "source-owner-approval-required",
    },
    {
        "source_row": "50",
        "source_id": "out_econ:row:50",
        "category": "Societal Benefits",
        "current_label": "Non-monetary Societal Benefits",
        "current_definition": "",
        "proposed_label": "Non-monetized societal benefit",
        "proposed_definition": "Benefit accruing beyond the private operator or household that is reported without monetary valuation; state beneficiary scope, measured property, unit or scale, and time basis.",
        "action": "source-owner-approval-required",
    },
]


ENERGY_HOLDS = {
    "prac:c1": ("practice-candidate", "Biogas production or use requires explicit process and system scope."),
    "prac:c4": ("deprecated-material-or-practice-conflict", "Deprecated source describes biodigester slurry rather than generic biofertilizer identity."),
    "prac:c3": ("change-or-switching-practice", "Switching requires source and target energy systems."),
    "prac:c2": ("practice-candidate", "Improved cookstove use or adoption requires device and application scope."),
    "prac:c5": ("change-or-switching-practice", "Switching requires source and target cookstove systems."),
    "prac:h14": ("condition-or-comparator", "Unimproved technology may be baseline state rather than practice identity."),
    "prac:h15": ("condition-or-comparator", "Conventional feedstock is material and baseline context, not necessarily practice identity."),
    "prac:h16": ("deprecated-source-descriptor", "Deprecated row lacks definition and names a model descriptor."),
    "prac:h26": ("condition-or-comparator", "Conventional source is baseline context requiring explicit energy-source identity."),
    "out:323": ("outcome-property", "Fuel use requires fuel, device, procedure, quantity, unit, and denominator basis."),
    "out:320": ("derived-outcome-property", "Fuel savings requires baseline, comparison, derivation, quantity, unit, and denominator basis."),
    "out:321": ("outcome-property", "Cooking time requires activity, procedure, time unit, and denominator basis."),
    "out:322": ("derived-outcome-property", "Specific fuel use requires numerator, denominator, procedure, and unit."),
    "out:324": ("outcome-property", "Cookstove emissions require pollutant, device, procedure, quantity, unit, and denominator basis."),
}


STRONG_CLOSE_MATCHES = {
    ("prac:a11", "AGRO_00000580"),
    ("prac:a12", "AGRO_00000581"),
    ("prac:d16", "AGRO_00000430"),
    ("prac:b54", "AGRO_00000588"),
}


def build_guided_decisions() -> list[dict[str, str]]:
    rows = []
    for source_row in read_csv("guided_review.csv"):
        recommendation = GUIDED_DECISIONS[source_row["review_id"]]
        rows.append(
            {
                "review_id": source_row["review_id"],
                "priority": source_row["priority"],
                "review_topic": source_row["review_topic"],
                "original_question": source_row["review_question"],
                **recommendation,
                "evidence": source_row["primary_evidence"],
                "recommendation_status": "proposed",
                "human_decision": "",
                "reviewer": "",
                "review_date": "",
                "decision_note": "",
            }
        )
    return rows


def build_hierarchy_dispositions() -> list[dict[str, str]]:
    rows = []
    for source_row in read_csv("hierarchy_node_review.csv"):
        role = source_row["reviewed_role"]
        scoped_label = ""
        if role == "editorial-navigation":
            disposition = "collection-with-scoped-label" if source_row["same_label_child_ids"] else "collection"
            if source_row["same_label_child_ids"]:
                suffix = "outcomes" if source_row["scheme_id"] == "era:scheme:outcome" else "practice group"
                scoped_label = f'{source_row["preferred_label"]} {suffix}'
            rationale = "Reporting navigation does not establish inherent semantic broader meaning."
        elif role == "duplicate-group-and-leaf":
            disposition = "collapse-generated-parent-into-reviewed-leaf"
            rationale = "Generated parent and source leaf share identity signal; preserve one reviewed concept and reattach approved children."
        else:
            disposition = "hold-for-extensional-concept-versus-collection-review"
            rationale = "Worksheet grouping alone cannot decide whether members are narrower kinds of one practice."
        rows.append(
            {
                "concept_id": source_row["concept_id"],
                "scheme_id": source_row["scheme_id"],
                "concept_type": source_row["concept_type"],
                "preferred_label": source_row["preferred_label"],
                "source_notation": source_row["source_notation"],
                "parent_id": source_row["parent_id"],
                "direct_child_count": source_row["direct_child_count"],
                "same_label_child_ids": source_row["same_label_child_ids"],
                "reviewed_role": role,
                "guided_disposition": disposition,
                "proposed_scoped_collection_label": scoped_label,
                "target_leaf_id": source_row["same_label_child_ids"] if role == "duplicate-group-and-leaf" else "",
                "recommendation_status": "held" if role == "candidate-practice-group" else "proposed",
                "evidence_ids": source_row["evidence_ids"],
                "rationale": rationale,
            }
        )
    return rows


def build_source_actions() -> list[dict[str, str]]:
    rows = []
    for source_row in read_csv("source_quality_issues.csv"):
        action_class, guided_action, action_status, source_edit_required = ISSUE_ACTIONS[source_row["issue_type"]]
        if source_row["source_id"] == "prac:h16":
            action_class = "lifecycle-hold"
            guided_action = "Retain deprecated source provenance; do not activate or mint an identity from missing definition."
            source_edit_required = "no"
        rows.append(
            {
                **source_row,
                "guided_action_class": action_class,
                "guided_action": guided_action,
                "guided_status": action_status,
                "source_edit_required": source_edit_required,
                "approval_status": "pending",
            }
        )
    return rows


def mapping_disposition(source_row: dict[str, str]) -> tuple[str, str, str]:
    key = (source_row["source_id"], source_row["authority_id"])
    if key in STRONG_CLOSE_MATCHES:
        return (
            "candidate-close-match",
            "skos:closeMatch-after-human-approval",
            "Definitions and entity types substantially align; exact equivalence remains unapproved.",
        )
    if key == ("prac:h2", "AGRO_00000481"):
        return (
            "conditional-close-match",
            "skos:closeMatch-after-comparator-role-split-and-human-approval",
            "Monoculture identity aligns, but source also encodes temporal experimental-control context.",
        )
    if key == ("prac:d19", "AGRO_00000434"):
        return (
            "hold-definition-overlap",
            "none",
            "Source controlled-grazing definition overlaps rotational grazing and is broader than authority intensive rotational scope.",
        )
    if source_row["source_sheet"] == "out":
        reason = "Source row is an observed property; authority term denotes process or material entity."
    elif source_row["source_sheet"] == "out_econ":
        reason = "Source row is an economic measure; authority term denotes cost object, input, material, or activity."
    elif source_row["source_id"] == "prac:a8.1":
        reason = "Source row denotes incorporation or management system; authority term denotes scattered trees as landscape entities."
    elif source_row["source_id"] == "prac:c4":
        reason = "Deprecated source describes biodigester slurry use; authority term denotes biofertilizer material."
    elif source_row["source_id"] in {"prac:b68", "prac:b58"}:
        reason = "Source row denotes construction or use practice; authority term denotes physical structure or excavation."
    else:
        reason = "Source row denotes material application practice; authority term denotes input material or chemical identity."
    return ("reject-identity-use-as-facet-evidence", "none", reason)


def build_mapping_dispositions() -> list[dict[str, str]]:
    rows = []
    for source_row in read_csv("authority_label_candidates.csv"):
        disposition, relation, rationale = mapping_disposition(source_row)
        rows.append(
            {
                **source_row,
                "guided_disposition": disposition,
                "candidate_relation": relation,
                "guided_status": "held" if disposition == "hold-definition-overlap" else "proposed",
                "approval_status": "pending",
                "guided_rationale": rationale,
            }
        )
    return rows


def build_energy_holds() -> list[dict[str, str]]:
    source_rows = {row["source_id"]: row for row in read_csv("source_row_dispositions.csv")}
    rows = []
    for source_id, (resource_shape, rationale) in ENERGY_HOLDS.items():
        source_row = source_rows[source_id]
        rows.append(
            {
                "source_sheet": source_row["source_sheet"],
                "source_row": source_row["source_row"],
                "source_id": source_id,
                "source_label": source_row["source_label"],
                "source_status": source_row["source_status"],
                "resource_shape": resource_shape,
                "module_disposition": "unassigned-agricultural-or-household-energy",
                "recommendation_status": "held",
                "approval_status": "pending",
                "rationale": rationale,
            }
        )
    return rows


def build_evidence_register() -> list[dict[str, str]]:
    rows = read_csv("evidence_register.csv")
    rows.extend(
        [
            {
                "evidence_id": "E-ADR0053-GUIDED",
                "evidence_type": "governance-decision-proposal",
                "title": "ADR 0053 guided-review recommendation",
                "locator": "../../docs/decisions/0053-agricultural-practice-outcome-and-economic-variable-foundation.md",
                "version_or_date": "2026-08-28",
                "sha256": "",
                "supports": "Twelve consolidated guided-decision recommendations and implementation gates.",
                "claim_boundary": "Proposed ADR and recommendation artifacts do not record human approval or authorize implementation.",
            },
            {
                "evidence_id": "E-AGRO-DEFINITION-REVIEW",
                "evidence_type": "official-ontology-snapshot-review",
                "title": "AgrO definition and entity-type review",
                "locator": "https://github.com/AgriculturalSemantics/agro/blob/master/agro.owl",
                "version_or_date": "snapshot reviewed 2026-08-28",
                "sha256": "d861a6fbf09e01fffcf4312dee29f20a15a1a4a65b2a7012e50c02f65a495b55",
                "supports": "Definition and entity-type comparison for 26 exact-label candidates.",
                "claim_boundary": "Snapshot comparison supports candidate dispositions only; no mapping relation is approved.",
            },
        ]
    )
    return rows


def main() -> None:
    guided_rows = build_guided_decisions()
    hierarchy_rows = build_hierarchy_dispositions()
    source_action_rows = build_source_actions()
    mapping_rows = build_mapping_dispositions()
    energy_rows = build_energy_holds()
    evidence_rows = build_evidence_register()

    write_csv("guided_decision_recommendations.csv", list(guided_rows[0]), guided_rows)
    write_csv("hierarchy_guided_dispositions.csv", list(hierarchy_rows[0]), hierarchy_rows)
    write_csv("same_label_decomposition_review.csv", list(SAME_LABEL_DECOMPOSITIONS[0]), SAME_LABEL_DECOMPOSITIONS)
    write_csv("external_mapping_dispositions.csv", list(mapping_rows[0]), mapping_rows)
    write_csv("source_issue_action_plan.csv", list(source_action_rows[0]), source_action_rows)
    write_csv("economic_source_correction_proposals.csv", list(ECONOMIC_CORRECTIONS[0]), ECONOMIC_CORRECTIONS)
    write_csv("energy_module_holds.csv", list(energy_rows[0]), energy_rows)
    write_csv("evidence_register.csv", list(evidence_rows[0]), evidence_rows)

    summary = {
        "review_version": "crop-foundation-v2",
        "adr": "0053",
        "status": "recommendation-only",
        "adr_status": "Proposed",
        "implementation_authorized": False,
        "source_workbook_modified": False,
        "public_identifiers_allocated": False,
        "external_mappings_approved": False,
        "module_assignments_approved": False,
        "guided_decision_count": len(guided_rows),
        "guided_decision_recommendations": dict(Counter(row["recommended_decision"] for row in guided_rows)),
        "hierarchy_node_count": len(hierarchy_rows),
        "hierarchy_dispositions": dict(Counter(row["guided_disposition"] for row in hierarchy_rows)),
        "same_label_decomposition_count": len(SAME_LABEL_DECOMPOSITIONS),
        "source_issue_count": len(source_action_rows),
        "source_issue_actions": dict(Counter(row["guided_action_class"] for row in source_action_rows)),
        "external_candidate_count": len(mapping_rows),
        "external_candidate_dispositions": dict(Counter(row["guided_disposition"] for row in mapping_rows)),
        "economic_correction_proposal_count": len(ECONOMIC_CORRECTIONS),
        "energy_module_hold_count": len(energy_rows),
        "evidence_record_count": len(evidence_rows),
    }
    (OUTPUT / "acceptance_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
