# ADR 0046: Ingredient descriptor lifecycle and browser deprecation

- Status: Accepted
- Date: 2026-08-13
- Owners: ERA-AOM semantic governance
- Tracking: [era-program #53](https://github.com/ERAgriculture/era-program/issues/53)
- Evidence: [Cohort B review](../../review/livestock-v32/RECOMMENDATIONS.md)

## Context

ADR 0044 approved retirement of `AOM_000531` through `AOM_000535` as
Feed-material browse concepts and retained their field semantics through formal
properties or quantified ingredient-component representation.

Implementation marks concepts `deprecated` but retains every
`skos:broader AOM_100850` relation. Livestock release serializer emits custom
`era:status` only. Skosmos 3.3 recognizes `owl:deprecated`, not custom status,
and its hierarchy query does not remove deprecated children automatically.

Phase-2 pipeline already treats IDs as compatibility contract keys. It does not
use their SKOS hierarchy. Consumer audit found no other exact implementation
consumer among named program repositories.

## Decision

### Lifecycle

1. Keep all five published IDs permanently resolvable.
2. Keep labels, notation, source definition, mappings, and governance evidence.
3. Mark them with both `era:status "deprecated"` and boolean
   `owl:deprecated true`.
4. Add explicit history notes describing normalized representation.
5. Remove them from active Feed-material hierarchy.
6. Do not create an active Ingredient descriptors/details/modifiers concept
   branch.

Approved retirement suppresses active incoming browse edges unless a separate
approved archival-navigation exception exists. Duplicate deprecation with a
replacement concept remains a separate lifecycle and may retain reviewed
hierarchy context.

### Browser policy

Retired schema identifiers remain:

- searchable by exact notation/label during compatibility window;
- directly resolvable indefinitely;
- visibly deprecated on concept cards;
- absent from active hierarchy.

Deployment declares `skosmos:showDeprecated` explicitly. Initial value
is `true` to honor searchable-ID compatibility; review after documented
consumer cutover. Clean-load acceptance must verify hierarchy and search
separately because Skosmos applies different queries.

### Semantic representation

| Legacy ID | Canonical representation | Required correction |
|---|---|---|
| `AOM_000531` | Canonical material `skos:prefLabel`; row-local source label on ingredient component/source record | Choose new source-label predicate or redefine `aom:ingredientName`; current FeedMaterial domain is wrong for pipeline use. |
| `AOM_000532` | Explicit component/form/process/role/constituent facets plus raw compatibility text | Scope `aom:legacyComponentDescriptor` to IngredientComponent and hide raw text outside review view. |
| `AOM_000533` | `aom:sourceTaxon` | Relabel "has source taxon"; distinguish canonical material facts from provisional row assertions. |
| `AOM_000534` | `aom:ingredientProportion` with QUDT quantity value | Require explicit unit and denominator basis; review DimensionlessRatio. |
| `AOM_000535` | Acquisition source relation | Relabel/redefine `aom:ingredientSource` for IngredientComponent or procurement assertion, not FeedMaterial identity. |

## Consequences

### Positive

- Feed-material hierarchy contains feed materials, not data-entry fields.
- Stable legacy IDs and evidence trail remain intact.
- Skosmos and other OWL-aware consumers receive interoperable deprecation.
- Feed-material cards expose meaningful normalized facets.
- Pipeline migration remains controlled and reversible.

### Costs

- Normalizer needs explicit retirement-navigation logic.
- Turtle, RDF/XML, JSON-LD, and browser tests need parity checks.
- `era-data-pipeline` pinned contract and semantic tables need reviewed update.
- AOM_000531 and AOM_000535 predicate naming choices need human approval.

## Alternatives considered

### Active Ingredient descriptors branch

Rejected. Improves visual grouping but continues treating schema fields as
domain concepts.

### Delete retired records

Rejected. Breaks published identifiers, source mappings, and auditability.

### Standard deprecation without edge suppression

Rejected. Skosmos 3.3 hierarchy still returns deprecated children.

### Edge suppression without standard deprecation

Rejected. Retirement remains invisible to interoperable consumers and cards.

## Implementation gates

1. Human approval of this ADR and every row disposition.
2. Governed source change; no direct distribution patch.
3. Explicit retirement browse-edge policy and exceptions.
4. `owl:deprecated true` parity across Turtle, RDF/XML, and JSON-LD.
5. Pipeline contract migration with rollback and source/output parity.
6. Clean graph replacement from empty or verified `PUT` baseline.
7. Skosmos checks for exact search, direct cards, deprecation warning, and
   absence beneath Feed materials.
8. Global collision, identifier, SHACL, release checksum, and full CI gates.

## Approval record

Pete Steward accepted this decision and all five Cohort B row dispositions on
2026-08-13. Acceptance authorizes implementation planning; ontology and
pipeline changes remain separate reviewed work.
