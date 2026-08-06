# Final definition hard-tail review

Frozen cohort contains 210 active definition gaps after canonical-workbook review.
One decision ledger integrates Feedipedia, public ontology/taxon, canonical
workbook, core hierarchy, and structured feed-material evidence.

Approval requires either controlled category/core scope or governed source plus
explicit descriptors mapped to existing approved facets. Generic taxon mappings,
shared pages, source warnings, unreachable pages, commercial labels, and
unmodelled descriptors remain holds. Each hold carries blocker code and concrete
next action. Wrong or broad mappings are never converted into definitions.

Current public validation confirmed representative finished Feedipedia pages for
cowpea haulms and peanut hulls; unreachable Lotus corniculatus evidence remains
held. No ILRI feed code participates.

Rebuild decision and facet tables:

```sh
python scripts/build_definition_hard_tail_review.py
```

Do not recreate frozen cohort without explicit new review cycle.
