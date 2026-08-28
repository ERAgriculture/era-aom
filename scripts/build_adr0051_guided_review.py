#!/usr/bin/env python3
"""Build deterministic ADR 0051 guided-review artifacts."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "review/whole-vocabulary-v1"
OUTPUT = ROOT / "review/whole-vocabulary-v2"


GUIDED_DECISIONS = [
    {
        "review_id": "GV-01",
        "priority": "1",
        "review_topic": "AOM product and module boundary",
        "review_question": "Should AOM remain an umbrella product with core, crop, livestock, and governed mappings rather than livestock or feed shorthand?",
        "recommended_decision": "accept",
        "decision_detail": "Retain AOM as the umbrella product and preserve separately governed core, crop, livestock, and mapping products.",
        "conditions_or_holds": "No concept enters shared core from lexical overlap, convenience, or one-domain use; require reviewed crop-and-livestock identity and scope evidence.",
        "evidence": "../whole-vocabulary-v1/resource_coverage.csv;../../MODULES.md",
    },
    {
        "review_id": "GV-02",
        "priority": "1",
        "review_topic": "Function-first resource routing",
        "review_question": "Should each canonical resource be classified by semantic function before any row migration?",
        "recommended_decision": "accept",
        "decision_detail": "Route domain concepts, schemas, code lists, mappings, catalog metadata, operational resources, and excluded evidence to distinct governed products.",
        "conditions_or_holds": "Approval of a sheet route does not approve row identity, hierarchy, mapping, publication, or one-row-one-concept conversion; revise prac, out, and out_econ from crop-only routing to cross-domain row routing under accepted ADR 0053.",
        "evidence": "../whole-vocabulary-v1/resource_coverage.csv;../../docs/decisions/0053-agricultural-practice-outcome-and-economic-variable-foundation.md",
    },
    {
        "review_id": "GV-03",
        "priority": "1",
        "review_topic": "Data-model and semantic-binding boundary",
        "review_question": "Should field registries, lookup assignments, and units remain data contracts linked to AOM semantics rather than agricultural concept schemes?",
        "recommended_decision": "accept-with-conditions",
        "decision_detail": "Route field, profile, value-set, unit, product-schema, and compatibility contracts through their governed registries with explicit AOM bindings.",
        "conditions_or_holds": "Apply accepted ADR 0052 boundaries; field records and lookup values do not become aom-core concepts by default, and implementation remains separately gated.",
        "evidence": "../data-model-v1/RECOMMENDATIONS.md;https://github.com/ERAgriculture/era-aom/blob/agent/adr0052-acceptance/docs/decisions/0052-data-model-registry-and-shared-core-contract.md",
    },
    {
        "review_id": "GV-04",
        "priority": "1",
        "review_topic": "Supporting livestock workbook resources",
        "review_question": "Should AOM_diets, ani_diet, and ani_process remain supporting assignment, correction, decomposition, or crosswalk evidence rather than sibling public schemes?",
        "recommended_decision": "accept-with-conditions",
        "decision_detail": "Use the three sheets as governed evidence and mappings into stable livestock identities and relationships.",
        "conditions_or_holds": "Preserve source lineage and reviewed corrections; promote any independent identity only through row-level evidence and global collision review.",
        "evidence": "../whole-vocabulary-v1/resource_coverage.csv#ani_diet;../whole-vocabulary-v1/resource_coverage.csv#ani_process;../whole-vocabulary-v1/resource_coverage.csv#AOM_diets",
    },
    {
        "review_id": "GV-05",
        "priority": "2",
        "review_topic": "Migration waves and dependency order",
        "review_question": "Should migration proceed as eight bounded waves while allowing dependency-independent cohorts to run in parallel?",
        "recommended_decision": "accept-with-revision",
        "decision_detail": "Retain eight bounded waves and explicit dependencies; treat wave labels 0 through 7 as identifiers and narrative positions 1 through 8 as ordinals, and revise the practice/outcome wave from crop-only to cross-domain row routing.",
        "conditions_or_holds": "ADR 0049 remains a separate livestock visual-acceptance gate and must not block unrelated data-model, crop, reference, or mapping reviews; no long-running branch combines all waves.",
        "evidence": "../whole-vocabulary-v1/migration_waves.csv",
    },
    {
        "review_id": "GV-06",
        "priority": "2",
        "review_topic": "Whole-vocabulary coverage contract",
        "review_question": "Should every release candidate report disposition and migration state for every canonical resource?",
        "recommended_decision": "accept",
        "decision_detail": "Report canonical-resource denominator, target product, owner, source-row coverage, semantic state, holds, exclusions, and consumer dependencies.",
        "conditions_or_holds": "Source-row counts and deep completion of one module never establish whole-AOM semantic completeness.",
        "evidence": "../whole-vocabulary-v1/coverage_summary.json;../whole-vocabulary-v1/resource_coverage.csv",
    },
    {
        "review_id": "GV-07",
        "priority": "2",
        "review_topic": "Source and identifier continuity",
        "review_question": "Should the canonical workbook remain operational authority until cutover while migration preserves stable identifiers and row provenance?",
        "recommended_decision": "accept",
        "decision_detail": "Preserve source rows, stable identifiers, labels, provenance, lifecycle, and review status while decomposing compound rows through reviewed relationships.",
        "conditions_or_holds": "Never infer one row equals one concept, reuse identity from labels alone, delete published IDs, or hand-edit generated distributions.",
        "evidence": "../../docs/decisions/0051-whole-vocabulary-resource-boundaries-and-migration-sequence.md;https://github.com/ERAgriculture/era-program/blob/main/project-management/decisions/ADR-0007-canonical-vocab-source.md",
    },
    {
        "review_id": "GV-08",
        "priority": "1",
        "review_topic": "Publication, privacy, and exclusion boundaries",
        "review_question": "Should restricted, operational, legacy, scratch, and unresolved-provenance resources remain outside active public schemes?",
        "recommended_decision": "accept-with-holds",
        "decision_detail": "Retain explicit exclusions and provenance while publishing only rights-safe governed derivatives through the correct owner repository.",
        "conditions_or_holds": "Keep site_list on sensitivity review, ssa_feedsdb excluded, and scio - Custom Terms on provenance review; no acceptance implies public release.",
        "evidence": "../whole-vocabulary-v1/resource_coverage.csv#site_list;../whole-vocabulary-v1/resource_coverage.csv#ssa_feedsdb;../whole-vocabulary-v1/resource_coverage.csv#scio-Custom-Terms",
    },
]


def read_csv(name: str) -> list[dict[str, str]]:
    with (SOURCE / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, rows: list[dict[str, str]]) -> None:
    path = OUTPUT / name
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def route_recommendation(row: dict[str, str]) -> tuple[str, str, str]:
    sheet = row["sheet"]
    if sheet in {"prac", "out", "out_econ"}:
        return (
            "revise-to-cross-domain-row-routing",
            "Treat source as a cross-domain registry and route each approved identity to its reviewed module rather than routing the whole sheet to aom-crop.",
            "Apply accepted ADR 0053; retain energy/module and row-level identity holds, and do not implement from sheet name or pilot history.",
        )
    if sheet == "ssa_feedsdb":
        return (
            "retain-confirmed-restricted-exclusion",
            "Keep restricted source values outside public products.",
            "Only rights-safe reviewed assertions with provenance may leave the controlled source.",
        )
    if sheet == "site_list":
        return (
            "hold-publication-review",
            "Retain location registry under sensitivity review.",
            "Do not publish coordinates or approve public disposition before explicit privacy review.",
        )
    if sheet == "scio - Custom Terms":
        return (
            "hold-provenance-review",
            "Retain custom terms as mapping evidence pending provenance and identity review.",
            "Do not mint identities or mappings from labels alone.",
        )
    if row["publication_disposition"] == "exclude":
        return (
            "accept-exclusion-with-retained-provenance",
            "Keep resource outside active public products while preserving governed migration provenance.",
            "Any future promotion requires explicit rights, lifecycle, and semantic review.",
        )
    if sheet in {"ani_diet", "ani_process", "AOM_diets"}:
        return (
            "accept-supporting-evidence-route",
            "Use resource as governed assignment, correction, decomposition, subset, or crosswalk evidence into aom-livestock.",
            "Do not publish as an independent sibling concept scheme.",
        )
    return (
        "accept-proposed-route-with-row-review",
        f"Route resource to {row['target_product']} using {row['recommended_treatment']}.",
        "Route acceptance does not approve row identity, hierarchy, mapping, or publication; preserve stated next action and wave gates.",
    )


def build_routes() -> list[dict[str, str]]:
    routes = []
    for index, source_row in enumerate(read_csv("resource_coverage.csv"), start=1):
        decision, rationale, conditions = route_recommendation(source_row)
        routes.append(
            {
                "route_id": f"RR-{index:02d}",
                **source_row,
                "recommended_decision": decision,
                "decision_rationale": rationale,
                "conditions_or_holds": conditions,
                "recommendation_status": "proposed",
                "human_decision": "",
                "reviewer": "",
                "review_date": "",
                "decision_note": "",
            }
        )
    return routes


def build_evidence() -> list[dict[str, str]]:
    return [
        {
            "evidence_id": "E-ADR0051-COVERAGE",
            "evidence_type": "governance-review",
            "title": "Whole-vocabulary resource coverage",
            "locator": "../whole-vocabulary-v1/resource_coverage.csv",
            "version_or_date": "2026-08-24",
            "supports": "Complete structural routing proposal for all 33 canonical workbook resources.",
            "claim_boundary": "Routing evidence does not approve row identity, hierarchy, mapping, publication, or implementation.",
        },
        {
            "evidence_id": "E-ADR0051-INVENTORY",
            "evidence_type": "canonical-structural-inventory",
            "title": "Canonical workbook sheet inventory",
            "locator": "../../inventory/workbook_sheets.csv",
            "version_or_date": "2026-08-24",
            "supports": "Sheet names, order, columns, and nonblank structural row counts.",
            "claim_boundary": "Structural metadata does not establish semantic type or publication rights.",
        },
        {
            "evidence_id": "E-ADR0051-WAVES",
            "evidence_type": "governance-plan",
            "title": "Eight migration waves",
            "locator": "../whole-vocabulary-v1/migration_waves.csv",
            "version_or_date": "2026-08-24",
            "supports": "Bounded objectives, exit artifacts, and dependencies for waves 0 through 7.",
            "claim_boundary": "Sequence does not authorize implementation or require independent cohorts to wait unnecessarily.",
        },
        {
            "evidence_id": "E-ADR0051-AUTHORITY",
            "evidence_type": "authority-comparison",
            "title": "Resource-model authority comparison",
            "locator": "../whole-vocabulary-v1/authority_comparison.csv",
            "version_or_date": "2026-08-24",
            "supports": "Claim-bounded use of ERA governance, SKOS, CSVW, SHACL, and DCAT.",
            "claim_boundary": "Standards define representation capabilities, not agricultural identity or source approval.",
        },
        {
            "evidence_id": "E-ADR0051-DATA-MODEL",
            "evidence_type": "accepted-governance-decision",
            "title": "ADR 0052 data-model boundary",
            "locator": "https://github.com/ERAgriculture/era-aom/blob/agent/adr0052-acceptance/docs/decisions/0052-data-model-registry-and-shared-core-contract.md",
            "version_or_date": "human acceptance recorded 2026-08-28 in era-aom #108",
            "supports": "Separation of data contracts, semantic bindings, products, and shared-core evidence gates.",
            "claim_boundary": "ADR 0052 does not approve ADR 0051 resource routes by implication.",
        },
        {
            "evidence_id": "E-ADR0051-CROSS-DOMAIN",
            "evidence_type": "accepted-governance-decision",
            "title": "ADR 0053 cross-domain practice and outcome boundary",
            "locator": "../../docs/decisions/0053-agricultural-practice-outcome-and-economic-variable-foundation.md",
            "version_or_date": "accepted 2026-08-28",
            "supports": "prac, out, and out_econ are cross-domain source registries requiring row-level module routing.",
            "claim_boundary": "ADR 0053 acceptance does not approve every row identity, module assignment, hierarchy, or implementation.",
        },
        {
            "evidence_id": "E-ADR0051-GUIDED",
            "evidence_type": "governance-decision-proposal",
            "title": "ADR 0051 guided-review recommendations",
            "locator": "GUIDED_REVIEW_RECOMMENDATIONS.md",
            "version_or_date": "2026-08-28",
            "supports": "Eight policy recommendations and all 33 resource-route recommendations prepared for human review.",
            "claim_boundary": "Recommendations contain blank decision fields and authorize no source, semantic, publication, or migration change.",
        },
    ]


def write_readme() -> None:
    text = """# ADR 0051 guided-review checkpoint

