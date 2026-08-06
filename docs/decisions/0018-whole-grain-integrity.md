# ADR 0018: Model whole grain as material integrity

- Status: Accepted
- Date: 2026-08-05
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Context

Legacy `Whole` conflates whole crop, whole grain, whole organism, dairy
composition, and physical presentation. Whole Grain Initiative defines whole
grain as intact or processed kernel retaining endosperm, germ, and bran in their
characteristic relative proportions. Grinding therefore does not negate
whole-grain status. AGROVOC similarly defines whole-grain flour through retention
of endosperm, bran, and germ.

Evidence:

- https://www.wholegraininitiative.org/media/attachments/2021/04/12/adapted-2021-03-17-definition-of-whole-grain-as-food-ingredient-proposed-by-global-working-group.pdf
- https://agrovoc.fao.org/browse/agrovoc/en/page/c_9f0af347
- review/livestock-v7/ingredient_model_gap_families.csv

## Decision

Add `aom:MaterialIntegrity` and `aom:materialIntegrity`. Add governed value
`Whole grain`. Assert it for reviewed maize, wheat, and rice materials whose
labels and crop-product context explicitly denote whole grain. Keep Grinding as
an independent processing assertion. Relabel concepts to state whole-grain scope
clearly.

Do not apply this value to whole-crop silage, whole milk, whole animals, or an
unqualified physical presentation. Do not infer it from token `Whole` without
reviewed cereal-grain context.

## Consequences

- Maize, wheat, and rice share one reusable integrity model.
- Whole-grain materials remain distinct from generic crop/source concepts.
- Ground whole grain remains queryable by both integrity and process.
- Legacy identifiers and old labels remain resolvable.
