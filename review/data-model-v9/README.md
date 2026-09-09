# ADR 0054 cross-repository registry implementation plan

Recommendation-only checkpoint translating accepted ADR 0052 architecture into
repository contracts, artifact contracts, ordered delivery waves, rollback
boundaries, and programme closure gates.

## Boundaries

- Six repositories were inspected read only at pinned clean commits.
- No canonical workbook source was edited.
- No stable identifier was allocated.
- No registry, schema, semantic binding, package object, or documentation
  consumer was modified.
- No release, migration, latest-pointer change, or issue closure is authorized.
- Accepted source, unit, product-field, and consumer-difference holds remain
  explicit and complete.

## Files

- `source_snapshot.json` — pinned repository, file, and tracking-issue evidence.
- `repository_contracts.csv` — producer, publisher, consumer, and governor roles.
- `artifact_contracts.csv` — proposed registry artifacts, keys, links, and gates.
- `implementation_waves.csv` — dependency order, deliverables, gates, and rollback.
- `governance_constraints.csv` — accepted cohorts, holds, immutable releases, and non-actions.
- `GUIDED_IMPLEMENTATION_PLAN.md` — concise human review sequence.
- `guided_decision_recommendations.json` — 12 proposed policy decisions.
- `authority_comparison.csv` — authority support and limitations.
- `evidence_register.csv` — claim-level pinned evidence boundaries.
- `implementation_plan_summary.json` — machine-readable counts and non-actions.

## Proposed sequence

1. Accept governance plan and split owner-scoped issues.
2. Build deterministic normalized candidate in `era-data-pipeline`.
3. Publish immutable non-latest candidate in `era-data`.
4. Bind stable registry subjects through reviewed `era-aom` evidence.
5. Migrate and verify release-pinned `eragri` compatibility.
6. Generate release-pinned `era-docs` guidance.
7. Cut over release and close issues only after all consumers align.

## Human checkpoint

Review `RI-01` through `RI-12` and exact plan artifacts. Acceptance must be
recorded in a separate hash-pinned acceptance pack before IW-01 starts.
