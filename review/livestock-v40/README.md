# Livestock v40 composition, form, and retention implementation

Implements accepted [ADR 0049](../../docs/decisions/0049-composition-form-and-component-retention-model.md).

## Contents

- `composition_form_implementation_register.csv`: every reviewed concept disposition.
- `material_assertion_migration_register.csv`: three migrations, one removal, and one added role.
- `chemical_mapping_implementation.csv`: four exact and two broad ChEBI mappings.
- `component_binding_migration_register.csv`: retired Ash constituent mapping converted to explicit raw-value hold.
- `identity_collision_audit.csv`: seven applied labels and two rejected bare-label collisions.
- Governed hierarchy revisions move three active axes and suppress deprecated Physical form from active browsing.
- `specific_material_implementation.csv`: Mineral Block, Mineral Lick, and Chicken Offal decisions.
- `implementation_holds.csv`: Lick delivery and Gluten identity preserved without inference.
- `composition_form_implementation_summary.json`: machine-readable implementation counts.

## Evidence trail

Claim evidence remains in `review/livestock-v39/evidence_register.csv`; method is documented in `docs/methods/composition-form-and-retention-governance.md`.
