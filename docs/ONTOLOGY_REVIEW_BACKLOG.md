# ERA-AOM ontology review backlog

## Feed taxonomy axis reclassification

- Status: implemented in accepted ADR 0044; 66 evidence holds remain governed
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

### Completed work

1. Reviewed and implemented all 220 row-level dispositions as one governed
   cohort, retaining 66 explicit evidence-dependent holds.
2. Separated feed materials, formulations, additives, chemicals, roles,
   components, processes, and composition states.
3. Retired eight published source concepts through compatibility policy and
   reserved two rejected generated identifiers without reuse.
4. Published method, authority comparison, evidence register, decision record,
   implementation register, and deterministic validation.
5. Regenerated release artifacts, rebuilt empty Fuseki storage, and passed
   exact notation search plus full local Skosmos acceptance.

Remaining holds require evidence types recorded in the v30 implementation
register; they must not be resolved by hierarchy inheritance alone.

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

- Status: structural root implemented in ADR 0044; biological subhierarchy review remains
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

### Completed work

1. Retired `AOM_000532` as a browse concept while preserving its schema-binding
   compatibility record.
2. Placed `AOM_101019 Anatomical components` under one governed
   `AOM_101085 Feed material components` architecture.
3. Separated cereal milling fractions, animal body substances, and composite
   crop-residue components from anatomical structures.
4. Added global collision checks before generated concept allocation.

### Remaining work

1. Compare every `AOM_101019` child with all legacy AOM identities and external
   anatomical authorities—not preferred labels alone.
2. Consolidate genuine duplicates with replacement crosswalks while preserving
   stable identifiers and source records.
3. Keep source-specific feed materials separate; link them to generic component
   values through explicit predicates.
4. Build useful plant/animal component hierarchy rather than one flat list,
   including polyhierarchy where biologically valid.

Do not deprecate or merge any concept until workbook occurrence, definition,
hierarchy, and downstream assertion impact are reviewed.
