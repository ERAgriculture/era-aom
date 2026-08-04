# ADR 0009: Large batch-4 source-taxon approval

- Status: Accepted for staged migration
- Date: 2026-08-04
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Decision

Approve all eighty live-verified batch-4 source-name decisions as external NCBI
Taxonomy bindings. This includes 55 exact mappings, 11 synonyms, 5 wrong-ID
replacements, 5 explicit unspecified-species-to-genus mappings, 3 enumerated
misspelling corrections, and 1 retired-ID replacement. Preserve source text
and explicit species, genus, or subspecies rank.

Add guarded batch-promotion tooling. Promotion requires explicit `--approve-all`,
reviewer, and date; rejects duplicate governed source values; and carries
review evidence/action into approved rationale. Promotion never performs live
matching or fuzzy inference.

Refresh live NCBI integrity snapshot after promotion. All 125 approved
biological bindings must pass identifier, current-name, and rank validation.
WFO remains deferred.

## Consequences

Pipeline may adopt 125 governed biological source names in one pinned contract
upgrade. One known non-taxon remains an explicit governed hold. Unknown and
ambiguous source names remain null and review-required. No AOM IDs are minted;
canonical cutover remains separately gated.
