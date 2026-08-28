# ADR 0051 acceptance record

Human acceptance record for
[ADR 0051](../../docs/decisions/0051-whole-vocabulary-resource-boundaries-and-migration-sequence.md),
based on the complete guided checkpoint in
[`whole-vocabulary-v2`](../whole-vocabulary-v2/).

## Accepted scope

- all eight policy decisions accepted with stated revisions, conditions, and
  holds;
- all 33 resource-route recommendations accepted as recorded;
- `prac`, `out`, and `out_econ` revised from stale crop-only routing to
  cross-domain row routing under accepted ADR 0053;
- `site_list` retained on publication and sensitivity review;
- `scio - Custom Terms` retained on provenance review;
- `ssa_feedsdb` retained as confirmed restricted exclusion;
- seven excluded resources retain migration provenance;
- `ani_diet`, `ani_process`, and `AOM_diets` remain supporting evidence or
  crosswalk resources rather than independent sibling schemes.

## Files

- [`policy_decision_approvals.csv`](policy_decision_approvals.csv): final human
  decisions for `GV-01` through `GV-08`.
- [`resource_route_approvals.csv`](resource_route_approvals.csv): final human
  decision for `RR-01` through `RR-33`.
- [`evidence_register.csv`](evidence_register.csv): claim-bounded acceptance
  evidence.
- [`acceptance_summary.json`](acceptance_summary.json): machine-readable status,
  counts, and implementation boundaries.

## Boundary

Acceptance approves product boundaries, resource-routing policy, migration
sequence revisions, coverage obligations, and explicit holds. It does not edit
canonical source, approve row identities or hierarchy, allocate identifiers,
emit mappings, publish resources, implement migrations, release artifacts,
migrate consumers, or authorize canonical cutover.

Validate with:

```bash
python3 tests/validate_adr0051_acceptance.py
```
