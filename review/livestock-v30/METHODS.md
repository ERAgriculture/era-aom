# Feed taxonomy implementation methods

Implementation follows [Feed taxonomy governance method](../../docs/methods/feed-taxonomy-governance.md)
and accepted [ADR 0044](../../docs/decisions/0044-feed-taxonomy-axis-reclassification.md).

## Inputs

- [v29 recommendations](../livestock-v29/RECOMMENDATIONS.md)
- [v29 row-level dispositions](../livestock-v29/feed_taxonomy_adversarial_review.csv)
- normalized livestock staging tables
- external authority sources listed in [evidence register](evidence_register.csv)

## Outputs

- [220-row implementation register](feed_taxonomy_implementation_register.csv)
- [feed product-role review](feed_product_role_review.csv)
- [implementation summary](feed_taxonomy_implementation_summary.json)
- [evidence register](evidence_register.csv)
- governed source tables and generated ontology distributions

## Boundary

Implementation applies evidence-supported product-kind and structural decisions,
routes 66 evidence-dependent rows to explicit holds, and leaves six direct Feed
materials branches outside current adversarial scope. Hold routing does not
assert specific feed product kind.
