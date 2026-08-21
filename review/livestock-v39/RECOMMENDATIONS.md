# Cohort E recommendations: composition, form, and component retention

Status: accepted by Pete Steward on 2026-08-21 under
[era-program #56](https://github.com/ERAgriculture/era-program/issues/56).

Decision proposal:
[ADR 0049](../../docs/decisions/0049-composition-form-and-component-retention-model.md).

## Snapshot

Complete bounded review covers 40 concepts and 796 current material-facet
assertions:

- 358 presentation-form assertions;
- 400 moisture-condition assertions;
- seven bulk-consistency assertions;
- five component-retention assertions;
- three legacy composition-state assertions requiring migration;
- 23 primary-constituent assertions.

Thirty-eight dispositions are approved and two remain held. No implementation
change or identifier allocation occurs in this review.

## Authority comparison

| Authority | Supported conclusion | Boundary |
|---|---|---|
| [FoodOn physical quality](https://foodon.org/food-facets/food-physical-quality/) and [facet design](https://foodon.org/food-facets/) | Keep physical quality, presentation, process, chemical identity, and other descriptive facets independent. | FoodOn is not a feed-regulatory catalogue and exact mappings need concept review. |
| [ChEBI](https://www.ebi.ac.uk/chebi/) | Carbohydrate, protein, starch, essential oil, and lipid provide reusable chemical-identity references. | Fat and oil are contextual mixture categories; broad lipid mapping is safer than exact equivalence. |
| [FAO feed analysis](https://www.fao.org/4/i2441e/i2441e00.pdf) | Ash is analytical residue after incineration, not one chemical constituent. | Ash result does not identify each mineral species. |
| [FAO multinutrient blocks](https://www.fao.org/4/w4988e/W4988E10.htm) | Block is coherent physical presentation; licking is consumption or delivery behaviour. | One publication cannot define every mineral formulation. |
| [Feedipedia poultry offal meal](https://www.feedipedia.org/node/12474) and [poultry by-product meal](https://www.feedipedia.org/node/214) | Chicken offal meal is an animal by-product; role is independent of source, drying, grinding, and meal form. | Family-level rendering evidence should not be inherited automatically without exact mapped-page review. |
| [EU Catalogue](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02013R0068-20220724) | Product names and processing qualifiers are distinct from analytical composition and physical presentation. | Legal catalogue does not define universal ontology hierarchy. |

Claim-level support and limitations are frozen in `evidence_register.csv`; full
authority roles are in `authority_comparison.csv`.

## Physical architecture

Keep four questions independent:

1. **What measurable physical quality does item have?** Use Feed physical
   characteristics, including particle size and water-retention capacity.
2. **How is item physically described or presented?** Use presentation form,
   bulk consistency, and moisture condition through separate properties.
3. **What process was applied?** Use processing method. Grinding does not imply
   one particle threshold; drying does not imply one presentation.
4. **What native component remains?** Use component-retention state and
   positive retained-component relations, not measured composition.

Rename `AOM_000326` to **Feed physical characteristics**. Deprecate legacy
`AOM_000324 physical form`: its definition mixes dry, wet, pellet, and paste
across three independent axes. After approval, allocate one **Feed physical
descriptors** navigation concept under `AOM_000328 Feed Characteristic`, as a
sibling of measured Feed physical characteristics. Place `AOM_101020`,
`AOM_101132`, and `AOM_101133` beneath it without changing their governed
properties.

### Presentation

Retain Meal and Powder beneath Comminuted particle form. They do not imply one
particle-size threshold or drying. Keep Grinding as processing method and
particle size as measured characteristic.

Remove `AOM_101050 Lick form` from presentation after a replacement relation is
designed. A block can be licked: **Block** describes shape or presentation;
**lick** describes consumption or delivery. This replacement remains held.

### Moisture and consistency

Keep Dried and Fresh as moisture conditions. Dried is not a physical form;
solids can be dried or undried, and dried materials can be meal, block, pellet,
powder, or another presentation.

Retain Liquid, Slurry, and Pulp as distinct bulk consistencies:

- Liquid has no governed dispersed-solid requirement.
- Slurry requires solid particles dispersed in a liquid continuous phase.
- Pulp denotes moist fibrous or cellular, commonly semisolid, material.

## Component retention

Rename `AOM_101115` to **Feed component-retention states** and relabel
Whole-crop and Whole-grain to expose retention meaning. Keep their existing
positive retained-component relations.

Rename `AOM_101134` to **Native-fat retention** and migrate its two current
materials from `compositionState` to `componentRetentionState`.

Deprecate `AOM_101116 Whole-milk composition` after moving its one Whole Milk
use to Native-fat retention. Whole Milk already has product identity; current
state's only governed retained-component relation is fat. Do not create
negative “not defatted” categories.

## Chemical identities and composition

- Retain `AOM_001577 Carbohydrate` and `AOM_001571 Protein` as chemical
  identities and review exact ChEBI mappings.
- Retain Starch constituent and review exact `CHEBI:28017` mapping. Bare
  **Starch** is blocked because it already labels a feed-material identity.
- Rename Essential-oil constituent to **Essential oil constituent** and review
  exact `CHEBI:83630` mapping.
- Retain Fat constituent and Oil constituent with broad lipid mapping only.
  Bare **Oil** is blocked by existing `AOM_001333 Oil` feed material.
- Keep `AOM_101120 Protein constituent` deprecated and replaced by Protein.
- Hold Gluten constituent until chemical-mixture versus processed-material
  identity is resolved.
- Deprecate `AOM_101080 Ash constituent`; remove the Bone Ash
  `primaryConstituent` assertion. Use measured `AOM_000226 Ash` and explicit
  mineral identities when known.

Chemical identity remains separate from measured composition and feed-material
or additive use. A chemical can be used as feed material without becoming a
narrower chemical class.

## Specific materials

- Keep `AOM_000764 Mineral Block` and `AOM_000766 Mineral Lick` as distinct
  FeedFormulations, not synonyms.
- Keep Block form on Mineral Block.
- Do not infer Block form for Mineral Lick; current unspecified form is valid.
- Add `aom:productRole AOM_101062 By-product role` to `AOM_001938 Chicken Offal
  Dried Ground` after approval.
- Retain Chicken source, offal identity, Dried condition, Meal presentation,
  Drying, and Grinding independently.
- Hold any Rendering assertion until mapped-page versus family-page evidence is
  explicitly accepted; do not inherit family process automatically.

## Required decisions

1. Approve measured physical characteristics versus categorical physical
   descriptors.
2. Approve legacy physical-form deprecation and one unallocated physical
   descriptor navigation concept.
3. Approve Meal/Powder, Dried, Liquid/Slurry/Pulp, and process boundaries.
4. Approve component-retention renames and three composition-state migrations.
5. Approve Whole-milk state deprecation in favour of Native-fat retention.
6. Approve Ash constituent retirement and dual-use constituent decisions.
7. Approve Mineral Block versus Mineral Lick distinction and held lick mode.
8. Approve Chicken Offal Dried Ground By-product role.

## Implementation gates

1. Human approval of ADR 0049 and every proposed or held row.
2. Global preferred, alternative, hidden, deprecated, and external-label audit.
3. Allocate no new ID before accepted label and collision review.
4. Governed source migration for all affected assertions; never edit
   distributions directly.
5. Deterministic second-run generation and complete validators.
6. Clean Fuseki volume reload from exact committed checkout.
7. Guided Skosmos acceptance for physical roots, retention states, constituents,
   Mineral Block/Lick, Chicken Offal Dried Ground, and deprecated redirects.

## Guided Skosmos acceptance plan

After implementation, check:

- `AOM_000326`, replacement for `AOM_000324`, `AOM_101020`, `AOM_101132`, and
  `AOM_101133` as separate navigable roots;
- `AOM_101126 Meal form`, `AOM_101051 Powder form`, `AOM_101054 Dried moisture
  condition`, `AOM_101077 Liquid consistency`, and `AOM_101118 Slurry
  consistency` definitions and narrower/broader links;
- `AOM_101115`, `AOM_101086`, `AOM_101110`, `AOM_101116`, and `AOM_101134`
  labels, redirects, and positive retained-component relations;
- constituent mappings and absence of active duplicate Protein/Ash cards;
- `AOM_000764`, `AOM_000766`, and `AOM_001938` independent facets;
- notation search for every changed, deprecated, and replacement concept.

No hierarchy, schema, identifier, binding, generated distribution, or Skosmos
change is made by this review.
