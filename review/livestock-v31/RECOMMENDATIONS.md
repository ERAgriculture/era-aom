# Cohort A recommendations: feed product kinds and source navigation

Status: accepted by Pete Steward on 2026-08-13 under
[era-program #52](https://github.com/ERAgriculture/era-program/issues/52).

## Snapshot

The current generated graph has:

- 20 direct and 1,625 total descendants beneath `AOM_100850 Feed materials`;
- 33 descendants beneath `AOM_101135 Feed additives`;
- eight descendants beneath `AOM_101147 Feed chemical substances`;
- 768 Forage Plants descendants, 185 Crop product descendants, and 504 Crop
  Byproduct descendants;
- no shared concept IDs and no shared normalized labels between the Forage and
  either Crop branch.

That absence of overlap reflects current modelling, not a valid claim that crops
and forage are disjoint. Full membership is generated in
`feed_product_kind_inventory.csv` from checksummed graph inputs.

## Authority comparison

| Authority | Supported conclusion | Boundary |
|---|---|---|
| [Regulation 767/2009](https://eur-lex.europa.eu/eli/reg/2009/767/oj/eng) | Feed materials primarily meet nutritional needs and may be used directly, after processing, in compound feed, or as premixture carriers. | Does not classify ambiguous labels globally; excludes water from regulation scope. |
| [Regulation 1831/2003](https://eur-lex.europa.eu/eli/reg/2003/1831/oj/eng) | Feed additives are intentionally added products, other than feed materials and premixtures, with specified functions. | Authorization remains product-, use-, species-, dose-, and time-specific. |
| [Recommendation 2011/25/EU](https://eur-lex.europa.eu/eli/reco/2011/25/oj/eng) | One product cannot be both legal kinds; classification considers processing, purity, safety, mode of use, and functionality together. | Low inclusion rate is common for additives but also occurs for feed materials and is not decisive. |
| [Implementing Regulation 2021/758](https://eur-lex.europa.eu/eli/reg_impl/2021/758/oj/eng) | Product status requires case-by-case multi-criterion assessment. | Decisions for listed products do not transfer automatically to AOM labels. |
| [Catalogue amendment 2022/1104](https://eur-lex.europa.eu/eli/reg/2022/1104/oj/eng) | Crude and refined glycerine/glycerol are catalogue feed materials. | AOM generic Glycerol still needs scope alignment to catalogue entries. |
| [Feedipedia categories](https://www.feedipedia.org/content/feeds?category=13591) | Practical browsing separates Forage plants, Plant products/by-products, Feeds of animal origin, and Other feeds. | Navigation is not a formal disjoint ontology or legal classification. |
| [AGROVOC Crops](https://agrovoc.fao.org/browse/agrovoc/en/page/c_1972), [Feed crops](https://agrovoc.fao.org/browse/agrovoc/en/page/c_2829), and [Forage](https://agrovoc.fao.org/browse/agrovoc/en/page/c_36108) | Crops include plants cultivated for livestock fodder; feed crops are crops, and forage is plants or plant parts used as feed. | These relations establish overlap but not exact AOM material identity. |

## Findings

### Feed material versus additive

Feed additive should not be nested beneath Feed materials. Under reviewed EU
definitions, they are mutually exclusive legal product kinds and correctly sit
as siblings beneath broad Feed. Percentage contribution is not the defining
criterion. Intended principal use, function, processing, purity,
standardisation, safety controls, and regulatory status matter together.

This is a jurisdictional product-classification rule, not justification for a
global OWL disjointness axiom. AOM should preserve jurisdiction, authorization,
and effective-date context when legal status is asserted. Broad domain language
may call additives part of feed, but broad `Feed`—not `FeedMaterial`—captures
that shared scope.

Same chemical identity may occur in differently classified products or uses.
Model chemical identity independently, then classify the exact product. Reuse
one stable concept only when identity and scope truly match; create a distinct
product concept when purity, preparation, authorization, or intended use makes
it a different entity.

### AOM_101147

Do not move `AOM_101147 Feed chemical substances` under Feed materials or Feed
additives. Current descendants mix chemical identities, chemical categories,
constituents, and one ground product-like term. Retain an independent chemical
axis provisionally, rename this branch to neutral `Chemical substances`, and
add a reviewed `aom:chemicalIdentity` relation from exact feed products when
needed. Rename and relation remain subject to global label-collision and
canonical-reuse review.

`AOM_101146 Feed chemical entities` remains a Cohort D hold because it may
duplicate `AOM_000196 Chemical Composition`. Cohort A establishes only the
required axis independence; it does not approve another chemical root.

### Unclassified feed materials

Create a temporary `Unclassified feed materials` navigation grouping beneath
Feed materials only for concepts whose FeedMaterial status is evidenced but
whose durable navigation placement is not. Membership must carry unresolved
reason, evidence gap, owner, target cohort, and review date. Empty or resolve it
within one release cycle. Never use it as a replacement Supplement/Other bucket.

- `AOM_001866 Glycerol`: FeedMaterial status is supported by catalogue entries;
  temporary unclassified placement is acceptable until generic scope is aligned
  to crude/refined glycerine or another durable branch.
- `AOM_006349 Pleurotus ostreatus`: source context establishes ingredient-list
  occurrence, but exact identity and FeedMaterial status remain unclear.
  Determine fruiting body, powder, mycelial biomass, or fungus-treated substrate
  before placing it under Unclassified feed materials or a durable branch.
- Do not put either under `AOM_101142 Feed classification holds` when retaining
  FeedMaterial typing because that grouping explicitly denies product-kind
  classification.

### Crop and forage

A crop can be a forage source. `Crop` concerns cultivation; `forage` concerns
plant material or parts fed or grazed. Current disjoint branches are therefore
misleading.

Use Feedipedia structure as explicit editorial navigation, not as disjoint
biological classes:

1. Forage materials;
2. Plant products/by-products;
3. Feeds of animal origin;
4. Other feeds.

Rename `Forage Plants` to `Forage materials`. Merge `Crop product` and `Crop
Byproduct` into Plant products/by-products navigation. Keep source taxon and
economic `aom:productRole` independent, and show Product/By-product/Waste role
on each feed-material card. This avoids separate role-driven material trees.

Plant, Animal, and Other may support user-facing collections, but should not be
minted as exclusive semantic product kinds. Prefer explicit source relations
and editorial collections; use SKOS broader/narrower navigation only when UI
constraints require it and definitions state that branches overlap.

## Proposed model

```text
Feed
├── Feed materials
├── Formulated feeds
└── Feed additives

Independent axes
├── Chemical identity
├── Biological/material source
├── Product role
├── Intended function
├── Process
└── Composition and form

Feed-material navigation
├── Forage materials
├── Plant products/by-products
├── Feeds of animal origin
└── Other feeds
```

Use existing `aom:sourceTaxon`, `aom:productRole`, `aom:functionalRole`,
`aom:processingMethod`, and `aom:primaryConstituent`. Proposed
`aom:chemicalIdentity` requires schema review because current schema lacks a
direct product-to-chemical-identity relation.

## Required decisions

1. Approve sibling FeedMaterial and FeedAdditive product kinds.
2. Reject inclusion percentage as standalone classifier.
3. Keep chemical identity outside product-kind hierarchy without asserting
   global legal disjointness.
4. Approve temporary governed Unclassified feed materials lifecycle.
5. Approve Feedipedia-aligned overlapping navigation and card-level product role.
6. Hold `AOM_101146`, Pleurotus exact scope, water product kind, animal manures,
   and Chromium Oxide Ground for their named follow-up cohorts.

All rows in `feed_product_kind_review.csv` received human disposition on
2026-08-13. Implementation remains separate and must wait for PR #90 resolution
plus normal collision, reuse, identifier, regeneration, validation, and Skosmos
gates.
