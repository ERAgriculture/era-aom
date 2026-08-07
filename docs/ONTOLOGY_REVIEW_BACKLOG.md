# ERA-AOM ontology review backlog

## Processing-method hierarchy consolidation

- Status: pending review
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

### Required work

1. Inventory every new processing facet against legacy process concepts,
   definitions, hierarchy, workbook use, and feed-material assertions.
2. Classify each pair as exact duplicate, narrower/broader, related, or truly
   distinct.
3. Prefer one canonical processing-method concept per meaning. Preserve stable
   legacy IDs where semantics are sound; add explicit mappings and replacement
   crosswalks for retired duplicates.
4. Preserve useful biological/chemical/mechanical/thermal hierarchy. Support
   polyhierarchy where one process legitimately belongs to multiple groups.
5. Migrate generated feed-material assertions and ingestion crosswalks without
   changing source records.
6. Validate no duplicate preferred process identities remain and document
   decision in ADR before release cutover.

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
