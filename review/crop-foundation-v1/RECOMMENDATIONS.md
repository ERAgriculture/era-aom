# Agricultural practice, outcome, and economic-variable recommendations

Status: recommendation-only Wave 2 foundation review for
[era-program #17](https://github.com/ERAgriculture/era-program/issues/17).

Decision proposal:
[ADR 0053](../../docs/decisions/0053-agricultural-practice-outcome-and-economic-variable-foundation.md).

## Snapshot

Canonical review covers 377 source rows: 196 practices, 116 outcomes, and 65
economic variables. Current pilot contains 421 concepts, including 109 generated
intermediate nodes, and converts all 405 source hierarchy edges to
`skos:broader`. `out_econ` is absent.

Review records:

- 377 row-level dispositions: 244 proposals and 133 holds;
- 265 source-quality and lifecycle issues;
- 36 pilot-internal normalized-label collision groups;
- 100 source-to-AOM collision records affecting 97 source rows;
- 59 exact normalized label-definition identity signals;
- 97 rows with one or more legacy ERA-to-AOM code mappings;
- 26 AgrO, ENVO, or ChEBI exact-label candidates affecting 24 rows;
- 15 shared-core model candidates and 12 guided-review decisions.

Counts describe review coverage, not approved identities.

## Main finding

`prac` and `out` are cross-domain ERA registries, not crop-only concept schemes.
They contain crop, livestock, energy, environmental, social, and economic
content. Current names “AOM crop agricultural practices” and “AOM crop
outcomes” therefore misstate scope. Routing every row to `aom-crop` would also
duplicate stable AOM identities already present in livestock staging.

Treat source tables as governed registries. Assign each approved identity to
crop, livestock, core, or another approved module after row-level identity
review. Do not mint public parallel `era:practice:*` or `era:outcome:*`
identities where stable AOM identity already exists.

## Practice model

Current hierarchy mixes several different things:

- agricultural practice identities;
- practice-group navigation;
- application conditions and material choices;
- generated comparison records;
- conventional, absent, unspecified, or control states;
- experimental treatment and comparator roles;
- source-schema descriptors such as “Predominant Biodigestor Model”.

Separate four layers:

1. agricultural practice concept;
2. occurrence applying practice to managed system;
3. condition or baseline specification;
4. experimental role borne by study arm or condition.

“Control” must not become part of practice identity. Conventional tillage can
remain a valid practice, while its comparator role belongs to study design.
Absence rows such as no fertilizer or no irrigation may require condition
modeling rather than positive practice identity. Automatically generated
reduction and substitution rows require derivation review before promotion.

Same labels do not imply same identities. Field application of `Urea` or `Ash`
is not feed-material identity. Crop-variety `Heat Tolerance` is distinct from
animal-breed use currently carrying same AOM label. Generic `Unspecified`
cannot be globally reused without scoped meaning.

## Outcome model

Pillar, subpillar, and indicator levels are reporting navigation. They should
default to `skos:Collection` membership, not inherent `skos:broader` meaning.
Every leaf outcome should be reviewed as structured property specification:

- `sosa:Property` identity;
- feature of interest;
- observation or calculation procedure;
- direct or derived measure;
- numerator, denominator, and formula where derived;
- QUDT quantity kind, unit, scale, and denominator basis;
- interpretation direction and analytical constraints;
- membership in one or more reporting collections.

This follows W3C SOSA/SSN observation semantics and, where appropriate, Crop
Ontology trait-method-scale pattern. Free-text example units, `Sign`,
`TC.Ratio`, `Negative Values`, and `Not.Perc` are source analytical metadata;
they are not one-dimensional SKOS concept properties.

## Economic variables

`out_econ` cannot enter pilot as a seventh-level taxonomy. Every row still uses
same placeholder `AOM_will_add_unique_value`; two definitions are missing;
`Equipment` appears under fixed and variable costs with different accounting
contexts; several definitions are swapped, example-only, or ambiguous.

Model economic rows using:

- economic property such as cost, income, benefit, or product value;
- cost or benefit classification;
- object, input, asset, activity, or product concerned;
- transaction type and actor where relevant;
- time, currency, physical denominator, and allocation basis;
- valuation or accounting method.

Fixed versus variable treatment can depend on context. It must not always be
intrinsic to identity. Use FSDN and SEEA-AFF as accounting-boundary evidence,
not automatic mappings.

## Hierarchy review

Current generator mints intermediate identities from parent, label, and source
notation. This creates parallel parents and leaves with same labels, including
`Aquasilviculture`, `Biochar`, `Conventional Tillage`, `Feed Intake`, `Yield
Stability`, and many others.

Recommendations:

1. Do not promote any of 109 generated intermediate nodes as-is.
2. Collapse same-label parent/leaf duplicates unless evidence establishes two
   identities.
3. Represent themes and reporting levels as collections.
4. Review remaining practice groups extensionally: some are true broader
   practices, others are editorial collections.
5. Replace each current edge only after node disposition is approved.

Every node and edge disposition is recorded in
[`hierarchy_node_review.csv`](hierarchy_node_review.csv) and
[`hierarchy_edge_review.csv`](hierarchy_edge_review.csv).

## Source and identifier contract

Outcome `Code` is a numeric spreadsheet column but functions as identifier
notation. Current vector-wide formatting adds `.0` to 58 integer codes. Govern
codes as lexical identifiers and preserve displayed source notation. Never use
spreadsheet numeric formatting to generate public IDs.

Practice source also contains 89 literal `NA` sentinels in suffix and linkage
fields. Normalize them to null while preserving raw source provenance. Do not
publish literal `NA` as semantic value.

Legacy ERA mappings and exact labels are evidence candidates only. Identity
reuse requires compatible definition, scope, entity type, lifecycle, and
module. Existing published AOM IDs have priority when identity is confirmed;
ambiguous codes remain held and IDs are never reassigned.

## Authority comparison

Full claim boundaries are recorded in
[`authority_comparison.csv`](authority_comparison.csv).

| Authority | Supports | Boundary |
|---|---|---|
| [W3C SKOS](https://www.w3.org/TR/skos-reference/) | Concepts, semantic relations, mappings, and collections | Source reporting order does not establish semantic hierarchy |
| [W3C SOSA/SSN 2023](https://www.w3.org/TR/vocab-ssn-2023/) | Properties, observations, features, procedures, and results | Does not establish ERA row identity or reporting pillars |
| [Crop Ontology](https://cropontology.org/about) | Crop trait-method-scale variable pattern | Does not cover all management, livestock, social, energy, or economic rows |
| [AgrO](https://github.com/AgriculturalSemantics/agro) | Agronomic practices, techniques, and experimental-variable candidates | Exact label is not identity proof |
| [FAO AGROVOC](https://agrovoc.fao.org/) | Broad multilingual agricultural terminology | Does not establish experiment roles or variable derivations |
| [FoodOn](https://foodon.org/food-facets/food-transformation-process/) | Food transformation and process-output modeling | Does not cover field management, study roles, or economics |
| [QUDT](https://www.qudt.org/catalog/qudt-catalog.html) | Quantity kinds, units, dimensions, and values | Does not establish agricultural property identity |
| [EU FSDN](https://agriculture.ec.europa.eu/data-and-analysis/farm-structures-and-economics/fsdn_en) | Farm bookkeeping, costs, outputs, inputs, and assets | Accounting scope is not direct ontology mapping |
| [FAO SEEA-AFF](https://www.fao.org/fileadmin/templates/ess/ess_test_folder/Publications/Agrienvironmental/SEEA_AFF_FINAL_Clean_03.pdf) | Output, consumption, capital, inventories, and income boundaries | Sector accounting does not establish study-variable identity |

## Guided review

Review 12 decisions in [`guided_review.csv`](guided_review.csv), beginning with:

1. cross-domain source scope and module routing;
2. lexical source-code contract;
3. reporting collections versus semantic hierarchy;
4. stable AOM identity reuse rule;
5. practice, condition, and experimental-role separation;
6. SOSA-based outcome-variable model.

Then review generated practice parents, known same-label distinctions, economic
source corrections, economic decomposition, external candidates, and energy
module ownership.

## Evidence

- [Source snapshot](source_snapshot.csv)
- [Row dispositions](source_row_dispositions.csv)
- [Source-quality issues](source_quality_issues.csv)
- [Identity collision audit](identity_collision_audit.csv)
- [Pilot contract audit](pilot_contract_audit.csv)
- [Authority comparison](authority_comparison.csv)
- [Authority label candidates](authority_label_candidates.csv)
- [Shared-core candidates](shared_core_candidate_review.csv)
- [Claim-level evidence register](evidence_register.csv)
- [Machine summary](review_summary.json)

No source workbook, pilot distribution, AOM identity, hierarchy, semantic
binding, mapping, module assignment, or release artifact changes in this review.
