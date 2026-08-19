# Livestock v36 process-axis implementation

Implements accepted [ADR 0047](../../docs/decisions/0047-feed-process-objective-benefit-and-effect-model.md).

## Contents

- `process_axis_implementation_register.csv`: every reviewed process disposition and implementation state.
- `identity_collision_audit.csv`: global collision result for every allocated or relabelled concept.
- `defatting_material_migration_holds.csv`: eight material assertions withheld until operation and composition evidence are reviewed.
- `process_axis_implementation_summary.json`: machine-readable implementation counts.

## Evidence trail

Claim-level sources remain in `review/livestock-v35/evidence_register.csv`; row-level evidence IDs remain in `review/livestock-v35/process_axis_review.csv`. Implementation method is documented in `docs/methods/feed-process-axis-governance.md`.
