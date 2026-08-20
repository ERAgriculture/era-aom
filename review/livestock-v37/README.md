# Livestock v37: component and chemical-identity review

Recommendation-only Cohort D pack for
[era-program #55](https://github.com/ERAgriculture/era-program/issues/55).

This pack reviews complete closures of:

- `AOM_101146 Feed chemical entities`;
- `AOM_000196 Feed Chemical Composition`;
- `AOM_101085 Feed material components`.

It compares current ERA structure with FoodOn, ChEBI, Plant Ontology, Uberon,
the EU Catalogue of feed materials, AGROVOC, and NALT. It records every current
material assertion targeting reviewed concepts.

Generated artifacts:

- `component_chemical_review.csv`: one disposition for every reviewed concept;
- `component_chemical_inventory.csv`: current hierarchy, semantic type,
  definition, and use counts;
- `material_usage_inventory.csv`: complete affected material-facet assertions;
- `anatomical_authority_mapping.csv`: complete `AOM_101019` child comparison;
- `identity_overlap_review.csv`: nine identity/reuse cases requiring explicit
  merge, replacement, distinction, or hold decisions;
- `authority_comparison.csv` and `evidence_register.csv`: governed evidence;
- `component_chemical_summary.json`: deterministic counts and input hashes.

Run:

```sh
python3 scripts/build_component_chemical_identity_review.py
python3 tests/validate_component_chemical_identity_review.py
```

No ontology hierarchy, identifier, schema, generated distribution, or Skosmos
data changes are made.
