# ADR 0051: Whole-vocabulary resource boundaries and migration sequence

- Status: Accepted
- Date: 2026-08-24
- Accepted: 2026-08-28 by P. Steward
- Owners: ERA-AOM semantic and data-model governance
- Tracking: [era-program #17](https://github.com/ERAgriculture/era-program/issues/17)
- Evidence:
  [Whole-vocabulary coverage review](../../review/whole-vocabulary-v1/RECOMMENDATIONS.md),
  [guided-review checkpoint](../../review/whole-vocabulary-v2/README.md),
  [human acceptance record](../../review/whole-vocabulary-v3/README.md)
- Method: [Whole-vocabulary migration governance](../methods/whole-vocabulary-migration-governance.md)
- Depends on:
  [ERA ADR 0007](https://github.com/ERAgriculture/era-program/blob/main/project-management/decisions/ADR-0007-canonical-vocab-source.md),
  [ERA ADR 0008](https://github.com/ERAgriculture/era-program/blob/main/project-management/decisions/ADR-0008-normalized-vocabulary-architecture.md),
  [AOM ADR 0001](0001-semantic-model-layers.md)

## Context

AOM is an umbrella semantic product with shared-core, crop, livestock, and
mapping products. Recent work deeply reviewed livestock feed and diet, while
most crop, shared-core, non-feed-livestock, schema, code-list, and crosswalk
resources remained at inventory stage.

Canonical workbook contains 33 sheets and 19,845 nonblank structural rows.
Twenty-three sheets are proposed public, one location sheet remains under
publication review, and nine are excluded operational, restricted, legacy,
documentation, or scratch resources. Fourteen sheets are currently inventoried
as concept schemes, but normalized source-row coverage exists only for `prac`,
`out`, and `AOM`. No workbook resource has yet been normalized as `aom-core`.

Workbook structure also mixes different resource types. Field registries,
lookup assignments, reference code lists, crosswalks, working subsets,
operational source tables, and restricted evidence should not all become SKOS
concept schemes.

## Decision

### Product boundary

AOM remains an umbrella product, never shorthand for livestock or feed.

- `aom-core` contains only demonstrated cross-domain study, intervention,
  observation, quantity, unit, provenance, and context semantics.
- `aom-crop` contains crop practices, outcomes, products, components, inputs,
  biological identities, and crop-specific context.
- `aom-livestock` contains livestock identities, diets, feed materials,
  physiology, husbandry, pasture, and outcomes.
- `mappings` contains reviewed cross-module and external alignments with source,
  relation, evidence, reviewer, and status.
- `era-data` owns published schemas, code-list distributions, catalog records,
  and approved model or vocabulary release pointers.
- `era-data-pipeline` owns operational ingestion and source-management tables.

Concepts move into `aom-core` only after reviewed crop/livestock comparison.
Convenience, lexical overlap, or one-domain reuse does not establish shared
identity.

### Resource routing

Route canonical workbook resources by semantic function before row migration.

1. Publish domain identities and navigation values as governed SKOS concepts.
2. Publish field definitions, datatypes, cardinalities, and lookup assignments
   as machine-readable schemas with AOM semantic bindings and SHACL validation.
3. Publish reference values as versioned code lists with external identifiers.
4. Publish crosswalks as governed mapping assertions, not as inferred identity.
5. Publish dataset and distribution metadata through DCAT/PROV catalog records.
6. Keep operational, restricted, legacy, and scratch resources outside active
   concept schemes unless explicit review approves promotion.

`AOM_diets`, `ani_diet`, and `ani_process` are supporting subsets, assignments,
corrections, and crosswalk evidence into `aom-livestock`; they are not
independent public concept schemes. `era_fields_v1`, `era_fields_v2`, and
`lookup_levels` are data contracts rather than agricultural hierarchies.

### Migration order

Execute bounded waves with explicit dependency gates:

1. approve whole-resource boundaries and coverage reporting;
2. formalize current data model, lookup bindings, units, and shared-core
   observation contracts;
3. review `prac`, `out`, and `out_econ` as cross-domain source registries and
   route approved identities row by row;
4. review crop products, components, and residue mappings;
5. review fertilizers, chemicals, formulations, active ingredients, and use;
6. review crop and animal biological identities, varieties, accessions, and
   traits;
7. complete livestock review outside recent feed-heavy cohorts;
8. publish remaining reference code lists, context registries, and crosswalks.

Dependency-independent cohorts may run in parallel. No long-running branch may
combine all waves.

### Coverage contract

Every AOM release candidate reports:

- every canonical workbook resource and publication disposition;
- target product and owner repository;
- current normalization and reconciliation state;
- source-row coverage without presenting it as semantic completeness;
- unresolved holds, privacy or rights gates, and consumer dependencies;
- schema, concept, mapping, code-list, and excluded-resource counts.

No release may claim complete AOM migration while a public or review resource
lacks an approved target disposition. Deep completion of one module does not
offset missing coverage in another.

### Source and identifier continuity

Workbook remains operational authority until existing cutover gates pass.
Migration preserves source rows, stable identifiers, labels, provenance, and
review status. One source row does not automatically equal one concept.
Compound rows must be decomposed through reviewed relationships. Existing IDs
are reused only after global identity and collision review; published IDs are
never deleted or reassigned.

### Near-term priority

ADR 0049 remains a separate livestock visual-acceptance gate and does not block
independent data-model, crop, reference, or mapping review. Pause further
feed-first structural expansion unless correcting a defect or publication
blocker. Next implementation work is Wave 1 data-model and shared-core
contracts, followed by governed cross-domain practice and outcome foundation
review. Livestock work continues through explicit non-feed coverage, including
`vars_animals`, rather than feed alone.

## Authority comparison

- ERA ADR 0007 establishes canonical workbook authority until cutover but does
  not make workbook sheet layout the target architecture.
- ERA ADR 0008 and `MODULES.md` establish AOM's core, crop, livestock, and
  mappings products but do not approve row-level identity or hierarchy.
- Public AOM Livestock v2 establishes livestock lineage, IDs, authorship, and
  DOI but does not cover crop resources.
- [W3C SKOS](https://www.w3.org/TR/skos-reference/) supports concept schemes,
  labels, notations, relations, collections, and mappings.
- [W3C CSVW](https://www.w3.org/TR/tabular-data-model/) supports tabular field
  and column metadata.
- [W3C SHACL](https://www.w3.org/TR/shacl/) supports RDF graph constraints and
  validation reports.
- [W3C DCAT 3](https://www.w3.org/TR/vocab-dcat-3/) supports catalog, dataset,
  distribution, checksum, and version metadata.

Full support and limitation statements are recorded in
[`authority_comparison.csv`](../../review/whole-vocabulary-v1/authority_comparison.csv).

## Evidence

- [Whole-vocabulary recommendations](../../review/whole-vocabulary-v1/RECOMMENDATIONS.md)
- [Resource coverage matrix](../../review/whole-vocabulary-v1/resource_coverage.csv)
- [Migration waves](../../review/whole-vocabulary-v1/migration_waves.csv)
- [Authority comparison](../../review/whole-vocabulary-v1/authority_comparison.csv)
- [Claim-level evidence register](../../review/whole-vocabulary-v1/evidence_register.csv)
- [Machine summary](../../review/whole-vocabulary-v1/coverage_summary.json)
- [Guided policy recommendations](../../review/whole-vocabulary-v2/guided_decision_recommendations.csv)
- [All resource-route recommendations](../../review/whole-vocabulary-v2/resource_routing_recommendations.csv)
- [Guided-review evidence register](../../review/whole-vocabulary-v2/evidence_register.csv)
- [Guided-review summary](../../review/whole-vocabulary-v2/acceptance_summary.json)
- [Human policy approvals](../../review/whole-vocabulary-v3/policy_decision_approvals.csv)
- [Human route approvals](../../review/whole-vocabulary-v3/resource_route_approvals.csv)
- [Acceptance evidence register](../../review/whole-vocabulary-v3/evidence_register.csv)
- [Acceptance summary](../../review/whole-vocabulary-v3/acceptance_summary.json)

## Guided decision checkpoint

Eight policy decisions and all 33 resource routes are prepared for one human
review cohort. Recommendations retain explicit publication and provenance holds
for `site_list` and `scio - Custom Terms`, preserve confirmed exclusion of
`ssa_feedsdb`, revise stale crop-only routes for `prac`, `out`, and `out_econ`
to cross-domain row routing under accepted ADR 0053, and keep all
human-decision fields blank.

Guided recommendations revise migration wording so wave labels `0` through `7`
remain identifiers while narrative positions are ordinals. ADR 0049 remains a
separate livestock visual-acceptance gate and does not block independent
data-model, crop, reference, or mapping review.

This checkpoint records no approval and authorizes no source, identity,
hierarchy, mapping, publication, implementation, release, consumer migration,
or canonical-cutover change.

## Human decision

P. Steward accepted `GV-01` through `GV-08` and `RR-01` through `RR-33` on
2026-08-28 with all stated revisions, conditions, and holds. Acceptance approves
whole-product boundaries, function-first resource routing, bounded migration
waves, coverage reporting, source and identifier continuity, and publication
boundaries.

Accepted revisions route `prac`, `out`, and `out_econ` row by row across modules
instead of treating each sheet as crop-only. Accepted holds retain `site_list`
on publication review, `scio - Custom Terms` on provenance review, and
`ssa_feedsdb` as restricted exclusion.

Acceptance does not approve row identities, hierarchy, mappings, source edits,
identifier allocation, publication, implementation, release, consumer
migration, or canonical cutover.

## Consequences

### Positive

- AOM progress becomes measurable across whole canonical vocabulary.
- Crop and shared-core work receive explicit priority after livestock pilot.
- Data schemas, code lists, mappings, and operational records stop being
  misrepresented as one ontology hierarchy.
- Cross-repository ownership and consumer obligations become visible before
  implementation.
- Restricted and sensitive resources retain explicit publication barriers.

### Costs

- Migration becomes several governed cohorts instead of one bulk conversion.
- Some proposed sheet classifications change after resource-content review.
- Existing crop pilot requires identity and hierarchy review before promotion.
- Shared-core extraction waits for demonstrated cross-domain equivalence.
- Release reporting must include unresolved scope rather than only completed
  modules.

## Alternatives considered

### Finish livestock before starting crop

Rejected. This perpetuates module imbalance and makes feed quality look like
whole-AOM readiness.

### Convert every public workbook row into one SKOS concept

Rejected. Workbook includes fields, datatypes, code lists, crosswalks,
operational assignments, and compound rows that require different models.

### Put every reusable term directly into `aom-core`

Rejected. Shared identity requires reviewed evidence across domains; premature
promotion creates false equivalence and unstable dependencies.

### Publish one combined concept scheme

Rejected. Module separation preserves lineage, review ownership, release
independence, and intelligible navigation.

## Implementation gates

1. Human approval of ADR and all resource-level routing dispositions. Complete.
2. Complete row inventory and affected-consumer inventory per bounded cohort.
3. Claim-level authority comparison and row-level dispositions with holds.
4. Global label, identifier, deprecation, and external-mapping collision audit.
5. Governed source changes only; never hand-edit generated distributions.
6. Deterministic rebuild and complete schema, RDF, SHACL, and checksum checks.
7. Clean browser load and guided visual acceptance for changed schemes.
8. Contract tests or explicit deferral for pipeline, catalog, package, and docs
   consumers.
9. Updated whole-vocabulary coverage report before release approval.

## Approval record

Accepted by P. Steward on 2026-08-28 with revisions, conditions, and holds
recorded in the
[acceptance pack](../../review/whole-vocabulary-v3/README.md). Acceptance
allocates no identifier and changes no hierarchy, schema, mapping, source data,
generated distribution, publication status, or canonical authority.
