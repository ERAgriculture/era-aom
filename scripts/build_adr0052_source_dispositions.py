#!/usr/bin/env python3
"""Build deterministic ADR 0052 field-key and lookup disposition recommendations."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "review/data-model-v1"
OUTPUT = ROOT / "review/data-model-v3"


GUIDED_DECISIONS = [
    {
        "review_id": "SD-01",
        "priority": "1",
        "review_topic": "Non-overlapping duplicate logical fields",
        "recommended_decision": "accept-profile-consolidation",
        "decision_detail": "Represent 13 duplicate table-field keys with disjoint extraction-round coverage as one stable logical field plus round-specific profiles.",
        "conditions_or_holds": "Preserve every canonical source row and round-specific property; allocate stable keys only during separately approved registry implementation.",
        "evidence": "field_key_disposition_recommendations.csv",
    },
    {
        "review_id": "SD-02",
        "priority": "1",
        "review_topic": "Overlapping duplicate logical fields",
        "recommended_decision": "hold-source-row-comparison",
        "decision_detail": "Hold three duplicate keys whose source rows overlap in the same extraction round.",
        "conditions_or_holds": "Compare full row properties and source intent before merge, retirement, or profile assignment; overlap prevents automatic consolidation.",
        "evidence": "field_key_disposition_recommendations.csv#overlapping-rounds",
    },
    {
        "review_id": "SD-03",
        "priority": "1",
        "review_topic": "Irrigation date-key conflict",
        "recommended_decision": "hold-source-key-correction",
        "decision_detail": "Hold duplicate Irrig.Out.I.Date.Start rows because one carries Date End display identity in the same round.",
        "conditions_or_holds": "Source owner must confirm whether row 406 is an end-date key; never rename from display label alone.",
        "evidence": "../data-model-v1/field_key_issues.csv#FIELD-DUP-014",
    },
    {
        "review_id": "SD-04",
        "priority": "2",
        "review_topic": "Blank field rows",
        "recommended_decision": "hold-metadata-or-removal-classification",
        "decision_detail": "Hold three rows without field identity until classified as table metadata, intentional separator, or removable source artifact.",
        "conditions_or_holds": "Do not mint blank field identities or silently drop rows without reviewed source disposition.",
        "evidence": "field_key_disposition_recommendations.csv#blank-field-row",
    },
    {
        "review_id": "SD-05",
        "priority": "1",
        "review_topic": "Missing table identity",
        "recommended_decision": "hold-table-assignment-or-retirement",
        "decision_detail": "Hold source row 480 because populated field Time has no table identity and current generation drops it.",
        "conditions_or_holds": "Assign table only from source evidence or explicitly retire row; field label alone cannot establish table membership.",
        "evidence": "../data-model-v1/field_key_issues.csv#FIELD-TABLE-480",
    },
    {
        "review_id": "SD-06",
        "priority": "1",
        "review_topic": "Lookup pairs without registry candidates",
        "recommended_decision": "hold-add-field-or-retire-lookup",
        "decision_detail": "Hold 39 lookup pairs with no candidate field key in the current registry.",
        "conditions_or_holds": "For each pair, add or restore a governed field definition from source evidence, or retire the lookup pair; never create a fuzzy binding.",
        "evidence": "lookup_binding_disposition_recommendations.csv#no-candidate",
    },
    {
        "review_id": "SD-07",
        "priority": "1",
        "review_topic": "Lookup table-key candidates",
        "recommended_decision": "hold-table-key-realignment-review",
        "decision_detail": "Hold Fert.Method.M.Source and Res.Out.M.Process despite one same-field candidate each in Res.Method.",
        "conditions_or_holds": "Confirm source table identity, value scope, and consumer use before key correction; candidate similarity is not approval.",
        "evidence": "lookup_binding_disposition_recommendations.csv#candidate-key",
    },
    {
        "review_id": "SD-08",
        "priority": "1",
        "review_topic": "Stable field-to-value-set relationship",
        "recommended_decision": "accept-explicit-binding-policy",
        "decision_detail": "Bind every approved value set to a stable field key and stable value-set key rather than table/field label coincidence.",
        "conditions_or_holds": "No unmatched pair is approved by this policy; all 41 remain held until source disposition.",
        "evidence": "../../docs/decisions/0052-data-model-registry-and-shared-core-contract.md",
    },
]


def read_csv(name: str) -> list[dict[str, str]]:
    with (SOURCE / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, rows: list[dict[str, str]]) -> None:
    with (OUTPUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def active_round_sets(value: str) -> list[set[str]]:
    sets = []
    for source_entry in value.split(" | "):
        _, rounds = source_entry.split(":", 1)
        sets.append(set(rounds.split("+")) if rounds else set())
    return sets


def rounds_overlap(value: str) -> bool:
    sets = active_round_sets(value)
    return bool(sets[0].intersection(*sets[1:]))


def build_field_dispositions() -> list[dict[str, str]]:
    rows = []
    for source_row in read_csv("field_key_issues.csv"):
        issue_type = source_row["issue_type"]
        if issue_type == "duplicate-logical-field-key":
            if rounds_overlap(source_row["active_rounds"]):
                disposition = "hold-overlapping-duplicate-source-rows"
                source_edit_required = "yes"
                basis = "Duplicate key has overlapping extraction-round coverage; profile consolidation is not sufficient evidence."
            else:
                disposition = "consolidate-logical-field-with-round-profiles"
                source_edit_required = "no"
                basis = "Duplicate key has disjoint extraction-round coverage and can retain source rows through one logical field plus profiles."
        elif issue_type == "duplicate-key-label-conflict":
            disposition = "hold-source-key-correction"
            source_edit_required = "yes"
            basis = "Same-round duplicate key carries conflicting display identities."
        elif issue_type == "blank-field-row":
            disposition = "hold-classify-metadata-or-remove"
            source_edit_required = "yes"
            basis = "Row has no field identity and cannot enter field registry."
        elif issue_type == "missing-table-key":
            disposition = "hold-assign-table-or-retire"
            source_edit_required = "yes"
            basis = "Field lacks table identity and cannot receive a stable logical key."
        else:
            raise AssertionError(f"Unhandled field issue type: {issue_type}")
        rows.append(
            {
                **source_row,
                "guided_disposition": disposition,
                "source_edit_required": source_edit_required,
                "decision_basis": basis,
                "recommendation_status": "proposed",
                "human_decision": "",
                "reviewer": "",
                "review_date": "",
                "decision_note": "",
            }
        )
    return rows


def build_lookup_dispositions() -> list[dict[str, str]]:
    rows = []
    for source_row in read_csv("lookup_binding_audit.csv"):
        if source_row["exact_match"] != "no":
            continue
        if source_row["candidate_registry_keys"]:
            disposition = "hold-table-key-realignment-review"
            basis = "One same-field candidate exists under another table; source identity and value scope require review."
        else:
            disposition = "hold-add-field-or-retire-lookup"
            basis = "No candidate field key exists; source must add or restore field identity, or retire lookup pair."
        rows.append(
            {
                **source_row,
                "guided_disposition": disposition,
                "source_edit_required": "yes",
                "decision_basis": basis,
                "recommendation_status": "held",
                "human_decision": "",
                "reviewer": "",
                "review_date": "",
                "decision_note": "",
            }
        )
    return rows


def build_evidence() -> list[dict[str, str]]:
    return [
        {
            "evidence_id": "E-SD-FIELD-AUDIT",
            "evidence_type": "source-structure-audit",
            "title": "Field-key issue register",
            "locator": "../data-model-v1/field_key_issues.csv",
            "version_or_date": "2026-08-24",
            "supports": "Twenty-one complete field-key issue records with source rows, active rounds, evidence, and proposed handling.",
            "claim_boundary": "Audit does not expose full canonical source rows or authorize correction.",
        },
        {
            "evidence_id": "E-SD-LOOKUP-AUDIT",
            "evidence_type": "binding-audit",
            "title": "Lookup binding audit",
            "locator": "../data-model-v1/lookup_binding_audit.csv",
            "version_or_date": "2026-08-24",
            "supports": "All 83 field-scoped lookup pairs, including 41 unmatched pairs and candidate field keys.",
            "claim_boundary": "Candidate keys are review aids and never fuzzy or approved bindings.",
        },
        {
            "evidence_id": "E-SD-ADR0052",
            "evidence_type": "accepted-governance-decision",
            "title": "ADR 0052 data-model contract",
            "locator": "../../docs/decisions/0052-data-model-registry-and-shared-core-contract.md",
            "version_or_date": "accepted 2026-08-28",
            "supports": "Stable logical fields, round profiles, explicit value-set bindings, and source-disposition gates.",
            "claim_boundary": "ADR acceptance does not decide individual source rows or allocate keys.",
        },
        {
            "evidence_id": "E-SD-CANONICAL-AUTHORITY",
            "evidence_type": "governance-decision",
            "title": "ERA ADR 0007 canonical source authority",
            "locator": "https://github.com/ERAgriculture/era-program/blob/main/project-management/decisions/ADR-0007-canonical-vocab-source.md",
            "version_or_date": "accepted 2026-07-07",
            "supports": "Canonical workbook remains source authority until governed cutover.",
            "claim_boundary": "Authority does not make labels sufficient evidence for inferred corrections.",
        },
        {
            "evidence_id": "E-SD-TOOLING-BLOCK",
            "evidence_type": "implementation-boundary",
            "title": "Canonical workbook unchanged",
            "locator": "disposition_summary.json",
            "version_or_date": "2026-08-28",
            "supports": "Recommendation cohort records no canonical workbook modification or source correction.",
            "claim_boundary": "Required approved spreadsheet artifact tooling was unavailable; recommendations must not be treated as applied edits.",
        },
    ]


def write_readme() -> None:
    text = """# ADR 0052 source-disposition checkpoint

