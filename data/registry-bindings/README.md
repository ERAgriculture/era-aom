# Registry semantic-binding sources

`approved_semantic_bindings.csv` is governed AC-09 source for active bindings
between stable `era-data` registry identifiers and ERA-AOM targets.
`semantic_binding_id_ledger.csv` is append-only: identifiers are never reused or
renumbered. Registry row fingerprints permit validation without copying private
registry definitions into this public repository.

Unresolved source decisions remain generated, explicit holds in versioned
distribution. They receive hold-record identifiers, not semantic-binding IDs.

Build and validate with:

```bash
python scripts/build_registry_semantic_bindings.py build
python scripts/build_registry_semantic_bindings.py validate
python scripts/build_registry_semantic_bindings.py validate --registry-root ../era-data
```
