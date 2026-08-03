# Agriculture Ontology for Meta-analysis

Agriculture Ontology for Meta-analysis (AOM): shared semantic framework and
controlled vocabularies for integrating agricultural research evidence.

AOM began as a livestock prototype built from Evidence for Resilient
Agriculture data. This repository preserves that lineage while extending AOM
with crop modules. Livestock and crop work remain distinct modules until
reviewed mappings justify shared concepts.

## Status

Migration in progress. The authoritative source remains the controlled master
workbook until every cutover gate in
[`MIGRATION.md`](MIGRATION.md) passes and the designated approver accepts the
cutover.

Current work:

1. freeze and profile authoritative ERA workbook;
2. pilot normalized crop `prac` and `out` sources;
3. inventory and preserve existing AOM livestock assets;
4. design shared core from evidence, not forced merging;
5. migrate every approved public resource;
6. regenerate and validate downstream artifacts;
7. cut over only after pipeline and package parity.

Crop `prac` and `out` pilot design and validation:
[`PILOT.md`](PILOT.md).
Module boundaries and existing AOM lineage: [`MODULES.md`](MODULES.md).
Published livestock v2 reconciliation:
[`inventory/AOM_LIVESTOCK_RECONCILIATION.md`](inventory/AOM_LIVESTOCK_RECONCILIATION.md).
Normalized livestock review staging:
[`data/livestock-staging/README.md`](data/livestock-staging/README.md).
Contribution and review workflow: [`CONTRIBUTING.md`](CONTRIBUTING.md).
Persistent identifier allocation policy: [`IDENTIFIERS.md`](IDENTIFIERS.md).
Livestock domain-review pack:
[`review/livestock-v2/README.md`](review/livestock-v2/README.md).

No workbook content is published during inventory. This protects closed and
unreviewed sheets while recording reproducible structural metadata.

## Licensing

- Ontology/vocabulary sources, releases, and documentation: CC BY 4.0.
- Build and validation tooling: Apache-2.0.

See [`LICENSE.md`](LICENSE.md), [`LICENSE-CODE`](LICENSE-CODE), and
[`NOTICE`](NOTICE).

## Attribution

AOM is maintained and published by the Alliance of Bioversity International
and CIAT. Existing livestock AOM authorship and DOI provenance remain explicit.
Crop-module development builds on collaborative Evidence for Resilient
Agriculture work across CGIAR centres and partner institutions.
