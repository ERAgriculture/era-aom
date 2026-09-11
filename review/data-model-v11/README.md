# IW-03 registry semantic-binding candidate

Status: **implemented candidate; downstream refresh held**

This pack records AC-09 implementation under
[ADR 0054](../../docs/decisions/0054-cross-repository-data-model-registry-implementation-plan.md)
and [era-aom issue 121](https://github.com/ERAgriculture/era-aom/issues/121).

## Scope and result

- pinned merged IW-02 `era-data` candidate at commit
  `363c81ee709d939bd58a5f0980b3eb5e5d490fd2`;
- allocated five append-only semantic-binding IDs for five exact field rows;
- activated four distinct approved source decisions because Ingredient species
  maps two canonical registry fields to `aom:sourceTaxon`;
- preserved all remaining 307 decisions as explicit versioned holds; and
- published deterministic CSV, CSVW, OWL, SHACL, Turtle, JSON-LD, manifest, and
  checksum artifacts under `dist/registry-bindings/version=2026.2-rc.1/`.

No value-member binding is active. Reviewed On-farm and Purchased targets remain
held because their IW-02 value members and parent value set are held. Scientific
name values remain held because IW-02 allocated no normalized value-member IDs.

## Active bindings

| Binding | Registry subject | AOM target |
|---|---|---|
| `ERA-SBN-000001` | `ERA-FLD-000092` | `aom:ingredientName` |
| `ERA-SBN-000002` | `ERA-FLD-000093` | `aom:legacyComponentDescriptor` |
| `ERA-SBN-000003` | `ERA-FLD-000084` | `aom:sourceTaxon` |
| `ERA-SBN-000004` | `ERA-FLD-000041` | `aom:sourceTaxon` |
| `ERA-SBN-000005` | `ERA-FLD-000111` | `aom:ingredientSource` |

## Hold disposition

| Reason | Count |
|---|---:|
| Registry value-member not allocated | 295 |
| Registry field not allocated | 8 |
| Registry subject held | 2 |
| Amount field does not establish proportion | 1 |
| Registry subject held and target ambiguous | 1 |
| **Total** | **307** |

The eight unallocated fields are grazing observables awaiting registry schema
work. `AOM_000534` is held against `ERA-FLD-000088`: candidate content may
represent an absolute amount or a proportion, so unit and composition basis are
required.

## Public/private boundary

`era-data` is private and ERA-AOM is public. Public source contains stable
registry IDs, canonical-row checksums, necessary semantic assertions, and
bounded evidence only. It does not copy registry labels, definitions, source
values, or other private content. Optional local validation checks complete
private rows at their pinned hashes.

## Authority comparison

- [ADR 0054](../../docs/decisions/0054-cross-repository-data-model-registry-implementation-plan.md)
  governs artifact ownership, stable IDs, holds, versioning, and delivery order;
  it does not itself approve individual binding rows.
- Existing approved semantic sources govern row targets and reviewer state;
  they do not prove that a corresponding stable IW-02 registry subject exists.
- IW-02 registry artifacts govern subject identity and lifecycle; held subjects
  cannot become active because their semantic target is known.
- [W3C SHACL](https://www.w3.org/TR/shacl/) supports machine validation of graph
  constraints; it does not supply domain mappings.
- [W3C CSVW](https://www.w3.org/TR/tabular-metadata/) supports portable source
  table metadata; it does not authorize ERA identities or semantic assertions.

Detailed boundaries are recorded in
[`authority_comparison.csv`](authority_comparison.csv).

## Evidence

- [`registry_semantic_binding_summary.json`](registry_semantic_binding_summary.json)
- [`clean_store_acceptance.json`](clean_store_acceptance.json)
- [`evidence_register.csv`](evidence_register.csv)
- [`authority_comparison.csv`](authority_comparison.csv)
- [Governed active source](../../data/registry-bindings/approved_semantic_bindings.csv)
- [Append-only ID ledger](../../data/registry-bindings/semantic_binding_id_ledger.csv)
- [Generated candidate manifest](../../dist/registry-bindings/version=2026.2-rc.1/manifest.json)
- [Generated hold register](../../dist/registry-bindings/version=2026.2-rc.1/semantic_binding_holds.csv)
- [Governance method](../../docs/methods/registry-semantic-binding-governance.md)

## Validation

```bash
python scripts/build_registry_semantic_bindings.py build
python scripts/build_registry_semantic_bindings.py validate
python scripts/build_registry_semantic_bindings.py validate --registry-root ../era-data
python tests/validate_registry_semantic_bindings.py
```

Clean-store acceptance loads livestock release and binding candidate into
separate named graphs and checks five binding identities plus five direct field
property assertions. Local empty-volume acceptance passed on 2026-09-11 across
55 representative concept cards. Candidate remains non-latest. IW-03 remains
open until merged AOM candidate is pinned by refreshed pipeline and `era-data`
candidates.
