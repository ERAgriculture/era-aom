# Cohort B ingredient-descriptor lifecycle review

Status: accepted recommendation; no ontology, schema, hierarchy, identifier, or
release change is authorized by this review PR.

Tracking: [era-program #53](https://github.com/ERAgriculture/era-program/issues/53).

## Purpose

This cohort traces the complete lifecycle and browser behavior of:

- `AOM_000531 Ingredient name`;
- `AOM_000532 Ingredient part`;
- `AOM_000533 Ingredient species`;
- `AOM_000534 Ingredient proportion`;
- `AOM_000535 Ingredient source`.

It tests whether these published IDs should remain browse concepts, become an
active Ingredient descriptors branch, or remain retired schema identifiers
connected to explicit properties and component records.

## Artifacts

- [Recommendations](RECOMMENDATIONS.md)
- [Evidence register](evidence_register.csv)
- [Row-level dispositions](ingredient_descriptor_review.csv)
- [Generated lifecycle inventory](ingredient_descriptor_lifecycle_inventory.csv)
- [Generated pipeline inventory](ingredient_descriptor_pipeline_inventory.csv)
- [Consumer audit](ingredient_descriptor_consumer_audit.csv)
- [Generated summary](ingredient_descriptor_summary.json)
- [Proposed ADR 0046](../../docs/decisions/0046-ingredient-descriptor-lifecycle-and-browser-deprecation.md)

## Rebuild

```bash
python scripts/build_ingredient_descriptor_lifecycle_review.py
```

Generator reads committed governed tables, formal schema, release graph,
deployment configuration, and normalizer. It verifies all five approved
retirements and bindings, then writes inventories and summary without changing
source ontology data or distributions.

## Browser baseline correction

Local Skosmos graph contained 27 triples for rejected pre-revert concepts
`AOM_101156`, `AOM_101157`, and `AOM_101158`. Clean `PUT` plus governed schema
and binding reload restored exact merged-baseline counts: 37,517 triples and
3,494 subjects; all three rejected IDs now have zero triples. Browser evidence
before that clean reload is invalid.

## Acceptance boundary

Pete Steward accepted ADR 0046 and all five row-level dispositions on
2026-08-13. Acceptance authorizes implementation planning only. Implementation
needs a separate PR covering governed retirement-navigation rules, standard
deprecation serialization, property scope corrections, consumer contract
migration, regeneration, clean graph loading, and Skosmos visual acceptance.
