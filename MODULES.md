# AOM modules and lineage

## Product boundary

AOM means Agriculture Ontology for Meta-analysis. It is an umbrella semantic
product, not shorthand for livestock alone.

Existing livestock work remains a first-class module. ERA crop work becomes a
sibling module. Shared core concepts emerge only after explicit comparison and
domain review.

## Modules

| Module | Scope | Current state |
|---|---|---|
| `aom-core` | cross-domain study, intervention, observation, unit, provenance, and context semantics | layered semantic model accepted; no workbook source normalized into core yet |
| `aom-crop` | ERA practices, outcomes, crop products, inputs, sites, and field model | `prac` + `out` pilot only; product, input, identity, trait, and economic-outcome sources pending |
| `aom-livestock` | diets, feed ingredients, animals, physiology, husbandry practices, livestock outcomes | public v2 normalized and deeply reviewed for feed; non-feed and `vars_animals` coverage remains open |
| `mappings` | reviewed links among modules and external resources | livestock mappings generated; whole-workbook and crop mapping migration pending |

## Existing livestock AOM

Published record:

- title: *Agriculture Ontology for Meta-analysis (AOM): Livestock Prototype*;
- authors: Todd S. Rosenstock, Peter Richard Steward, and Namita Joshi;
- issued: 2024;
- DOI: <https://doi.org/10.7910/DVN/75E7HV>;
- license: CC BY 4.0;
- CGSpace record: <https://cgspace.cgiar.org/items/a5ccf264-c671-4ec2-b0e3-9504ff8ffaa7>.

Record describes prototype built from over 400 ERA livestock publications,
covering livestock diet, pasture management, and breeds, with links to NCBI,
NCIT, FoodOn, ChEBI, EOL, AGROVOC, and Feedipedia.

Later AOM material expands livestock-feed scope and reports mappings to
Feedipedia and SSA Feeds. Those assets must be inventoried against workbook
`AOM`, `AOM_diets`, `ani_diet`, and `ani_process` sheets before normalization.

## Integration rules

- Preserve published AOM codes, definitions, authorship, DOI, and provenance.
- Never relabel livestock prototype as complete cross-domain AOM.
- Never flatten crop concepts into livestock hierarchy.
- Reuse shared concepts through reviewed identity/alignment decisions.
- Use mappings when concepts overlap but are not identical.
- Preserve `era:*` identifiers from crop lineage during migration.
- Keep `ssa_feedsdb` and any restricted linkage nonpublic until rights review.
- Record every external mapping source, relation, evidence, reviewer, and
  status.

Reconciliation report:
[`inventory/AOM_LIVESTOCK_RECONCILIATION.md`](inventory/AOM_LIVESTOCK_RECONCILIATION.md).

## Next analysis

1. Review the
   [whole-vocabulary coverage matrix](review/whole-vocabulary-v1/resource_coverage.csv)
   and [ADR 0051](docs/decisions/0051-whole-vocabulary-resource-boundaries-and-migration-sequence.md).
2. Formalize current field, lookup, unit, and shared observation contracts.
3. Review and promote crop practice, outcome, and economic-outcome foundations.
4. Migrate crop products, components, inputs, identities, and traits in bounded
   cohorts.
5. Complete livestock coverage outside the recent feed-heavy cohorts.
6. Promote only demonstrated cross-domain semantics into `aom-core`.

Semantic layering decision:
[`docs/decisions/0001-semantic-model-layers.md`](docs/decisions/0001-semantic-model-layers.md).

Wave 1 data-model decision:
[`docs/decisions/0052-data-model-registry-and-shared-core-contract.md`](docs/decisions/0052-data-model-registry-and-shared-core-contract.md).
