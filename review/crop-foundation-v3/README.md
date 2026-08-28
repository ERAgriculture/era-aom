# ADR 0053 acceptance record

Human acceptance record for
[ADR 0053](../../docs/decisions/0053-agricultural-practice-outcome-and-economic-variable-foundation.md),
based on complete guided recommendations in
[`crop-foundation-v2`](../crop-foundation-v2/).

## Accepted scope

- all 12 guided decisions accepted with recorded revisions, conditions, and
  holds;
- seven economic source-correction proposals approved;
- `Nutrient/Soil management` retained on source-clarification hold;
- four AgrO `skos:closeMatch` decisions approved for later implementation;
- Monoculture and Controlled Grazing mappings retained on hold;
- 20 exact-label identity mappings rejected while preserving facet evidence;
- all 14 energy and cookstove rows retained on module hold.

## Files

- [`guided_decision_approvals.csv`](guided_decision_approvals.csv): final human
  decision for `GR-01` through `GR-12`.
- [`source_correction_approvals.csv`](source_correction_approvals.csv): final
  decision for all eight proposed economic source corrections.
- [`evidence_register.csv`](evidence_register.csv): claim-bounded acceptance
  evidence.
- [`acceptance_summary.json`](acceptance_summary.json): machine-readable status,
  counts, and implementation boundaries.

## Boundary

ADR acceptance authorizes approved canonical source corrections and preserves
mapping decisions for later implementation. It does not modify workbook cells,
allocate identifiers, emit mappings, alter hierarchy, assign energy module,
change semantic distributions, publish release, or migrate consumers.

Validate with:

```bash
python3 tests/validate_adr0053_acceptance.py
```
