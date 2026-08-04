# ADR 0007: Third reviewed source-taxon bindings

- Status: Accepted for staged migration
- Date: 2026-08-04
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Decision

Approve twenty-one species-level source-name bindings from review batch 3.
Replace two incorrect legacy targets: `Theba pisana` maps to
`NCBITaxon_145622`, not `NCBITaxon_2315439` (`Lissachatina fulica`), and
`Psophocarpus tetragonolobus` maps to `NCBITaxon_3891`, not
`NCBITaxon_3847` (`Glycine max`).

Preserve original source text while recording current accepted names for
`Opuntia ficus indica`, misspelled `Gliciridia sepium`, and synonym
`Pennisetum clandestinum`. These approved source-name decisions are explicit
exceptions; they do not authorize fuzzy matching or general spelling repair.
`Saccharomyces cerevisiae` is approved as fungal taxon without WFO assertion.

WFO reconciliation remains deferred. Matching remains exact after
whitespace/case normalization. Original source text remains available for
provenance and rollback.

## Consequences

Pipeline may populate `sourceTaxon` for forty-five governed biological source
names across three approved batches. Known non-taxa remain governed holds;
unknown names remain null and enter review. No new AOM IDs are minted.
Canonical cutover remains separately gated.
