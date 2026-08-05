# ADR 0016: Gate bulk ingredient-rule promotion

- Status: Accepted
- Date: 2026-08-05
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Context

ADR 0015 replaced individual ingredient review with reusable proposal rules.
Lexical regularity alone is insufficient for promotion: terms such as `oil`,
`cake`, `pulp`, `meal`, `hay`, colours, and maturity states cross semantic
dimensions.

## Decision

Approve explicit processing rules in bulk. Approve component and unambiguous
physical-form rules only with a guard requiring retained source identity and
context-compatible use. Hold ambiguous forms, qualities, and unqualified
`Whole` until corresponding product-state, quality, maturity, or material-role
models exist.

Require named reviewer approval, exclusion of held rules, stratified family
sampling, semantic regression tests, and legacy-ID compatibility before any
generated assertion enters staging or release artifacts.

Approve 20 explicit processing rules in bulk and 20 component/form rules under
the retained-source-identity guard. Defer 12 unobserved rules. Hold 15 ambiguous
or model-gap rules. Mint 22 missing governed target values by appending new
identifiers after `AOM_101086`; existing identifiers do not move. Generated
assertions retain rule provenance and remain independently reproducible.

## Consequences

High-volume harmonization becomes possible without treating a normalized label
signature as proof of identity. Quality gaps remain explicit work rather than
being encoded into incorrect ontology relations.
