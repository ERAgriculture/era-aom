# AOM Livestock v2 release reconciliation

_Inventory date: 2026-07-29. Comparison only; no canonical-source change._

## Sources

Published dataset:

- *Agriculture Ontology for Meta-analysis (AOM): Livestock Prototype*;
- Harvard Dataverse version 2.0, released 2026-01-21;
- DOI: <https://doi.org/10.7910/DVN/75E7HV>;
- license: CC BY 4.0;
- authors: Todd Stuart Rosenstock, Peter Richard Steward, Namita Joshi, Lolita
  Muller, and Charity Ephamia Nabwire Juma;
- files: field descriptions plus `02a. AOM v2.0.0.csv`.

Comparison source: current authoritative ERA workbook `AOM` and related
livestock sheets. Workbook path and fingerprint remain private.

## Main result

Published v2 and workbook `AOM` are closely related snapshots:

| Check | Result |
|---|---:|
| Rows | 2,503 in each |
| Meaningful columns | 38 in each, same names/order |
| Published CSV raw columns | 134; 96 trailing columns empty |
| AOM ID differences by aligned row | 0 |
| L1–L10 hierarchy differences by aligned row | 0 |
| Normalized cell differences | 203 |

Differences after normalizing line endings, trailing whitespace, and Excel
`_x000D_` artifacts:

| Column | Different cells | Interpretation |
|---|---:|---|
| `Path` | 197 | stale/non-derived path strings dominate drift |
| `Edge_Value` | 1 | published trailing blank row contains `#N/A` |
| `Synonym` | 3 | one spelling correction and two added synonyms |
| `Scientific Name` | 1 | workbook adds `Zea mays` |
| `NCBI` | 1 | workbook adds maize NCBI Taxonomy URI |

Workbook is newer for some annotations. Published v2 is authoritative for its
released DOI version; workbook remains transition source for ERA until full
AOM cutover. Neither snapshot should overwrite the other.

## Critical integrity findings

### `Path` cannot be canonical

- 250 published paths disagree with their own nonblank L1–L10 hierarchy.
- 54 workbook paths disagree with their own nonblank L1–L10 hierarchy.
- Published and workbook hierarchy levels themselves align exactly.

Decision: normalize explicit parent relations from L1–L10. Generate `Path` as a
view. Never use stored `Path` for concept identity or hierarchy.

### Duplicate identity

`AOM_006275` identifies two different concepts:

- *Panicum antidotale Dried*;
- *Panicum maximum Dried*.

Stable IDs cannot identify two concepts. Review subsequently found existing
`AOM_001676` already represents *Megathyrsus maximus Dried*, equivalent to the
*Panicum maximum Dried* row. Approved resolution retains `AOM_006275` for
*Panicum antidotale Dried* and maps the other legacy row to `AOM_001676` through
an explicit crosswalk; no replacement concept is minted. Legacy evidence stays
unchanged.

### Duplicate concept path

Two IDs identify the same path/edge *Brewers Grain*:

- `AOM_000564`;
- `AOM_001884`.

Review approved `AOM_000564` as retained concept and `AOM_001884` as deprecated
with explicit replacement link. Retained preferred label is `Brewers grains,
dehydrated`; legacy labels remain synonyms. Decision is encoded as normalized
governance overlay without changing published-v2 source evidence.

## Related workbook assets

| Sheet | Rows | Columns | Role |
|---|---:|---:|---|
| `AOM_diets` | 1,193 | 25 | working feed subset/crosswalk |
| `ani_diet` | 1,806 | 21 | diet normalization and AOM assignment |
| `ani_process` | 175 | 13 | processing-term correction |
| `vars_animals` | 445 | 17 | animal variety/trait working table |
| `ssa_feedsdb` | 771 | 32 | restricted linkage/nutrient data; never publish |

Link integrity:

- all 849 distinct `AOM_diets` IDs exist in `AOM`;
- all 1,569 distinct mapped `ani_diet` AOM IDs exist in `AOM`;
- 22 `ani_diet` rows explicitly say `No Match in AOM`.

These sheets are provenance and curation inputs, not automatically independent
concept schemes.

## External mapping assets

Published v2 contains substantial mappings:

- generic ontology URI: 307 rows;
- AGROVOC: 320;
- NCBI Taxonomy: 1,337;
- WFO: 1,280;
- Feedipedia: 1,673;
- ILRI/SSA feed codes: 1,642;
- CPC product/component codes: 1,629/1,633;
- ERA codes: 332.

Mapping columns require normalization into one mapping per row with relation,
target scheme, target identifier/URI, evidence, status, source release, and
reviewer. At least 79 generic `Ontology` values use malformed `http:/...`
syntax. AI may propose repairs; human review approves them.

`ssa_feedsdb` cell values remain nonpublic. Public AOM mappings may be preserved
from DOI release under CC BY 4.0, but reuse must retain release provenance and
must not expose restricted linked nutrient records.

## Module implications

- Existing release belongs in `aom-livestock`.
- Current `prac`/`out` pilot belongs in `aom-crop`.
- AOM IDs and ERA IDs remain separate identifier lineages.
- Shared `aom-core` requires identity/definition review, not label matching.
- Existing livestock mapping work must be migrated, not discarded.

## Next implementation

1. Import published v2 into normalized staging tables without changing IDs.
2. Model L1–L10 as explicit broader relations; derive paths.
3. Quarantine duplicate ID/path cases for human decision.
4. Normalize external mappings and URI syntax with review status.
5. Link AOM-family curation sheets as provenance, not duplicate canonical data.
6. Build round-trip and semantic validation before module approval.
