# ADR 0054: Cross-repository data-model registry implementation plan

- Status: Accepted
- Date: 2026-09-09
- Last reviewed: 2026-09-11
- Accepted: 2026-09-10 by P. Steward
- Owners: ERA data-model and AOM semantic governance
- Tracking:
  [era-program #17](https://github.com/ERAgriculture/era-program/issues/17),
  [era-program #21](https://github.com/ERAgriculture/era-program/issues/21),
  [era-program #27](https://github.com/ERAgriculture/era-program/issues/27),
  [era-aom #121](https://github.com/ERAgriculture/era-aom/issues/121)
- Evidence:
  [Implementation-plan acceptance](../../review/data-model-v10/README.md),
  [implementation planning pack](../../review/data-model-v9/README.md),
  [IW-03 semantic-binding candidate](../../review/data-model-v11/README.md)
- Method: [Cross-repository registry implementation planning](../methods/cross-repository-registry-implementation-planning.md)
- Depends on:
  [AOM ADR 0052](0052-data-model-registry-and-shared-core-contract.md),
  [ERA ADR 0007](https://github.com/ERAgriculture/era-program/blob/main/project-management/decisions/ADR-0007-canonical-vocab-source.md)

## Context

ADR 0052 accepts eight linked contract layers and assigns ownership across
`era-data-pipeline`, `era-data`, `era-aom`, `eragri`, `era-docs`, and
`era-program`. It does not define concrete artifact boundaries, stable-ID
allocation, cross-repository PR order, rollback, or issue-closure sequence.

Current pipeline generator reads workbook data into one nested JSON artifact.
Current `era-data` model contains 45 tables and 750 field entries but exposes
only three extraction rounds. Product schemas each contain 138 columns with
blank descriptions. Current `eragri` data has 137 columns and its dictionary has
106 rows. Public documentation describes a more complete formal model than
current released artifacts provide.

Accepted reviews approve 13 later round-profile consolidations while retaining
eight field-key holds, 41 unmatched lookup holds, 66 unit holds, 138 product-
field evidence holds, and 44 consumer-difference evidence holds. No stable ID,
source edit, schema, release, or migration has been authorized.

## Decision

### Artifact contract

Implement 14 linked artifacts covering source provenance, tables, fields,
round-specific profiles, value sets, value members, field/value-set bindings,
unit mappings, AOM semantic bindings, product profiles, product fields,
consumer compatibility, release manifest, and catalog discovery.

Tabular registries use CSV with CSVW metadata. Portable product contracts may
also use Frictionless Table Schema. AOM semantic bindings remain governed in
`era-aom` and publish as reviewed source records, SHACL, JSON-LD, and Turtle.
PROV-O and DCAT metadata connect generation, release, distributions, checksums,
and catalog records.

Each artifact has one accountable producer and publisher, explicit primary and
foreign keys, required content, and a release gate. Detailed proposed contracts
are recorded in
[`artifact_contracts.csv`](../../review/data-model-v9/artifact_contracts.csv).

### Stable identifiers

Use central append-only ledgers for table, field, value-set, value-member,
profile, product, and binding identities. IDs are opaque, contain no mutable
table or field name, survive label and lifecycle changes, and are never reused.

Allocation occurs only during accepted IW-01 implementation. This ADR proposal
does not allocate any identifier. Held field or lookup cases may receive
source-record identities needed for preservation, but they receive no merged or
active logical identity until their accepted hold is resolved.

### Repository boundaries

- `era-data-pipeline` generates normalized candidates and completeness reports.
- `era-data` publishes immutable candidates and releases with manifests,
  product contracts, compatibility views, and catalog metadata.
- `era-aom` governs semantic-binding identity, evidence, predicates, SHACL, and
  RDF distributions.
- `eragri` pins package data and dictionaries to compatible release IDs.
- `era-docs` generates human guidance from pinned released contracts.
- `era-program` governs dependency issues, cutover, and end-to-end closure.

Repository responsibilities and non-overlap boundaries are recorded in
[`repository_contracts.csv`](../../review/data-model-v9/repository_contracts.csv).

### Delivery order

Deliver one preparatory wave and six implementation waves:

1. accept this plan and create owner-scoped implementation issues;
2. build schemas, ledgers, generator, and deterministic tests in the pipeline;
3. publish an immutable, non-latest candidate in `era-data`;
4. integrate reviewed AOM bindings and refresh the pinned candidate;
5. migrate and verify `eragri` against that candidate;
6. generate release-pinned `era-docs` guidance; and
7. publish final release, advance pointers, observe, and close programme issues.

Every downstream wave starts from exact upstream commit and artifact hashes.
Entry, exit, dependency, and rollback gates are recorded in
[`implementation_waves.csv`](../../review/data-model-v9/implementation_waves.csv).

### Holds and completeness

Candidate generation must preserve every source record and every accepted hold.
It fails if an extraction round, source field row, lookup group, unit row,
product field, consumer difference, or disposition disappears.

The 13 approved duplicate-key consolidations become one logical identity with
round profiles and complete source lineage. Eight field cases remain held from
logical merging. Forty-one lookup groups remain unbound. All 66 unit cases
retain raw evidence without canonical mapping or conversion. Product-field and
consumer-difference cohorts retain their exact 138 and 44 row boundaries.

Detailed boundaries are recorded in
[`governance_constraints.csv`](../../review/data-model-v9/governance_constraints.csv).

### Versioning and rollback

Existing v2026.1 remains immutable. Registry implementation publishes under a
new candidate version and cannot become `latest` until pipeline, AOM, package,
documentation, migration, and rollback checks pass.

Rollback restores prior release pointers and consumer defaults. It never
deletes a published release, rewrites an immutable artifact, recycles a stable
registry ID, or reassigns an AOM IRI. Failed candidates and reports remain as
audit evidence.

### Programme closure

Close era-program #27 after machine-readable registry and schemas are released
with deterministic generation and valid relationships. Close #21 after both
138-column product dictionaries have reviewed content or explicit visible
deferrals and package/docs parity passes. Close #17 only after managed
publication, governance, versioning, catalog, semantic bindings, consumers,
migration, and observation window are complete.

Residual holds remain separately tracked after closure and cannot be erased by
release publication.

## Authority comparison

- [AOM ADR 0052](0052-data-model-registry-and-shared-core-contract.md) supports
  eight contract layers, repository ownership, immutable releases, and consumer
  gates; it does not specify artifact or delivery mechanics.
- [ERA ADR 0007](https://github.com/ERAgriculture/era-program/blob/main/project-management/decisions/ADR-0007-canonical-vocab-source.md)
  supports current workbook authority; it does not make workbook rows target
  registry architecture.
- [W3C CSVW](https://www.w3.org/TR/tabular-metadata/) supports tabular metadata,
  datatypes, keys, foreign keys, annotations, and validation; it does not decide
  ERA identities or source corrections.
- [Frictionless Table Schema](https://specs.frictionlessdata.io/table-schema/)
  supports portable table descriptors and constraints; it does not govern RDF
  identity or release authority.
- [W3C PROV-O](https://www.w3.org/TR/prov-o/) supports generation and derivation
  provenance; it does not define ERA delivery order.
- [W3C DCAT 3](https://www.w3.org/TR/vocab-dcat-3/) supports datasets,
  distributions, versions, checksums, and catalogs; it does not define
  field-level registry content.

Full support and limitations are recorded in
[`authority_comparison.csv`](../../review/data-model-v9/authority_comparison.csv).

## Evidence

- [Planning-pack overview](../../review/data-model-v9/README.md)
- [Pinned source snapshot](../../review/data-model-v9/source_snapshot.json)
- [Repository contracts](../../review/data-model-v9/repository_contracts.csv)
- [Artifact contracts](../../review/data-model-v9/artifact_contracts.csv)
- [Implementation waves](../../review/data-model-v9/implementation_waves.csv)
- [Governance constraints](../../review/data-model-v9/governance_constraints.csv)
- [Guided recommendations](../../review/data-model-v9/GUIDED_IMPLEMENTATION_PLAN.md)
- [Decision rows](../../review/data-model-v9/guided_decision_recommendations.json)
- [Authority comparison](../../review/data-model-v9/authority_comparison.csv)
- [Claim-level evidence register](../../review/data-model-v9/evidence_register.csv)
- [Machine summary](../../review/data-model-v9/implementation_plan_summary.json)

## Human decision

P. Steward accepted `RI-01` through `RI-12` as recommended on 2026-09-10.
Acceptance covers exact hash-pinned artifacts containing 12 guided decisions,
14 artifact contracts, seven implementation waves, and 11 governance
constraints. Durable decisions and fingerprints are recorded in the
[implementation-plan acceptance pack](../../review/data-model-v10/README.md).

All conditions and holds remain. Acceptance approves implementation direction,
repository order, artifact contracts, identifier policy, completeness gates,
rollback, and issue-closure conditions. No stable identifier was allocated. No
canonical source, registry data, schema, AOM binding, package, documentation
consumer, release, migration, latest pointer, or issue state changed.

## Consequences

### Positive

- Cross-repository ownership and dependencies become explicit and testable.
- Source cases and human holds cannot disappear during normalization.
- New release work no longer mutates v2026.1 or outruns consumers.
- Package and documentation claims become pinned to released contracts.
- Rollback preserves identifiers, releases, and evidence.

### Costs

- Delivery requires coordinated PRs across six repositories.
- Candidate publication precedes consumer migration and final cutover.
- Stable-ID ledgers and compatibility reports add maintained artifacts.
- Existing field, lookup, unit, product, and consumer holds remain work.

## Alternatives considered

### Extend current nested JSON in place

Rejected. One artifact cannot safely express normalized identity, profiles,
foreign keys, values, units, semantic bindings, products, and consumer states.

### Implement all repositories in parallel

Rejected. Unpinned parallel changes obscure contract ownership, drift, and
rollback boundaries.

### Replace v2026.1

Rejected. In-place rebuild would break immutable source and release provenance.

### Close programme issues after pipeline generation

Rejected. Public schemas, product dictionaries, AOM bindings, package objects,
documentation, catalog, migration, and cutover would remain incomplete.

## Implementation gates

1. **Complete 2026-09-10:** P. Steward accepted `RI-01` through `RI-12` and
   exact plan artifacts in the hash-pinned data-model-v10 acceptance pack.
2. Owner-scoped implementation issues linked to IW-01 through IW-06.
3. Deterministic pipeline candidate with complete source preservation and valid keys.
4. Immutable non-latest `era-data` candidate with migration and rollback drafts.
5. **Candidate implemented 2026-09-11:** reviewed AOM binding source, stable
   binding IDs, explicit holds, RDF distributions, and clean-store checks exist
   against pinned IW-02 subjects. Gate remains open until merge and downstream
   candidate pins are refreshed.
6. Release-pinned `eragri` compatibility with complete difference dispositions.
7. Generated `era-docs` guidance with visible release identity and holds.
8. Final compatibility bundle, tested rollback, cutover observation, and ordered issue closure.

## Approval record

Accepted by P. Steward on 2026-09-10 with conditions and holds recorded in the
[implementation-plan acceptance pack](../../review/data-model-v10/README.md).
Acceptance authorizes owner-scoped issue decomposition and the agreed delivery
sequence. It allocates no identifier and changes no workbook, registry,
semantic binding, generated distribution, package object, documentation
consumer, release, migration, latest pointer, or programme issue state.
