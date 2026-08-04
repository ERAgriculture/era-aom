# ADR 0003: Govern ingredient-source value bindings

- Status: Accepted
- Date: 2026-08-04
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Context

Phase-2 defines `aom:ingredientSource` as normalized feed-material structure,
but a property alone does not govern values entering it. Existing AOM livestock
work already contains `On-farm` (`AOM_000141`) and `Purchased` (`AOM_000142`)
under `Management / Livestock Management / Feed Management / Diet Source`.
Reusing these identifiers preserves that work and avoids parallel terms.

`Unspecified` is different. It may mean absent, unknown, not collected, or not
applicable. Four existing AOM concepts share that label, so automatic identity
would erase meaning and create unstable data.

## Decision

Define `aom:IngredientSourceCategory` as a SKOS-compatible value class and set
it as range of `aom:ingredientSource`. Publish reviewed, machine-readable value
bindings beside structural bindings:

| Source value | Decision | Target |
|---|---|---|
| On-farm | map to existing | `AOM_000141` |
| Purchased | map to existing | `AOM_000142` |
| Unspecified | hold ambiguous | none |

Ingestion may emit mapped concept IRIs only for approved `map_to_existing`
rows. `hold_ambiguous` produces no concept assertion; source text may remain in
legacy/audit data. This is a semantic-null decision, not a new concept request.

CSV is governance source. Deterministic JSON-LD and Turtle are exchange forms.
OWL declares vocabulary semantics; SHACL rejects mapped bindings without a
target and held bindings with one. No new AOM identifiers are allocated.

## Consequences

- Consumers get stable IRIs instead of free-text source categories.
- Existing AOM livestock work remains authoritative for exact matches.
- Ambiguity stays visible and reversible rather than becoming false knowledge.
- Future crop integration can add reviewed mappings without changing property
  semantics or current identifiers.
- Ingredient-part and taxon bindings remain deferred pending expert review;
  superficial label matches are insufficient evidence.
- Future terminology alignment, including controvoc/terminag, and multilingual
  labels remain planned extension points, not current dependencies.

## Rejected alternatives

- Mint three new ERA concepts: duplicates approved AOM concepts and invents a
  meaning for `Unspecified`.
- Store all values as strings: weak interoperability and machine validation.
- Guess among same-label concepts: nondeterministic and scientifically unsafe.
