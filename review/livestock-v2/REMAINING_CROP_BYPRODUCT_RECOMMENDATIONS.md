# Remaining crop-by-product hierarchy recommendations

Decision record for 55 unresolved hierarchy cases covering cash-crop, fruit, oil-plant,
other-plant, root/tuber, sugar-processing, and vegetable feed materials.

## Approved disposition

- Mint 46 source-context groupings using append-only identifiers `AOM_100875`–`AOM_100920`.
- Reparent 102 affected feed materials, closing all 55 reviewed missing-parent cases.
- Use `skos:broader` only for classification and nine `skos:related` links to existing
  crop/product concepts. Existing crop/product concepts are not reused as by-product groups.
- Flatten absent legacy branch labels for cash crops, fruit, and vegetables under
  `AOM_001916` Crop Byproduct. Empty containers add no retrieval value and can be added
  later through governed concepts if a broader faceted classification is required.
- Flatten nine one-purpose nested processing/part paths into their source grouping.
  Processing state and plant part belong in later compositional modeling, not chains of
  near-duplicate SKOS concepts.

## Taxonomic and hierarchy exceptions

- African yam bean (`Sphenostylis stenocarpa`) is a legume. Its grouping is placed under
  `AOM_000615` Legume ByProducts, correcting the legacy root-and-tuber path.
- Marula kernel and seed materials share one Marula by-products grouping; no kernel-only
  or seed-only container is minted.
- Palm kernel is placed directly under Oil Plant ByProducts because no reviewed Palm
  grouping exists and all affected records are kernel-derived.
- Carob's duplicated `Carob/Carob` legacy path is represented by one Carob by-products
  grouping.
- Other Plant ByProducts is retained as a useful category because it directly classifies
  the existing Hops concept.

## Deferred modeling review

Eleven records that may describe processed whole crops, seeds, or primary co-products are
queued in `schema_remodeling_candidates.csv`. This batch restores navigable hierarchy but
does not silently decide contested product/by-product boundaries.

## Identifier and provenance controls

Identifiers were checked against the canonical ERA workbook before allocation; the full
range was unused on 2026-08-03. Governance records preserve reviewer, date, evidence,
rationale, affected children, and related-product links. Generated CSV, JSON-LD, Turtle,
edge, node, and manifest outputs remain reproducible through the normal build scripts.
