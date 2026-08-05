# ADR 0017: Resolve remaining ingredient exceptions by model family

- Status: Proposed
- Date: 2026-08-05
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: TBD

## Context

Bulk rule promotion covers nearly all governed feed ingredients. Remaining
exceptions recur around six semantic gaps rather than 29 unrelated concepts.
Current workbench also exposed stale legacy edge labels that differ from approved
preferred labels.

## Proposed decision

Use governed preferred labels as harmonization input. Group remaining work into
source-identity fallback, whole-grain integrity, dairy composition state, pulp
product material, conserved-forage state, and formulated-feed category models.
Do not force these meanings into physical form or anatomical-part facets.

Treat normalized signatures only as candidate generators. In particular,
`AOM_006500` is not a duplicate of `AOM_006231`: its governed preferred label
also specifies decortication and soaking. Keep model-gap clusters distinct until
corresponding model exists. Submit only exact, evidence-compatible duplicate
cases for explicit deprecation approval.

## Consequences

Remaining expert work becomes six design decisions plus cluster review. Existing
bulk assertions remain valid; governed-label changes regenerate additional
approved process assertions without changing identity.
