# ADR 0053 guided-review recommendations

## Decision boundary

This checkpoint recommends decisions. It does not accept ADR 0053, alter the
canonical workbook, allocate identifiers, approve external mappings, assign an
energy module, modify generated ontology data, or authorize release.

## Recommended decisions

1. **Cross-domain scope — accept.** Govern `prac`, `out`, and `out_econ` as
   cross-domain source registries. Route approved identities row by row.
2. **Source-code contract — accept with revision.** Preserve lexical source
   notation. Replace the question's inaccurate “eight corrections” with the
   audited 58 pilot notation mutations and 65 placeholder economic identifiers.
3. **Navigation — accept with revision.** Use collections by default. Give
   same-label collection/member pairs scoped navigation labels.
4. **Stable-ID reuse — accept with conditions.** Reuse only after compatible
   identity, entity type, lifecycle, module, label, and definition review.
5. **Practice context — accept.** Separate practice identity, application,
   condition or baseline, and experimental role.
6. **Outcome variable — accept.** Use `sosa:Property` with explicit feature,
   procedure, quantity, unit or basis, and derivation where applicable.
7. **Generated parents — accept policy with holds.** Convert 43 editorial
   nodes to collections, collapse 13 duplicate parent/leaf nodes, and hold 53
   practice groups for extensional review.
8. **Same-label rows — revise and decompose.** Model Urea and Ash as application
   practices linked to materials, Heat Tolerance as crop-variety use plus trait,
   and Unspecified as field-scoped missing information.
9. **Economic defects — accept source-correction gate.** Correct or hold defects
   before identifier allocation; source owner must approve workbook edits.
10. **Economic model — accept.** Separate measure, accounting context, object,
    activity, actor, transaction, time, currency, denominator, allocation basis,
    and valuation method.
11. **External candidates — accept individual review.** Retain four strong and
    one conditional `skos:closeMatch` candidates, one definition-overlap hold,
    and 20 non-identity facet candidates. Approve none yet.
12. **Energy boundary — hold.** Keep 14 rows module-unassigned until a later
    architecture decision establishes agricultural or household energy scope.

Full wording and blank human-decision fields are in
[`guided_decision_recommendations.csv`](guided_decision_recommendations.csv).

## Hierarchy result

| Disposition | Count | Meaning |
|---|---:|---|
| Collection | 35 | Editorial navigation without same-label collision |
| Collection with scoped label | 8 | Navigation and member property/practice share current label |
| Collapse generated parent into leaf | 13 | Same-label generated group duplicates source leaf |
| Hold for extensional review | 53 | Group membership does not yet prove broader-concept semantics |

No generated hierarchy node is promoted as-is. Detailed rows are in
[`hierarchy_guided_dispositions.csv`](hierarchy_guided_dispositions.csv).

## Source correction gate

All 265 source-quality issues have actions. Generator-only fixes cover 147
records. Remaining records require lifecycle hold, navigation-model change,
semantic decomposition, source correction, or source-owner decision. Eight
economic corrections are proposed separately; no workbook cell changed.

Notable proposals:

- distinguish equipment acquisition/depreciation from rental/maintenance;
- define loan interest cost rather than generic Loans;
- repair swapped female-family-labour and hired-labour definitions;
- hold Nutrient/Soil management until measure versus input is clarified;
- define monetary and non-monetized societal benefit measures with scope and
  measurement basis.

## External mappings

Definition and entity-type review supports later human consideration of:

- `prac:a11` Silvopasture → `AGRO_00000580`;
- `prac:a12` Multistrata Agroforestry → `AGRO_00000581`;
- `prac:d16` Rotational Grazing → `AGRO_00000430`;
- `prac:b54` Supplemental Irrigation → `AGRO_00000588`;
- `prac:h2` Monoculture → `AGRO_00000481`, conditional on separating
  experimental comparator context.

`prac:d19` Controlled Grazing remains held because source scope overlaps
rotational grazing and is broader than AgrO's intensive rotational definition.
Other exact-label candidates refer to materials, structures, processes, or cost
objects rather than source practice or observed-property identities.

## Authority comparison

- [W3C SKOS](https://www.w3.org/TR/skos-reference/) supports collections,
  concepts, semantic relations, and mapping relations; it does not turn source
  worksheet levels into semantic hierarchy.
- [W3C SOSA/SSN](https://www.w3.org/TR/vocab-ssn-2023/) supports property,
  feature, procedure, observation, and result modeling; it does not establish
  ERA source-row identity.
- [AgrO](https://github.com/AgriculturalSemantics/agro) provides relevant
  practice and material definitions; exact labels still require entity-type and
  scope review.
- [QUDT](https://www.qudt.org/) supports quantity and unit semantics; it does
  not establish agricultural outcome identity.

## Evidence

- [Baseline recommendations](../crop-foundation-v1/RECOMMENDATIONS.md)
- [Guided decision rows](guided_decision_recommendations.csv)
- [Hierarchy dispositions](hierarchy_guided_dispositions.csv)
- [Source issue actions](source_issue_action_plan.csv)
- [Economic correction proposals](economic_source_correction_proposals.csv)
- [External mapping dispositions](external_mapping_dispositions.csv)
- [Energy holds](energy_module_holds.csv)
- [Evidence register](evidence_register.csv)
- [Acceptance summary](acceptance_summary.json)

## Human review sequence

1. Record decision for GR-01 through GR-12.
2. Resolve any rejected or revised recommendation.
3. Approve source-correction wording separately from ontology design.
4. Update canonical workbook only after source-owner approval.
5. Regenerate review from corrected source.
6. Accept ADR 0053 only when remaining holds and implementation gates are
   explicit.
7. Start implementation in a separate change.