Consolidated recommendation-only checkpoint for human review of
[ADR 0051](../../docs/decisions/0051-whole-vocabulary-resource-boundaries-and-migration-sequence.md).
It refines evidence in [`whole-vocabulary-v1`](../whole-vocabulary-v1/) but does
not approve the ADR or authorize source, semantic, mapping, publication,
migration, release, or canonical-cutover changes.

## Scope

- 8 guided policy decisions;
- 33 resource-route recommendations, preserving every canonical sheet in source
  order;
- 3 stale crop-only routes revised to cross-domain row routing under accepted
  ADR 0053;
- 2 explicit review holds (`site_list` publication and `scio - Custom Terms`
  provenance);
- 1 confirmed restricted exclusion (`ssa_feedsdb`);
- 7 proposed exclusions retaining migration provenance;
- 3 supporting livestock resources routed as evidence or crosswalks rather
  than independent schemes.

## Files

- [`GUIDED_REVIEW_RECOMMENDATIONS.md`](GUIDED_REVIEW_RECOMMENDATIONS.md):
  human-readable decision checklist.
- [`guided_decision_recommendations.csv`](guided_decision_recommendations.csv):
  eight proposed policy decisions with blank human-decision fields.
- [`resource_routing_recommendations.csv`](resource_routing_recommendations.csv):
  complete recommendation for all 33 resources.
