# ADR 0047: Feed-process objective, benefit, and effect model

- Status: Proposed
- Date: 2026-08-18
- Owners: ERA-AOM semantic governance
- Tracking: [era-program #54](https://github.com/ERAgriculture/era-program/issues/54)
- Evidence: [Cohort C review](../../review/livestock-v35/RECOMMENDATIONS.md)
- Supersedes in part: [ADR 0042](0042-feed-process-and-material-state-axes.md)

## Context

ADR 0042 separated process mechanisms from objectives through polyhierarchy.
Guided Skosmos review found remaining ambiguity. Mechanical, Thermal,
Biological, and Chemical describe how operations occur. Particle-size
reduction, component separation, shaping, and moisture removal describe direct
technical objectives. Proposed Composition modification additionally conflated
direct transformation with nutritional reasons such as improved digestibility.

Current process closure contains 53 concepts including root, 12 direct children,
and 1,065 feed-material processing assertions. Definitions often claim improved
digestibility, nutrient availability, safety, or preservation as universal
effects despite dependence on material, protocol, animal, and measurement.

FoodOn models transformation processes through inputs and outputs, states that
processes add or remove qualities, and explicitly recognizes multi-purpose
processes. Its source table includes component separation, modification,
preservation, component addition, fat removal, water removal, fermentation,
hydrolysis, distillation, and rendering. FoodOn also mixes some mechanisms and
objectives in class hierarchy, so ERA uses it as vocabulary and modelling
evidence rather than copying its tree.

## Decision

### Semantic layers

ERA separates five layers:

1. **Process operation** — what was done, such as Grinding or Fermentation.
2. **Process mechanism** — how operation acts, such as Mechanical or Thermal.
3. **Technical process objective** — direct transformation sought, such as
   particle-size reduction or component separation.
4. **Intended feed benefit** — contextual reason for applying process, such as
   improved digestibility or storage stability.
5. **Observed process effect** — measured result from one process application.

`aom:processingMethod` targets operation concepts only. Root, mechanism
groupings, and objective groupings are never direct processingMethod values.

### Relations

Schema implementation will review these proposed relations:

- `aom:processMechanism` from ProcessingMethod to ProcessMechanism;
- `aom:technicalProcessObjective` from ProcessingMethod to
  ProcessTechnicalObjective;
- `aom:maySupportFeedBenefit` from ProcessingMethod to FeedBenefit;
- `aom:productionProcessProvenance` from FeedMaterial to upstream Process;
- `aom:observedProcessEffect` from ProcessApplication to Observation.

`maySupportFeedBenefit` is explicitly modal. Generic process identity never
entails achieved benefit. `observedProcessEffect` requires application and
measurement context and is not asserted on generic process concepts.

### Composition modification

Do not use broad Composition modification as assignable terminal purpose.
Replace it with non-terminal `Constituent transformation` objective and use
narrower objectives when known:

- component separation or fraction recovery;
- fat or other constituent removal;
- constituent conversion or degradation;
- component addition or application;
- moisture addition or reduction;
- preservation or stabilisation where directly intended.

Digestibility, nutrient availability, antinutritional-factor reduction, safety,
palatability, storage stability, and handling are separate possible feed
benefits. Measured changes remain observed effects.

### Process dispositions

1. Retain Mechanical, Thermal, Chemical, and Biological as mechanism
   categories; add Enzymatic or biochemical mechanism.
2. Retain particle-size reduction, component separation,
   shaping/agglomeration, and moisture removal as technical objectives.
3. Do not create permanent Other process. Unresolved mechanism remains
   review-visible hold.
4. Keep Grinding, Crushing, Chopping, Cracking, and Hammer milling as
   Mechanical size-reduction operations.
5. Keep Flour milling as Mechanical operation serving size reduction and
   component separation.
6. Keep Decortication, Threshing, and current Pressing uses as Mechanical
   separation operations.
7. Keep Pelleting as Mechanical shaping and Extrusion as thermo-mechanical
   shaping. Other extrusion transformations and benefits require parameters.
8. Keep Distillation as Thermal separation. Keep Heating generic and
   purpose-neutral.
9. Keep Rendering as multi-stage Thermal operation serving separation or
   stabilisation; represent Drying and Grinding separately when evidenced.
10. Move Enzyme Treatment and subtypes to Enzymatic or biochemical mechanism.
11. Keep Fermentation as Biological transformation and preservation; keep
    Ensiling as narrower preservation operation.
12. Remove Molasses Treatment from Chemical mechanism; represent component
    addition/application.
13. Move Defatting from process operation to Fat removal technical objective;
    review eight material uses for actual operation and composition state.
14. Keep Hydrolysis and Extraction without generic mechanism assignment because
    routes differ.
15. Keep Inoculation and Stacking as explicit holds pending scope evidence.
16. Move Sugar processing from processingMethod to production provenance,
    following retired Brewhouse processing precedent.

## Evidence

- [FoodOn transformation model](https://foodon.org/food-facets/food-transformation-process/)
- [FoodOn structure](https://foodon.org/design/foodon-structure/)
- [FoodOn process source table](https://docs.google.com/spreadsheets/d/17Bh-mKIzutH7q4_7gXMbUScpyOF8fDOCvUBk-dHH9BM/edit)
- [EU Catalogue of feed materials process glossary](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02013R0068-20220724)
- [OBI core process model](https://obi-ontology.org/docs/core-classes/)
- [Claim-specific evidence register](../../review/livestock-v35/evidence_register.csv)
- [Complete row-level dispositions](../../review/livestock-v35/process_axis_review.csv)

## Consequences

### Positive

- Skosmos cards can distinguish operation from mechanism and purpose.
- Nutritional rationale no longer masquerades as guaranteed process effect.
- FoodOn-aligned input/output and multi-purpose modelling becomes possible.
- Defatting and production workflows stop occupying incorrect operation roles.
- Experimental evidence can record actual outcomes without changing generic
  process definitions.

### Costs

- Schema needs new relation and range concepts.
- Process hierarchy requires governed rebuild and browser projection decisions.
- Existing definitions need benefit claims rewritten as modal scope notes.
- Eight Defatting bindings and three Sugar processing bindings need migration.
- Pipeline and consumers must support provenance, objective, benefit, and
  application-level effect separately.

## Alternatives considered

### Keep Composition modification as one purpose

Rejected. It combines direct chemical or constituent transformation with
nutritional intention and observed animal response.

### Copy FoodOn hierarchy directly

Rejected. FoodOn provides strong vocabulary and process/output precedent but
its hierarchy deliberately combines several classification dimensions.

### Put unmatched operations under Other process

Rejected. Permanent catch-all hides evidence gaps. Explicit holds preserve
reviewability without asserting false common mechanism.

### Assert improved digestibility on process concepts

Rejected. Same operation can improve, preserve, reduce, or leave digestibility
unchanged depending on execution and context.

## Implementation gates

1. Human approval of ADR and every row disposition.
2. Property-name, domain/range, and global collision review.
3. Identifier allocation only after objective and benefit vocabulary approval.
4. Migration plan for Defatting and Sugar processing material bindings.
5. Definition remediation for benefit-heavy process concepts.
6. Deterministic governed-source regeneration and second-run stability.
7. Full collision, hierarchy, SHACL, parity, checksum, and CI validation.
8. Clean Fuseki reload and guided Skosmos review of representative operations.
9. Pipeline consumer update or explicit versioned deferral.

## Approval record

Pete Steward accepted separation of mechanism, technical objective, intended
feed benefit, and observed effect during guided review on 2026-08-18. Specific
row dispositions and implementation remain pending explicit approval.
