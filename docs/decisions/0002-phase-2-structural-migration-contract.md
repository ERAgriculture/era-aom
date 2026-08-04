# ADR-0002: Phase-2 structural migration contract

- Status: accepted
- Date: 2026-08-04
- Decision owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward
- Scope: 13 approved AOM Livestock v2 remodeling cases

## Context

Legacy AOM Livestock represents some record fields and measurements as nodes in
its SKOS hierarchy. That representation preserves codes and browsing paths, but
does not tell software where values belong, what kind of value is expected, or
how a number and its unit travel together. It also makes downstream AI and data
integration depend on label interpretation.

ADR-0001 selected a layered model: SKOS for knowledge organization, OWL for
domain structure, SOSA/SSN for observations, QUDT for quantities and units,
SHACL for validation, and JSON-LD/Turtle for exchange. This decision turns the
13 phase-2 dispositions into a governed, machine-readable contract.

## Decision

`approved_semantic_bindings.csv` is the authoritative governance overlay for
phase-2 structural migration. Generation publishes equivalent JSON-LD and
Turtle contracts. Each binding records legacy concept, binding kind, target
class and property, value class, quantity kind, unit requirement, compatibility
policy, approval, reviewer, date, and evidence case.

Four field-like concepts become explicit `aom:FeedMaterial` properties:

| Legacy concept | Normalized use |
|---|---|
| AOM_000531 Ingredient name | `aom:ingredientName` |
| AOM_000532 Ingredient part | `aom:ingredientPart` |
| AOM_000533 Ingredient species | `aom:sourceTaxon` |
| AOM_000535 Ingredient source | `aom:ingredientSource` |

AOM_000534 Ingredient proportion becomes a `qudt:QuantityValue` reached through
`aom:IngredientComponent` and `aom:ingredientProportion`. Its quantity kind is
dimensionless and each migrated value must state a unit, such as percentage or
a dimensionless ratio unit.

Eight quantitative concepts remain at their existing AOM URIs and gain
`sosa:ObservableProperty` type. Values become `aom:QuantitativeObservation`
records with `sosa:observedProperty` and a QUDT quantity result. Binding rows
state broad quantity kinds—ratio, length, area, time, or count—while each record
states its actual QUDT unit.

## Compatibility and cutover

No legacy URI is removed or redirected in this phase. Property-like concepts
remain active until consumer cutover; observable-property concepts remain SKOS
concepts and gain a second semantic type.

During pipeline migration, producers must dual-publish:

1. Existing source code/column, unchanged, for rollback and parity checks.
2. Normalized semantic record conforming to this binding contract.
3. Source-row provenance linking both representations.

Deprecation of property-like legacy concepts requires consumer inventory,
successful full pipeline regeneration, value and row-count parity, validation,
rollback inputs, release notes, and explicit canonical-cutover approval. This
ADR does not grant that approval.

## Why this form

- Stable identifiers preserve citations, links, and existing integrations.
- Explicit classes and properties remove label-dependent interpretation.
- SOSA and QUDT make observations, values, quantity kinds, and units portable.
- SKOS plus `sosa:ObservableProperty` supports vocabulary browsers and data APIs.
- CSV supports stewardship; JSON-LD and Turtle support graphs, APIs, and AI tools.
- SHACL makes contract violations testable before ingestion or release.
- Broad quantity kinds permit future units without changing vocabulary codes.

## Alternatives rejected

- **Keep every item only as SKOS:** preserves browsing but leaves value structure
  implicit.
- **Mint replacement identifiers immediately:** causes avoidable integration
  breakage and weakens traceability.
- **Encode units in labels or columns:** cannot represent mixed units safely and
  is hard to validate.
- **Require one unit per concept:** blocks valid local measurement practice and
  future unit choices.
- **Replace AOM with an external ontology:** loses ERA-owned governance and does
  not cover all crop and livestock requirements. External mappings remain a
  later governed phase, including TerminAg alignment.

## Consequences

Short-term pipeline work increases because values must move into normalized
records and old/new outputs must coexist. In return, migration becomes explicit,
testable, reversible, standards-aligned, multilingual-ready, and usable by
semantic search, knowledge graphs, validation agents, and AI systems without
guessing meaning from labels.

## Artifacts and verification

- `data/livestock-staging/approved_semantic_bindings.csv`
- `schemas/owl/aom-semantic-model.ttl`
- `schemas/shacl/semantic-model.ttl`
- `dist/livestock-staging/aom-semantic-bindings.jsonld`
- `dist/livestock-staging/aom-semantic-bindings.ttl`
- `tests/validate_semantic_model.py`

Next implementation PR belongs in `era-data-pipeline`: consume this contract,
dual-publish old and normalized representations, and produce parity evidence.
