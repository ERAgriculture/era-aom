# AOM migration

Normalized sources are not canonical yet. Workbook remains authoritative during
transition.

## Phases

1. Freeze and profile all 33 workbook sheets.
2. Pilot normalized crop `prac` and `out`.
3. Inventory published livestock AOM and reconcile it with AOM-family workbook
   sheets without merging crop/livestock hierarchies.
4. Propose shared `aom-core` concepts only where comparison proves common
   identity.
5. Migrate every approved public concept scheme, code list, crosswalk, and
   data-model table.
6. Generate standards-based and analyst-ready distributions.
7. Replace ingestion and package readers.
8. Validate clean-build reproducibility and consumer parity.
9. Obtain canonical-cutover approval.

Phase-2 livestock structural contract is defined in
[`docs/decisions/0002-phase-2-structural-migration-contract.md`](docs/decisions/0002-phase-2-structural-migration-contract.md).
It does not itself authorize canonical cutover or concept deprecation.

## Cutover rule

Pilot approval proves architecture only. Canonical cutover requires approved
disposition for every workbook sheet, reviewed semantic differences, successful
pipeline run, regenerated package data, reproducible release, rollback inputs,
and Pete Steward's approval.

Detailed decision record:
[`ERAgriculture/era-program ADR-0008`](https://github.com/ERAgriculture/era-program/blob/main/project-management/decisions/ADR-0008-normalized-vocabulary-architecture.md).
