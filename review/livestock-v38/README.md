# Livestock v38 component and chemical-identity implementation

Implements accepted [ADR 0048](../../docs/decisions/0048-chemical-identity-composition-and-component-model.md).

## Contents

- `component_chemical_implementation_register.csv`: every reviewed concept disposition.
- `material_assertion_migration_register.csv`: all 627 retained, removed, retargeted, or repredicated assertions.
- `anatomical_mapping_implementation.csv`: all 31 anatomy hierarchy and authority-mapping decisions.
- `identity_collision_audit.csv`: full label collision gate for new and renamed concepts.
- `implementation_holds.csv`: 19 unresolved cases carried forward without inference.
- `component_chemical_implementation_summary.json`: machine-readable implementation counts.

## Evidence trail

Claim evidence remains in `review/livestock-v37/evidence_register.csv`; method is documented in `docs/methods/component-chemical-identity-governance.md`.
