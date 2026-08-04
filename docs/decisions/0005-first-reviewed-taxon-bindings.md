# ADR 0005: First reviewed source-taxon bindings

- Status: Accepted for staged migration
- Date: 2026-08-04
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Decision

Approve ten exact source-name bindings to NCBI Taxonomy IRIs from merged review
batch 1. Bindings describe organism identity only; they do not assert identity
between feed material and taxon concepts. `Gossypium` remains genus rank and
`Ostreidae` family rank. Legacy `Pennisetum purpureum` maps to unchanged
`NCBITaxon_154765`, whose current name is `Cenchrus purpureus`.

WFO candidates remain held pending independent nomenclatural review. Matching
is exact after whitespace/case normalization; fuzzy matching and rank promotion
are forbidden. Original scientific-name text remains available for rollback.

## Consequences

Pipeline may populate `sourceTaxon` only for these governed names. Unknown names
stay null and enter review. No new AOM IDs are minted. Contract remains additive
and canonical cutover remains separately gated.
