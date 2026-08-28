# ADR 0052 source-disposition checkpoint

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

## Rebuild

```bash
python3 scripts/build_adr0052_source_dispositions.py
python3 tests/validate_adr0052_source_dispositions.py
```
