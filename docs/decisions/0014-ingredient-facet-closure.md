# ADR 0014: Ingredient facet decision closure

- Status: Accepted for staged migration
- Date: 2026-08-05
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Context

ADR 0013 deliberately deferred 31 lower-confidence source descriptors. Public
feed terminology alone could not resolve context-sensitive labels. Aggregate
private-release context was therefore reviewed without publishing source rows.

## Decision

Add 11 typed facet values while preserving every identifier allocated by ADR
0013. Approve 11 further atomic mappings and 26 assertions decomposing 11
further source descriptors. Record nine remaining ambiguous values as explicit
targetless `hold_ambiguous` decisions.

All 83 classified descriptors now have exactly one value-governance outcome:
46 atomic mappings, 28 decomposed descriptors containing 65 assertions, or nine
holds. Reclassify `Hash` from unresolved to composite because audited context
and published evidence identify potato-processing hash. Do not reclassify other
held values without a model or source-key change.

## Consequences

Facet vocabulary contains 66 concepts. Semantic distribution contains 418
value bindings: 298 earlier source/taxon decisions, 46 atomic facet mappings,
65 decomposition assertions, and nine holds. Canonical cutover remains false.

Source-only matching cannot safely map `Heads`, `Meal`, `Vine`, or other held
labels. Future resolution may require material-aware composite keys or new
facets for processing state/grade. External ontology alignment remains separate
reviewed work; evidence citations do not assert equivalence.
