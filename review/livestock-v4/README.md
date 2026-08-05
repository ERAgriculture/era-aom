# Livestock v4 feed-identity review

This review layer audits apparent synonyms and shared external identifiers before
any identifier merge or deprecation. It uses the repository's immutable public-v2
snapshot, whose AOM IDs and L1–L10 hierarchy align with the current ERA workbook.

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
  ILRI, Feedipedia, or CPC product identifier. Shared mappings trigger review but
  never prove identity because source systems may describe different semantic
  levels;
- `maize_feed_material_harmonization.csv`: family-level dimensional analysis.

Review requires definitions, hierarchy, source occurrences, and external-system
scope. Confirmed duplicates retain one persistent identifier and deprecate others
with replacement links. Ambiguous records remain held.
