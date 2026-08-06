# ADR 0025: Public-authority source-scope cohort

- Status: accepted
- Date: 2026-08-06
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Decision

Review taxon and public-ontology definition routes as one frozen 244-concept
cohort. WFO may support direct plant-source identity; NCBI Taxonomy may support
direct animal or microbial-source identity. Neither supports a processed part,
product, form, or role without separate evidence.

Approve direct source scope only for allowed ingredient families without a
derived-material descriptor. Exact AGROVOC oil identities decompose into source
plus oil constituent. Non-exact, conflicting, or broad public mappings remain
holds. Ingestion consumes structured assertions and never reparses labels.
