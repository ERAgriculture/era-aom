# Public-authority source cohort

Frozen cohort combines 218 taxon-routed and 26 public-ontology-routed definition
gaps. Direct biological-source concepts may receive source-scope definitions;
derived-material descriptors remain held because taxon identity alone is
insufficient. Exact AGROVOC oil materials receive source + oil-constituent
assertions, never physical-form inference.

`public_authority_cohort.csv` is immutable review input. Rebuild decisions with:

```sh
python scripts/build_public_authority_source_review.py
```

Do not run `--snapshot` after approvals; that option exists only to establish a
new explicitly reviewed cohort. No ILRI feed code participates.
