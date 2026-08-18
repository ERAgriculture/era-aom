# Cohort C recommendations: process mechanism, objective, benefit, and effect

Status: proposed under
[era-program #54](https://github.com/ERAgriculture/era-program/issues/54).

## Snapshot

Current graph contains:

- 53 concepts including `AOM_000845 Feed processes`;
- 52 descendants and 12 direct children;
- four mechanism groupings: Biological, Chemical, Mechanical, Thermal;
- four objective groupings: particle-size reduction, component separation,
  shaping/agglomeration, and moisture removal;
- 1,065 material-to-processingMethod assertions using 28 process concepts;
- one deprecated duplicate, `AOM_000841 Extrusion`;
- ungrouped Hydrolysis, Soaking, Stacking, and Sugar processing operations or
  workflows.

Complete generated membership and usage counts are in
`process_hierarchy_inventory.csv`. Every row and overlap is in
`process_axis_overlap_matrix.csv`.

## Authority comparison

| Authority | Supported conclusion | Boundary |
|---|---|---|
| [FoodOn transformation model](https://foodon.org/food-facets/food-transformation-process/) | Processes connect material inputs and outputs, add or remove qualities, and require ordered application modelling. | Does not prescribe ERA properties or feed-specific classifications. |
| [FoodOn structure](https://foodon.org/design/foodon-structure/) | One process may have several purposes; purpose cannot be inferred from mechanism alone. | Public design remains evolving. |
| [FoodOn process source table](https://docs.google.com/spreadsheets/d/17Bh-mKIzutH7q4_7gXMbUScpyOF8fDOCvUBk-dHH9BM/edit) | Provides component separation, modification, preservation, component addition, fat removal, water removal, forming, fermentation, extraction, hydrolysis, distillation, and rendering concepts, often with multiple parents. | Mixes mechanism, operation, objective, and preservation in one hierarchy; use as vocabulary evidence, not exact tree template. |
| [EU feed-process glossary](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02013R0068-20220724) | Defines feed operations through mechanisms and direct transformations such as reduction, removal, concentration, detoxification, drying, fermentation, extraction, and hydrolysis. | Regulatory definitions do not guarantee nutritional benefit. |
| [OBI core model](https://obi-ontology.org/docs/core-classes/) | Separates planned process, plan, material input/output, and resulting data. | Investigation ontology, not feed authority. |

FoodOn is architectural basis, not hierarchy copied verbatim. ERA adopts its
input/output, qualities, multi-purpose, and polyhierarchy lessons while making
mechanism, technical objective, intended benefit, and observed result explicit.

## Core finding

`Composition modification` is too broad as assignable purpose. It conflates:

1. **mechanism** — how process operates;
2. **technical objective** — direct transformation sought;
3. **intended feed benefit** — why operator applies process;
4. **observed effect** — measured outcome in one material, protocol, species,
   and context.

Example:

```text
Grinding
├── mechanism: Mechanical
├── technical objective: Particle-size reduction
├── may support: Digestibility or handling improvement
└── observed effect: only on a specific treatment/measurement record
```

Grinding does not universally improve digestibility. Heating may improve or
damage nutritional value. Fermentation outcome varies with substrate,
microorganism, temperature, duration, and animal. Generic process concepts must
not carry universal benefit or observed-effect entailments.

## Proposed model

### Process operations

`aom:processingMethod` continues linking feed material to actual operation such
as Grinding, Fermentation, Drying, or Extraction. Root and grouping concepts
are not valid material processingMethod values.

### Mechanisms

Use `aom:processMechanism` for definitional mechanism:

- Mechanical;
- Thermal;
- Chemical;
- Biological;
- Enzymatic or biochemical.

Do not create permanent `Other process`. Unknown mechanism remains explicit
hold until evidence supports category or justified new mechanism.

### Technical objectives

Use `aom:technicalProcessObjective` for direct operation objective:

- Particle-size reduction;
- Component separation or fraction recovery;
- Shaping or agglomeration;
- Moisture reduction;
- Moisture addition or conditioning;
- Constituent transformation;
- Component addition or application;
- Preservation or stabilisation.

`Constituent transformation` replaces assignable generic Composition
modification. Keep it as non-terminal grouping where narrower objective is
known. Fat removal is narrower than component separation. Defatting is an
objective or resulting composition state, not one mechanism.

### Intended feed benefits

Use modal `aom:maySupportFeedBenefit`, never universal `has benefit`, for:

- digestibility improvement;
- nutrient availability or bioavailability improvement;
- antinutritional-factor reduction;
- safety improvement;
- palatability or intake improvement;
- preservation or storage-stability improvement;
- handling, mixing, or dosing improvement.

Benefits require authority evidence and limitation. Generic process labels
alone cannot assert them.

### Observed effects

Use `aom:observedProcessEffect` only on process application, treatment, or
measurement records. Record material, protocol parameters, animal or assay
context, result, unit, comparator, and evidence. Do not attach measured outcome
as universal process-class fact.

### Production provenance

Use `aom:productionProcessProvenance` or explicit input/output pattern for
upstream workflows. `AOM_101084 Sugar processing` produces molasses; it is not
one treatment applied to molasses as feed. This follows already-retired
`AOM_101068 Brewhouse processing` precedent.

## Cohort findings

### Mechanical and objective overlap

- Chopping, Cracking, Crushing, Grinding, and Hammer milling: Mechanical plus
  particle-size reduction.
- Flour milling: Mechanical plus size reduction and component separation.
- Decortication and Threshing: Mechanical plus component separation.
- Pressing: Mechanical plus component separation for current governed uses;
  outputs and moisture state remain material-specific.
- Pelleting: Mechanical plus shaping.
- Extrusion: Mechanical and Thermal plus shaping; chemical change and
  nutritional benefit depend on parameters.

### Thermal and multi-stage operations

- Heating: Thermal mechanism; purpose remains context-dependent.
- Autoclaving, Boiling, and Roasting: Thermal operations with constituent
  transformation; claimed safety or nutrition benefit remains modal.
- Distillation: Thermal mechanism plus component separation.
- Rendering: multi-stage thermal operation serving separation and
  stabilisation; Drying and Grinding remain separate evidence-backed steps.
- Drying and Wilting: moisture-reduction objective; generic mechanism remains
  unspecified because natural and artificial routes differ.

### Biological, chemical, and enzymatic operations

- Fermentation: Biological mechanism plus constituent transformation and
  preservation objectives.
- Ensiling: fermentation subtype with preservation objective.
- Enzyme Treatment and specific enzymes: Enzymatic or biochemical mechanism,
  not broad Biological mechanism.
- Acid, Alkali, Ammonia, and Urea treatments: chemical or mixed biochemical
  mechanisms with constituent-transformation objectives.
- Molasses Treatment: component addition/application, not Chemical mechanism.
- Inoculation remains hold until microbial inoculation is separated from enzyme
  addition.

### Cross-axis corrections

- Defatting moves from operation vocabulary to Fat removal technical objective;
  eight material assertions require actual-operation or composition-state
  review.
- Hydrolysis remains operation with constituent-transformation objective and no
  generic mechanism because acid, alkali, enzyme, heat, and pressure routes
  differ.
- Extraction remains separation operation with method-specific mechanism.
- Soaking remains conditioning operation; leaching, heating, or germination
  purposes require context.
- Stacking remains explicit hold, not permanent Other branch.
- Sugar processing moves to production provenance.

## Proposed predicates

| Predicate | Domain | Range | Semantics |
|---|---|---|---|
| `aom:processMechanism` | ProcessingMethod | ProcessMechanism | Definitional means by which operation occurs. |
| `aom:technicalProcessObjective` | ProcessingMethod | ProcessTechnicalObjective | Direct intended transformation inherent to operation scope. |
| `aom:maySupportFeedBenefit` | ProcessingMethod | FeedBenefit | Evidence-backed possible benefit; never universal outcome. |
| `aom:productionProcessProvenance` | FeedMaterial | Process | Upstream process or workflow that produced material. |
| `aom:observedProcessEffect` | ProcessApplication | Observation | Measured outcome from specified application and context. |

Property names remain proposals subject to schema collision and domain/range
review.

## Required decisions

1. Approve operation, mechanism, technical objective, benefit, and observed
   effect separation.
2. Approve FoodOn-informed but ERA-specific relation model.
3. Approve Constituent transformation as non-terminal replacement for generic
   assignable Composition modification.
4. Approve modal benefit semantics and application-level observed effects.
5. Approve Defatting and Sugar processing migrations.
6. Approve no permanent Other process branch.
7. Review held Inoculation, Defatting-material, and Stacking rows.

No hierarchy, identifier, binding, schema, generated distribution, or Skosmos
change is made by this review.
