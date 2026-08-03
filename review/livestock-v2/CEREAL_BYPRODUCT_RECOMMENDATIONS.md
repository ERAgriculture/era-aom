# Cereal by-product hierarchy decisions

Approved 2026-08-03 by Pete Steward. Batch covers 14 missing-parent cases and
37 child relations.

## Minted contextual groupings

Ten source-specific by-product groupings are minted under `AOM_000594`, Cereal
ByProducts: Baby corn, Barley, Cheka, Finger millet, Millet, Oat, Rice, Rye,
Sorghum, and Wheat by-products.

Barley, Millet, Oat, Sorghum, and Wheat groupings use `skos:related` links to
existing crop/product concepts. Links do not assert identity or hierarchy.

## Flattened paths

- `PARENT-034`: attach Distillers Grain Dried directly to Cereal ByProducts;
  reject redundant `Distillers Grain/Distillers Grain` path.
- `PARENT-039`: attach processed oat-leaf forms to Oat by-products.
- `PARENT-043`: attach dried-ground sorghum sprout to Sorghum by-products.
- `PARENT-045`: attach wheat remoulage to Wheat by-products.

These decisions avoid four single-purpose or duplicate contextual nodes.

## Deferred classification

Processed whole-grain, fodder, leaf, and sprout forms remain usable but enter
classification review. Future compositional modeling should separate source
crop, plant part, processing state, and feed-material role.
