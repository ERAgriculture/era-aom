# ADR 0052 unit-disposition checkpoint

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
