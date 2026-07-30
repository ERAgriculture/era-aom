# AOM livestock normalization staging

Generated from public AOM Livestock v2.0, DOI
<https://doi.org/10.7910/DVN/75E7HV>.

Review staging only: not canonical AOM and not a formal semantic release.
Existing AOM identifiers remain unchanged. Records sharing duplicate ID
`AOM_006275` are excluded from generated graph and recorded in
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
