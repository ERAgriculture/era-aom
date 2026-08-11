# ERA-AOM ontology review backlog

## Feed taxonomy axis reclassification

- Status: proposed in ADR 0044; recommendation review pending
- Priority: critical
- Added: 2026-08-11

### Problem

`Supplement` and `Other Ingredients` are residual buckets mixing materials,
formulations, additives, chemical identities, roles, placeholders, and unknown
products. Five schema fields remain direct `Feed materials` children. Linked
defects affect Organic Acid, Protected Fat, Elancoban, Brewhouse processing,
component/separation hierarchy, Bran, and whole-component retention states.

### Review package

`review/livestock-v29/` covers 220 concepts, including every direct Feed
materials child, all 94 Supplement descendants, all 54 Other Ingredients
descendants, and complete implicated structural branches.

### Required work

1. Review and approve or amend every hold and split disposition.
2. Implement approved product-kind migrations as complete cohorts.
3. Move roles, chemical identities, components, processes, and states to
   independent axes.
4. Preserve stable IDs through deprecation and replacement links.
5. Regenerate release artifacts, rebuild empty Fuseki storage, and rerun
   notation search plus full Skosmos browse/card review.

Do not patch named cards before cohort dispositions are approved.

## Processing-method hierarchy consolidation

- Status: implemented in ADR 0042; three material-level holds remain
- Priority: high
- Added: 2026-08-07

### Problem

AOM currently exposes two processing systems:

1. legacy `AOM_000845` Feed Process hierarchy, organized under biological,
   chemical, dehydration, mechanical, and thermal process groups;
2. new `AOM_101021` Ingredient processing methods facet hierarchy, containing
   mostly flat method values created for feed-material assertions.

Several pairs appear semantically duplicate, including:

- Milling: `AOM_000838` / `AOM_101082`
- Grinding: `AOM_000836` / `AOM_101095`
- Drying: `AOM_000843` / `AOM_101071`
- Wilting: `AOM_000844` / `AOM_101102`
- Boiling: `AOM_000827` / `AOM_101089`
- Crushing: `AOM_000835` / `AOM_101091`
- Fermentation: `AOM_000830` / `AOM_101094`
- Enzyme treatment: `AOM_000820` / `AOM_101092`
- Alkali treatment: `AOM_000819` / `AOM_101087`
- Roasting: `AOM_000832` / `AOM_101098`

Current facet governance already reuses legacy Ensiling `AOM_000831`, making
parallel treatment inconsistent. Legacy AOM also contains two Extrusion
concepts (`AOM_000833` thermal and `AOM_000841` mechanical), requiring
polyhierarchy or another explicit modelling decision rather than label-only
deduplication.

### Completed work

1. Reused `AOM_000845` as canonical process root and removed generated parallel
   root from active release.
2. Resolved Extrusion to canonical `AOM_000833` with thermal, mechanical, and
   shaping parents; deprecated duplicate `AOM_000841`.
3. Added particle-reduction, separation/fractionation, and
   shaping/agglomeration objective branches while retaining mechanism branches.
4. Split presentation, bulk consistency, and moisture condition into independent
   predicates and hierarchies.
5. Migrated governed assertions and recorded full review under
   `review/livestock-v27/`.

Remaining holds: `AOM_001961`, `AOM_002008`, and `AOM_006004` retain Grinding
but receive no automatic comminuted-particle presentation until source evidence
resolves their ground-fluid contradiction.

Do not merge concepts automatically from labels alone. Existing definitions
include scope differences and some source text still needs authority review.

## Ingredient-part hierarchy consolidation

- Status: pending review
- Priority: high
- Added: 2026-08-07

### Problem

Legacy AOM already contains `AOM_000532` Ingredient part, defined as the part
of raw material entering an animal diet. Facet work created parallel root
`AOM_101019` Ingredient anatomical parts instead of first reviewing and
extending that existing concept.

Confirmed exact preferred-label collisions include:

- Shell: legacy `AOM_000558` / facet `AOM_101040`
- Blood: legacy `AOM_001616` / facet `AOM_101103`

Many other apparent matches are not exact duplicates. For example, Maize Husk
is a source-specific feed material while Husk is a reusable material-part
value. Such pairs require an explicit `aom:materialComponent` assertion, not
identity merging.

### Required work

1. Audit `AOM_000532`, its intended scope, workbook fields, and current uses.
2. Compare every `AOM_101019` child with all legacy AOM identities and external
   anatomical authorities—not preferred labels alone.
3. Reuse or extend `AOM_000532` if scope review confirms it as canonical root;
   otherwise document exact distinction between roots.
4. Consolidate genuine duplicates with replacement crosswalks while preserving
   stable identifiers and source records.
5. Keep source-specific feed materials separate; link them to generic component
   values through explicit predicates.
6. Build useful plant/animal component hierarchy rather than one flat list,
   including polyhierarchy where biologically valid.
7. Add collision tests preventing allocation of a facet concept before legacy
   identity review.

Do not deprecate or merge any concept until workbook occurrence, definition,
hierarchy, and downstream assertion impact are reviewed.
