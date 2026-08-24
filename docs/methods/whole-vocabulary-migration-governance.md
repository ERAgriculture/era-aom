# Whole-vocabulary migration governance

## Purpose

Apply one auditable method across AOM core, crop, livestock, mappings, schemas,
code lists, and catalog contracts. Prevent deep work in one domain from being
reported as whole-vocabulary completion.

## Inputs

- canonical controlled workbook under ADR 0007;
- immutable structural inventory without workbook cell publication;
- public AOM releases and lineage records;
- existing normalized sources, ID registries, mappings, ADRs, and holds;
- pipeline, catalog, package, and documentation consumer contracts;
- relevant standards and domain authorities.

## Resource-level review

1. Verify canonical workbook fingerprint privately.
2. Regenerate structural inventory and fail on unreviewed sheet drift.
3. Classify every resource as concept scheme, schema, code list, crosswalk,
   operational evidence, restricted evidence, legacy, documentation, or
   scratch.
4. Assign target product, owner repository, publication disposition, migration
   wave, dependencies, and next action.
5. Record authority support and limitations for each architectural claim.
6. Approve resource routing through ADR before row migration.

## Row-level cohort review

For each bounded resource cohort:

1. inventory every source row and current downstream use;
2. separate identity, label, hierarchy, component, process, role, quality,
   composition, use, field metadata, and mapping assertions;
3. search all active, alternative, hidden, deprecated, and external labels
   before proposing identity reuse or ID allocation;
4. compare relevant authorities by claim and limitation;
5. record one disposition per row or assertion, including explicit holds;
6. review duplicates, replacements, rights, privacy, and source provenance;
7. approve recommendation ADR before implementation.

One source row does not imply one concept. Compound source rows may generate
multiple typed assertions or remain held. Lexical equality does not establish
identity.

## Cross-domain promotion

Promote a concept or property into `aom-core` only when crop and livestock
comparison demonstrates same identity and scope. Otherwise retain domain
concepts and use reviewed mappings or shared properties. Record source IDs,
definitions, usage, differences, reviewer, and rationale.

## Implementation

1. edit governed normalized sources, overlays, schemas, or mapping tables;
2. preserve published identifiers and append-only ID allocation records;
3. generate distributions through pinned tooling;
4. run global collision, dangling-target, cycle, deprecation, rights, schema,
   SHACL, graph-equivalence, and checksum checks;
5. rebuild twice and require byte identity under supported toolchain;
6. reload empty browser storage and inspect representative cards;
7. verify affected consumers or record explicit, owned deferrals.

## Cross-repository responsibilities

| Repository | Responsibility |
|---|---|
| `era-aom` | Concept schemes, ontology schema, semantic bindings, mappings, review evidence, and release candidates |
| `era-data-pipeline` | Canonical-source ingestion, transformation, QA, and pinned semantic-contract consumption |
| `era-data` | Field schemas, code-list and vocabulary distributions, catalog records, release pointers, and checksums |
| `eragri` | Stable R-facing fields, lookups, helpers, and compatibility checks |
| `era-docs` | Human-readable model, vocabulary, access, migration, and release documentation |
| `era-program` | ADRs, issue dependencies, approval gates, progress, handover, and closure evidence |

Producer merge alone does not close cross-repository work.

## Coverage reporting

Every review and release reports:

- total workbook resources by disposition and type;
- target product and owner;
- normalized, reconciled, inventory-only, review-blocked, and excluded states;
- source rows covered without claiming semantic completeness;
- allocated, reused, deprecated, replaced, and held identifiers;
- affected consumers and validation evidence;
- unresolved public, review, restricted, and privacy gates.

Do not report whole-AOM completion from one module's concept count or browser
acceptance.
