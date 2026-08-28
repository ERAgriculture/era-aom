# ADR 0053 guided-review checkpoint

Consolidated recommendation-only checkpoint for human review of
[ADR 0053](../../docs/decisions/0053-agricultural-practice-outcome-and-economic-variable-foundation.md).
It refines the evidence in [`crop-foundation-v1`](../crop-foundation-v1/) but
does not approve the ADR or authorize source, ontology, mapping, module, or
release changes.

## Scope

- 12 guided decisions;
- 109 generated hierarchy-node dispositions;
- 4 same-label source decompositions;
- 265 source-quality issue actions;
- 26 external mapping dispositions;
- 8 economic source-correction proposals;
- 14 energy module holds.

## Files

- [`GUIDED_REVIEW_RECOMMENDATIONS.md`](GUIDED_REVIEW_RECOMMENDATIONS.md):
  human-readable recommendation pack.
- [`guided_decision_recommendations.csv`](guided_decision_recommendations.csv):
  proposed decision for each guided-review question, with blank human-decision
  fields.
- [`hierarchy_guided_dispositions.csv`](hierarchy_guided_dispositions.csv):
  complete disposition for all 109 generated nodes.
- [`same_label_decomposition_review.csv`](same_label_decomposition_review.csv):
  revised handling of Urea, Ash, Heat Tolerance, and Unspecified.
- [`source_issue_action_plan.csv`](source_issue_action_plan.csv): complete
  action classification for all 265 source-quality issues.
- [`economic_source_correction_proposals.csv`](economic_source_correction_proposals.csv):
  source-owner proposals; canonical workbook remains unchanged.
- [`external_mapping_dispositions.csv`](external_mapping_dispositions.csv):
  definition- and entity-type review for all 26 exact-label candidates.
- [`energy_module_holds.csv`](energy_module_holds.csv): all energy and cookstove
  rows retained outside an approved module.
- [`evidence_register.csv`](evidence_register.csv): inherited and added
  claim-bounded evidence.
- [`acceptance_summary.json`](acceptance_summary.json): machine-readable counts
  and authorization flags.

## Rebuild

```bash
python3 scripts/build_adr0053_guided_review.py
python3 tests/validate_adr0053_guided_review.py
```

Generated recommendations must not be edited to record approval. Human
decisions belong in a later approval artifact after review; approved source
corrections then occur in the canonical workbook and trigger regeneration.
