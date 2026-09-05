# ADR 0052 product-contract review

Recommendation-only checkpoint for published agronomy and livestock schemas,
the `eragri` package data snapshot, and package dictionary. It preserves all
138 product fields and all 44 known consumer differences for human review.

## Boundaries

- Source repositories were read only at pinned clean commits.
- Package dictionary rows are candidate evidence, never automatic mappings.
- No field description, logical type, derivation, unit, basis, values, alias,
  source correction, schema change, package change, release, or migration is
  approved.
- Unknown cases remain explicit holds.
- No spreadsheet artifact was authored; approved spreadsheet runtime remained
  unavailable, and the existing source CSV was read only and hash pinned.

## Files

- `METHOD.md` — source, classification, and decision method.
- `GUIDED_PRODUCT_CONTRACT_RECOMMENDATIONS.md` — human review sequence.
- `source_snapshot.json` — hash-pinned schema and package evidence.
- `product_field_recommendations.json` — complete 138-field cohort.
- `consumer_difference_recommendations.json` — complete 44-difference cohort.
- `guided_decision_recommendations.json` — twelve proposed policy decisions.
- `authority_comparison.json` — authority support and limitations.
- `evidence_register.json` — claim-level evidence boundaries.
- `disposition_summary.json` — machine-readable counts and non-actions.

## Human checkpoint

P. Steward accepted `PC-01` through `PC-12` and exact 138-field and
44-difference artifacts as recorded on 2026-09-01. Durable record:
[`data-model-v8`](../data-model-v8/README.md). Acceptance authorizes no source,
schema, package, release, or migration change.
