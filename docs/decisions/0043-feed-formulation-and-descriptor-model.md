# ADR 0043: Separate feed formulations and generalize feed descriptors

- Status: accepted for staging
- Date: 2026-08-11
- Reviewer: Pete Steward

## Context

Skosmos review exposed linked structural defects rather than isolated labels:

- diets, rations, premixes, concentrates, and compound feeds were nested under `Feed ingredient` and typed as `FeedMaterial` when a facet happened to be asserted;
- physical-state roots were named only for ingredients even though presentation, bulk consistency, moisture condition, and processing can also describe formulated feeds;
- `Ingredient constituents` blurred chemical constituents of one material with ingredient components of a formulation;
- `Whole form`, `Whole grain`, and whole-crop concepts mixed presentation and material integrity in navigation;
- heating, autoclaving, extraction, defatting, distillation, brewing, sprouting, soaking, and steeping remained inconsistently grouped or duplicated.

Review covered 29 formulation-branch concepts, all 25 chemical-constituent assertions, all governed descriptor concepts, all governed process concepts, and 12 concepts carrying a current or legacy `whole` label.

## Decision

1. Rename generated `Feed ingredient` to `Feed materials`.
2. Rename legacy `Preformulated Feed` to `Formulated feeds` and move it beside, not under, `Feed materials`.
3. Type 23 reviewed diets, rations, premixes, concentrates, mashes, mixes, meals, pellets, and feeds as `aom:FeedFormulation`.
4. Reclassify branch outliers:
   - Megalac as `aom:FeedMaterial` under Protected Fat;
   - Elancoban as `aom:FeedAdditive` under Anti-coccidia;
   - Prime Gluten 60 and its ground form as `aom:FeedMaterial` under Protein;
   - ACTIPAL HP 1 as an explicit product-class hold under Other Ingredients.
5. Introduce common superclass `aom:Feed`; make `FeedMaterial`, `FeedFormulation`, and `FeedAdditive` subclasses.
6. Generalize physical descriptor classes and roots from ingredient-only names to feed-level names. Preserve old generated labels as searchable alternatives.
7. Rename `Whole form` to `Intact presentation` and `Whole grain` to `Whole-grain integrity`. Keep presentation, whole-crop component, whole-grain integrity, and whole-milk composition independent.
8. Replace active `aom:ingredientConstituent` use with `aom:primaryConstituent` and `aom:ChemicalConstituent`. Retain old property and class as deprecated compatibility terms.
9. Replace two incorrect full-fat constituent assertions with new `AOM_101134 Full-fat composition`; full-fat means native fat was not intentionally removed, not that material identity is fat or a concentration was measured.
10. Reuse existing Sprouted process concept as `Sprouting`; retire generated duplicate before publication. Reuse Soaking for Steeping and preserve `Steeping` as alternative label.
11. Put Heating under Thermal processes; Autoclaving under Heating; Defatting and Extraction under Separation; Distillation under Separation and Thermal.
12. Rename generated `Brewing` to `Brewhouse processing`, place it under Separation and Thermal, and keep microbial Fermentation in Biological processes.

## Evidence

- [Regulation (EC) 767/2009](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009R0767) distinguishes feed materials from compound, complete, and complementary feeds.
- [Commission Regulation (EU) 68/2013](https://eur-lex.europa.eu/eli/reg/2013/68/oj/eng) defines heating, distillation, extraction, flour milling, fermentation, and one combined soaking/steeping process.
- [CDC steam sterilization guidance](https://www.cdc.gov/infection-control/hcp/disinfection-sterilization/steam-sterilization.html) identifies autoclaving as saturated-steam treatment governed by pressure, temperature, and time.
- [Brewers Association brewhouse guidance](https://www.brewersassociation.org/resource-hub/brewhouse/) identifies mashing, lautering, and boiling as brewhouse operations; fermentation remains separately represented.
- [Megalac product evidence](https://www.megalac.com/products/2-megalac) identifies Megalac as a rumen-protected fat supplement.
- [EFSA Elancoban assessment](https://efsa.onlinelibrary.wiley.com/doi/10.2903/j.efsa.2026.10123) identifies Elancoban G200 as a feed additive containing monensin sodium.

## Consequences

- Skosmos navigation separates materials from formulated feeds while cards retain explicit form, process, source, component, composition, and role links.
- Presentation, bulk consistency, and moisture remain independent; no hierarchy implies that pellets, meals, powders, or solids are dried.
- Chemical constituents remain available for oil, starch, ash, and protein identity without representing diet ingredients.
- Legacy generated labels remain searchable. Retired generated IDs remain reserved and cannot be reassigned.
- ACTIPAL HP 1 remains unresolved until stable product evidence establishes its class.
