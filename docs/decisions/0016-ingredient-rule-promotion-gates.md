# ADR 0016: Gate bulk ingredient-rule promotion

- Status: Proposed
- Date: 2026-08-05
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: TBD

## Context

ADR 0015 replaced individual ingredient review with reusable proposal rules.
Lexical regularity alone is insufficient for promotion: terms such as `oil`,
`cake`, `pulp`, `meal`, `hay`, colours, and maturity states cross semantic
dimensions.

## Proposed decision

Approve explicit processing rules in bulk. Approve component and unambiguous
physical-form rules only with a guard requiring retained source identity and
context-compatible use. Hold ambiguous forms, qualities, and unqualified
`Whole` until corresponding product-state, quality, maturity, or material-role
models exist.

Require named reviewer approval, exclusion of held rules, stratified family
sampling, semantic regression tests, and legacy-ID compatibility before any
generated assertion enters staging or release artifacts.

## Consequences

High-volume harmonization becomes possible without treating a normalized label
signature as proof of identity. Quality gaps remain explicit work rather than
being encoded into incorrect ontology relations.
