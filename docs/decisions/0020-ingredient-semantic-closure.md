# ADR 0020: ingredient semantic closure

Status: accepted  
Date: 2026-08-06  
Reviewer: Pete Steward

## Context

Ingredient visualization exposed 19 labels whose words could not safely map to existing physical-form, anatomical-part, or processing facets: 13 pulps, four named ration meals, one hay, and whole milk. Seven normalized-signature clusters also required explicit identity decisions. Treating `pulp`, `meal`, `hay`, or `whole` as simple lexical synonyms would erase domain distinctions.

## Evidence and decision

- Feedipedia describes sugar-beet pulp as a fibrous processing by-product with wet, pressed, and dehydrated forms. Model pulp as `aom:FeedProductType`, value `Processing pulp`; keep drying, grinding, ensiling, and other processes separate.
- AGROVOC defines compound feeds as combinations of feedingstuffs and supplements formulated as balanced diets. Model named livestock meals as `Compound feed`; never infer grinding from `meal`.
- FAO forage guidance distinguishes fresh, dry, and ensiled forage and describes haymaking as conservation. Model hay as product type `Hay` plus independently evidenced `Drying`.
- Codex food categories distinguish whole milk from reduced-fat and skim milk. Model whole milk with `aom:CompositionState`, value `Whole-milk composition`; never use physical `Whole form`.

Add two OWL/SHACL facets:

- `aom:feedProductType` → `aom:FeedProductType`
- `aom:compositionState` → `aom:CompositionState`

Allocate persistent concepts AOM_101111–AOM_101116. Apply 20 manual assertions across 19 source concepts; hay receives both product-type and drying assertions.

## Identity clusters

- Deprecate AOM_001898 in favor of AOM_001459. Bothriochloa records share corrected label, NCBI Taxonomy, WFO, and CPC mappings and lack distinguishing definitions.
- Hold AOM_001312 versus AOM_003973 (Cotton Seed). Product/by-product role and CPC granularity remain unresolved.
- Retain maize, rice, wheat, and milk pairs as distinct because approved integrity or composition assertions now encode their difference.

## Consequences

Exception queue closes from 19 to zero. All seven clusters have governed dispositions; Cotton remains an explicit approved hold, not an unattended merge candidate. Legacy IDs remain stable, deprecated IDs receive replacement links, ILRI identifiers remain out of scope, and semantic facets remain machine-readable in SKOS, OWL, SHACL, Turtle, and JSON-LD.

## Sources

- Feedipedia, Sugar beet pulp: https://www.feedipedia.org/node/710
- Feedipedia, Dried sugar beet pulp: https://www.feedipedia.org/node/24378
- AGROVOC, Compound feeds: https://agrovoc.fao.org/browse/agrovoc/en/page/c_1796
- AGROVOC, Forage: https://agrovoc.fao.org/browse/agrovoc/en/page/c_36108
- Codex GSFA, Dairy products and analogues: https://www.fao.org/gsfaonline/foods/details.html?id=3
