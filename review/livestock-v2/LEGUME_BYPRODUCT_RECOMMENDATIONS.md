# Legume by-product hierarchy decisions

Approved 2026-08-03 by Pete Steward. Batch covers 13 missing-parent cases and
27 child relations.

## Minted contextual groupings

Ten groupings are minted under `AOM_000615`, Legume ByProducts: Chickpea,
Common bean, Cowpea, Fava bean, Groundnut, Guar bean, Lentil, Lima bean, Pea,
and Pigeon pea by-products.

Fava bean, Groundnut, Pea, and Pigeon pea groupings use `skos:related` links to
existing product concepts. Links do not assert identity or hierarchy.

## Taxonomy normalization

Common Bean Straw/Tops/Haulm, Green Bean Vine, and Haricot Bean Vine all map to
*Phaseolus vulgaris*, `NCBITaxon_3885`, and WFO `wfo-0000207144`. Green bean
and Haricot bean paths therefore flatten into Common bean by-products instead
of creating duplicate source groupings.

Green Bean Vine (`AOM_003960`) and Haricot Bean Vine (`AOM_004000`) remain
separate legacy concepts pending direct identity/deprecation review.

## Other flattening

`PARENT-071` attaches Groundnut Husk Ground directly to Groundnut by-products,
avoiding a single-purpose Groundnut Husk intermediate.

## Deferred classification

Cowpea Dried and Guar Gum Ground remain usable but require later review as
processed whole-crop/product materials rather than assumed by-products.
