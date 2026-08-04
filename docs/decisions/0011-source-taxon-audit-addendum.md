# ADR 0011: Source-taxon audit addendum

- Status: Accepted for staged migration
- Date: 2026-08-04
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Decision

Govern 23 source labels exposed by pipeline audit of an older livestock
release. Approve 22 external NCBI Taxonomy bindings and preserve
`Pennisetum petiolare` as `hold_ambiguous` without target URI.

Correct unsafe inherited identifiers rather than treating legacy mappings as
authority. Preserve explicit source rank. Resolve NCBI homonyms using known feed
context only where source label itself is exact; do not use fuzzy matching or
accepted target labels as implicit source aliases.

## Consequences

Approved value contract grows to 298 decisions: 238 external taxon mappings,
56 ambiguous taxon holds, one non-taxon hold, and three ingredient-source
bindings. Pipeline may repin exact contract and rerun aggregate audit. No AOM
IDs are minted and no private row values are published.
