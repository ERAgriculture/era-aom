# AOM livestock normalization staging

Generated from public AOM Livestock v2.0, DOI
<https://doi.org/10.7910/DVN/75E7HV>.

Review staging only: not canonical AOM and not a formal semantic release.
Legacy release rows remain unchanged in `legacy_records.csv`. Approved
row-level identity decisions live in `approved_identity_resolutions.csv`;
reviewed mapping corrections live in `approved_mapping_replacements.csv`.
Approved identifier deprecations and replacement links live in
`approved_deprecations.csv`.
Approved minted concepts live in `approved_new_concepts.csv`; allocations live
in append-only `livestock_id_registry.csv`. See [`../../IDENTIFIERS.md`](../../IDENTIFIERS.md).
Approved non-hierarchical concept links live in
`approved_semantic_relations.csv`.
Generator applies these governance overlays without rewriting source evidence.
Unresolved duplicate identifiers remain excluded and recorded in
`quarantine.csv`. Duplicate paths remain visible for review.

`Path` is derived from explicit `L1`–`L10` values. Missing explicit parent
concepts go to `hierarchy_gaps.csv`; generator never invents IDs or silently
connects children to distant ancestors.

External mappings use one assertion per row with evidence, source release,
status, and reviewer. Legacy mappings remain `legacy-unreviewed`. Deterministic
repair fixes malformed `http:/` syntax while preserving original values.

Regenerate:

```bash
python scripts/normalize_livestock_release.py /path/to/02a_AOM_v2.0.0.csv .
```

Dataverse requires guestbook submission for direct file download. Committed
immutable snapshot is also valid deterministic input:

```bash
python scripts/normalize_livestock_release.py data/livestock-staging/legacy_records.csv .
```
