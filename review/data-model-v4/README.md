# ADR 0052 source-disposition acceptance

Human acceptance record for the complete source-disposition checkpoint in
[`data-model-v3`](../data-model-v3/), under
[ADR 0052](../../docs/decisions/0052-data-model-registry-and-shared-core-contract.md).

## Accepted scope

- all eight source-disposition policy decisions accepted as recommended;
- 13 non-overlapping duplicate field keys approved for one stable logical
  field plus round-specific profiles during later governed implementation;
- eight field cases retained as explicit source holds;
- all 41 unmatched lookup pairs retained as explicit source holds;
- stable field-to-value-set binding policy accepted without approving any
  current unmatched pair.

## Files

- [`policy_decision_approvals.csv`](policy_decision_approvals.csv): final human
  decisions for `SD-01` through `SD-08`.
- [`cohort_approvals.csv`](cohort_approvals.csv): hash-pinned acceptance of all
  21 field-key and 41 lookup-binding recommendations.
- [`evidence_register.csv`](evidence_register.csv): claim-bounded acceptance
  evidence.
- [`acceptance_summary.json`](acceptance_summary.json): machine-readable status,
  counts, and implementation boundaries.

## Retained holds

- three overlapping duplicate field keys require full source-row comparison;
- three blank-field rows require metadata, separator, or removal classification;
- one irrigation date-key conflict requires source-owner correction;
- one missing-table row requires table assignment or explicit retirement;
- 39 lookup pairs require governed field addition or lookup retirement;
- two lookup pairs require table-key realignment review.

## Boundary

Acceptance records policy and row-disposition decisions. It does not edit the
canonical workbook, allocate stable keys, create profiles or bindings,
regenerate schemas, publish a release, or migrate consumers. Recommendation
rows remain immutable and are approved through exact row counts and SHA-256
fingerprints.

Validate with:

```bash
python3 tests/validate_adr0052_source_disposition_acceptance.py
```
