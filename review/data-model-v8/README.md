# ADR 0052 product-contract acceptance

Human acceptance record for complete product-contract recommendation checkpoint
in [`data-model-v7`](../data-model-v7/), under
[ADR 0052](../../docs/decisions/0052-data-model-registry-and-shared-core-contract.md).

## Accepted scope

- all 12 product-contract governance recommendations accepted as recorded;
- exact 138-field product recommendation cohort accepted as recorded;
- exact 44-row consumer-difference cohort accepted as recorded;
- one shared 138-field logical set and separate ordered agronomy and livestock
  product profiles accepted as design direction;
- complete field documentation or explicit reviewed deferral accepted as gate;
- release-pinned package and documentation compatibility accepted as gate;
- every field and consumer-difference disposition remains an evidence hold
  pending field-level authoring, provenance, compatibility, or retirement work.

## Files

- [`policy_decision_approvals.json`](policy_decision_approvals.json): final
  human decisions for `PC-01` through `PC-12`.
- [`cohort_approval.json`](cohort_approval.json): hash-pinned acceptance of
  guided, 138-field, and 44-difference recommendation artifacts.
- [`evidence_register.json`](evidence_register.json): claim-bounded acceptance
  evidence.
- [`acceptance_summary.json`](acceptance_summary.json): machine-readable status,
  counts, holds, and implementation boundaries.

## Boundary

Acceptance records governance, product-profile direction, completeness gates,
and hold dispositions. It does not author field descriptions, logical types,
derivations, units or bases, controlled values, aliases, mappings, source
corrections, schema changes, package changes, documentation changes, release,
or consumer migration. Recommendation artifacts remain immutable and are
approved through exact row counts and SHA-256 fingerprints.

Approved spreadsheet artifact runtime remains unavailable. This acceptance pack
authors JSON and Markdown only.

Validate with:

```bash
python tests/validate_adr0052_product_contract_acceptance.py
```
