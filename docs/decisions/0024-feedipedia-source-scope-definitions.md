# ADR 0024: Feedipedia source-scope definitions

- Status: accepted
- Date: 2026-08-06
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Context

Concept-by-concept definition work does not scale across livestock feed
materials. Feedipedia pages often describe narrower analytical materials than
AOM source concepts. Shared links and similar labels cannot establish synonymy.

## Decision

Review complete Feedipedia cohort using frozen public-page evidence. Approve a
source-scope definition only when page is retrievable, carries no source warning,
maps to one AOM concept, and directly names AOM preferred identity in heading.

Definition states governed feed-material identity. Component, processing method,
physical form, product role, integrity, composition, and constituent remain
unspecified unless independently approved. Descriptors appearing only in
Feedipedia heading are not inherited. All failed cases remain explicit holds.

## Consequences

Definitions become useful for search and AI retrieval without converting page
co-reference into synonymy or reparsing labels during ingestion. Rule can process
large cohorts deterministically while preserving expert review boundaries.
