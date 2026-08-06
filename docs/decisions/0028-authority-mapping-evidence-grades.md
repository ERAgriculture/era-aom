# ADR 0028: Authority mapping evidence grades

- Status: accepted
- Date: 2026-08-06
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Decision

Separate mapping usefulness from definition evidence. Retain correct cross-domain,
broad, shared-page, warned, or unreachable links as `skos:relatedMatch` with
`definition_evidence_grade=insufficient`. Exclude mappings whose authority target
identifies a different taxon or material. Preserve every excluded assertion in
frozen audit cohort.

Definition routing must ignore reviewed-related and review-held mappings. Exact or
close identity requires explicit future approval; lexical similarity or shared
target never upgrades relation automatically. This policy supports AI retrieval
without allowing related links to become false equivalence or generated prose.
