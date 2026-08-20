# Cohort D recommendations: chemical identity and material components

Status: proposed under
[era-program #55](https://github.com/ERAgriculture/era-program/issues/55).

## Snapshot

Complete current review scope contains 164 concepts:

- 18 chemical-identity concepts including `AOM_101146`;
- 105 composition concepts including `AOM_000196`;
- 41 material-component concepts including `AOM_101085`.

Reviewed targets carry 627 current material-facet assertions: 509
`ingredientPart`, 87 `materialComponent`, 23 `primaryConstituent`, and eight
`compositionState` assertions. Exact rows are in `material_usage_inventory.csv`.

## Authority comparison

| Authority | Supported conclusion | Boundary |
|---|---|---|
| [FoodOn](https://github.com/FoodOntology/foodon) | Keep material, source, component, processing, and chemical facets independent; reuse external anatomy and chemistry ontologies. | FoodOn includes inherited LanguaL classes and is not a feed-regulatory hierarchy template. |
| [ChEBI chemical entity](https://www.ebi.ac.uk/chebi/CHEBI%3A24431) and [chemical substance](https://www.ebi.ac.uk/chebi/CHEBI%3A59999) | Chemical identity is distinct from measured amount or feed-product use. | ChEBI does not classify feed materials or additive authorization. |
| [Plant Ontology](https://github.com/Planteome/plant-ontology) | Endosperm is anatomy; germ is only a related synonym for plant embryo. | Commercial germ fractions need manufacturing evidence and cannot be assumed exact embryo. |
| [EU Catalogue](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02013R0068-20220724) | Maize bran and maize germ are manufacturing products containing mixtures of grain tissues. | Regulatory product definitions do not define universal anatomy. |
| [AGROVOC Straw](https://agrovoc.review.fao.org/browse/agrovoc/en/page/c_7441) and [NALT crop residues](https://lod.nal.usda.gov/nalt/en/page/24251) | Straw and stover are crop-residue products/materials. | Thesaurus broader relations are not formal identity axioms. |

Full supported claims and limitations are in `evidence_register.csv` and
`authority_comparison.csv`.

Nine reuse or collision cases are explicit in `identity_overlap_review.csv`,
including Blood, Protein, Starch, Oil, Straw, Bran, Germ, Carbohydrate, and Ash.
No rename or reclassification bypasses those identity decisions.

## Core architecture

Keep four independent questions:

1. **What chemical entity is present?** Chemical identity, mapped to ChEBI when
   exact.
2. **How much is present?** Measured feed-composition characteristic and
   quantitative observation.
3. **What material or anatomical component is represented?** Component
   relation with an externally mapped component value.
4. **How is item used or regulated?** Feed material, formulation, additive, or
   another product kind, already separated by ADR 0045.

A chemical substance can be used as feed material or additive, but use does
not make chemical identity a narrower chemical class. Low inclusion rate is
not sufficient to define additive status. Link identity to product kind or use;
do not duplicate chemical concept under each use branch.

## Chemical identity versus composition

`AOM_101146 Feed chemical entities` does not duplicate `AOM_000196 Feed
Chemical Composition` in meaning, but current labels and definitions make the
boundary hard to see.

Recommendations:

- retain `AOM_101146`, rename it **Feed-related chemical entities**, and scope it
  to identity-level chemical entities used in feed description;
- retain `AOM_000196`, rename it **Feed composition characteristics**, and
  scope descendants to measurable or observable composition properties;
- map `AOM_101146` broadly to ChEBI chemical entity rather than copying ChEBI;
- retain `AOM_101147 Chemical substances` only for chemically identified
  substances or substance groups and review exact ChEBI mappings per child;
- rename `AOM_101023 Primary chemical constituents` to **Chemical constituent
  categories** because `aom:primaryConstituent` already supplies primary role;
- keep feed-material identities such as starch products or oils under Feed
  materials while linking their chemical constituent separately;
- deprecate `AOM_101120 Protein constituent` after migration to existing
  `AOM_001571 Protein`, subject to definition correction and collision gates;
- retain other role-suffixed constituent values temporarily, but review exact
  identity, mappings, and label collisions before removing “constituent”.

Composition labels such as `AOM_000228 Carbohydrate` denote concentration
characteristics, not chemical identity. Cohort E should relabel ambiguous
composition concepts as “content”, “concentration”, or another measured
characteristic without merging their stable IDs with chemical entities.

## Component relation

`aom:ingredientPart` is already a subproperty of `aom:materialComponent`.
Retain that specialization for true anatomical/source-part assertions and use
`materialComponent` as canonical broad query. Consumers without subproperty
reasoning may materialize broad triples or query both properties; no blanket
migration of 509 valid specialized assertions is proposed.

Target semantic type and subproperty scope should distinguish anatomical
structures, body substances, processed fractions, and other components.

## Anatomical components

Retain `AOM_101019 Anatomical components`, then add reviewed **Plant anatomical
components** and **Animal anatomical components** navigation groups. Do not add
Other anatomical components. Unmapped or ambiguous values remain visible holds
rather than a permanent catch-all.

The complete 31-child review is in `anatomical_authority_mapping.csv`:

- 15 plant values have direct exact-label Plant Ontology candidates;
- Liver has direct Uberon candidate;
- Viscera needs collective-versus-singular review;
- Germ requires explicit semantic split;
- remaining common-language values need taxon-aware exact mapping review.

`AOM_101145 Animal body substances` remains separate from anatomy. Review
`AOM_101103 Blood component` as duplicate of existing `AOM_001616 Blood`; if
definitions match, deprecate newer component ID and reuse stable Blood identity.
Blood feed materials may separately bear by-product role; body substance and
economic role are independent.

## Bran, germ, and endosperm

These should follow one modelling principle, not one forced parent:

- `AOM_101153 Endosperm` is anatomical tissue and remains under Plant
  anatomical components, mapped to `PO:0009089`;
- `AOM_101104 Bran` is a process-defined milling fraction containing several
  tissues; move it directly under `AOM_101143 Processed material fractions`;
- retire one-child `AOM_101144 Cereal milling fractions` unless a reviewed
  multi-member cohort justifies it;
- split `AOM_101029 Germ`: plant embryo anatomy maps only relatedly to
  `PO:0009009`, while commercial maize germ is a manufacturing product and
  should remain a feed-material/fraction identity with process provenance.

This removes Bran-specific hierarchy without falsely calling Bran anatomy.

## Straw and stover

Retire `AOM_101154 Composite crop-residue components`. Straw and stover are
crop-residue product/material identities, not components of a material whose
identity is already “maize straw” or “maize stover”. Do not repurpose published
component IDs as material IDs without identity review.

Implementation should:

- remove component use of `AOM_101105 Stover` and `AOM_101106 Straw`;
- migrate 66 tautological `materialComponent` assertions;
- review `AOM_101106` against `AOM_000582 Unspecified Straw` and determine
  whether any generic Stover concept remains necessary after source-specific
  material hierarchy is complete;
- retain source, process, form, moisture, and crop-residue product-role facets;
- assert Stem, Leaf, or other anatomy only when source evidence supports actual
  retained structures.

## Native-component retention

`AOM_101115 Native-component retention states` does not belong under chemical
composition as one undifferentiated branch.

- move Whole-crop and Whole-grain toward component-integrity modelling;
- review Whole-milk and Native-fat-retained separately in Cohort E because one
  may express retained components while the other is composition state;
- retain positive `retainsComponent` assertions; do not model absence of a
  process as a positive category.

## Required decisions

1. Approve identity, measured composition, component, and product-use
   separation.
2. Approve Plant and Animal anatomical navigation; reject permanent Other.
3. Approve Bran direct placement under Processed material fractions and retire
   one-child Cereal milling fractions.
4. Approve Germ anatomy-versus-manufacturing split and Endosperm anatomy.
5. Approve retirement of Composite crop-residue components and migration of
   Straw/Stover to material identities.
6. Approve `materialComponent` as canonical broad component query while
   retaining `ingredientPart` as scoped subproperty for true anatomical parts.
7. Approve chemical-root and composition-root renames plus constituent-role
   cleanup direction.
8. Approve component-integrity direction for Whole-crop and Whole-grain while
   leaving full Composition and Form implementation to Cohort E.

No hierarchy, identifier, schema, binding, generated distribution, or Skosmos
change is made by this review.
