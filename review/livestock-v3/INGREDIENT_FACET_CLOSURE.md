# Ingredient facet closure review

## Scope and evidence boundary

This review closes 31 descriptors deferred by ADR 0013. Decisions combine
public agricultural/feed definitions with an aggregate-only contextual audit of
the private livestock release. No source row, study code, or private material
label is committed.

Primary evidence:

- FAO feed nomenclature separates physical description, processing, and usage:
  <https://www.fao.org/4/x5487e/x5487e06.htm>.
- FAO groups straw and haulm as crop residues and molasses/pulps as processing
  by-products: <https://www.fao.org/4/x6554e/X6554E03.htm>.
- AGROVOC defines straw as dry stems and leaves left after crop harvest:
  <https://agrovoc.fao.org/browse/agrovoc/en/page/c_7441>.
- Feedipedia describes wheat and maize bran as milling by-products:
  <https://www.feedipedia.org/node/726> and
  <https://www.feedipedia.org/node/712>.
- FAO defines molasses as several sugar-crop by-product feeds:
  <https://www.fao.org/4/s8850e/S8850E19.htm>.
- Published potato-hash review identifies a mixture of peel, starch, rejected
  potato, and maize produced by snack processing:
  <https://doi.org/10.1016/j.anifeedsci.2017.02.008>.
- FoodOn supports compositional graph statements across food material,
  processing, anatomical-part, and characteristic facets:
  <https://obofoundry.org/ontology/foodon>.

External resources support meaning and future alignment only. This review does
not claim `skos:exactMatch` to AGROVOC, FoodOn, or Plant Ontology.

## Decisions

| Source descriptor | Governed outcome |
|---|---|
| Ash | ash constituent |
| Binder | binder role |
| Grain | grain anatomical part |
| Manure | waste role |
| Mix | mixture form |
| Oil | oil constituent |
| Shell / Shells | shell anatomical part |
| Sludge | processing-waste role |
| Tops | plant-top anatomical part |
| Whole | whole form |
| Bran | milling + by-product role |
| Cake | cake form + pressing + by-product role |
| Haulm | stem + leaf + crop-residue role |
| Hydrolysate | hydrolysis |
| Juice | liquid form + extraction |
| Molasses | liquid form + sugar processing + by-product role |
| Pods Husk | pod + husk |
| Pulp | pulp form + by-product role |
| Seed Kernel | seed + kernel |
| Straw | stem + leaf + dried form + crop-residue role |
| Hash | mixture form + by-product role |

Nine values remain approved null-target holds: `Beans`, `Full Fat`, `Heads`,
`Litter`, `Meal`, `Oil Crude`, `Shaft`, `Vine`, and `Weeds`. Reasons are stored
per row in `approved_ingredient_component_value_holds.csv`. Holds are governed
outcomes, not unfinished silent gaps.

## Context audit effect

Aggregate private context prevented unsafe mappings. `Heads` referred to animal
heads in audited data, so plant-head mapping was rejected. `Meal` occurred in a
named complete ration, so ground-form mapping was rejected. `Hash` consistently
referred to potato hash and public literature established a processing
by-product meaning, allowing decomposition. `Shaft` remained unsupported.