Recommendation-only human-review checkpoint for 21 field-key issues and 41
unmatched lookup pairs identified by
[ADR 0052](../../docs/decisions/0052-data-model-registry-and-shared-core-contract.md).

## Scope

- 8 guided disposition decisions;
- 13 non-overlapping duplicate field keys recommended for one logical identity
  plus round-specific profiles;
- 3 overlapping duplicate field keys held for full source-row comparison;
- 3 blank-field rows held for metadata/removal classification;
- 1 irrigation date-key conflict held for source-owner correction;
- 1 missing-table row held for table assignment or retirement;
- 39 lookup pairs with no field candidate held for governed field addition or
  lookup retirement;
- 2 lookup pairs with one table-key candidate held for source identity review.

## Boundary

No human decision is recorded. No canonical workbook cell, stable key, field,
profile, value set, binding, schema, release, or consumer is changed. All 41
unmatched lookup pairs remain held; no fuzzy binding is proposed.

Human acceptance of this exact recommendation cohort is recorded in
[`data-model-v4`](../data-model-v4/README.md). This recommendation checkpoint
remains immutable and records no implementation.

## Rebuild

```bash
python3 scripts/build_adr0052_source_dispositions.py
python3 tests/validate_adr0052_source_dispositions.py
```
"""
    (OUTPUT / "README.md").write_text(text, encoding="utf-8")


def write_recommendations(
    field_rows: list[dict[str, str]], lookup_rows: list[dict[str, str]]
) -> None:
    lines = [
        "# ADR 0052 source-disposition recommendations",
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
            "## Disposition summary",
            "",
            "| Cohort | Disposition | Cases |",
            "|---|---|---:|",
        ]
    )
    for disposition, count in sorted(Counter(row["guided_disposition"] for row in field_rows).items()):
        lines.append(f"| Field keys | `{disposition}` | {count} |")
    for disposition, count in sorted(Counter(row["guided_disposition"] for row in lookup_rows).items()):
        lines.append(f"| Lookup pairs | `{disposition}` | {count} |")
    lines.extend(
        [
            "",
            "Complete row-level recommendations:",
            "",
            "- [`field_key_disposition_recommendations.csv`](field_key_disposition_recommendations.csv)",
            "- [`lookup_binding_disposition_recommendations.csv`](lookup_binding_disposition_recommendations.csv)",
            "",
            "## Decision boundary",
            "",
            "Accepting this cohort would approve 13 profile consolidations and retain",
            "49 source-edit cases as holds. It would not edit source, allocate keys,",
            "create bindings, regenerate schemas, publish releases, or migrate consumers.",
            "",
        ]
    )
    (OUTPUT / "GUIDED_DISPOSITION_RECOMMENDATIONS.md").write_text("\n".join(lines), encoding="utf-8")


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
    field_rows = build_field_dispositions()
    lookup_rows = build_lookup_dispositions()
    evidence = build_evidence()
    write_csv("guided_decision_recommendations.csv", guided)
    write_csv("field_key_disposition_recommendations.csv", field_rows)
    write_csv("lookup_binding_disposition_recommendations.csv", lookup_rows)
    write_csv("evidence_register.csv", evidence)
    write_readme()
    write_recommendations(field_rows, lookup_rows)
    summary = {
        "adr": "0052",
        "review_version": "data-model-v3",
        "status": "recommendation-only",
        "adr_status": "Accepted",
        "guided_decision_count": len(guided),
        "field_issue_count": len(field_rows),
        "field_dispositions": dict(sorted(Counter(row["guided_disposition"] for row in field_rows).items())),
        "lookup_issue_count": len(lookup_rows),
        "lookup_dispositions": dict(sorted(Counter(row["guided_disposition"] for row in lookup_rows).items())),
        "profile_consolidation_recommendations": sum(row["guided_disposition"] == "consolidate-logical-field-with-round-profiles" for row in field_rows),
        "field_holds": sum(row["guided_disposition"].startswith("hold-") for row in field_rows),
        "lookup_holds": len(lookup_rows),
        "source_edit_holds": sum(row["source_edit_required"] == "yes" for row in field_rows + lookup_rows),
        "human_decision_recorded": False,
        "source_workbook_modified": False,
        "stable_keys_allocated": False,
        "bindings_created": False,
        "schema_regeneration_authorized": False,
        "release_authorized": False,
        "consumer_migration_authorized": False,
    }
    (OUTPUT / "disposition_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
