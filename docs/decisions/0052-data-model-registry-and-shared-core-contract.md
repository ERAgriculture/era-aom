# ADR 0052: Data-model registry and shared-core contract

- Status: Accepted
- Date: 2026-08-24
- Accepted: 2026-08-28 by P. Steward
- Owners: ERA data-model and AOM semantic governance
- Tracking:
  [era-program #27](https://github.com/ERAgriculture/era-program/issues/27),
  [era-program #21](https://github.com/ERAgriculture/era-program/issues/21),
  [era-program #17](https://github.com/ERAgriculture/era-program/issues/17)
- Evidence:
  [Wave 1 data-model review](../../review/data-model-v1/RECOMMENDATIONS.md),
  [human acceptance record](../../review/data-model-v2/README.md)
- Method: [Data-model and shared-core contract review](../methods/data-model-and-shared-core-contract-review.md)
- Depends on:
  [AOM ADR 0051](0051-whole-vocabulary-resource-boundaries-and-migration-sequence.md),
  [ERA ADR 0007](https://github.com/ERAgriculture/era-program/blob/main/project-management/decisions/ADR-0007-canonical-vocab-source.md),
  [ERA ADR 0008](https://github.com/ERAgriculture/era-program/blob/main/project-management/decisions/ADR-0008-normalized-vocabulary-architecture.md),
  [AOM ADR 0001](0001-semantic-model-layers.md)

## Context

ADR 0051 routes `era_fields_v2` as schema, `lookup_levels` as mixed field-scoped
code-list source, and `unit_harmonization` as crosswalk. It makes formal data
model and shared-core contracts first implementation wave across whole AOM.

Current canonical field sheet contains 754 workbook rows but only 733 unique
valid table-field keys. Seventeen keys are duplicated, one populated field lacks
table identity, 270 populated fields lack descriptions, 117 lack datatypes, and
239 lack requiredness. Current generator publishes 750 field entries over those
733 keys and omits `courageous_camel_2024`, although 324 source field rows carry
that round.

`lookup_levels` contains 83 table-field pairs, but only 42 exactly match current
field keys. Current output exposes 399 allowed values on 43 field entries and
silently omits unmatched lookup pairs. `unit_harmonization` has 64 unresolved
rows and conflicting corrections for `ZMK/ha`; it carries labels rather than
reviewed unit identifiers, quantity kinds, or conversion semantics.

Current public agronomy and livestock product schemas each list 138 columns but
no descriptions. `eragri::ERA.Compiled` has 137 columns while package dictionary
contains 106 field names. Extraction source, analytical product, package, and
documentation contracts therefore cannot be treated as one schema.

Existing AOM semantic model has reusable-looking governance, observation,
quantity, and process scaffolds. Approved structural and value bindings remain
livestock scoped: 13 structural bindings, 298 value bindings, and no crop source
field binding. Generic names alone do not justify `aom-core` promotion.

## Decision

### Contract layers

ERA will govern separate, linked contract layers:

1. canonical workbook authoring records;
2. normalized table and logical-field registry;
3. extraction-round field profiles;
4. field-scoped value sets and members;
5. raw-to-canonical unit mappings;
6. AOM semantic bindings;
7. released product-field schemas;
8. release compatibility and consumer views.

Canonical workbook remains authority under ERA ADR 0007 until explicit cutover.
Workbook row shape is not target architecture.

### Stable field identity and lifecycle

Each logical field receives stable `field_id` linked to one stable `table_id`.
Current source table and field names remain governed labels and lineage.

Extraction-round differences in name, order, datatype, format, requiredness,
validation, and source presence belong in `field_profiles`. They do not create
duplicate logical field identities. Active, deprecated, replaced, and retired
states remain explicit and versioned.

All 21 current field-key issues require source disposition. Probable errors,
including duplicate `Irrig.Out.I.Date.Start` rows carrying Start/End labels, are
reviewed from source evidence and never auto-renamed from display text.

### Value-set relationships

Each approved field-scoped value set receives stable `value_set_id`; every
member receives stable code or value identity appropriate to its resource type.
Field-to-value-set relation uses stable keys, not table/field string coincidence.

Current 41 unmatched lookup pairs remain review cases. Candidate same-name
fields may guide review but cannot establish automatic joins. Every value set is
routed as concept scheme, reference code list, input enumeration, unit set, or
operational control before publication.

### Units and quantities

Raw unit strings are preserved unchanged. Canonical unit label, external unit
IRI, quantity kind, conversion factor, offset, denominator or composition basis,
effective context, evidence, reviewer, and status are separate governed fields.

Lexical correction does not imply numeric conversion. Missing or conflicting
unit mappings remain explicit holds. QUDT is preferred for covered physical
units and quantity kinds; uncovered currency, ratio, score, count, or contextual
agronomic units retain ERA mappings or reviewed alternative authorities.

### Extraction and product schemas

Extraction model and released analytical products are separate contracts.
Product schemas include source and derived fields, physical datatype,
description, derivation lineage, controlled values, quantity/unit contract,
release identity, and compatibility status.

Agronomy and livestock products may share a base profile, but identical current
physical schemas do not erase product-specific meaning. Every public product
column requires a reviewed description or explicit documented deferral.

### Publication forms

- CSVW metadata governs published tabular metadata, keys, foreign keys, and
  annotations.
- Frictionless Table Schema may provide portable JSON descriptors for tabular
  consumers.
- SHACL validates RDF semantic bindings and ontology-layer constraints.
- PROV-O and DCAT govern derivation, release, distribution, checksum, and
  version metadata.
- SKOS remains for governed concept schemes and mappings, not field definitions
  or every lookup value by default.

### Shared core

`aom-core` promotion requires demonstrated use and equivalent scope across crop
and livestock. Release/evidence governance, semantic-binding governance,
observation, and quantity scaffolds are candidates pending comparison.

Feed, formulation, additive, ingredient, feed role, feed form, feed composition,
and feed process classes remain in `aom-livestock`. Domain observable properties
and value concepts remain in their domain modules even when shared observation
scaffold is approved.

Future observation review uses current SOSA/SSN property model and does not add
new dependence on deprecated `sosa:ObservableProperty` class semantics.

### Consumer and closure gates

`era-data-pipeline` owns deterministic generation and drift failures.
`era-data` owns immutable published model, value-set, unit, product-schema, and
catalog artifacts. `eragri` owns release-pinned package compatibility.
`era-docs` owns generated human guidance. `era-aom` owns semantic model and
reviewed bindings. `era-program` closes issues only after all consumers align.

Existing v2026.1 remains immutable despite later canonical workbook changes.
Changed canonical source requires a new release version and explicit migration
report.

## Authority comparison

- ERA ADR 0007 establishes canonical workbook authority but not target schema
  architecture.
- AOM ADR 0051 establishes resource routing and migration order but not field,
  lookup, unit, or consumer dispositions.
- [W3C CSVW](https://www.w3.org/TR/tabular-metadata/) supports column metadata,
  datatypes, keys, foreign keys, annotations, and validation.
- [Frictionless Table Schema](https://specs.frictionlessdata.io/table-schema/)
  supports portable JSON field descriptors, constraints, primary keys, and
  foreign keys.
- [W3C SHACL](https://www.w3.org/TR/shacl/) supports RDF graph constraints, not
  raw product-schema authority.
- [W3C SOSA/SSN 2023](https://www.w3.org/TR/vocab-ssn-2023/) supports observation,
  feature, procedure, result, and property relations.
- [QUDT](https://www.qudt.org/catalog/qudt-catalog.html) supports quantity
  values, quantity kinds, units, dimensions, and conversion semantics.
- [W3C PROV-O](https://www.w3.org/TR/prov-o/) and
  [DCAT 3](https://www.w3.org/TR/vocab-dcat-3/) support provenance, dataset,
  distribution, version, and checksum metadata.

Full claim support and limitations are recorded in
[`authority_comparison.csv`](../../review/data-model-v1/authority_comparison.csv).

## Evidence

- [Wave 1 recommendations](../../review/data-model-v1/RECOMMENDATIONS.md)
- [Source contracts](../../review/data-model-v1/source_contracts.csv)
- [Field-key issues](../../review/data-model-v1/field_key_issues.csv)
- [Field quality metrics](../../review/data-model-v1/field_quality_metrics.csv)
- [Lookup binding audit](../../review/data-model-v1/lookup_binding_audit.csv)
- [Unit mapping audit](../../review/data-model-v1/unit_mapping_audit.csv)
- [Consumer comparison](../../review/data-model-v1/consumer_contract_comparison.csv)
- [Consumer differences](../../review/data-model-v1/consumer_contract_diffs.csv)
- [Semantic binding scope](../../review/data-model-v1/semantic_binding_scope.csv)
- [Shared-core boundaries](../../review/data-model-v1/shared_core_boundary.csv)
- [Recommendation register](../../review/data-model-v1/recommendation_register.csv)
- [Claim-level evidence register](../../review/data-model-v1/evidence_register.csv)
- [Machine summary](../../review/data-model-v1/review_summary.json)
- [Human decision approvals](../../review/data-model-v2/decision_approvals.csv)
- [Acceptance evidence register](../../review/data-model-v2/evidence_register.csv)
- [Acceptance summary](../../review/data-model-v2/acceptance_summary.json)
- [Source-disposition checkpoint](../../review/data-model-v3/README.md)
- [Field-key recommendations](../../review/data-model-v3/field_key_disposition_recommendations.csv)
- [Lookup-binding recommendations](../../review/data-model-v3/lookup_binding_disposition_recommendations.csv)
- [Source-disposition summary](../../review/data-model-v3/disposition_summary.json)

## Human decision

P. Steward accepted `DM-01` through `DM-12` on 2026-08-28. Acceptance approves
the registry architecture, source-disposition work, publication forms,
consumer-compatibility gates, and evidence conditions described above.

Acceptance retains 21 field-key, 41 unmatched lookup, 64 unresolved unit, and
two conflicting-unit review cases. It requires complete documentation or
reviewed deferral for each 138-column public product schema and crop-and-livestock
evidence before shared-core promotion.

Acceptance does not edit the canonical workbook, allocate stable keys,
regenerate schemas, promote shared-core resources, mutate `v2026.1`, publish a
new release, migrate consumers, or close programme issues.

## Source-disposition checkpoint

All 21 field-key issues and 41 unmatched lookup pairs are classified for one
human review cohort. Thirteen duplicate field keys with disjoint round coverage
are recommended for one logical identity plus round-specific profiles. Eight
field cases remain held: three overlapping duplicate keys, three blank-field
rows, one irrigation date-key conflict, and one missing-table row.

All 41 unmatched lookup pairs remain held. Thirty-nine have no candidate field
key; two have one same-field candidate under a different table but require
source identity and value-scope review. No fuzzy or automatic binding is
recommended.

This checkpoint records no human decision, source edit, stable-key allocation,
binding, schema regeneration, release, or consumer migration.

## Consequences

### Positive

- Field identities remain stable while extraction-round variation stays
  explicit.
- Lookup relationships and unit mappings stop depending on fragile labels.
- Extraction and product schemas become intelligible and independently
  versioned.
- Package and documentation drift becomes testable.
- Shared core grows from cross-domain evidence, not livestock-first naming.
- Issue closure requires end-to-end consumer parity rather than one generated
  JSON artifact.

### Costs

- Canonical workbook needs 21 field-key and 41 lookup-key dispositions before
  clean normalization.
- Complete product dictionaries need human descriptions and derivation review.
- Unit work requires authority and conversion-basis review beyond string cleanup.
- Pipeline, data, package, docs, and ontology repositories need coordinated but
  bounded PRs.
- Some current documentation claims must be narrowed until implementation lands.

## Alternatives considered

### Treat current generated JSON as completed formal model

Rejected. It omits one extraction round, preserves duplicate logical keys,
exposes only part of lookup source, omits units, and does not model lifecycle or
relationships.

### Use one schema for extraction, agronomy, livestock, and package data

Rejected. Source tables and analytical products have different identities,
derived fields, release histories, and consumer obligations.

### Inline every allowed value in each field schema

Rejected. This duplicates value-set identity, obscures reuse and lifecycle, and
cannot repair stale field keys.

### Convert every lookup value and unit into AOM concept

Rejected. Interface enumerations, units, code lists, operational controls, and
domain concepts require different authorities and publication forms.

### Move generic-looking livestock schema classes directly to shared core

Rejected. Cross-domain scope requires crop and livestock evidence; label
generality is insufficient.

### Overwrite v2026.1 from current workbook

Rejected. Immutable release provenance must be preserved; changed source creates
new release.

## Implementation gates

1. Human approval of ADR 0051 and ADR 0052. ADR 0052 accepted; ADR 0051
   remains pending.
2. Reviewed disposition for every field-key and lookup-key issue.
3. Stable identifiers and foreign-key-valid normalized registry.
4. Four-round field-profile completeness and explicit lifecycle.
5. Governed outcome for every unit row without inferred conversion.
6. Separate extraction and product schemas with derivation lineage.
7. Complete 138-column product dictionaries or explicit reviewed deferrals.
8. Release-pinned package and documentation consumers.
9. Crop and livestock evidence for every shared-core promotion.
10. Deterministic rebuild, source fingerprints, cross-repository compatibility
    report, and green contract tests.

## Approval record

Accepted by P. Steward on 2026-08-28 with conditions and holds recorded in the
[acceptance pack](../../review/data-model-v2/README.md). Acceptance allocates no
identifier and changes no workbook source, schema, hierarchy, binding, mapping,
generated distribution, package object, release, or publication status.
