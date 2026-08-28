# ADR 0053: Agricultural practice, outcome, and economic-variable foundation

- Status: Accepted
- Date: 2026-08-24
- Last reviewed: 2026-08-28
- Accepted: 2026-08-28 by P. Steward
- Owners: ERA-AOM semantic and data-model governance
- Tracking: [era-program #17](https://github.com/ERAgriculture/era-program/issues/17)
- Evidence:
  [Human acceptance record](../../review/crop-foundation-v3/README.md),
  [Guided-review recommendations](../../review/crop-foundation-v2/GUIDED_REVIEW_RECOMMENDATIONS.md),
  [baseline crop-foundation review](../../review/crop-foundation-v1/RECOMMENDATIONS.md)
- Method: [Agricultural practice and outcome foundation governance](../methods/agricultural-practice-outcome-foundation-governance.md)
- Depends on:
  [ADR 0051](0051-whole-vocabulary-resource-boundaries-and-migration-sequence.md),
  [ADR 0052](0052-data-model-registry-and-shared-core-contract.md)

## Context

Wave 2 begins with canonical workbook resources `prac`, `out`, and `out_econ`.
Current pilot normalizes 196 practice rows and 116 outcome rows into two
crop-labeled SKOS schemes. It creates 421 concepts, including 109 generated
intermediate nodes, and converts all 405 source hierarchy edges to
`skos:broader`. Sixty-five economic rows are omitted.

Sources are not crop-only. Practice rows include livestock and energy
management. Outcome rows include crop, livestock diet and production,
cookstove, environmental, social, and economic measures. Source hierarchy also
mixes identity, navigation, application state, comparison logic, control roles,
analytical metadata, and accounting categories.

Current pilot changes 58 integer outcome notations by appending `.0`, emits 89
literal `NA` sentinels as semantic values, and creates identities parallel to
existing AOM concepts. `out_econ` repeats one placeholder identifier on every
row and contains missing, duplicate, swapped, and ambiguous definitions.

## Decision

### Registry scope and module routing

Treat `prac`, `out`, and `out_econ` as cross-domain ERA source registries, not
crop concept schemes. Current pilot scheme names are not suitable for public
release.

Assign approved identities by row to `aom-crop`, `aom-livestock`, demonstrated
`aom-core`, or another approved module. Energy and cookstove terms remain on
module hold until architecture assigns ownership. Reporting convenience or
reuse in one source sheet does not establish shared-core identity.

### Practice semantics

Separate:

1. agricultural practice concept;
2. occurrence applying practice to managed system;
3. condition or baseline specification;
4. experimental treatment, comparator, or control role.

Do not encode study role in preferred practice label. Conventional management
can remain valid practice identity and separately bear comparator role. Absence,
unspecified states, generated reductions, generated substitutions, and source
descriptors require explicit dispositions before promotion.

### Outcome semantics

Represent reviewed outcome variables as `sosa:Property` specifications linked
as needed to feature of interest, observation procedure, direct or derived
measure, numerator, denominator, formula, QUDT quantity kind, unit, scale,
denominator basis, and interpretation constraint.

Use current SOSA `sosa:Property`; do not introduce deprecated
`sosa:ObservableProperty`. Apply Crop Ontology trait-method-scale pattern where
crop phenotype scope fits. Do not treat example-unit strings or analytical
flags as complete semantic bindings.

### Economic semantics

Integrate `out_econ` through same observation foundation, extended with
economic property, cost or benefit classification, object, activity,
transaction, actor, time, currency, denominator, allocation basis, and valuation
method.

Accounting category is contextual unless evidence proves it intrinsic. Fixed
and variable `Equipment` rows therefore require decomposition or unambiguous
scoped names. No `out_econ` identifier is allocated until placeholder values and
source-definition defects are resolved.

### Navigation and hierarchy

Treat theme, pillar, subpillar, and indicator as reporting navigation and model
them through `skos:Collection` membership by default. Source order and worksheet
levels do not establish inherent `skos:broader` meaning.

Do not promote any current generated intermediate node or edge as-is. Collapse
same-label parent and child duplicates unless evidence establishes separate
identities. Review remaining practice groups extensionally to decide true
broader concept versus editorial collection.

### Source codes and missing values

Govern source codes as lexical identifiers. Preserve displayed workbook
notation and raw source provenance. Prohibit vector-wide numeric formatting,
including automatic `.0` suffixes or binary floating representations, when
constructing public IDs.

Normalize literal `NA` source sentinels to null in semantic output while
retaining raw source cell provenance. Operational `Linked.Tab` and `Linked.Col`
values remain provenance until field-key contracts are approved.

### Identity continuity

Run global label, definition, code-mapping, lifecycle, and module review before
ID allocation. Existing stable AOM IDs have priority when compatible identity
is confirmed. Same label, exact external label, or legacy `relatedMatch` does
not prove equivalence. Ambiguous code mappings remain held. Published IDs are
never deleted, reassigned, or duplicated.

Do not mint same-label context concepts when source rows conflate different
resource types. Model field `Urea` and `Ash` rows as application practices linked
to governed materials; model crop `Heat Tolerance` as use of a heat-tolerant
crop variety linked to trait and variety facets; model breed `Unspecified` as a
field-scoped missing or unspecified value with raw provenance, not a public
global identity.

### Shared-core scaffold

Carry 15 candidates into later implementation design: practice identity,
practice application, experimental roles, baseline condition, outcome property,
procedure, derivation, feature of interest, quantity/unit profile, reporting
collection, economic measure, accounting classification, and module assignment.

Candidate status does not approve class IRIs or axioms. Cross-domain promotion
requires crop and livestock evidence plus ADR 0052 field-contract alignment.

### Guided-review decision

On 2026-08-28 P. Steward accepted:

1. accept cross-domain routing, practice-context separation, SOSA outcome
   modeling, and economic decomposition;
2. accept lexical source codes and collection navigation with revised wording
   and scoped collection labels;
3. accept stable-ID priority only with identity, entity-type, lifecycle, and
   module conditions;
4. convert 43 editorial nodes to collections, collapse 13 duplicate parent/leaf
   nodes, and hold 53 practice groups for extensional review;
5. decompose Urea, Ash, Heat Tolerance, and Unspecified rather than minting
   same-label context identities;
6. require source-owner correction or hold for economic defects before ID
   allocation;
7. review external candidates individually: four strong close-match candidates,
   one conditional close-match candidate, one definition-overlap hold, and 20
   non-identity facet candidates; and
8. keep all 14 energy and cookstove rows on module hold.

Detailed recommendations remain unchanged in
[`guided_decision_recommendations.csv`](../../review/crop-foundation-v2/guided_decision_recommendations.csv).
Final human decisions, conditions, and holds are recorded separately in
[`guided_decision_approvals.csv`](../../review/crop-foundation-v3/guided_decision_approvals.csv).

## Authority comparison

- [W3C SKOS](https://www.w3.org/TR/skos-reference/) supports concept,
  collection, relation, and mapping semantics but not automatic workbook
  hierarchy.
- [W3C SOSA/SSN 2023](https://www.w3.org/TR/vocab-ssn-2023/) supports property,
  observation, feature, procedure, and result semantics but not ERA row identity.
- [Crop Ontology](https://cropontology.org/about) supports crop
  trait-method-scale variables within its domain boundary.
- [AgrO](https://github.com/AgriculturalSemantics/agro) supports agronomic
  practice and variable candidates but exact labels do not establish identity.
- [FAO AGROVOC](https://agrovoc.fao.org/) supports broad agricultural lexical
  mapping candidates but not experiment-variable structure.
- [FoodOn](https://foodon.org/food-facets/food-transformation-process/) supports
  food transformation and output modeling, not all field practices.
- [QUDT](https://www.qudt.org/catalog/qudt-catalog.html) supports quantities,
  units, and dimensions, not agricultural property identity.
- [EU FSDN](https://agriculture.ec.europa.eu/data-and-analysis/farm-structures-and-economics/fsdn_en)
  and [FAO SEEA-AFF](https://www.fao.org/fileadmin/templates/ess/ess_test_folder/Publications/Agrienvironmental/SEEA_AFF_FINAL_Clean_03.pdf)
  support accounting boundaries but not direct ERA variable mappings.

Full support and limitation statements are recorded in
[`authority_comparison.csv`](../../review/crop-foundation-v1/authority_comparison.csv).

## Evidence

- [Recommendations](../../review/crop-foundation-v1/RECOMMENDATIONS.md)
- [Human acceptance record](../../review/crop-foundation-v3/README.md)
- [Guided decision approvals](../../review/crop-foundation-v3/guided_decision_approvals.csv)
- [Source correction approvals](../../review/crop-foundation-v3/source_correction_approvals.csv)
- [Guided-review recommendations](../../review/crop-foundation-v2/GUIDED_REVIEW_RECOMMENDATIONS.md)
- [Guided decision rows](../../review/crop-foundation-v2/guided_decision_recommendations.csv)
- [Guided hierarchy dispositions](../../review/crop-foundation-v2/hierarchy_guided_dispositions.csv)
- [Same-label decomposition review](../../review/crop-foundation-v2/same_label_decomposition_review.csv)
- [Source issue action plan](../../review/crop-foundation-v2/source_issue_action_plan.csv)
- [Economic correction proposals](../../review/crop-foundation-v2/economic_source_correction_proposals.csv)
- [External mapping dispositions](../../review/crop-foundation-v2/external_mapping_dispositions.csv)
- [Energy module holds](../../review/crop-foundation-v2/energy_module_holds.csv)
- [Source snapshot](../../review/crop-foundation-v1/source_snapshot.csv)
- [Row dispositions](../../review/crop-foundation-v1/source_row_dispositions.csv)
- [Hierarchy-node review](../../review/crop-foundation-v1/hierarchy_node_review.csv)
- [Hierarchy-edge review](../../review/crop-foundation-v1/hierarchy_edge_review.csv)
- [Identity collision audit](../../review/crop-foundation-v1/identity_collision_audit.csv)
- [Source-quality issues](../../review/crop-foundation-v1/source_quality_issues.csv)
- [Pilot contract audit](../../review/crop-foundation-v1/pilot_contract_audit.csv)
- [Authority candidates](../../review/crop-foundation-v1/authority_label_candidates.csv)
- [Shared-core candidates](../../review/crop-foundation-v1/shared_core_candidate_review.csv)
- [Guided review](../../review/crop-foundation-v1/guided_review.csv)
- [Evidence register](../../review/crop-foundation-v1/evidence_register.csv)

## Consequences

### Positive

- Practice, outcome, and economic sources gain complete row-level review.
- Crop work no longer absorbs livestock, energy, or shared semantics by default.
- Observation properties, methods, quantities, units, and reporting navigation
  become separable.
- Existing AOM identifiers can be reused without silent duplication.
- Source defects and authority claim boundaries remain traceable.

### Costs

- Current pilot cannot be promoted without structural rebuild.
- Source corrections and human identity decisions precede implementation.
- Some convenient source hierarchies become collections or contextual facets.
- Energy module ownership and economic-accounting details need further ADR work.
- Consumer migration must account for replacement of provisional pilot IDs.

## Alternatives considered

### Promote current pilot and repair later

Rejected. It would publish wrong scope, duplicate identities, mutable numeric
notations, literal missing-value sentinels, and unreviewed broader relations.

### Put all registries in `aom-crop`

Rejected. Source content is cross-domain and includes existing livestock AOM
identities plus energy and shared observational semantics.

### Make every source level a SKOS concept

Rejected. Reporting and editorial groups do not automatically bear semantic
broader meaning; duplicate parent/leaf identities already demonstrate failure.

### Mint one concept per source row

Rejected. Rows can be deprecated, compound, contextual, generated, duplicated,
or schema-like, while several rows already match stable AOM identities.

### Use exact authority labels as automatic mappings

Rejected. Exact labels can refer to different entities, scopes, roles, or
process applications. Mapping relation requires claim-level review.

## Implementation gates

1. **Complete 2026-08-28:** human approval of ADR 0053 and all guided-review
   decisions, including explicit revisions, conditions, and holds.
2. Apply approved canonical source corrections for missing, placeholder,
   duplicate, swapped,
   ambiguous, status, and sentinel defects.
3. Approval or hold for all 377 row dispositions.
4. Approval or replacement for all 109 generated nodes and 405 current edges.
5. Global stable-ID and module review for all collision and mapping candidates.
6. ADR 0052 acceptance and explicit shared-core class or property design.
7. Deterministic implementation from governed sources; no hand-edited generated
   outputs.
8. RDF, SHACL, identity, mapping, clean-rebuild, and checksum validation.
9. Consumer contract tests and guided Skosmos acceptance before release.

## Approval record

Accepted by P. Steward on 2026-08-28 after guided review of `GR-01` through
`GR-12`.

- `GR-01`–`GR-06`: accepted with stated lexical-code, navigation, stable-ID,
  practice-context, and outcome-property conditions.
- `GR-07`–`GR-08`: accepted with 53 practice-group holds and explicit
  practice/material/trait/missing-value decomposition.
- `GR-09`–`GR-10`: accepted; seven economic source corrections approved and
  `Nutrient/Soil management` retained on clarification hold.
- `GR-11`: four AgrO close matches approved for later implementation;
  Monoculture and Controlled Grazing held; 20 other identity mappings rejected
  while retaining facet evidence.
- `GR-12`: all 14 energy and cookstove rows retained on module hold.

Acceptance authorizes approved source correction. It does not itself change
source workbook, pilot distribution, AOM identity, hierarchy, mapping assertion,
shared-core axiom, module assignment, publication status, consumer contract, or
release artifact. Semantic implementation remains a separate approval and PR.
