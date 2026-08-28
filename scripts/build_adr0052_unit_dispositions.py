#!/usr/bin/env python3
"""Build recommendation-only ADR 0052 unit-disposition review artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "review/data-model-v1/unit_mapping_audit.csv"
OUTPUT = ROOT / "review/data-model-v5"
SOURCE_SHA256 = "29fbec8fc3fb2b2153532bcbfdaea8f32b1918b3b397e445f33aa1c192063b8c"

MISSING_SENTINELS = {"N/A", "NA"}
CURRENCY_EXPRESSIONS = {"3k/NGN/individual", "per USD", "USD/tonne"}
AMBIGUOUS_SYMBOLS = {"BW", "DM", "ETA/ha", "ETH/ha", "FCM", "in", "mg C / ha", "ms/cm"}
SOURCE_FRAGMENTS = {"of", "the", "truly"}
BASIS_OR_QUALIFIERS = {
    "body",
    "concentrate",
    "excreta",
    "feed",
    "forage",
    "metabolic",
    "milk",
    "organic",
    "weight",
    "wool",
    "Wool",
}

CLASS_DETAILS = {
    "hold-basis-or-qualifier-model": {
        "classification": "basis-or-qualifier-not-unit",
        "required_evidence": "Identify measured quantity and model material, population, state, or basis separately from unit.",
        "authority_route": "ERA source context; QUDT quantity kind only after measured property is known.",
    },
    "hold-currency-and-basis-review": {
        "classification": "currency-or-economic-ratio",
        "required_evidence": "Confirm currency code, numerator meaning, denominator or basis, geography, and effective date.",
        "authority_route": "ISO 4217 currency identity plus ERA economic context; QUDT or UCUM only for physical denominator syntax.",
    },
    "hold-currency-effective-context": {
        "classification": "conflicting-currency-correction",
        "required_evidence": "Resolve source record date and intended pre-2013 ZMK or post-rebasing ZMW identity before correction.",
        "authority_route": "ISO 4217 historical/current codes and Bank of Zambia rebasing guidance.",
    },
    "hold-missing-value-source-correction": {
        "classification": "missing-value-sentinel",
        "required_evidence": "Confirm sentinel use and replace with governed null through approved source correction.",
        "authority_route": "ERA source governance; no unit authority mapping.",
    },
    "hold-non-unit-source-correction": {
        "classification": "non-unit-or-misplaced-value",
        "required_evidence": "Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value.",
        "authority_route": "ERA source owner first; external unit authority only after measured quantity is established.",
    },
    "hold-ratio-decomposition": {
        "classification": "incomplete-or-contextual-ratio",
        "required_evidence": "Identify numerator unit, denominator unit or basis, population, time, area, and scaling factor explicitly.",
        "authority_route": "ERA source context, then UCUM expression validation and QUDT quantity-kind/unit review.",
    },
    "hold-source-fragment-correction": {
        "classification": "source-text-fragment",
        "required_evidence": "Recover complete source value or confirm removal; fragment cannot identify a unit.",
        "authority_route": "ERA source governance; no unit authority mapping.",
    },
    "hold-symbol-case-and-context-review": {
        "classification": "ambiguous-symbol-case-or-abbreviation",
        "required_evidence": "Confirm expanded meaning, exact case, measured quantity, and contextual basis from source field evidence.",
        "authority_route": "UCUM case-sensitive syntax and QUDT quantity kind after source meaning is known.",
    },
}

GUIDED_DECISIONS = [
    {
        "review_id": "UD-01",
        "priority": 1,
        "review_topic": "Raw unit preservation",
        "recommended_decision": "retain-raw-unit-and-source-row",
        "decision_detail": "Preserve every raw unit label and source-row identity independently from reviewed canonical unit assertions.",
        "conditions_or_holds": "Normalization, correction, and mapping never overwrite source evidence.",
    },
    {
        "review_id": "UD-02",
        "priority": 1,
        "review_topic": "Complete held cohort",
        "recommended_decision": "accept-recommendation-only-hold",
        "decision_detail": "Retain all 64 unresolved rows and both conflicting ZMK/ha rows as holds pending source context.",
        "conditions_or_holds": "No row receives canonical unit identity, quantity kind, or conversion from label evidence alone.",
    },
    {
        "review_id": "UD-03",
        "priority": 1,
        "review_topic": "Missing-value sentinels",
        "recommended_decision": "hold-missing-sentinel-source-correction",
        "decision_detail": "Treat N/A and NA as candidate missing-value sentinels rather than units.",
        "conditions_or_holds": "Normalize to null only through approved source correction after confirming source intent.",
    },
    {
        "review_id": "UD-04",
        "priority": 1,
        "review_topic": "Non-unit values and fragments",
        "recommended_decision": "hold-non-unit-and-fragment-source-correction",
        "decision_detail": "Hold apparent outcomes, statuses, values, and text fragments for field-level source correction.",
        "conditions_or_holds": "Lexical classification is triage, not approval to delete, move, or replace a source value.",
    },
    {
        "review_id": "UD-05",
        "priority": 1,
        "review_topic": "Bases and qualifiers",
        "recommended_decision": "separate-basis-and-qualifier",
        "decision_detail": "Represent material, population, state, and reporting basis independently from physical unit identity.",
        "conditions_or_holds": "Terms such as DM, BW, feed, milk, and metabolic require expanded source meaning before modeling.",
    },
    {
        "review_id": "UD-06",
        "priority": 1,
        "review_topic": "Ratio decomposition",
        "recommended_decision": "decompose-ratio-before-unit-mapping",
        "decision_detail": "Resolve numerator, denominator, scaling, population, area, and time before assigning compound-unit identity.",
        "conditions_or_holds": "A slash-containing label does not prove a valid or complete unit expression.",
    },
    {
        "review_id": "UD-07",
        "priority": 1,
        "review_topic": "Symbol case and abbreviation",
        "recommended_decision": "require-case-sensitive-symbol-review",
        "decision_detail": "Review exact case and expanded meaning before interpreting ambiguous symbols or abbreviations.",
        "conditions_or_holds": "Do not silently reinterpret mg as Mg, ms as mS, in as inch, or abbreviations as quantities.",
    },
    {
        "review_id": "UD-08",
        "priority": 1,
        "review_topic": "Quantity kind before unit URI",
        "recommended_decision": "require-quantity-kind-before-unit-uri",
        "decision_detail": "Establish measured property and quantity kind before selecting a QUDT or other canonical unit identifier.",
        "conditions_or_holds": "Same label can occur under different quantities, bases, or contexts.",
    },
    {
        "review_id": "UD-09",
        "priority": 2,
        "review_topic": "UCUM expression validation",
        "recommended_decision": "use-ucum-validation-not-identity-inference",
        "decision_detail": "Use UCUM to validate approved unit expressions and semantics, not to infer source meaning from malformed labels.",
        "conditions_or_holds": "Case-sensitive codes, annotations, and compound expressions require explicit reviewed construction.",
    },
    {
        "review_id": "UD-10",
        "priority": 1,
        "review_topic": "Currency and effective context",
        "recommended_decision": "require-currency-code-and-effective-context",
        "decision_detail": "Model currency code, denominator or basis, geography, and effective date separately.",
        "conditions_or_holds": "Never replace ZMK with ZMW without source date and rebasing context.",
    },
    {
        "review_id": "UD-11",
        "priority": 1,
        "review_topic": "Conversion semantics",
        "recommended_decision": "require-explicit-conversion-record",
        "decision_detail": "Store conversion factor, offset, formula, direction, basis, applicability, authority, and evidence separately.",
        "conditions_or_holds": "Label normalization alone authorizes no numeric conversion.",
    },
    {
        "review_id": "UD-12",
        "priority": 1,
        "review_topic": "Implementation boundary",
        "recommended_decision": "retain-unit-implementation-gates",
        "decision_detail": "Keep recommendation, human acceptance, source correction, registry implementation, release, and migration as separate gates.",
        "conditions_or_holds": "This cohort changes no workbook, schema, unit registry, binding, distribution, or consumer.",
    },
]

AUTHORITIES = [
    {
        "authority": "QUDT 3.1.10",
        "url": "https://www.qudt.org/doc/2026/01/DOC_SCHEMA-QUDT.html",
        "supports": "Separate quantity, quantity kind, unit, dimension, value, and conversion semantics.",
        "limitation": "Does not establish what an ERA source label means without measured-property and source context.",
    },
    {
        "authority": "UCUM 2.2",
        "url": "https://ucum.org/ucum",
        "supports": "Case-sensitive unit atoms and formal multiplication, division, exponentiation, scalar, and annotation syntax.",
        "limitation": "Expression validity does not repair malformed, incomplete, misplaced, or context-free source labels.",
    },
    {
        "authority": "ISO 4217",
        "url": "https://www.iso.org/iso-4217-currency-codes.html",
        "supports": "Current and historical alphabetic and numeric currency-code identity.",
        "limitation": "Currency code does not provide denominator, price basis, geography, effective date, or exchange conversion.",
    },
    {
        "authority": "Bank of Zambia 2012 rebasing guidance",
        "url": "https://www.boz.zm/17-2012.pdf",
        "supports": "ZMW became the new alphabetic code from 2013-01-01 and ZMK ceased current use after rebasing.",
        "limitation": "Source observation date and intended monetary basis are still required for each ERA row.",
    },
    {
        "authority": "ERA ADR 0007 canonical workbook policy",
        "url": "../../docs/decisions/0007-canonical-vocabulary-source.md",
        "supports": "Canonical workbook remains source authority and source changes require governed edits.",
        "limitation": "Canonical authority does not make incomplete unit labels semantically sufficient.",
    },
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name: str, value: object) -> None:
    (OUTPUT / name).write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def classify(row: dict[str, str]) -> str:
    raw_unit = row["raw_unit"]
    if row["mapping_status"] == "conflicting-canonical-label":
        return "hold-currency-effective-context"
    if raw_unit in MISSING_SENTINELS:
        return "hold-missing-value-source-correction"
    if raw_unit in CURRENCY_EXPRESSIONS:
        return "hold-currency-and-basis-review"
    if raw_unit in AMBIGUOUS_SYMBOLS:
        return "hold-symbol-case-and-context-review"
    if "/" in raw_unit:
        return "hold-ratio-decomposition"
    if raw_unit in SOURCE_FRAGMENTS:
        return "hold-source-fragment-correction"
    if raw_unit in BASIS_OR_QUALIFIERS:
        return "hold-basis-or-qualifier-model"
    return "hold-non-unit-source-correction"


def load_cases() -> list[dict[str, object]]:
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle))
    held = [
        row
        for row in source_rows
        if row["mapping_status"] in {"unresolved", "conflicting-canonical-label"}
    ]
    cases = []
    for row in held:
        disposition = classify(row)
        detail = CLASS_DETAILS[disposition]
        cases.append(
            {
                "case_id": f"UNIT-{int(row['source_row']):04d}",
                "source_row": int(row["source_row"]),
                "raw_unit": row["raw_unit"],
                "canonical_label": row["canonical_label"],
                "raw_occurrences": int(row["raw_occurrences"]),
                "distinct_nonblank_corrections": int(row["distinct_nonblank_corrections"]),
                "source_mapping_status": row["mapping_status"],
                "lexical_classification": detail["classification"],
                "recommended_disposition": disposition,
                "required_evidence": detail["required_evidence"],
                "authority_route": detail["authority_route"],
                "canonical_unit_uri": "",
                "quantity_kind_uri": "",
                "conversion_rule": "",
                "recommendation_status": "proposed",
                "human_decision": "",
                "reviewer": "",
                "review_date": "",
                "decision_note": "",
            }
        )
    return sorted(cases, key=lambda row: int(row["source_row"]))


def write_readme() -> None:
    text = """# ADR 0052 unit-disposition checkpoint

