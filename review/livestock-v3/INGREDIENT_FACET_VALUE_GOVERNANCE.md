# Ingredient facet value governance

ADR 0013 converts safe classification routes into explicit semantics while
retaining conservative boundaries.

Approved contracts:

- `approved_ingredient_facet_concepts.csv`: 66 governed facet roots/values;
- `approved_ingredient_component_value_mappings.csv`: 46 atomic mappings;
- `approved_ingredient_component_decompositions.csv`: 65 assertions across 28
  compound source descriptors.
- `approved_ingredient_component_value_holds.csv`: nine explicit null-target
  decisions.

Dedicated facet concepts avoid false reuse of legacy equal-label concepts such
as measured ash composition, animal shell by-product, or oil feed material.
Plural source forms may map to one normalized facet value, while original text
remains preserved.

All 83 descriptors now have one governed outcome. Nine remain null-target holds
because current source-only matching cannot represent their context safely. No
fuzzy matching or unverified external equivalence is allowed.