- [`evidence_register.csv`](evidence_register.csv): claim-bounded evidence.
- [`acceptance_summary.json`](acceptance_summary.json): machine-readable counts
  and authorization boundaries.

## Rebuild

```bash
python3 scripts/build_adr0051_guided_review.py
python3 tests/validate_adr0051_guided_review.py
```

Generated recommendations must not be edited to record approval. Human
decisions belong in a later acceptance artifact.
"""
    (OUTPUT / "README.md").write_text(text, encoding="utf-8")


def write_recommendations(routes: list[dict[str, str]]) -> None:
    lines = [
        "# ADR 0051 guided-review recommendations",
        "",
        "Status: recommendation-only; human decision pending.",
        "",
        "## Guided decisions",
        "",
    ]
    for decision in GUIDED_DECISIONS:
        lines.extend(
            [
                f"### {decision['review_id']} — {decision['review_topic']}",
                "",
                f"**Recommendation:** `{decision['recommended_decision']}`",
                "",
                decision["decision_detail"],
                "",
                f"**Condition or hold:** {decision['conditions_or_holds']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Resource-route summary",
            "",
            "| Recommended decision | Resources |",
            "|---|---:|",
        ]
    )
    route_counts = Counter(row["recommended_decision"] for row in routes)
    for decision, count in sorted(route_counts.items()):
        lines.append(f"| `{decision}` | {count} |")
    lines.extend(
        [
            "",
            "All 33 row-level recommendations are in",
            "[`resource_routing_recommendations.csv`](resource_routing_recommendations.csv).",
            "",
            "## Decision boundary",
            "",
            "Accepting this recommendation cohort would approve resource-routing policy",
            "and stated holds only. It would not approve row identities, hierarchy,",
            "mappings, source edits, publication, implementation, release, consumer",
            "migration, or canonical cutover.",
            "",
        ]
    )
    (OUTPUT / "GUIDED_REVIEW_RECOMMENDATIONS.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    guided = [
        {
            **row,
            "recommendation_status": "proposed",
            "human_decision": "",
            "reviewer": "",
            "review_date": "",
            "decision_note": "",
        }
        for row in GUIDED_DECISIONS
    ]
    routes = build_routes()
    evidence = build_evidence()
    write_csv("guided_decision_recommendations.csv", guided)
    write_csv("resource_routing_recommendations.csv", routes)
    write_csv("evidence_register.csv", evidence)
    write_readme()
    write_recommendations(routes)
    summary = {
        "adr": "0051",
        "adr_status": "Proposed",
        "review_version": "whole-vocabulary-v2",
        "status": "recommendation-only",
        "guided_decision_count": len(guided),
        "guided_decision_recommendations": dict(sorted(Counter(row["recommended_decision"] for row in guided).items())),
        "resource_route_count": len(routes),
        "resource_route_recommendations": dict(sorted(Counter(row["recommended_decision"] for row in routes).items())),
        "publication_dispositions": dict(sorted(Counter(row["publication_disposition"] for row in routes).items())),
        "explicit_route_holds": 2,
        "confirmed_restricted_exclusions": 1,
        "human_decision_recorded": False,
        "resource_routes_approved": False,
        "source_workbook_modified": False,
        "semantic_implementation_authorized": False,
        "public_identifiers_allocated": False,
        "publication_authorized": False,
        "release_authorized": False,
        "consumer_migration_authorized": False,
        "canonical_cutover_authorized": False,
    }
    (OUTPUT / "acceptance_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
