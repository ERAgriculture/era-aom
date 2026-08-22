# Livestock v39 composition, form, and retention review

Recommendation-only Cohort E review for
[era-program #56](https://github.com/ERAgriculture/era-program/issues/56).

## Scope

The bounded review contains 40 concepts and every current material assertion
targeting them:

- five measured or legacy physical-characteristic concepts;
- 11 presentation-form concepts;
- four bulk-consistency concepts;
- three moisture-condition concepts;
- five component-retention concepts;
- nine dual-use constituent concepts;
- Mineral Block, Mineral Lick, and Chicken Offal Dried Ground.

The 796 affected rows are frozen in `affected_material_assertions.csv`. No
ontology hierarchy, schema, identifier, binding, distribution, or Skosmos data
changes are made by this pack.

## Artifacts

- `composition_form_inventory.csv`: complete 40-concept closure and impact
  counts.
- `composition_form_review.csv`: one approved or held disposition per concept.
- `affected_material_assertions.csv`: complete current assertion impact surface.
- `specific_material_review.csv`: mineral formulation and poultry-offal cases.
- `axis_overlap_review.csv`: eight cross-axis ambiguity decisions.
- `label_collision_audit.csv`: proposed-label audit including blocked bare
  Starch and Oil labels.
- `authority_comparison.csv`: authority roles and boundaries.
- `evidence_register.csv`: claim-level sources, limitations, and access dates.
- `composition_form_summary.json`: counts and SHA-256 output manifest.
- `RECOMMENDATIONS.md`: human-readable recommendation.

## Rebuild

```bash
python scripts/build_composition_form_review.py
python tests/validate_composition_form_review.py
```

Second generation must leave every generated artifact byte-identical.
