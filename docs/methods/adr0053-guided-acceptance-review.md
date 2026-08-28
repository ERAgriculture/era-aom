# ADR 0053 guided acceptance review method

## Purpose

Convert the 12 open ADR 0053 questions into one reviewable recommendation pack
without collapsing recommendation, acceptance, source correction, ontology
implementation, release, or deployment into one event.

## Inputs

- canonical-source evidence and checksum recorded in `crop-foundation-v1`;
- all 377 source-row dispositions;
- all 109 generated node and 405 edge reviews;
- all 265 source-quality issues;
- all 26 authority exact-label candidates;
- official authority definitions and entity types;
- ADR 0052 shared-core constraints.

## Review rules

1. Review complete cohorts, not isolated examples.
2. Preserve source notation lexically and retain raw provenance.
3. Treat reporting levels as navigation unless semantic broader meaning is
   demonstrated extensionally.
4. Compare identity by definition, entity type, scope, lifecycle, and module;
   labels and mappings are evidence signals only.
5. Decompose practice, input material, observed property, experimental role,
   and accounting context before identity allocation.
6. Record unresolved questions as explicit holds.
7. Keep human-decision fields blank until reviewer records acceptance.
8. Never edit canonical source through generated review artifacts.

## Rebuild and validation

```bash
python3 scripts/build_adr0053_guided_review.py
python3 tests/validate_adr0053_guided_review.py
```

Validator requires exact cohort coverage, blank human-decision fields, no
approved mappings, no implementation authorization, and unchanged recommendation
status.

## Lifecycle

1. Recommendation pack generated.
2. Human records guided decisions.
3. Source owner approves correction proposals.
4. Canonical source corrected and review regenerated.
5. ADR accepted or revised.
6. Separate implementation change assigns IDs, mappings, hierarchy, and module.
7. Release and consumer migration follow independent validation and approval.
