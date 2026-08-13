# ADR 0045: Separate feed product kind from source navigation

- Status: accepted for implementation planning
- Date: 2026-08-13
- Approved: 2026-08-13
- Reviewer: Pete Steward
- Tracking: [era-program #52](https://github.com/ERAgriculture/era-program/issues/52)
- Method: [Feed taxonomy governance](../methods/feed-taxonomy-governance.md)
- Review: [livestock-v31](../../review/livestock-v31/README.md)

## Context

Skosmos review questions whether Feed additives should sit beside Feed
materials, whether chemical substances belong under either product kind, how
unclassified materials should be handled, and whether Crop and Forage are
disjoint. Current Feed materials hierarchy has 20 direct children and mixes
source navigation, product role, individual materials, and five schema fields.

## Decision

1. Keep Feed materials, Formulated feeds, and Feed additives as sibling product
   kinds beneath broad Feed.
   Treat legal mutual exclusion as jurisdiction- and time-scoped product status,
   not a global OWL disjointness axiom.
2. Do not use inclusion percentage alone to distinguish material from additive.
   Evaluate exact products using intended principal purpose, function,
   processing, purity, standardisation, safety controls, and applicable
   authority status.
3. Keep chemical identity independent of product kind. Provisionally retain
   `AOM_101147` outside both product branches, rename it `Chemical substances`,
   and review a new `aom:chemicalIdentity` relation after global collision and
   canonical-reuse checks.
4. Defer final disposition of `AOM_101146` to Cohort D because it may duplicate
   `AOM_000196 Chemical Composition`.
5. Permit a temporary Unclassified feed materials navigation grouping only for
   evidenced FeedMaterials lacking durable placement. Require reason, owner,
   evidence gap, target cohort, review date, and resolution within one release
   cycle.
6. Treat crop and forage as overlapping dimensions. Rename Forage Plants to
   Forage materials and use Feedipedia-aligned editorial navigation: Forage
   materials, Plant products/by-products, Feeds of animal origin, and Other
   feeds.
7. Represent biological source using `aom:sourceTaxon` and product/waste status
   using `aom:productRole`; expose role on material cards rather than duplicating
   source branches by role.
8. Retain all row-level holds in the livestock-v31 review. No identifier,
   hierarchy, typing, relation, distribution, or publication change is approved
   by this proposed ADR.

## Evidence

Authority comparison and limitations are recorded in
[evidence_register.csv](../../review/livestock-v31/evidence_register.csv).
Primary authorities are Regulation 767/2009, Regulation 1831/2003,
Recommendation 2011/25/EU, Implementing Regulation 2021/758, Regulation
2022/1104, Feedipedia categories, and AGROVOC Crop/Feed crop/Forage concepts.

## Consequences if accepted

- Feed additives remain visible beside Feed materials but are not materials.
- Chemical terms no longer imply legal product classification by hierarchy.
- Glycerol may move from an isolated direct child to temporary unclassified
  navigation while exact catalogue scope is resolved.
- Pleurotus remains a product-kind and identity hold rather than receiving
  invented fungal-product detail.
- Crop and Forage navigation becomes intuitive without false disjointness.
- Cohort B resolves the five ingredient-schema concepts; Cohort D resolves the
  chemical root; Cohort E resolves Composition and Form.

## Rejected shortcuts

- Nest Feed additives under Feed materials.
- Classify additives by low inclusion rate alone.
- Move all chemical identities under one product kind.
- Create a permanent Other/Unclassified catch-all.
- Treat all forage as non-crop or all crop products as non-forage.
- Infer source, role, process, or legal status from browse parentage alone.
