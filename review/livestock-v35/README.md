# Cohort C process mechanism, objective, and benefit review

Status: proposed recommendation; no ontology implementation.

Tracking: [era-program #54](https://github.com/ERAgriculture/era-program/issues/54).

## Purpose

This cohort reviews every current concept in the `AOM_000845 Feed processes`
closure plus retired `AOM_101068 Brewhouse processing` as provenance precedent.
It separates:

1. process operation;
2. process mechanism;
3. direct technical objective;
4. possible intended feed benefit;
5. observed effect on a specific process application.

FoodOn provides primary ontology-design precedent for process input/output,
multi-purpose processes, component separation, modification, preservation, and
component addition. EU feed-process terminology provides feed-specific scope.

## Artifacts

- [Recommendations](RECOMMENDATIONS.md)
- [Evidence register](evidence_register.csv)
- [Row-level review](process_axis_review.csv)
- [Generated hierarchy inventory](process_hierarchy_inventory.csv)
- [Generated axis overlap matrix](process_axis_overlap_matrix.csv)
- [Generated summary](process_purpose_summary.json)
- [Proposed ADR 0047](../../docs/decisions/0047-feed-process-objective-benefit-and-effect-model.md)

## Rebuild

```bash
python scripts/build_process_purpose_review.py
```

Generator reads committed staging graph and release facet bindings, verifies
complete row coverage and expected counts, and writes inventory, overlap matrix,
and summary. It makes no ontology, identifier, hierarchy, or distribution
changes.

## Acceptance boundary

Pete Steward accepted four-layer architecture during guided review on
2026-08-18, including separation of nutritional benefit from direct composition
or constituent transformation. Row-level dispositions, proposed predicates,
and new objective vocabulary remain pending explicit acceptance. Implementation
must occur in separate PR after acceptance.
