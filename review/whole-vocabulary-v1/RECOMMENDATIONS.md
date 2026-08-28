# Whole-vocabulary coverage and migration recommendations

Status: recommendation-only review for
[era-program #17](https://github.com/ERAgriculture/era-program/issues/17).

Decision proposal:
[ADR 0051](../../docs/decisions/0051-whole-vocabulary-resource-boundaries-and-migration-sequence.md).

Human decisions are recorded separately in the
[ADR 0051 acceptance pack](../whole-vocabulary-v3/README.md); this evidence
snapshot remains immutable and recommendation-only.

## Snapshot

AOM is not livestock shorthand. Current canonical workbook contains 33 sheets
and 19,845 nonblank structural rows. Twenty-three sheets are proposed public,
one location sheet remains under publication review, and nine operational,
restricted, legacy, documentation, or scratch sheets are excluded.

Current normalization is asymmetric:

- `AOM` contributes 2,503 normalized livestock source rows;
- `prac` contributes 196 normalized crop-practice source rows;
- `out` contributes 116 normalized crop-outcome source rows;
- no workbook resource has yet been normalized as `aom-core`;
- 11 of the 14 sheets currently inventoried as concept schemes have no
  normalized source-row output;
- `vars_animals` was reconciled but remains semantically unnormalized, so
  recent feed work does not complete livestock scope.

These counts measure source-resource coverage, not semantic completeness.
Generated concepts and reviewed overlays can make distribution row counts
larger than source-row counts.

## Main finding

Recent ERA-AOM work produced deep, governed livestock-feed review. That work is
valid but must remain one module cohort. It must not define AOM completion or
continue consuming the whole semantic queue while crop, shared-core,
non-feed-livestock, schema, code-list, and mapping resources remain mostly at
inventory stage.

Next semantic work should therefore move from feed-first cleanup to a
whole-vocabulary migration programme.

## Resource boundaries

Do not turn every workbook sheet or row into a SKOS concept.

| Resource shape | Governed target |
|---|---|
| Domain terms, identities, and navigation hierarchies | `aom-crop` or `aom-livestock` SKOS concepts plus reviewed AOM predicates |
| Demonstrated cross-domain semantics | `aom-core`, promoted only after crop/livestock comparison |
| Field registries, datatypes, cardinalities, and lookup assignments | `era-data` schema plus AOM semantic bindings and SHACL constraints |
| Reference code lists | Versioned `era-data` code-list distributions with external identifiers |
| Crosswalks and external alignments | Governed mappings with source, relation, evidence, reviewer, and status |
| Dataset, distribution, and release metadata | `era-data` DCAT/PROV catalog records |
| Operational source management | `era-data-pipeline`; never a public concept scheme by default |
| Restricted, legacy, and scratch material | Excluded evidence unless explicit rights and governance review approves promotion |

This changes several proposed inventory classifications. `AOM_diets`,
`ani_diet`, and `ani_process` should be treated as working subsets, assignments,
corrections, or crosswalk evidence into `aom-livestock`, not independent public
concept schemes. `era_fields_v1`, `era_fields_v2`, and `lookup_levels` are data
contracts, not agricultural concept hierarchies.

## Module priorities

### Shared model and data contracts

Formalize `era_fields_v2`, field-specific `lookup_levels`, and
`unit_harmonization` first. This establishes entities, fields, datatypes,
cardinalities, units, controlled-value bindings, and consumer contracts before
more vocabulary is normalized. Retain `era_fields_v1` only as migration history.

### Crop observation foundation

Review and promote the existing `prac` and `out` pilots, then integrate
`out_econ`. Preserve existing `era:*` identities unless governed migration
requires stable replacement links.

### Crop products and inputs

Review `prod`, `prod_comp`, and `residues` as one dependency chain. Then review
`fert` and `chem`. These source sheets mix identity, component, process,
composition, role, commercial product, active ingredient, and external mapping
columns; normalization requires decomposition rather than one-row/one-concept
conversion.

### Biological identity and traits

Review `trees`, `vars`, `vars_animals`, and `var_traits` across crop and
livestock. Separate taxon, cultivar, accession, breed, maturity, trait, and
practice context. Reuse WFO, NCBI, GBIF, and existing AOM identities only after
identity and mapping review.

### Livestock beyond feed

Complete ADR 0049 visual acceptance, then audit `AOM` by domain to quantify
animals, breeds, physiology, husbandry, pasture, outcomes, and remaining feed
coverage. Normalize supporting diet and process tables as evidence or mappings,
not sibling schemes. Explicitly close `vars_animals` gaps.

### Reference and context resources

Publish countries, journals, agroecological-zone codes, sites, units, and
remaining crosswalks through `era-data`. Complete location sensitivity review
before `site_list` publication. Keep `ssa_feedsdb` values excluded.

## Authority comparison

Full claim boundaries are recorded in
[`authority_comparison.csv`](authority_comparison.csv).

| Authority | Supports | Boundary |
|---|---|---|
| ERA ADR 0007 and canonical workbook inventory | Operational source content and lineage until cutover | Workbook layout does not determine target architecture |
| ERA ADR 0008 and `MODULES.md` | AOM umbrella with core, crop, livestock, and mappings products | Does not approve individual identities or parentage |
| Public AOM Livestock v2 | Livestock identifiers, hierarchy lineage, authorship, and DOI | Does not cover crop or make working diet tables independent schemes |
| [W3C SKOS](https://www.w3.org/TR/skos-reference/) | Concept schemes, labels, notations, relations, collections, and mappings | Not a field schema, catalog, or validation language |
| [W3C CSVW](https://www.w3.org/TR/tabular-data-model/) | Tables, columns, rows, cells, datatypes, and metadata | Does not establish agricultural identity |
| [W3C SHACL](https://www.w3.org/TR/shacl/) | RDF graph constraints and validation reports | Does not establish vocabulary authority |
| [W3C DCAT 3](https://www.w3.org/TR/vocab-dcat-3/) | Dataset, distribution, version, checksum, and catalog metadata | Does not replace source schemas or controlled vocabularies |

## Migration sequence

Eight bounded waves are recorded in
[`migration_waves.csv`](migration_waves.csv):

1. boundary governance;
2. data model and shared core;
3. crop observation foundation;
4. crop products and components;
5. crop inputs and chemicals;
6. biological identity and traits;
7. livestock non-feed completion;
8. reference context and crosswalks.

Waves express dependency order, not mandatory serial execution. Independent
review cohorts may run in parallel after their upstream contracts are accepted.

## Required gates

1. Human approval of ADR 0051 and resource-level routing.
2. Complete row inventory for each bounded source cohort before semantic edits.
3. Preferred, alternative, hidden, deprecated, and external-label collision
   audit across all modules before ID allocation.
4. Claim-level authority comparison and row-level dispositions with explicit
   holds.
5. Stable ID preservation and reviewed replacement links; no one-row/one-ID
   assumption.
6. Deterministic generation, schema and graph validation, and clean rebuild.
7. Consumer verification in `era-data-pipeline`, `era-data`, `eragri`, and
   `era-docs` for every changed contract.
8. Whole-vocabulary coverage report in each release; no claim of complete AOM
   migration while unresolved public/review resources remain.

## Evidence

- [Resource coverage matrix](resource_coverage.csv)
- [Migration waves](migration_waves.csv)
- [Authority comparison](authority_comparison.csv)
- [Claim-level evidence register](evidence_register.csv)
- [Machine summary](coverage_summary.json)
- [Canonical structural inventory](../../inventory/workbook_sheets.csv)

This review makes no hierarchy, schema, source-data, identifier, mapping,
release, publication, or canonical-cutover change.
