# ADR 0005: Compose feed materials from controlled dimensions

- Status: Accepted as harmonization target
- Date: 2026-08-05
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward
- Design evidence: `Feed Basket Schema DRAFT-Working Version.drawio.svg`

## Context

Legacy AOM encodes primary material, biological component, processing, and their
combinations as neighbouring SKOS concepts. This creates apparent synonyms such
as `Maize`, `Maize Grain`, and `Maize Whole`, plus repeated combinations such as
`Maize Ground` and `Maize Grain Ground`. Labels alone cannot determine whether
these records are duplicates or distinct materials.

Feed-basket design separates canonical feed identity into controlled dimensions:
primary feed term, optional component, and ordered processing profile. External
master-list identifiers describe either one dimension or resulting combination;
they must not be assumed to identify primary organism alone.

## Decision

Use ERA-AOM for controlled values and semantic mappings. Represent operational
feed materials as unique combinations of:

1. `feed_primary_id` — base feed source or primary material;
2. `component_id` — grain, cob, leaf, stover, whole crop, or another reviewed
   component; explicit unspecified value is permitted;
3. `process_profile_id` — ordered set of processing methods, including explicit
   none/unspecified profiles.

Canonical uniqueness is `(feed_primary_id, component_id, process_profile_id)`.
Generated material labels are display values, not evidence for new atomic
ontology concepts. Legacy compound AOM identifiers remain resolvable during
migration and map to reviewed combinations. True duplicates use one retained
identifier; deprecated identifiers point to replacement. Ambiguous compounds
remain held without inferred component or form.

## Maize example

`Maize Grain Ground` can normalize to `Maize + Grain + Grinding` when source
evidence confirms grain. Approved maize review resolves `AOM_001326` as
`Whole-crop maize silage`: material component `Whole crop` plus process
`Ensiling`. Legacy synonym `AOM_006072` is deprecated and replaced by
`AOM_001326`. Unqualified `Whole` remains held because it may mean whole crop,
whole organism, whole grain, or absence of a component. This prevents false
equivalence between whole grain and whole-crop silage.

## Consequences

- Feed baskets reference stable canonical combinations without expanding core
  vocabulary for every label permutation.
- AI systems can query primary material, component, and process independently.
- External identifiers attach at correct semantic level.
- Harmonization requires family-level review before merges or deprecations.
- Legacy labels remain searchable through compatibility mappings.
