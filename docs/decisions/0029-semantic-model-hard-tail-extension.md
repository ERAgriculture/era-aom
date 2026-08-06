# ADR 0029: Semantic-model hard-tail extension

- Status: accepted
- Date: 2026-08-06
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Decision

Extend reusable feed-material facets only where remaining source labels express a
stable independent dimension absent from current model. Add flower, slurry form,
steeping, protein constituent, rhizome, liver, stacking, and
distillation. Allocate persistent IDs by appending after `AOM_101116`.

Reuse existing decompositions for haulm, juice, pollard, hash, and by-product
roles. Keep vein versus vine, cassava shaft, locally named materials, commercial
products, and generic source terms held. Never approximate rhizome as root or
infer product composition beyond explicit reviewed descriptors. Ingestion uses
structured assertions; labels and definitions are not reparsed.

`African Palm Larvae` remains held: plant-source mapping cannot identify larval
organism. No larval-biomass facet is approved from that evidence.