Recommendation-only review of all 64 unresolved unit rows and both conflicting
`ZMK/ha` rows identified by
[ADR 0052](../../docs/decisions/0052-data-model-registry-and-shared-core-contract.md).

## Scope

- 12 guided unit-governance decisions;
- exact row-level recommendations for all 66 held source rows;
- eight conservative lexical triage classes;
- QUDT, UCUM, ISO 4217, Bank of Zambia, and ERA authority comparison;
- claim-level evidence and deterministic validation.

## Boundary

Every row remains held. Lexical triage identifies evidence needed next; it does
not establish unit identity, quantity kind, conversion, source correction, or
field context. No canonical workbook, stable key, unit registry, schema,
binding, distribution, release, or consumer changes.

Approved spreadsheet artifact runtime was unavailable, so this checkpoint
authors no CSV or workbook. Machine records use deterministic JSON; human review
uses Markdown. Source CSV remains read-only and hash-pinned.

## Files

- [`GUIDED_UNIT_RECOMMENDATIONS.md`](GUIDED_UNIT_RECOMMENDATIONS.md)
- [`unit_disposition_recommendations.json`](unit_disposition_recommendations.json)
- [`guided_decision_recommendations.json`](guided_decision_recommendations.json)
- [`authority_comparison.json`](authority_comparison.json)
- [`evidence_register.json`](evidence_register.json)
- [`disposition_summary.json`](disposition_summary.json)
- [`METHOD.md`](METHOD.md)

