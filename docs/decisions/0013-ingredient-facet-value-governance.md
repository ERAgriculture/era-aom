# ADR 0013: Ingredient facet value governance

- Status: Accepted for staged migration
- Date: 2026-08-05
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Decision

Create dedicated AOM livestock facet value vocabulary under five governed roots:
anatomical part, physical form, processing method, product role, and chemical
constituent. Allocate 55 sequential AOM identifiers from `AOM_101019` through
`AOM_101073`; type every concept with its semantic value class.

Approve 35 high-confidence atomic source-value mappings and 39 independently
typed assertions decomposing 17 high-confidence compound descriptors. Preserve
source text and material identity separately. Do not reuse equal labels from
incompatible legacy branches.

Keep 17 medium/low atomic values, 11 remaining composites, and three existing
holds without facet targets. `Oil Crude` remains pending despite high
classification confidence because `crude` describes state/grade more clearly
than a processing operation; classification does not justify assertion.

## Consequences

RDF distributions contain 372 validated semantic value bindings: 298 existing
value decisions plus 35 facet mappings and 39 decomposition assertions. SHACL
adds `decompose_to_existing` as target-required action. Pipeline may consume
exact contracts, but canonical cutover remains separately gated.

External ontology alignments remain later reviewed mappings. AOM identifiers
provide stable project semantics without claiming unverified equivalence to
Plant Ontology, FoodOn, ChEBI, or other external concepts.
