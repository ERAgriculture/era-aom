# Cross-repository registry implementation planning

## Purpose

Translate accepted ADR 0052 architecture and accepted disposition cohorts into
a bounded, dependency-ordered implementation plan. Preserve evidence and hold
boundaries while assigning producer, publisher, semantic, package,
documentation, and programme responsibilities.

## Scope

Read-only inputs:

- accepted AOM ADR 0052 and data-model acceptance packs v4, v6, and v8;
- current `era-data-pipeline` schema generator and AOM field contract;
- current `era-data` model, product schemas, and vocabulary manifest;
- current `eragri` data snapshot and field dictionaries;
- current `era-docs` data-model chapter; and
- open era-program issues #17, #21, and #27.

Planning outputs:

1. repository responsibility contracts;
2. proposed artifact contracts and relationships;
3. dependency-ordered implementation waves;
4. explicit accepted candidates, holds, immutable releases, and non-actions;
5. authority and claim-level evidence registers; and
6. guided human decisions for plan acceptance.

## Reproduction

```bash
python scripts/build_adr0054_registry_implementation_plan.py
python tests/validate_adr0054_registry_implementation_plan.py
```

`source_snapshot.json` pins clean repository commits and source-file hashes.
Generator consumes only that committed snapshot. Refresh requires a deliberate
read-only recapture and review of every changed hash, metric, or issue state.

## Planning rules

1. Keep canonical workbook authority separate from target normalized registry.
2. Assign one accountable producer and publisher for each artifact.
3. Make primary keys, foreign keys, required content, and release gates explicit.
4. Use opaque, append-only identifiers; never derive identity from mutable names.
5. Preserve every source case and accepted hold in candidate output.
6. Keep v2026.1 immutable and publish new work under a separate candidate version.
7. Start downstream work only from hash-pinned upstream candidates.
8. Separate semantic binding review from tabular identity allocation.
9. Keep package and docs consumers release pinned until cutover.
10. Roll back through release pointers and consumer defaults, never deletion or ID reuse.

## Evidence rules

- Every current-state claim points to a pinned repository file or accepted cohort.
- Every recommendation states conditions and non-actions.
- Existing candidate mappings and descriptions remain evidence, not authority.
- Held cases remain visible in artifacts, compatibility reports, and documentation.
- Current issue state is a planning snapshot, not durable completion evidence.
- Never read implementation success from acceptance of this recommendation pack.

## Human checkpoint

Human acceptance records decisions against exact hashes of the 12 guided
recommendations, 14 artifact contracts, seven waves, and 11 governance
constraints. Revised decisions require a rebuilt pack and new hashes.

Acceptance authorizes implementation sequencing and contract direction only. It
does not allocate stable IDs, edit workbook source, generate a registry, change
AOM bindings, modify package or docs consumers, publish a release, migrate a
consumer, advance a latest pointer, or close a programme issue.

## Completion gate

Planning completes when:

- all six repository roles have inputs, outputs, boundaries, and evidence;
- all 14 proposed artifacts have keys, links, content, and release gates;
- all seven waves have dependencies, entry and exit gates, and rollback paths;
- all accepted cases and holds remain explicit;
- deterministic builder and validator pass without rewriting source evidence;
- human decisions and exact approved artifact hashes are recorded separately.
