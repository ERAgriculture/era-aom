# ADR 0044: Reclassify feed taxonomy by independent axes

- Status: accepted for staging
- Date: 2026-08-11
- Approved: 2026-08-12
- Reviewer: Pete Steward
- Method: [Feed taxonomy governance](../methods/feed-taxonomy-governance.md)

## Context

Skosmos review after ADR 0043 exposed a larger structural defect. `Supplement`
and `Other Ingredients` remain residual buckets mixing feed materials,
formulations, additives, chemical identities, roles, placeholders, and unknown
products. Direct `Feed materials` children also include five legacy schema
fields. Component, whole-grain, composition-state, and separation-process
branches contain linked modelling errors.

Adversarial review covers 220 concepts: every direct `Feed materials` child,
all descendants of both catch-all branches, Organic Acid and Fumaric Acid, and
all implicated component, integrity, composition-state, and separation-process
branches. Row-level dispositions are published under `review/livestock-v29/`.

## Decision

1. Keep Feed materials, Formulated feeds, and Feed additives as sibling product
   kinds.
2. Retire Supplement and Other Ingredients after every descendant receives an
   approved evidence-backed disposition.
3. Represent supplemental use, additive function, experimental function,
   product role, source, component, process, presentation, moisture, and
   composition as independent facets.
4. Deprecate `AOM_000531` through `AOM_000535` as browse concepts and replace
   their schema-field use with properties while preserving searchable IDs.
5. Move Organic Acid to chemical identity; classify evidenced additive products
   and functions separately.
6. Move mineral/vitamin mixes, blocks, licks, premixtures, and other mixtures to
   Formulated feeds; move authorized additive products to authority-aligned Feed
   additive categories; keep unresolved products as explicit holds.
7. Reframe Protected Fat as rumen-protected fat feed materials and retain
   Megalac as a narrower named product. Move Elancoban under coccidiostatic feed
   additives.
8. Retire Brewhouse processing from active Feed processes. If later required,
   model Beer brewing as an upstream source-production process and link its
   feed by-products through output/provenance relations.
9. Rename Feed separation processes to Feed component separation processes and
   keep only processes whose definitions remove or recover components or
   fractions.
10. Consolidate component modelling under one root with anatomical components,
    processed material fractions, body substances, and component-retention
    scopes as distinct branches. Put Bran under cereal milling fractions.
11. Retire Material integrity; rename Whole-grain integrity to Whole-grain
    composition; represent whole-grain, whole-milk, and full-fat states using
    positive native-component retention semantics.

## Evidence

- [Regulation (EC) 767/2009](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009R0767)
  separates feed materials from complete and complementary feeds.
- [Regulation (EC) 1831/2003](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32003R1831)
  defines authority categories for feed additives.
- [Commission Regulation (EU) 68/2013](https://eur-lex.europa.eu/eli/reg/2013/68/oj/eng)
  defines feed materials and feed-processing terms.
- [AGROVOC feed additives](https://agrovoc.fao.org/browse/agrovoc/en/page/c_2827),
  [supplements](https://agrovoc.fao.org/browse/agrovoc/en/page/c_33996), and
  [organic acids](https://agrovoc.fao.org/browse/agrovoc/en/page/c_5383)
  separate product use from chemical identity.
- [FoodOn facets](https://foodon.org/food-facets/) and
  [relations](https://foodon.org/design/foodon-relations/) separate material,
  anatomy, process, quality, and process-output provenance.
- [Megalac product evidence](https://www.megalac.com/resources-advice/fats-advice/64-rumenprotected-fats-calcium-salt-supplements)
  identifies a calcium-salt rumen-protected fat product.
- [EFSA Elancoban assessment](https://efsa.onlinelibrary.wiley.com/doi/10.2903/j.efsa.2026.10123)
  identifies a monensin-sodium coccidiostatic feed additive.

## Consequences

- This ADR supersedes ADR 0043 decisions about Protected Fat, Anti-coccidia,
  Protein, Brewhouse processing, Whole-grain integrity, and composition-state
  placement.
- Evidence-supported decisions are implemented as one governed cohort; evidence-
  dependent rows remain explicit holds with broad or no semantic class.
- Implementation uses complete approved cohorts, deprecates rather than deletes
  stable IDs, preserves all unresolved holds, rebuilds release artifacts and
  empty Fuseki storage, and repeats Skosmos review before publication.

## Implementation record

- 220 recommendation rows received implementation dispositions: 67
  `implemented`, 81 `implemented-structural`, 66 `hold`, and six
  `outside-scope`.
- 21 collision-audited concepts were allocated as `AOM_101135` through
  `AOM_101155`; rejected generated IDs `AOM_101068` and `AOM_101109` remain
  reserved as `retired-before-publication`.
- Eight source concepts were retired, 16 explicit role relations and five
  positive component-retention relations were added, and 13 evidence sources
  were recorded with supported claims and limitations.
- Deterministic regeneration, 45 Python validators, RDF format parity, SHACL,
  release validation, clean-volume Fuseki load, 19-card Skosmos acceptance, and
  exact notation search passed on 2026-08-12.
