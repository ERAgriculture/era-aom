# ADR 0039: Maize Bran card semantics

Date: 2026-08-07
Status: accepted for release-candidate testing

## Context

`AOM_001614` (“Maize Bran”; alternative label “Corn Bran”) was searchable,
but its concept card did not expose enough machine-readable meaning. Bran was
also modelled as an anatomical plant part, although reviewed ERA material
describes maize bran as a by-product of milling shelled maize.

Evidence used:

- current ERA master workbook, `AOM` sheet row 699 and `AOM_diets` row 55:
  `AOM_001614`, source “Maize”, component “Bran”, scientific name
  `Zea mays`, NCBI Taxonomy `4577`, and crop-by-product hierarchy;
- current ERA master workbook, `OLD_diet_item` row 57: “A by-product of the
  milling of shelled maize”, AGROVOC maize-bran match, and Feedipedia page 712;
- repository snapshot `data/livestock-staging/legacy_records.csv`, retained as
  reproducible release input;
- reviewed taxon governance in
  `data/livestock-staging/approved_semantic_value_bindings.csv`.

Workbook path is not embedded in release artifacts because it is private and
machine-specific. Repository snapshot and public authority URLs provide
portable provenance.

## Decision

Represent `AOM_001614` using independent facets:

- `aom:sourceTaxon` → NCBI Taxonomy 4577 (`Zea mays`);
- `aom:materialComponent` → `AOM_101104` (`Bran`);
- `aom:processingMethod` → canonical existing `AOM_000838` (`Milling`);
- `aom:productRole` → `AOM_101062` (`By-product role`).

Retype `Bran` as `aom:FeedMaterialComponent`, not
`aom:IngredientPartCategory`, and apply that correction to every generated
Bran assertion. Keep `Maize Bran` as stable preferred identity and `Corn Bran`
as `skos:altLabel`; do not create duplicate concepts from alternate wording.

Provide definitions for Bran and By-product role, and label semantic
properties so Skosmos can present intelligible card fields. External taxon is
locally labelled `Zea mays` while retaining authoritative NCBI URI.

## Consequences

Concept card becomes understandable to people and traversable by software.
Feed-basket applications can query species, component, process, and role as
separate dimensions. Existing persistent concept IDs remain unchanged.

Skosmos displays `skos:altLabel` as “Synonyms”: accepted alternative names
used for search and discovery, not extra ingredients or subclasses. For this
card, `Corn Bran` is a synonym for `Maize Bran`.