## Rebuild

```bash
python3 scripts/build_adr0052_unit_dispositions.py
python3 tests/validate_adr0052_unit_dispositions.py
```
"""
    (OUTPUT / "README.md").write_text(text, encoding="utf-8")


def write_method() -> None:
    text = f"""# ADR 0052 unit-disposition method

## Inputs

- `review/data-model-v1/unit_mapping_audit.csv`
- source SHA-256: `{SOURCE_SHA256}`
- only rows with `unresolved` or `conflicting-canonical-label` status

## Method

1. Preserve source row, raw label, canonical correction, occurrence count, and
   source audit status unchanged.
2. Select all 64 unresolved rows and both conflicting rows; fail validation if
   source membership changes.
3. Assign one exact lexical triage class from explicit label sets and slash
   structure. Triage determines required evidence, not semantic identity.
4. Leave canonical unit URI, quantity-kind URI, conversion rule, and human
   decision blank for every case.
5. Compare QUDT, UCUM, ISO 4217, Bank of Zambia guidance, and ERA source
   authority with explicit limitations.
6. Generate JSON and Markdown byte-deterministically; validate counts,
   fingerprints, classifications, blank decisions, and implementation gates.

## Interpretation boundary

Current repository evidence does not connect these unit-harmonization rows to
specific outcome fields or observations. Terms such as `DM`, `BW`, `FCM`,
`in`, `mg C / ha`, and `ms/cm` therefore remain ambiguous. Slash syntax does
not prove a complete ratio. Case variants do not prove equivalence. Apparent
sentinels or fragments require governed source correction rather than silent
normalization.
"""
    (OUTPUT / "METHOD.md").write_text(text, encoding="utf-8")


def write_guided(cases: list[dict[str, object]]) -> None:
    counts = Counter(str(case["recommended_disposition"]) for case in cases)
    lines = [
        "# ADR 0052 unit-disposition recommendations",
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
                str(decision["decision_detail"]),
                "",
                f"**Condition or hold:** {decision['conditions_or_holds']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Cohort summary",
            "",
            "| Recommended disposition | Cases |",
            "|---|---:|",
        ]
    )
    for disposition, count in sorted(counts.items()):
        lines.append(f"| `{disposition}` | {count} |")
    lines.extend(["", "## Complete row cohort", ""])
    for disposition in sorted(counts):
        lines.extend(
            [
                f"### `{disposition}`",
                "",
                "| Case | Raw unit | Current correction | Required evidence |",
                "|---|---|---|---|",
            ]
        )
        for case in cases:
            if case["recommended_disposition"] != disposition:
                continue
            correction = str(case["canonical_label"]) or "—"
            lines.append(
                f"| `{case['case_id']}` | `{case['raw_unit']}` | `{correction}` | "
                f"{case['required_evidence']} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Decision boundary",
            "",
            "Accepting this recommendation cohort would accept review policy and",
            "retain all 66 rows as explicit holds. It would not correct source, assign",
            "unit or quantity-kind identity, define conversion, create registry records,",
            "regenerate schemas, publish releases, or migrate consumers.",
            "",
        ]
    )
    (OUTPUT / "GUIDED_UNIT_RECOMMENDATIONS.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def main() -> None:
    assert sha256(SOURCE) == SOURCE_SHA256, "Unit audit source fingerprint changed"
    OUTPUT.mkdir(parents=True, exist_ok=True)
    cases = load_cases()
    counts = Counter(str(case["recommended_disposition"]) for case in cases)
    evidence = [
        {
            "evidence_id": "E-ADR0052-UNIT-SOURCE",
            "evidence_type": "source-audit",
            "title": "ADR 0052 unit mapping audit",
            "locator": "../data-model-v1/unit_mapping_audit.csv",
            "version_or_date": "2026-08-24",
            "supports": "64 unresolved rows and two conflicting ZMK/ha correction rows.",
            "claim_boundary": "Audit provides labels and correction status but no outcome-field context, unit URI, quantity kind, or conversion evidence.",
        },
        {
            "evidence_id": "E-ADR0052-UNIT-QUDT",
            "evidence_type": "unit-authority",
            "title": "QUDT 3.1.10 schema",
            "locator": AUTHORITIES[0]["url"],
            "version_or_date": "2026-01-15",
            "supports": AUTHORITIES[0]["supports"],
            "claim_boundary": AUTHORITIES[0]["limitation"],
        },
        {
            "evidence_id": "E-ADR0052-UNIT-UCUM",
            "evidence_type": "unit-code-authority",
            "title": "UCUM specification 2.2",
            "locator": AUTHORITIES[1]["url"],
            "version_or_date": "2024-06-17",
            "supports": AUTHORITIES[1]["supports"],
            "claim_boundary": AUTHORITIES[1]["limitation"],
        },
        {
            "evidence_id": "E-ADR0052-UNIT-CURRENCY",
            "evidence_type": "currency-authority",
            "title": "ISO 4217 currency codes",
            "locator": AUTHORITIES[2]["url"],
            "version_or_date": "accessed 2026-08-29",
            "supports": AUTHORITIES[2]["supports"],
            "claim_boundary": AUTHORITIES[2]["limitation"],
        },
        {
            "evidence_id": "E-ADR0052-UNIT-ZAMBIA",
            "evidence_type": "currency-transition-authority",
            "title": "Bank of Zambia rebasing implementation guidance",
            "locator": AUTHORITIES[3]["url"],
            "version_or_date": "2012",
            "supports": AUTHORITIES[3]["supports"],
            "claim_boundary": AUTHORITIES[3]["limitation"],
        },
        {
            "evidence_id": "E-ADR0052-UNIT-BOUNDARY",
            "evidence_type": "implementation-boundary",
            "title": "Recommendation-only unit disposition",
            "locator": "disposition_summary.json",
            "version_or_date": "2026-08-29",
            "supports": "All 66 cases remain holds with blank canonical identity, conversion, and human-decision fields.",
            "claim_boundary": "No workbook, registry, schema, semantic binding, release, or consumer is modified.",
        },
    ]
    summary = {
        "adr": "0052",
        "adr_status": "Accepted",
        "review_version": "data-model-v5",
        "review_date": "2026-08-29",
        "status": "recommendation-only",
        "source_audit_sha256": SOURCE_SHA256,
        "guided_decision_count": len(GUIDED_DECISIONS),
        "held_case_count": len(cases),
        "unresolved_case_count": sum(
            case["source_mapping_status"] == "unresolved" for case in cases
        ),
        "conflicting_case_count": sum(
            case["source_mapping_status"] == "conflicting-canonical-label"
            for case in cases
        ),
        "disposition_counts": dict(sorted(counts.items())),
        "human_decision_recorded": False,
        "canonical_unit_mappings_created": False,
        "quantity_kind_mappings_created": False,
        "conversion_rules_created": False,
        "source_workbook_modified": False,
        "schema_regeneration_authorized": False,
        "release_authorized": False,
        "consumer_migration_authorized": False,
        "spreadsheet_artifact_authored": False,
    }
    write_json("unit_disposition_recommendations.json", cases)
    write_json("guided_decision_recommendations.json", GUIDED_DECISIONS)
    write_json("authority_comparison.json", AUTHORITIES)
    write_json("evidence_register.json", evidence)
    write_json("disposition_summary.json", summary)
    write_readme()
    write_method()
    write_guided(cases)


if __name__ == "__main__":
    main()
