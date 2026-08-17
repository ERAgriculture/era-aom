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
Phase-3 ingredient-component decomposition is defined in
[`docs/decisions/0004-ingredient-component-facet-model.md`](docs/decisions/0004-ingredient-component-facet-model.md).
Raw descriptors remain authoritative migration evidence until each facet
assertion receives reviewed value governance.

Feed product-kind and editorial source navigation are governed by
[`docs/decisions/0045-feed-product-kind-and-source-navigation.md`](docs/decisions/0045-feed-product-kind-and-source-navigation.md).
Feed materials, formulated feeds, and feed additives remain sibling product
kinds. Feed-material browse navigation now separates forage materials, plant
products/by-products, feeds of animal origin, and other feeds without treating
source, product role, chemical identity, process, or legal status as the same
axis. `AOM_101162 Unclassified feed materials` is temporary migration state,
not a permanent catch-all; every member requires an owner, evidence gap, target
cohort, and resolution before the next public livestock release.

Ingredient descriptor lifecycle and browser behavior are governed by
[`docs/decisions/0046-ingredient-descriptor-lifecycle-and-browser-deprecation.md`](docs/decisions/0046-ingredient-descriptor-lifecycle-and-browser-deprecation.md).
Ontology implementation preserves `AOM_000531` through `AOM_000535` as
resolvable deprecated identifiers but removes them from active hierarchy.
Their normalized predicate scopes changed in the ontology contract; pipeline
cutover remains a separate reviewed migration and must retain rollback parity.

Public packaging candidate `2026.1-rc.1` proves deterministic multi-format
generation and local semantic validation. Live namespace, Skosmos, AgroPortal,
named-reviewer, and canonical-cutover gates remain open; see
[`docs/releases/2026.1-rc.1.md`](docs/releases/2026.1-rc.1.md).

## Cutover rule

Pilot approval proves architecture only. Canonical cutover requires approved
disposition for every workbook sheet, reviewed semantic differences, successful
pipeline run, regenerated package data, reproducible release, rollback inputs,
and Pete Steward's approval.

Detailed decision record:
[`ERAgriculture/era-program ADR-0008`](https://github.com/ERAgriculture/era-program/blob/main/project-management/decisions/ADR-0008-normalized-vocabulary-architecture.md).
