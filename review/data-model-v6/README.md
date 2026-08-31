# ADR 0052 unit-disposition acceptance

Human acceptance record for complete unit-disposition checkpoint in
[`data-model-v5`](../data-model-v5/), under
[ADR 0052](../../docs/decisions/0052-data-model-registry-and-shared-core-contract.md).

## Accepted scope

- all 12 unit-governance decisions accepted as recommended;
- exact 66-row unit recommendation cohort accepted as recommended;
- all 64 unresolved rows and both conflicting `ZMK/ha` rows remain explicit
  holds;
- raw labels and source-row identities remain preserved;
- unit identity, quantity kind, basis, context, currency, and conversion remain
  separate governed assertions.

## Files

- [`policy_decision_approvals.json`](policy_decision_approvals.json): final
  human decisions for `UD-01` through `UD-12`.
- [`cohort_approval.json`](cohort_approval.json): hash-pinned acceptance of
  guided and row-level recommendation artifacts.
- [`evidence_register.json`](evidence_register.json): claim-bounded acceptance
  evidence.
- [`acceptance_summary.json`](acceptance_summary.json): machine-readable status,
  counts, and implementation boundaries.

## Boundary

Acceptance records governance and hold decisions. It does not edit canonical
workbook or source CSV, assign unit or quantity-kind identity, define
conversion, create registry records, regenerate schemas, publish release, or
migrate consumers. Recommendation artifacts remain immutable and are approved
through exact row counts and SHA-256 fingerprints.

Approved spreadsheet artifact runtime remains unavailable. This acceptance pack
authors JSON and Markdown only.

Validate with:

```bash
python3 tests/validate_adr0052_unit_disposition_acceptance.py
```
