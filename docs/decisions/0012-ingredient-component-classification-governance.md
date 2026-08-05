# ADR 0012: Ingredient-component classification governance

- Status: Accepted for staged migration
- Date: 2026-08-04
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Decision

Approve classification outcomes for all 83 profiled legacy ingredient-component
descriptors: 52 atomic values routed to one primary facet, 28 compound values
routed to decomposition, and three unresolved values held without semantic
target. Preserve raw source text for every record.

Classification approval does not approve concept identity, create an IRI, or
mint an AOM identifier. Atomic values still require reviewed value-to-concept
mapping. Composite values require two or more independently reviewed facet
assertions. Holds remain raw-only and review-required.

Pipeline may consume exact normalized source-value classifications to route
review work and measure coverage. Matching is limited to case/whitespace
normalization; fuzzy matching remains forbidden.

## Consequences

Every currently profiled descriptor has an explicit governed route while all
five facet IRI fields remain empty until separate mapping approval. Systems and
AI agents can distinguish atomic mapping candidates, decompositions, and holds
without mistaking predicted structure for ontology truth.
