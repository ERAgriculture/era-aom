# Livestock v4 feed-identity review

This review layer audits apparent synonyms and shared external identifiers before
any identifier merge or deprecation. It uses the repository's immutable public-v2
snapshot, whose AOM IDs and L1–L10 hierarchy align with the current ERA workbook.
Remediation sequence and approval gates are defined in
`ONTOLOGY_QUALITY_REMEDIATION_PLAN.md`.

Regenerate:

```sh
python scripts/build_feed_identity_audit.py
python tests/validate_feed_identity_audit.py
```

Outputs:

- `feed_lexical_identity_candidates.csv`: different AOM identifiers whose
  preferred/alternate terms collide after documented AOM process and maize/corn
  synonym normalization;
- `feed_external_granularity_candidates.csv`: different identifiers sharing an
  Feedipedia or CPC product identifier. Shared mappings trigger review but
  never prove identity because source systems may describe different semantic
  levels;
- `ontology_quality_summary.csv`: baseline counts and major quality signals for
  review planning;
- `ontology_pref_label_collision_candidates.csv`: whole-AOM preferred-label
  collision groups after documented terminology normalization;
- `cereal_feed_material_review.csv`: first coherent expert-review batch, with
  hierarchy, extracted process/form terms, definition coverage, lexical
  collisions, and public mapping evidence;
- `maize_feed_material_harmonization.csv`: family-level dimensional analysis.
- `MAIZE_IDENTITY_REVIEW.md` and
  `maize_identity_review_recommendations.csv`: canonical occurrence evidence,
  public-authority evidence, proposed decision rules, and 16 recommendations for
  expert approval.

ILRI feed identifiers are excluded from candidate generation and scoring. That
system is changing; existing values remain deferred private provenance only.

Review requires definitions, hierarchy, source occurrences, and external-system
scope. Confirmed duplicates retain one persistent identifier and deprecate others
with replacement links. Ambiguous records remain held.
