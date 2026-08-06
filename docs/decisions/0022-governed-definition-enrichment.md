# ADR 0022: governed definition enrichment

Status: accepted  
Date: 2026-08-06  
Reviewer: Pete Steward

## Context

Public livestock source contains 1,865 rows without original descriptions. Normalized vocabulary also adds 268 reviewed concepts. Copying labels into definitions or generating biological and nutritional prose would create false authority.

Two existing governance sources support safe definition composition:

- 268 new concepts have reviewer-approved scope text;
- 971 active feed materials lacking definitions have governed source identities and approved semantic facet assertions.

## Decision

Publish 1,239 approved English definition enrichments:

- promote reviewed new-concept scope text unchanged;
- compose feed-material definitions only from governed source identity and approved facets such as ingredient part, processing method, product type, material integrity, and composition state.

Composed definitions use explicit model language: “governed source identity” and “characteristics”. They make no inferred nutritional, biological, taxonomic, safety, or equivalence claims. Each record declares method, evidence, reviewer, date, and rationale in `approved_definition_enrichments.csv`.

Preserve legacy source descriptions unchanged. Enrichment overlays apply only during normalized release generation and cannot replace an existing source definition.

## Consequences

Active concepts lacking definitions fall from 2,127 to 888. Cereal review candidates lacking governed definitions fall from 368 to 138. Remaining gaps require domain-authority research or additional reviewed semantic modeling; they are not filled with tautological text.
