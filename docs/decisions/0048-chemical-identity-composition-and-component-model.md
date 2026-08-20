# ADR 0048: Chemical identity, composition, and component model

- Status: Proposed
- Date: 2026-08-19
- Owners: ERA-AOM semantic governance
- Tracking: [era-program #55](https://github.com/ERAgriculture/era-program/issues/55)
- Evidence: [Cohort D review](../../review/livestock-v37/RECOMMENDATIONS.md)
- Depends on: [ADR 0045](0045-feed-product-kind-and-source-navigation.md),
  [ADR 0046](0046-ingredient-descriptor-lifecycle-and-browser-deprecation.md)

## Context

Current browsing places `AOM_101146 Feed chemical entities` parallel to
`AOM_000196 Feed Chemical Composition`, but labels do not expose identity versus
measurement. `AOM_101085 Feed material components` mixes anatomy, body
substances, processed fractions, and crop-residue products. Bran has a
one-child milling hierarchy; Germ mixes anatomy and manufacturing usage;
Straw/Stover are asserted as components of materials already identified as
Straw/Stover.

Complete review covers 164 concepts and 627 affected material assertions.
FoodOn supports independent material, origin, component, process, and chemical
facets. ChEBI distinguishes chemical entity identity from use. Plant Ontology
identifies Endosperm as anatomy but treats Germ only as a related synonym for
plant embryo. EU feed regulation defines maize Bran and Germ as manufacturing
products containing mixtures of tissues. AGROVOC and NALT classify Straw and
Stover as crop-residue products.

## Proposed decision

### Independent axes

Keep chemical identity, measured composition, material component, and feed
product kind independent.

- Rename `AOM_101146` to **Feed-related chemical entities**.
- Rename `AOM_000196` to **Feed composition characteristics**.
- Link exact chemical identities to ChEBI when supported.
- Represent material/additive use independently; inclusion rate alone does not
  define product kind.
- Rename `AOM_101023` to **Chemical constituent categories** because relation
  `aom:primaryConstituent` supplies primary role.
- Deprecate `AOM_101120 Protein constituent` in favour of existing
  `AOM_001571 Protein` after governed migration and definition correction.

### Components

Use `aom:materialComponent` as canonical broad component query. Retain
`aom:ingredientPart` as scoped subproperty for true anatomical/source-part
assertions; consumers without subproperty reasoning must materialize or query
the broad relation explicitly.

Retain `AOM_101019 Anatomical components` with Plant and Animal navigation
groups. Do not create permanent Other anatomy branch. Keep animal body
substances separate from anatomy and economic product role.

### Fractions and residues

- Keep Endosperm as Plant anatomy mapped to `PO:0009089`.
- Put Bran directly under Processed material fractions and retire one-child
  Cereal milling fractions unless additional reviewed members justify it.
- Split Germ into anatomical plant embryo meaning and process-defined germ
  material/fraction meaning.
- Retire Composite crop-residue components.
- Remove Straw and Stover component use, migrate tautological assertions, and
  reuse existing material identities after collision review rather than
  repurposing component IDs automatically.

### Component integrity

Move Whole-crop and Whole-grain out of chemical composition toward positive
component-integrity modelling. Leave Whole-milk, Native-fat-retained, and full
Composition/Form restructuring to Cohort E.

## Evidence

- [FoodOn repository](https://github.com/FoodOntology/foodon)
- [FoodOn and LanguaL design](https://foodon.org/design/foodon-and-langual/)
- [ChEBI chemical entity](https://www.ebi.ac.uk/chebi/CHEBI%3A24431)
- [ChEBI chemical substance](https://www.ebi.ac.uk/chebi/CHEBI%3A59999)
- [Plant Ontology](https://github.com/Planteome/plant-ontology)
- [EU Catalogue of feed materials](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02013R0068-20220724)
- [AGROVOC Straw](https://agrovoc.review.fao.org/browse/agrovoc/en/page/c_7441)
- [NALT crop residues](https://lod.nal.usda.gov/nalt/en/page/24251)
- [Claim-level evidence register](../../review/livestock-v37/evidence_register.csv)
- [Complete dispositions](../../review/livestock-v37/component_chemical_review.csv)
- [Identity overlap review](../../review/livestock-v37/identity_overlap_review.csv)

## Consequences

### Positive

- Browser distinguishes chemical identity from measured content.
- Plant/animal component navigation becomes useful without catch-all branches.
- Bran, Germ, Endosperm, Straw, and Stover follow evidence-based semantics.
- Stable IDs remain reusable across product use, process, source, and role.
- Broad component queries become simpler while specific anatomy semantics stay
  available.

### Costs

- 627 material assertions need migration or explicit retention review; 509
  valid `ingredientPart` assertions may remain specialized.
- Broad-query handling for `ingredientPart` requires downstream coordination.
- Germ and several vernacular plant-part terms need concept-level evidence.
- Composition labels and Native-fat-retained remain for Cohort E.

## Alternatives considered

### Merge chemical identity into Feed Chemical Composition

Rejected. Identity of a substance and measured amount in a material are
different entities and require different relations.

### Put chemical identities directly under Feed materials

Rejected. Chemical identity can bear several product uses; use or authorization
must not redefine chemical identity.

### Put Bran, Germ, and Endosperm under one anatomy branch

Rejected. Endosperm is anatomy; commercial Bran and Germ are process-defined
material fractions with mixed tissue composition.

### Keep Composite crop-residue components

Rejected. Current assertions are mostly tautological and external agricultural
authorities classify Straw and Stover as residue products/materials.

### Add Other anatomical components

Rejected. Permanent catch-all hides mapping gaps. Explicit holds are safer.

## Implementation gates

1. Human approval of ADR and every proposed or held disposition.
2. Exact external-mapping review for all 31 anatomical children.
3. Global preferred, alternative, hidden, deprecated, and external-label
   collision audit for every rename, replacement, or new navigation concept.
4. Consumer plan for subproperty-aware component queries and 627 assertion rows.
5. Governed source migration; no direct distribution edits.
6. Deterministic second-run generation and complete validator suite.
7. Clean Fuseki reload and guided Skosmos review of roots, mappings, and
   representative Bran/Germ/Endosperm/Straw/Stover cards.
8. Cohort E recommendation and decision before Composition/Form implementation.

## Approval record

Pending Pete Steward review.
