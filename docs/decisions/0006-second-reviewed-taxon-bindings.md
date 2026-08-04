# ADR 0006: Second reviewed source-taxon bindings

- Status: Accepted for staged migration
- Date: 2026-08-04
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Decision

Approve fourteen biological source-name bindings from review batch 2. Bind
`Brassica napus` to `NCBITaxon_3708`, replacing incorrect legacy target
`NCBITaxon_4710`, which identifies Arecaceae. Preserve family rank for
`Arecaceae`, genus rank for `Brevoortia`, and source synonyms for `Panicum
maximum` and `Acacia tortilis` while targeting current NCBI names at unchanged
identifiers.

Add `hold_non_taxon` as governed value-binding action. Apply it to `sodium
carboxymethyl cellulose`: chemical material cannot receive taxon identity and
must enter source-data quality review. Held values have no target concept.

WFO remains deferred. Matching remains exact after whitespace/case
normalization. Fuzzy matching and rank promotion remain forbidden. Original
source text remains available for provenance and rollback.

## Consequences

Pipeline may populate `sourceTaxon` for twenty-four governed biological names
across both approved batches. Known non-taxa and ambiguous values remain null
with distinct machine-readable reasons. No new AOM IDs are minted. Canonical
cutover remains separately gated.
