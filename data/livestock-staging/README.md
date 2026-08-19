# AOM livestock normalization staging

Preferred-label identity governance lives in
`approved_ontology_collision_decisions.csv`. Equal SKOS labels remain permitted
where hierarchy and model role distinguish concepts; verified duplicates use
`approved_deprecations.csv` replacement links.

Definition overlays live in `approved_definition_enrichments.csv`. They promote
reviewed scope text or compose only approved source/facet assertions; legacy
source descriptions remain unchanged.

Generated from public AOM Livestock v2.0, DOI
<https://doi.org/10.7910/DVN/75E7HV>.

Public v2 provides reproducible release source. Its 2,503 AOM rows, identifiers,
and L1–L10 hierarchy were compared with current ERA transition workbook snapshot
modified 2026-07-09; see `inventory/AOM_LIVESTOCK_RECONCILIATION.md`. Workbook
path, restricted supporting sheets, and private fingerprint are not published.

Review staging only: not canonical AOM and not a formal semantic release.
Legacy release rows remain unchanged in `legacy_records.csv`. Approved
row-level identity decisions live in `approved_identity_resolutions.csv`;
reviewed mapping corrections live in `approved_mapping_replacements.csv`.
Approved identifier deprecations and replacement links live in
`approved_deprecations.csv`.
Approved retirements without replacements live in
`approved_concept_retirements.csv`. Each retains a governed history note and is
excluded from active browse hierarchy while its stable identifier remains in
generated RDF with `owl:deprecated true`.
Approved preferred-label corrections live in `approved_label_corrections.csv`;
legacy preferred labels remain published as `skos:altLabel` values.
Approved minted concepts live in `approved_new_concepts.csv`; allocations live
in append-only `livestock_id_registry.csv`. See [`../../IDENTIFIERS.md`](../../IDENTIFIERS.md).
Approved non-hierarchical concept links live in
`approved_semantic_relations.csv`.
Approved process-operation links to mechanisms, technical objectives, and
modal benefits live in `approved_process_axis_relations.csv`. Upstream
production provenance remains a feed-material facet. See ADR 0047 and
`docs/methods/feed-process-axis-governance.md`.
Approved hierarchy flattening and direct reparenting decisions live in
`approved_reparentings.csv`.
Approved phase-2 data-model migration bindings live in
`approved_semantic_bindings.csv`. These preserve legacy identifiers while
specifying normalized properties, observation patterns, quantity kinds, unit
requirements, and consumer-cutover policy.
Approved controlled-value decisions live in
`approved_semantic_value_bindings.csv`. Exact ingredient-source values reuse
existing AOM concepts; ambiguous values are explicit holds and never guessed.
Legacy ingredient-component descriptors remain strings until phase-3 review
decomposes them across typed part, physical-form, processing, product-role, and
constituent facets. See `../../review/livestock-v3/` and ADR 0004.
Approved descriptor routing lives in
`approved_ingredient_component_classifications.csv`; classification never
authorizes concept identity or a facet IRI. See ADR 0012.
Approved facet concepts, atomic mappings, compound decompositions, and explicit
null-target holds live in `approved_ingredient_facet_*` /
`approved_ingredient_component_*` contracts introduced by ADRs 0013–0014.
Generator applies these governance overlays without rewriting source evidence.
OWL domain semantics and SHACL constraints live under `schemas/`; remodeling
dispositions are staged separately from this backward-compatible SKOS release.
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
