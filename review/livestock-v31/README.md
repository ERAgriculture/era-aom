# Cohort A feed product-kind and source-navigation review

Status: accepted recommendation; implementation remains separate and blocked by
the stated gates.

Tracking: [era-program #52](https://github.com/ERAgriculture/era-program/issues/52).

## Purpose

This cohort adversarially reviews:

- Feed material versus Feed additive product kinds;
- placement of `AOM_101147 Feed chemical substances`;
- temporary handling of unclassified feed materials;
- Crop versus Forage scope and Feedipedia-aligned navigation;
- every direct child and descendant currently affected beneath Feed materials,
  Feed additives, and the chemical-substance branch.

## Artifacts

- [Recommendations](RECOMMENDATIONS.md)
- [Evidence register](evidence_register.csv)
- [Row-level review](feed_product_kind_review.csv)
- [Generated affected-concept inventory](feed_product_kind_inventory.csv)
- [Generated scope summary](feed_product_kind_summary.json)
- [Proposed ADR 0045](../../docs/decisions/0045-feed-product-kind-and-source-navigation.md)

## Rebuild

```bash
python scripts/build_feed_product_kind_review.py
```

The generator reads only the committed staging graph, verifies expected branch
counts, writes the complete inventory and summary, and makes no ontology,
identifier, hierarchy, or distribution changes.

## Acceptance boundary

Pete Steward accepted ADR 0045 and all row-level dispositions on 2026-08-13.
Rows are recorded as `approved` or `held`. Acceptance authorizes implementation
planning only: a separate implementation PR must still pass collision, reuse,
identifier, regeneration, validation, and Skosmos gates before data change.
