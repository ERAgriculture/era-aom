# ADR 0051 guided-review checkpoint

Consolidated recommendation-only checkpoint for human review of
[ADR 0051](../../docs/decisions/0051-whole-vocabulary-resource-boundaries-and-migration-sequence.md).
It refines evidence in [`whole-vocabulary-v1`](../whole-vocabulary-v1/) but does
not approve the ADR or authorize source, semantic, mapping, publication,
migration, release, or canonical-cutover changes.

## Scope

- 8 guided policy decisions;
- 33 resource-route recommendations, preserving every canonical sheet in source
  order;
- 3 stale crop-only routes revised to cross-domain row routing under accepted
  ADR 0053;
- 2 explicit review holds (`site_list` publication and `scio - Custom Terms`
  provenance);
- 1 confirmed restricted exclusion (`ssa_feedsdb`);
- 7 proposed exclusions retaining migration provenance;
- 3 supporting livestock resources routed as evidence or crosswalks rather
  than independent schemes.

## Files

- [`GUIDED_REVIEW_RECOMMENDATIONS.md`](GUIDED_REVIEW_RECOMMENDATIONS.md):
  human-readable decision checklist.
- [`guided_decision_recommendations.csv`](guided_decision_recommendations.csv):
  eight proposed policy decisions with blank human-decision fields.
- [`resource_routing_recommendations.csv`](resource_routing_recommendations.csv):
  complete recommendation for all 33 resources.
- [`evidence_register.csv`](evidence_register.csv): claim-bounded evidence.
- [`acceptance_summary.json`](acceptance_summary.json): machine-readable counts
  and authorization boundaries.

## Rebuild

```bash
python3 scripts/build_adr0051_guided_review.py
python3 tests/validate_adr0051_guided_review.py
```

Generated recommendations must not be edited to record approval. Human
decisions belong in a later acceptance artifact.

Human decisions are recorded separately in
[`whole-vocabulary-v3`](../whole-vocabulary-v3/README.md).
