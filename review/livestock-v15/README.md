# Authority mapping remediation

Frozen cohort contains 105 hard-tail concepts and 383 public mapping assertions.
Review distinguishes discoverability from identity evidence. Cross-domain taxon,
CPC, broad ontology, shared Feedipedia, warned, and unreachable targets remain
`skos:relatedMatch` and explicitly cannot generate definitions.

Twenty-seven contradictory mappings are excluded from normalized publication but
preserved in immutable assertion cohort. Verified examples include canola mapped
to palm family, maize yellow mapped to African yam bean, sorghum top mapped to
soybean, and multiple concepts mapped to different species. ILRI identifiers are
outside scope.

Rebuild:

```sh
python scripts/build_authority_mapping_review.py
```

Do not recreate frozen cohorts without explicit new review cycle.
