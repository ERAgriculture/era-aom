# Ingredient facet value governance

ADR 0013 converts safe classification routes into explicit semantics while
retaining conservative boundaries.

Approved contracts:

- `approved_ingredient_facet_concepts.csv`: 55 governed facet roots/values;
- `approved_ingredient_component_value_mappings.csv`: 35 atomic mappings;
- `approved_ingredient_component_decompositions.csv`: 39 assertions across 17
  compound source descriptors.

Dedicated facet concepts avoid false reuse of legacy equal-label concepts such
as measured ash composition, animal shell by-product, or oil feed material.
Plural source forms may map to one normalized facet value, while original text
remains preserved.

Thirty-one descriptors remain without facet targets: 17 atomic mapping reviews,
11 composite decomposition reviews, and three governed holds. No fuzzy matching
or unverified external equivalence is allowed.
