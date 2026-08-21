# ADR 0049: Composition, form, and component-retention model

- Status: Proposed
- Date: 2026-08-21
- Owners: ERA-AOM semantic governance
- Tracking: [era-program #56](https://github.com/ERAgriculture/era-program/issues/56)
- Evidence: [Cohort E review](../../review/livestock-v39/RECOMMENDATIONS.md)
- Method: [Composition, form, and retention governance](../methods/composition-form-and-retention-governance.md)
- Depends on: [ADR 0042](0042-feed-process-and-material-state-axes.md),
  [ADR 0048](0048-chemical-identity-composition-and-component-model.md)

## Context

Current ontology contains measured physical characteristics, presentation form,
bulk consistency, moisture condition, processing method, composition state, and
component-retention state. Most relations are already independent, but browser
navigation and several legacy labels still obscure boundaries.

`AOM_000324 physical form` conflates dry, wet, pellets, and paste. Meal and
Powder may be confused with particle-size measurements; Dried may be mistaken
for solid form; Liquid and Slurry need explicit distinction. Whole-milk and
Native-fat-retained remain under legacy composition-state wording. Ash is
misclassified as chemical constituent. Mineral Block and Mineral Lick appear
similar but represent presentation versus delivery meaning. Chicken Offal Dried
Ground lacks explicit by-product role.

Complete bounded review covers 40 concepts and 796 affected material
assertions. It records 38 proposed dispositions, two explicit holds, eight
cross-axis overlap decisions, nine global label-collision checks, and three
specific material reviews.

## Decision

### Physical axes

Keep measurable physical quality, categorical physical descriptors, processing
method, and component retention independent.

- Rename `AOM_000326` to **Feed physical characteristics** and retain measurable
  children such as particle size and water-retention capacity.
- Deprecate `AOM_000324 physical form` because its definition conflates
  independent axes.
- After acceptance and collision audit, allocate one **Feed physical
  descriptors** navigation concept under `AOM_000328 Feed Characteristic`, as
  a sibling of measured Feed physical characteristics.
- Place Feed presentation forms, Feed bulk consistencies, and Feed moisture
  conditions beneath that navigation concept while preserving separate
  properties and value hierarchies.
- Keep Meal and Powder beneath Comminuted particle form; do not infer one
  particle-size threshold or drying.
- Keep Dried as moisture condition; do not infer solid or presentation form.
- Keep Liquid, Slurry, and Pulp distinct by dispersed-solid and fibrous/cellular
  criteria.
- Remove Lick from presentation after a consumption or delivery relation is
  designed. Replacement axis remains held.

### Component retention

- Rename `AOM_101115` to **Feed component-retention states**.
- Rename Whole-crop and Whole-grain values to expose component-retention
  meaning, retaining positive component relations.
- Rename `AOM_101134` to **Native-fat retention** and migrate its current uses
  from `aom:compositionState` to `aom:componentRetentionState`.
- Deprecate `AOM_101116 Whole-milk composition` after migrating its one current
  Whole Milk use to Native-fat retention.
- Do not model negative lack-of-process categories such as “not defatted”.

### Chemical identity and analytical composition

- Retain Carbohydrate and Protein identities with candidate exact ChEBI
  mappings.
- Retain constituent-qualified Starch, Fat, and Oil labels where bare names
  collide with or risk conflating feed-material identities.
- Rename Essential-oil constituent to **Essential oil constituent** and review
  exact ChEBI mixture mapping.
- Keep Protein constituent deprecated and replaced by Protein.
- Hold Gluten constituent until chemical-mixture versus processed-material
  identity is resolved.
- Deprecate Ash constituent and remove its tautological Bone Ash assertion; use
  measured Ash characteristic and explicit mineral identities.

### Specific materials

- Retain Mineral Block and Mineral Lick as distinct FeedFormulations.
- Retain Block form for Mineral Block; do not infer Block form for Mineral Lick.
- Add independent By-product role to Chicken Offal Dried Ground while retaining
  source, offal identity, drying, grinding, dried condition, and meal form.
- Do not add Rendering from family-level Feedipedia evidence without explicit
  mapped-page inheritance review.

## Authority comparison

- [FoodOn physical quality](https://foodon.org/food-facets/food-physical-quality/)
  supports independent physical-quality and form facets.
- [FoodOn structure](https://foodon.org/design/foodon-structure/) separates
  observable qualities from transformation processes.
- [ChEBI carbohydrate](https://www.ebi.ac.uk/chebi/CHEBI%3A16646),
  [protein](https://www.ebi.ac.uk/chebi/CHEBI%3A36080),
  [starch](https://www.ebi.ac.uk/chebi/CHEBI%3A28017),
  [essential oil](https://www.ebi.ac.uk/chebi/CHEBI%3A83630), and
  [lipid](https://www.ebi.ac.uk/chebi/CHEBI%3A18059) support reusable chemical
  identity while leaving measured amount and feed use separate.
- [FAO feed analysis](https://www.fao.org/4/i2441e/i2441e00.pdf) defines ash as
  incineration residue, not one chemical entity.
- [FAO multinutrient blocks](https://www.fao.org/4/w4988e/W4988E10.htm)
  distinguishes coherent block presentation from licking behaviour.
- [Feedipedia poultry offal meal](https://www.feedipedia.org/node/12474) and
  [poultry by-product meal](https://www.feedipedia.org/node/214) support explicit
  by-product role.

## Evidence

- [Claim-level evidence register](../../review/livestock-v39/evidence_register.csv)
- [Authority comparison](../../review/livestock-v39/authority_comparison.csv)
- [Complete concept dispositions](../../review/livestock-v39/composition_form_review.csv)
- [Affected material assertions](../../review/livestock-v39/affected_material_assertions.csv)
- [Axis overlap review](../../review/livestock-v39/axis_overlap_review.csv)
- [Label collision audit](../../review/livestock-v39/label_collision_audit.csv)
- [Specific material review](../../review/livestock-v39/specific_material_review.csv)

## Consequences

### Positive

- Browser navigation exposes measurable physical qualities versus categorical
  descriptors.
- Process, presentation, moisture, consistency, and retention stop implying one
  another.
- Whole-grain remains valid after grinding and Dried remains valid across forms.
- Chemical identity, analytical composition, and feed-product use remain
  reusable and non-duplicative.
- Mineral and poultry examples receive explicit, evidence-backed semantics.

### Costs

- 796 current assertions form implementation impact surface, although most stay
  unchanged.
- Three legacy composition-state assertions need governed migration.
- One navigation ID may be allocated only after acceptance and collision audit.
- Lick delivery and Gluten identity remain explicit holds.
- Deprecated cards and downstream search compatibility require clean reload and
  browser acceptance.

## Alternatives considered

### Put every physical term under physical form

Rejected. Dried, liquid, meal, particle size, and grinding answer different
questions and require different relations.

### Put Dried above solid forms

Rejected. Dried and wet materials can share presentation; solids need not have
undergone drying.

### Treat Mineral Block and Mineral Lick as synonyms

Rejected. Block is presentation; lick is consumption or delivery. A block may
be licked without making terms equivalent.

### Keep Whole-milk and Native-fat states parallel

Rejected. Current Whole-milk state has one use and only fat-retention semantics;
product identity plus generic positive retention is simpler and reusable.

### Put chemical constituents under Feed materials

Rejected. Chemical identity can be used as feed material, additive, or measured
constituent without becoming narrower chemical identity.

## Implementation gates

1. Human approval of ADR and every proposed or held disposition.
2. Global preferred, alternative, hidden, deprecated, and external-label audit.
3. New-ID allocation only after accepted navigation label and collision review.
4. Governed source migration; no direct distribution edits.
5. Deterministic second-run generation and full semantic validators.
6. Clean Fuseki reload from exact committed checkout.
7. Guided Skosmos review of roots, representative values, mappings, specific
   materials, notation search, and deprecated redirects.

## Approval record

Awaiting human decision. Proposed rows are not implementation approval; held
rows remain blocked until their named questions are resolved.
