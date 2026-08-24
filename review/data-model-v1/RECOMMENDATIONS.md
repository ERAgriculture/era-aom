# Wave 1 data-model and shared-core review

## Status

Recommendation-only review for ADR 0051 Wave 1. It changes no ontology
hierarchy, semantic binding, source workbook, released schema, package object,
identifier, or publication artifact.

## Decision summary

ERA needs two related but distinct contracts:

1. a normalized extraction-model registry describing source tables, logical
   fields, round-specific profiles, value sets, units, relationships, and
   semantic bindings;
2. separate product-schema registries describing each released analytical
   product, including derived fields and consumer compatibility.

Current `era_fields_v2` must remain canonical authoring authority until governed
cutover, but its workbook rows are not yet a unique relational model. Current
`era_data_model.schema.json` is a useful publication prototype, not completion
of [era-program #27](https://github.com/ERAgriculture/era-program/issues/27).
Current 138-column product schemas are useful physical inventories, not a
complete data dictionary for
[era-program #21](https://github.com/ERAgriculture/era-program/issues/21).

## Key findings

### Field registry

- Canonical `era_fields_v2` has 754 workbook rows, 751 populated field rows, 750
  rows with both table and field, and only 733 unique table-field keys.
- Seventeen logical keys are duplicated. Many encode extraction-round variants
  and should become one stable field identity plus separate field profiles.
- One populated `Time` field lacks table identity and is silently lost by the
  current generator. Three workbook rows have no field value and need an
  explicit row role.
- `Irrig.Out.I.Date.Start` occurs twice with display labels `Date Start` and
  `Date End`. This is a probable source-key defect, but review must approve any
  correction rather than deriving identity from display text.
- 270 populated field rows lack descriptions, 117 lack datatypes, and 239 lack
  requiredness metadata.
- Canonical workbook has 324 fields marked for `courageous_camel_2024`; current
  generator hard-codes only three earlier rounds.
- Published model has 45 tables, 750 field entries, and 733 unique field keys.
  It retains duplicate logical fields, exposes only three extraction rounds,
  and does not publish units despite documentation claiming unit coverage.

See
[`field_key_issues.csv`](field_key_issues.csv) and
[`field_quality_metrics.csv`](field_quality_metrics.csv).

### Lookup relationships

- `lookup_levels` has 682 rows across 83 table-field pairs.
- Only 42 pairs exactly match current field-registry keys; 41 pairs are omitted
  by the generator's exact label join.
- Published output places 399 allowed values inline on 43 field entries. It
  therefore duplicates one logical field's value set and loses most source
  lookup rows.
- A value set needs its own stable identity and explicit `field_key` binding.
  Same-label candidate fields may support review, but never automatic fuzzy
  joining.
- Lookup rows must be routed by function: agricultural concepts, reference code
  lists, user-interface enumerations, units, and operational controls are not
  one undifferentiated SKOS hierarchy.

See [`lookup_binding_audit.csv`](lookup_binding_audit.csv).

### Units

- `unit_harmonization` has 1,105 rows and 1,103 distinct raw labels.
- Sixty-four rows have no canonical correction.
- `ZMK/ha` has conflicting corrections `ZMK/ha` and `ZMW/ha`; contextual or
  temporal review is required before choosing either.
- Remaining rows comprise 404 nonconflicting identity labels and 635 normalized
  labels. None has a reviewed canonical unit URI in this source.
- Raw label, canonical label, quantity kind, unit identifier, conversion rule,
  factor, offset, denominator/basis, effective context, evidence, and review
  status are separate assertions. Label normalization alone must not imply
  numeric conversion.
- QUDT is preferred for covered physical units and quantity kinds. Currency,
  contextual ratios, scores, counts, and agronomic application bases may need
  ERA-governed mappings or additional authorities.

See [`unit_mapping_audit.csv`](unit_mapping_audit.csv).

### Product and consumer contracts

- Published agronomy and livestock schemas each contain 138 unique columns and
  zero populated descriptions. Their names and physical types are identical.
- `eragri::ERA.Compiled` currently has 137 columns. Its dictionary contains 106
  field names, including pattern aliases and naming drift.
- Audit records 44 explicit package/schema/dictionary differences. Package
  snapshot may intentionally represent another release; missing release
  provenance makes that distinction untestable.
- Extraction tables and compiled analytical products are different models.
  Derived columns such as effect sizes, environmental enrichments, and expanded
  practice columns need product-level provenance rather than forced placement
  in extraction source tables.
- Immutable v2026.1 records workbook MD5
  `dfb9129e4001227ca85d566f913aacee`; current canonical workbook is
  `cb5d54c4bce97e23832b782cdebd8931`. This is expected lineage drift, not
  permission to overwrite v2026.1. A new approved source state requires a new
  release version.

See
[`consumer_contract_comparison.csv`](consumer_contract_comparison.csv),
[`consumer_contract_diffs.csv`](consumer_contract_diffs.csv), and
[`source_contracts.csv`](source_contracts.csv).

### Shared core

- Existing AOM semantic schema includes potentially reusable release,
  provenance, semantic-binding, observation, quantity, and process scaffolds.
- Approved structural contract has 13 livestock feed or grazing bindings;
  approved value contract has 298 livestock/feed rows. No crop source field is
  yet governed by those contracts.
- Generic class names do not prove shared scope. Feed, formulation, additive,
  ingredient, feed role, feed form, feed composition, and feed-process semantics
  remain in `aom-livestock`.
- Release/evidence governance, semantic-binding governance, observation, and
  quantity patterns are `aom-core` candidates. Promotion requires crop and
  livestock evidence plus explicit module review.
- Use current SOSA/SSN property model during review; do not build new assumptions
  around deprecated `sosa:ObservableProperty` class usage.

See
[`semantic_binding_scope.csv`](semantic_binding_scope.csv) and
[`shared_core_boundary.csv`](shared_core_boundary.csv).

## Target contract

Publish separate governed resources with stable identifiers and foreign keys:

| Resource | Required identity and content |
|---|---|
| `tables` | `table_id`, source name, title, description, lifecycle, domain, provenance |
| `fields` | `field_id`, `table_id`, canonical name, datatype, description, lifecycle |
| `field_profiles` | `field_id`, extraction round, source column, requiredness, format, validation, order |
| `value_sets` | `value_set_id`, function, scope, lifecycle, target publication form |
| `value_set_members` | `value_id`, `value_set_id`, code, label, definition, lifecycle, provenance |
| `field_value_sets` | `field_id`, `value_set_id`, binding status, effective rounds |
| `unit_mappings` | raw label, canonical label/IRI, quantity kind, transformation/basis, evidence, status |
| `semantic_bindings` | release, dataset, table, field/value key, target property/class/concept, evidence, status |
| `product_fields` | product/release ID, output field, type, description, derivation, controlled values, source lineage |
| `compatibility` | source and target releases, rename/add/remove/type change, migration action |

Logical `field_id` is stable across extraction rounds. Round-specific names,
requiredness, formats, and validation belong in `field_profiles`; they do not
create duplicate logical fields. Product fields have separate identities and
may link to one or more extraction fields or derivation rules.

CSVW metadata should describe published tables and foreign keys. Frictionless
Table Schema may provide portable JSON descriptors for product consumers.
SHACL validates RDF semantic bindings and ontology-layer constraints. None of
these standards substitutes for agricultural identity review.

## Cross-repository sequence

1. **Approve ADR 0052** without changing source semantics.
2. **Canonical workbook:** disposition all 21 field-key issues and 41 unmatched
   lookup pairs; preserve reviewed history.
3. **era-data-pipeline:** build normalized registries and fail on duplicate
   logical keys, omitted rounds, dangling lookups, unresolved release lineage,
   and source drift.
4. **era-aom:** approve shared-core candidates only after crop/livestock
   comparison; bind stable data-model keys without moving domain concepts.
5. **era-data:** publish a new immutable model/vocabulary release plus complete
   agronomy and livestock product schemas.
6. **eragri:** pin package data and generated dictionary to a declared release;
   publish compatibility profile.
7. **era-docs:** replace current claims with generated counts, complete field
   descriptions, lookup links, and version-specific limitations.
8. **era-program:** close issues #27 and #21 only after cross-repository parity
   and consumer tests pass.

Full action and acceptance criteria are in
[`recommendation_register.csv`](recommendation_register.csv).

## Authority comparison

[`authority_comparison.csv`](authority_comparison.csv) records support and
limitations for ERA authority decisions, CSVW, Frictionless Table Schema,
SHACL, SOSA/SSN, QUDT, PROV-O, and DCAT 3.

## Evidence

- [Source contract inventory](source_contracts.csv)
- [Field-key issues](field_key_issues.csv)
- [Field quality metrics](field_quality_metrics.csv)
- [Lookup binding audit](lookup_binding_audit.csv)
- [Unit mapping audit](unit_mapping_audit.csv)
- [Consumer comparison](consumer_contract_comparison.csv)
- [Consumer differences](consumer_contract_diffs.csv)
- [Semantic binding scope](semantic_binding_scope.csv)
- [Shared-core boundaries](shared_core_boundary.csv)
- [Recommendation register](recommendation_register.csv)
- [Authority comparison](authority_comparison.csv)
- [Claim-level evidence register](evidence_register.csv)
- [Machine summary](review_summary.json)

## Review limits

- No duplicate field rows are merged automatically.
- No missing table, lookup relation, datatype, requiredness, or unit is inferred.
- No unit conversion or QUDT mapping is proposed from labels alone.
- No package snapshot is declared wrong solely because it differs from current
  public release.
- No generic semantic class is promoted into `aom-core` from name alone.
- No current immutable release is rebuilt from changed canonical source under
  the same version.
