# Agricultural practice and outcome foundation governance

## Purpose

This method reviews `prac`, `out`, and `out_econ` before public semantic
promotion. It preserves decision and evidence trails while preventing source
hierarchy, labels, numeric formatting, or legacy mappings from becoming
unreviewed ontology assertions.

Method is recommendation-only. Output statuses are `proposed`, `held`, `open`,
or `pending`; never `approved`.

## Inputs

1. Canonical ERA master workbook and checksum.
2. Current `data/pilot` generated snapshot.
3. Current `data/livestock-staging` identity and mapping snapshot.
4. Pinned official AgrO `agro.owl` snapshot and checksum.
5. W3C SKOS and SOSA/SSN standards.
6. Crop Ontology, AGROVOC, FoodOn, and QUDT scope evidence.
7. FSDN, SEEA-AFF, and SNA accounting-boundary evidence.

Private absolute workbook paths are not committed. Evidence register records
governed source name, review date, and SHA-256 checksum.

## Source inventory

Read workbook cells without changing canonical source. Add one-based workbook
row number as provenance. Require exact expected columns for each source sheet.
Record row counts, unique source codes, unique normalized preferred labels,
missing definitions, and lifecycle counts.

One source row does not imply one public concept. `out_econ` placeholder AOM
values are retained as source evidence but never treated as identifiers.

## Normalization boundaries

Normalize Unicode, case, and whitespace only for collision discovery. Preserve
original labels and definitions in source. A normalized match is a review
signal, not an assertion.

Treat outcome codes as lexical identifiers even though workbook stores them in
numeric cells. Preserve displayed source notation. Never append `.0`, expose
binary floating representation, or allocate identifier from vector-wide numeric
formatting.

Treat literal `NA` in suffix and operational linkage columns as missing-value
sentinel. Proposed normalized value is null; raw cell remains available through
source provenance.

## Identity audit

For each source row, collect independently:

1. current pilot concept and path;
2. legacy AOM concepts mapped to same ERA code;
3. AOM concepts carrying same normalized English label;
4. AOM concepts carrying same normalized label and definition;
5. external exact-label candidates from pinned AgrO snapshot;
6. source lifecycle, domain, and semantic entity type.

Apply precedence:

- deprecated, undefined, unknown-status, placeholder, or ambiguous-code rows
  remain held;
- exact label-definition match creates stable AOM reuse candidate, not approval;
- one code mapping without compatible definition remains identity-review hold;
- same label with incompatible scope remains distinct-context hold;
- rows without candidates remain source candidates without public ID allocation.

Published AOM IDs are never deleted, reassigned, or duplicated when identity is
confirmed. Legacy `relatedMatch` and exact labels never establish equivalence by
themselves.

## Practice audit

Classify proposed modeling need, not final ontology class:

- agricultural practice concept;
- practice application occurrence;
- condition or baseline specification;
- treatment, comparator, or control role;
- derived comparison record;
- source field or context descriptor.

Conventional management may be valid practice identity and separately bear
comparator role. Absence or unspecified states require explicit condition
review. Preferred labels must not encode transient study role.

## Outcome audit

Review leaf rows as property specifications with possible decomposition into:

- `sosa:Property`;
- feature of interest;
- procedure or method;
- direct or derived measure;
- numerator, denominator, and formula;
- quantity kind, unit, scale, and basis;
- interpretation direction and analytical constraint;
- reporting collection membership.

Use Crop Ontology trait-method-scale pattern only where crop phenotype scope
fits. Use QUDT for reviewed quantity and unit bindings, not identity.

## Economic audit

Do not make accounting categories automatic semantic parents. Review each row
for economic property, category, object, transaction, actor, period, currency,
denominator, allocation basis, and valuation method. Resolve source-definition
defects and placeholder identifiers before ID allocation.

Fixed and variable treatment can depend on accounting context. Duplicate labels
such as `Equipment` require contextual decomposition or unambiguous scoped
labels.

## Hierarchy audit

Review every generated intermediate node and edge.

1. Theme, pillar, subpillar, and indicator default to editorial navigation.
2. Represent navigation through `skos:Collection` membership.
3. If generated parent and child share normalized preferred label, hold and
   collapse unless evidence establishes separate identities.
4. Practice groups may become concepts only after extensional review confirms
   true broader meaning.
5. No current pilot hierarchy edge is promoted automatically.

## Authority use

Record for every authority:

- supported claim;
- unsupported claim boundary;
- use in this review;
- stable evidence identifier and locator;
- access date or snapshot checksum.

External exact-label matching produces held candidates only. Definition,
scope, entity type, and relation type require human review before mapping.

## Reproducibility

Run:

```bash
python3 scripts/build_crop_foundation_review.py \
  --workbook /path/to/era_master_sheet.xlsx \
  --agro-snapshot /path/to/agro.owl
python3 tests/validate_crop_foundation_review.py
```

Run builder twice and compare output checksums. Validator requires all 377 rows,
109 generated nodes, 405 edges, explicit claim boundaries, no approved row
dispositions, and `implementation_authorized: false`.

## Human decision sequence

Use `review/crop-foundation-v1/guided_review.csv` in priority order. Record
reviewer, date, decision, and note in a later approval artifact; do not overwrite
recommendation evidence. Source corrections occur in canonical workbook, then
review is regenerated before semantic implementation.

Implementation needs separate ADR approval, explicit IDs and mappings, source
corrections, deterministic semantic rebuild, validation, consumer checks, and
guided browser acceptance.
