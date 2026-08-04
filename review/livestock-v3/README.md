# Livestock phase-3 semantic review

Machine-readable design decisions for reviewed classification and facet
decomposition. These files govern model shape; they are not source-value
mappings and do not authorize automatic assertions.

`ingredient_component_facets.csv` defines allowed dispositions for heterogeneous
legacy ingredient-component descriptors. See
[`../../docs/decisions/0004-ingredient-component-facet-model.md`](../../docs/decisions/0004-ingredient-component-facet-model.md).

`ingredient_component_value_candidates.csv` classifies 83 aggregate-profile
labels as noncanonical proposals. Review rationale and summary live in
`INGREDIENT_COMPONENT_VALUE_RECOMMENDATIONS.md`. Labels are included; private
counts and source rows are not.

`taxon_mapping_candidates_batch_1.csv` records ten NCBI-verified taxon proposals;
WFO candidates remain held and material-to-taxon assertions remain unapproved.

`taxon_mapping_candidates_batch_2.csv` adds 14 biological candidates and one
non-taxon hold; it explicitly repairs a Brassica/Arecaceae legacy mismatch.
