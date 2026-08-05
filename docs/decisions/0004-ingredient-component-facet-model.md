# ADR 0004: Decompose heterogeneous ingredient-component descriptors

- Status: Accepted for staged migration
- Date: 2026-08-04
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Context

ADR 0002 provisionally bound legacy `AOM_000532 Ingredient part` to
`aom:ingredientPart`. Pipeline profiling subsequently showed its source field,
`D.Item.Comp`, is heterogeneous. It contains anatomical structures, physical
forms, processed products, production roles, chemical fractions, and compound
descriptions. Exact label matching also returned concepts from incompatible AOM
branches: chemical composition, fodder storage, feed ingredients, crop products,
and animal by-products.

Therefore label equality does not establish identity, and field name does not
justify treating every value as an anatomical part. Automatic mapping would
produce formally valid but scientifically false RDF.

## Decision

Correct phase-2 binding for `AOM_000532` to
`aom:legacyComponentDescriptor` with `xsd:string` values. Preserve source text
unchanged during dual publication. No value from this field gains an IRI solely
through label equality.

Reviewed phase-3 decomposition uses independent facets:

| Facet | Property | Value class |
|---|---|---|
| Anatomical part | `aom:ingredientPart` | `aom:IngredientPartCategory` |
| Physical form | `aom:physicalForm` | `aom:IngredientPhysicalForm` |
| Processing method | `aom:processingMethod` | `aom:ProcessingMethod` |
| Product/by-product role | `aom:productRole` | `aom:ProductRole` |
| Chemical constituent | `aom:ingredientConstituent` | `aom:IngredientConstituent` |

Composite descriptors must split into multiple reviewed assertions. Unresolved
descriptors remain raw strings with no IRI. Measured chemical composition remains
a SOSA/QUDT observation rather than a categorical constituent assertion.

Worked example: `AOM_006072 Maize Whole Ensiled` remains a SKOS concept and an
`aom:FeedMaterial`. Its legacy `skos:broader AOM_001313 Maize Whole` supports
navigation; it does not carry compositional meaning. Reviewed evidence supports
`aom:processingMethod AOM_000831 Ensiling`. It does not yet establish whether
“whole” means whole crop, whole grain, or an omitted component, so no physical-form
or component assertion is published. `Ensilation` and `Ensiled` remain alternate
labels for search and source compatibility.

`aom:IngredientComponent` is not a part/form value. It represents use of a feed
material inside a formulation and may carry its proportion. Therefore “whole” is
a physical-form facet of feed material, even when inherited from a legacy source
column named “Component.”

`review/livestock-v3/ingredient_component_facets.csv` is machine-readable design
governance for classification work. It does not contain source-value mappings and
does not authorize concept creation.

## Compatibility

Correction is non-destructive. Legacy source column and value remain unchanged.
Pipeline currently emits `ingredient_part_label` and an empty
`ingredient_part_uri`, so no published semantic assertion is withdrawn. Pipeline
must update its pinned structural contract and rename normalized raw field before
canonical cutover.

Existing `aom:ingredientPart` remains valid for future reviewed anatomical-part
assertions. No AOM identifier is deleted, reused, or minted.

## Consequences

- Data and AI systems can distinguish raw evidence from reviewed semantics.
- SHACL can validate each facet against a specific value class.
- Compound values support multiple assertions instead of opaque concepts.
- Short-term migration adds classification work but prevents systematic semantic
  corruption.
- Full source-value classification remains a review artifact until approved;
  aggregate profiling evidence is not published as ontology truth.

## Rejected alternatives

- Map every exact label to AOM: branch context demonstrates false identities.
- Keep one broad `ingredientPart` property: hides heterogeneous meanings.
- Mint one concept per source string: encodes compound strings as ontology design.
- Discard source descriptor after decomposition: breaks provenance and rollback.
