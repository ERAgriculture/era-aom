# ADR 0045: Separate feed product kind from source navigation

- Status: accepted and implemented in staging candidate
- Date: 2026-08-13
- Approved: 2026-08-13
- Implemented: 2026-08-16
- Reviewer: Pete Steward
- Tracking: [era-program #52](https://github.com/ERAgriculture/era-program/issues/52)
- Method: [Feed taxonomy governance](../methods/feed-taxonomy-governance.md)
- Review: [livestock-v31](../../review/livestock-v31/README.md)
- Implementation: [livestock-v34](../../review/livestock-v34/README.md)

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
8. Implement all 21 approved row-level dispositions and preserve all 11 reviewed
   holds. Implementation approval changes staging ontology and generated release
   artifacts only; it does not approve public publication or canonical cutover.

## Authority comparison

| Authority | Supports | Does not support |
|---|---|---|
| Regulation 767/2009 and Recommendation 2011/25/EU | Feed-material product scope, catalogue naming, source/process descriptors | Universal crop/forage disjointness or ontology browse design |
| Regulation 1831/2003 and Implementing Regulation 2021/758 | Legal distinction and functional authorization of feed additives | Classification by inclusion percentage alone or timeless global status |
| Regulation 2022/1104 | Current catalogue treatment for represented feed-material classes | Identity claims for unresolved local workbook labels |
| Feedipedia | User-facing navigation among forage, plant products/by-products, animal-origin feeds, and other feeds | Legal authorization, exact product identity, or mandatory ontology hierarchy |
| AGROVOC | Crop, feed-crop, forage, and biological-source terminology overlap | Product-role, additive authorization, or local material identity |
| ERA-AOM local graph and workbook review | Existing identifiers, asserted parents, usage, mappings, and migration impact | External scientific or regulatory truth without supporting authority |

No authority alone determines final structure. Regulatory sources govern product
status, Feedipedia informs editorial navigation, AGROVOC informs terminology,
and local evidence proves implementation impact.

## Evidence

Authority comparison and limitations are recorded in
[evidence_register.csv](../../review/livestock-v31/evidence_register.csv).
Primary authorities are Regulation 767/2009, Regulation 1831/2003,
Recommendation 2011/25/EU, Implementing Regulation 2021/758, Regulation
2022/1104, Feedipedia categories, and AGROVOC Crop/Feed crop/Forage concepts.

Implementation evidence, including claim limitations, normalized-label
collision checks, temporary-unclassified governance, rejected-ID reservation,
and row-level disposition joins, is recorded in the
[livestock-v34 evidence register](../../review/livestock-v34/evidence_register.csv).

## Implementation

- `Feed materials` now has exactly four direct editorial navigation children:
  `AOM_000559 Feeds of animal origin`, `AOM_000735 Forage materials`,
  `AOM_101159 Plant products and by-products`, and `AOM_101160 Other feeds`.
- `AOM_101161 Other biological feed materials` groups microalgal and unresolved
  yeast materials; `AOM_101162 Unclassified feed materials` temporarily contains
  only `AOM_001866 Glycerol` under explicit one-release-cycle governance.
- `AOM_101147` is renamed `Chemical substances`; Essential Fatty Acid and Free
  Gossypol are typed and placed as chemical constituents rather than feed
  materials.
- Animal Manures, Water, Pleurotus ostreatus, Pseudovitamin, and Chromium Oxide
  Ground remain explicit classification holds.
- Rejected unapproved IDs `AOM_101156` through `AOM_101158` are reserved as
  retired-before-publication and remain absent from ontology output. Accepted
  new navigation IDs are `AOM_101159` through `AOM_101162`.

Deterministic implementation records 32 dispositions, 12 hierarchy revisions,
three label changes, four new navigation concepts, one temporary-unclassified
member, and zero hierarchy gaps. Generated staging contains 2,794 concepts and
2,801 broader/narrower pairs. Full Python validation, R pilot validation, RDF
parity, SHACL, release/deployment validation, and repeated byte-stable generation
pass. Clean-volume Fuseki/Skosmos acceptance also passes with 37,979 graph
triples, exact four-branch navigation, 13 nested-parent checks, 31 representative
cards, notation search, RDF downloads, and content negotiation; see the
[acceptance summary](../../review/livestock-v34/local_acceptance_summary.json).

## Consequences

- Feed additives remain visible beside Feed materials but are not materials.
- Chemical terms no longer imply legal product classification by hierarchy.
- Glycerol moves from an isolated direct child to temporary unclassified
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
