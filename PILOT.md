# AOM crop practice and outcome normalization pilot

## Purpose

This pilot tests AOM crop-module architecture selected by ADR-0008. It does not
change canonical source: workbook remains authoritative until full migration
and consumer cutover. Existing AOM livestock work remains separate and
preserved pending module comparison.

## Model

| Table | Role |
|---|---|
| `schemes.csv` | vocabulary schemes |
| `id_registry.csv` | permanent allocation of intermediate hierarchy IDs |
| `concepts.csv` | identity, scheme, type, notation, status, provenance row |
| `labels.csv` | preferred/alternative labels with BCP-47 language tags |
| `definitions.csv` | definitions and language |
| `notes.csv` | typed notes and language |
| `relations.csv` | explicit broader hierarchy |
| `properties.csv` | typed ERA-specific attributes |
| `source_records.csv` | leaf concept to legacy source-row linkage |

Practice hierarchy: theme → practice → subpractice.

Outcome hierarchy: pillar → subpillar → indicator → subindicator.

## Identifiers

- Leaf practice: `era:practice:{Code}`.
- Leaf outcome: `era:outcome:{Code}`.
- Intermediate concepts: opaque sequential identifiers allocated through
  `id_registry.csv`.
- Registry entries persist when concepts disappear; identifiers are never
  reused.
- Existing crop-lineage `era:*` IDs remain stable.
- Semantic pilot files express IDs as `urn:era:*`.
- Public resolvable HTTPS namespace remains deferred. Pilot URNs must not be
  advertised as permanent public concept URLs.

## Source-preserving normalization

Generator reads every source cell as text, then:

- converts CRLF/CR line endings to LF;
- removes trailing spaces at line boundaries while preserving text and
  indentation;
- normalizes eight binary floating-point artifacts in outcome codes to visible
  decimal forms, such as `150.19999999999999` → `150.2`;
- separates repeated hierarchy labels and codes into parent concepts;
- retains legacy leaf attributes in typed property rows;
- retains original workbook row linkage without publishing workbook path or
  fingerprint.

Legacy reconstruction passes after declared line-ending and numeric-code
normalization:

- `prac`: 196/196 rows, all 14 columns;
- `out`: 116/116 rows, all 20 columns.

## Pilot totals

- 2 schemes;
- 421 concepts;
- 109 persistent intermediate-ID registry entries;
- 656 SKOS-consistent labels;
- 311 definitions;
- 162 notes;
- 405 broader relations;
- 1,874 typed properties;
- 312 source-record links.

Concept status:

- practice: 257 active, 16 deprecated, 1 unknown;
- outcome: 144 active, 3 deprecated.

## Standards outputs

- normalized UTF-8 CSV sources;
- CSVW metadata;
- JSON Schema for concept rows;
- SKOS JSON-LD and Turtle;
- SHACL concept shapes;
- automated table, RDF parse, and SHACL validation.

## Regeneration

```sh
Rscript scripts/generate_pilot.R /path/to/era_master_sheet.xlsx data/pilot
Rscript tests/validate_pilot.R data/pilot
Rscript tests/check_roundtrip.R /path/to/era_master_sheet.xlsx
Rscript scripts/build_semantic.R data/pilot dist/pilot
```

## Approval meaning

Pilot approval confirms AOM crop-module normalized architecture, ID rules,
generated formats, and migration method. It does not approve livestock
integration, shared-core design, or canonical cutover. Every approved public
resource and live consumer still requires migration and parity testing.
