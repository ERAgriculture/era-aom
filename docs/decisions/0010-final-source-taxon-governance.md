# ADR 0010: Final source-taxon governance

- Status: Accepted for staged migration
- Date: 2026-08-04
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Decision

Govern all 146 labels in the final taxon review pack. Approve 91 exact,
synonym, corrected-ID, or explicit unspecified-species-to-genus candidates as
external NCBI Taxonomy bindings. Preserve 55 unresolved or contextual labels as
`hold_ambiguous` bindings with no target URI. Source text remains unchanged.

Extend guarded promotion tooling to support mixed mapping-and-hold packs.
Promotion requires explicit `--approve-all`, reviewer, and date. A populated
NCBI identifier produces `map_to_external`; only a declared `hold_*` action
without accepted name may produce `hold_ambiguous`. Duplicate governed values,
partial mappings, and undeclared empty targets fail promotion.

Refresh pinned NCBI evidence after promotion. All 216 approved biological
mappings must match live identifier, accepted name, and rank. Fuzzy inference
and WFO mapping remain forbidden.

## Consequences

Every inventoried source-taxon label now has a governed outcome. Pipeline may
consume 216 external mappings while retaining 56 explicit taxon holds: 55 from
this decision plus one previously governed non-taxon. Holds remain null and
review-required; they must never receive guessed IRIs. No AOM IDs are minted.
