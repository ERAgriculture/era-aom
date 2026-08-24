# Data-model and shared-core contract review

## Purpose

Audit ERA field, lookup, unit, semantic, product, package, and documentation
contracts together before implementing ADR 0051 Wave 1. Preserve source
authority and expose cross-repository drift without manufacturing semantics.

## Scope

Inputs:

- canonical workbook `era_fields_v2`, `lookup_levels`, and
  `unit_harmonization` sheets;
- `era-data` model, product schemas, and vocabulary manifest;
- `era-data-pipeline` model generator;
- `eragri` compiled snapshot and field dictionary;
- AOM OWL/SHACL model plus approved structural and value bindings;
- `era-docs` data-model and access guidance;
- current era-program issues #27 and #21.

This method distinguishes:

1. canonical authoring records;
2. normalized logical extraction model;
3. extraction-round field profiles;
4. field-scoped value sets and units;
5. RDF semantic bindings;
6. released analytical product schemas;
7. package and documentation consumer views.

## Reproduction

Requirements: R, `data.table`, `digest`, `jsonlite`, and `readxl`; local
read-only checkouts of `era-data`, `era-data-pipeline`, `eragri`, and `era-docs`;
canonical workbook access.

```bash
Rscript scripts/build_data_model_core_review.R \
  --master=/path/to/era_master_sheet.xlsx \
  --era-data=/path/to/era-data \
  --pipeline=/path/to/era-data-pipeline \
  --eragri=/path/to/eragri \
  --era-docs=/path/to/era-docs \
  --out=review/data-model-v1
python tests/validate_data_model_core_review.py
```

Generator records workbook hashes, repository commits or source-file hashes,
row/key counts, source-row references, and output hashes. Never publish local
absolute paths or workbook cell values beyond reviewed audit fields.

## Field audit

1. Count workbook rows separately from populated field rows.
2. Require both table and field identity for a valid logical key.
3. Detect duplicate table-field keys and preserve source-row plus extraction
   round profiles.
4. Treat duplicates as review cases, not automatic errors: they may represent
   round variants, accidental copies, or source-key defects.
5. Record missing descriptions, datatypes, requiredness, and extraction-round
   coverage.
6. Compare generated field entries and unique keys to canonical source.
7. Fail future generators when one populated field is silently omitted or one
   extraction round disappears.

## Lookup audit

1. Group lookup rows by declared table and field.
2. Compare exact composite keys to field registry.
3. Record same-field candidate keys only as review aids.
4. Never fuzzy-join or infer table identity from field label.
5. Give each approved value set stable identity independent of field label.
6. Classify publication function before routing values to SKOS, code-list,
   enumeration, unit, or operational products.

## Unit audit

1. Preserve source row, raw label, and corrected label.
2. Detect blank corrections, repeated raw labels, and conflicting corrections.
3. Distinguish identity-label and normalized-label mappings.
4. Leave canonical URI empty until authority, quantity kind, and context are
   reviewed.
5. Record numeric transformation separately from lexical normalization,
   including factor, offset, denominator/basis, effective context, evidence,
   and reviewer status.
6. Never infer dimensions or convert values from string similarity.

## Consumer audit

1. Compare extraction source, derived model, agronomy product schema, livestock
   product schema, package data, and package dictionary as separate contracts.
2. Compare field counts, unique names, descriptions, versions, and explicit
   additions/removals.
3. Do not assume package and public data represent same release without release
   provenance.
4. Require complete product-field dictionaries for released columns, including
   derived-field lineage.
5. Keep immutable release source fingerprint visible; changed canonical source
   requires a new release, never an in-place rebuild.

## Shared-core audit

1. Inventory generic-looking AOM schema families and approved bindings.
2. Separate generic vocabulary from demonstrated cross-domain use.
3. Require crop and livestock evidence for every shared-core promotion.
4. Keep feed-specific classes and concepts in `aom-livestock`.
5. Preserve domain concepts when a generic observation, quantity, provenance,
   or binding scaffold becomes shared.
6. Apply SHACL after RDF promotion; tabular schema standards govern source and
   product tables instead.

## Evidence rules

- Every claim has source evidence and limitation.
- Every recommendation names repository owner and acceptance evidence.
- Source row references are preserved for correction review.
- External authorities support only stated modeling claims.
- Recommendation artifacts authorize no semantic changes or identifiers.
- Re-run extraction after source or consumer change; changed metrics require
  reviewed evidence updates.

## Completion gate

Wave 1 implementation is complete only when:

- logical field keys are unique and round profiles are complete;
- every lookup pair has an explicit governed outcome;
- every unit row has governed mapping status;
- extraction and product schemas are separate and versioned;
- every released product column is documented;
- package and docs consumers pin release and pass compatibility tests;
- shared-core promotions have crop and livestock evidence;
- source, generated, released, package, and documentation counts reconcile.
