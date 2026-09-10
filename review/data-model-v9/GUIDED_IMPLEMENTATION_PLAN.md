# Guided registry implementation recommendations

Status: **proposed for human review**.

| ID | Recommendation | Conditions / holds |
|---|---|---|
| `RI-01` | Keep canonical workbook as authoring authority while generating a separate normalized registry. | No source edit or authority cutover is authorized by this plan. |
| `RI-02` | Implement AC-01 through AC-14 as separately validated and linked artifacts. | Names and columns are proposed contracts until ADR 0054 acceptance. |
| `RI-03` | Allocate table, field, value-set, member, profile, and binding IDs from central append-only ledgers. | No ID is allocated in this review; identifiers are never recycled or derived from mutable labels. |
| `RI-04` | Fail generation when source rows, rounds, lookup groups, unit rows, or accepted holds disappear. | Held records remain present and inactive rather than silently dropped. |
| `RI-05` | Publish registry work under a new immutable candidate version before any latest-pointer change. | Candidate status, supersession intent, migration draft, and rollback target must be explicit. |
| `RI-06` | Publish reviewed semantic bindings from era-aom against stable registry IDs and governed predicates. | No unreviewed value mapping, inferred unit mapping, or unsupported core promotion. |
| `RI-07` | Make eragri data and dictionary objects declare compatible era-data release IDs and checksums. | Prior package contract remains supported until migration release is explicit. |
| `RI-08` | Generate public data-model guidance from pinned released registry and product artifacts. | Generated pages must expose release identity, provenance, deferrals, and unresolved holds. |
| `RI-09` | Separate registry implementation from shared-core semantic promotion. | Each core promotion needs separate crop-and-livestock evidence and semantic review. |
| `RI-10` | Deliver IW-00 through IW-06 in dependency order with one compatibility checkpoint per boundary. | A downstream wave starts only from a hash-pinned upstream candidate. |
| `RI-11` | Rollback by restoring prior release pointers and consumer defaults while retaining failed artifacts and IDs. | Migration tests and rollback target are required before cutover. |
| `RI-12` | Close issue 27 after schema release, issue 21 after dictionary parity, then issue 17 after full managed publication and consumer alignment. | Residual holds remain linked and cannot disappear through issue closure. |

## Delivery sequence

| Wave | Repositories | Exit gate |
|---|---|---|
| `IW-00` Governance acceptance and issue decomposition | era-aom;era-program | Owners, artifact contracts, dependencies, holds, and rollback responsibility assigned |
| `IW-01` Registry schemas and deterministic producer | era-data-pipeline | AC-01 through AC-08 and AC-10 through AC-13 build twice identically with valid keys |
| `IW-02` Immutable release-candidate publication | era-data | Candidate is immutable, separately addressed, downloadable, and not latest |
| `IW-03` Semantic binding integration | era-aom;era-data-pipeline;era-data | All active bindings validate; unknown mappings remain explicit holds; graph rebuild is clean |
| `IW-04` Package compatibility migration | eragri | Package tests reconcile columns, order, types, definitions, release, and checksums |
| `IW-05` Generated documentation alignment | era-docs | Docs drift test passes and every unresolved hold remains visible |
| `IW-06` Release cutover and programme closure | era-data;era-program | Observation window passes; issues 27, 21, then 17 close against linked evidence |

## Human decision fields

Acceptance must record decision, reviewer, date, and conditions against exact hashes of
`guided_decision_recommendations.json`, `artifact_contracts.csv`,
`implementation_waves.csv`, and `governance_constraints.csv`.

Acceptance authorizes planning direction only. Each wave still requires its own issue,
implementation PR, validation evidence, and downstream compatibility checkpoint.
