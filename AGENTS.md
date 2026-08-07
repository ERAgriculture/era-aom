# ERA-AOM agent instructions

Read program handover and playbooks before substantial work:

- `../era-program/project-management/HANDOVER.md`
- `../era-program/project-management/PLAYBOOK.md`
- `../era-program/project-management/LEARNINGS.md`

## Semantic safety

1. Search preferred, alternative, hidden, deprecated, and external-mapping labels before allocating any concept ID.
2. Reuse an existing stable concept when identity and meaning match. Property context (`processingMethod`, `productRole`, `materialComponent`, etc.) does not justify a duplicate concept.
3. Create a same-label concept only when reviewed definitions prove distinct meanings. Record distinction, evidence, reviewer, and rationale in an ADR/review ledger.
4. Never infer identity from label, hierarchy, taxon mapping, or related mapping alone. External mappings and source taxa are evidence or facets, not feed-material synonyms.
5. Never reuse or delete published IDs. Resolve genuine duplicates through deprecation, `dcterms:isReplacedBy`, searchable legacy labels, and migration crosswalks.
6. Treat generated concepts as proposals until global identity-collision and canonical-reuse gates pass. Generated IDs receive no special presumption of correctness.
7. Model compound feed materials using explicit source, component, process, form, integrity, composition, and product-role relationships. Keep dimensions independent.
8. Do not hand-edit derived release distributions. Change governed source tables/schema, rebuild with pinned tooling, then verify staged Git payloads and checksums.

## Required gates

Before semantic PR:

- run global normalized-label collision audit across all active and deprecated concepts;
- classify every collision as reuse/deprecate, justified distinct meaning, or hold;
- fail on unexplained collisions, duplicate IDs, dangling targets, cycles, or unreviewed generated concepts;
- rebuild browser graph from empty storage; incremental graph accumulation is invalid acceptance evidence;
- inspect representative compound concepts in Skosmos, including visible source/component/process/role links;
- run full CI-equivalent validators and release checksum validation;
- update ERA program PROGRESS, BACKLOG, DECISIONS/ADR, and LEARNINGS.

## Work shape

- Branch + reviewed PR; never commit directly to `main`.
- Prefer complete semantic cohorts and milestone-sized PRs. Do not open micro-PRs for isolated labels.
- Preserve unresolved cases as explicit holds inside cohort.
- Keep public hosting/canonical cutover separate from local quality work.
- Never publish restricted inputs or write public storage without explicit approval.

## Review discipline

For large semantic changes, perform separate evidence, implementation, and adversarial-review passes. Report counts and exceptions, not only passing tests. Visual review is semantic QA: unexpected hierarchy or card output must reopen source modelling decisions.
