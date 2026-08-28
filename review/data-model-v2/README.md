# ADR 0052 acceptance record

Human acceptance record for
[ADR 0052](../../docs/decisions/0052-data-model-registry-and-shared-core-contract.md),
based on the recommendation-only review in
[`data-model-v1`](../data-model-v1/).

## Accepted scope

- separate governed registries for tables, fields, profiles, value sets, units,
  semantic bindings, product schemas, and compatibility records;
- stable table and field identities with extraction-round variation represented
  through profiles;
- explicit field-to-value-set relationships rather than label joins;
- separate extraction and analytical-product schemas;
- release-pinned package compatibility and end-to-end closure gates;
- shared-core promotion only from crop-and-livestock evidence;
- CSVW or Frictionless descriptors for tabular contracts and SHACL for RDF
  validation;
- raw unit preservation with separately reviewed identity, quantity,
  conversion, basis, context, and evidence.

## Retained holds

- 21 field-key issues require source disposition;
- 41 unmatched lookup pairs require reviewed binding or retirement;
- 64 unresolved unit rows and two conflicting `ZMK/ha` rows require review;
- every public 138-column product schema requires complete documentation or an
  explicit reviewed deferral;
- no shared-core promotion proceeds without crop-and-livestock evidence.

## Files

- [`decision_approvals.csv`](decision_approvals.csv): final human decision for
  `DM-01` through `DM-12`.
- [`evidence_register.csv`](evidence_register.csv): claim-bounded acceptance
  evidence.
- [`acceptance_summary.json`](acceptance_summary.json): machine-readable status,
  counts, and implementation boundaries.

## Boundary

ADR acceptance approves architecture and source-disposition work. It does not
edit the canonical workbook, allocate stable keys, regenerate schemas, promote
shared-core resources, mutate release `v2026.1`, publish a new release, migrate
consumers, or close programme issues. Dependent ADR 0051 remains Proposed and
must be accepted separately before its resource-routing policy is treated as
approved.

Validate with:

```bash
python3 tests/validate_adr0052_acceptance.py
```
