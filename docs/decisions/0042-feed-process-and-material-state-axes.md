# ADR 0042: Feed-process hierarchy and material-state axes

## Status

Accepted — 2026-08-11

## Context

Adversarial Skosmos review found two coupled modelling failures. Process concepts
were split between legacy `AOM_000845` Feed Process and generated `AOM_101021`
Ingredient processing methods, while mechanical methods mixed mechanisms and
objectives in one flat branch. Physical form also mixed particle presentation,
bulk consistency, and moisture condition. Consequently Grinding generated
`Comminuted solid form` even for three oil or molasses concepts, and `Dried form`
sat beside pellets, liquids, and slurries.

Review covers all 34 governed processing-method values, 343 materials with
Grinding, 399 with Drying, all 15 governed physical descriptors, both legacy
Extrusion records, and representative bran, blood, poultry meal, liquid, slurry,
and pulp concepts.

## Decision

1. Reuse `AOM_000845` as canonical Feed processes root. Retire generated root
   `AOM_101021` before canonical publication and migrate its children.
2. Preserve mechanism branches such as Mechanical, Thermal, Biological, and
   Chemical. Add objective branches for particle-size reduction, separation and
   fractionation, and shaping and agglomeration. Use polyhierarchy when a process
   has more than one mechanism or objective.
3. Place Chopping, Crushing, Grinding, Cracking, and Flour milling under
   particle-size reduction. Place Flour milling, Decortication, Pressing, and
   Threshing under separation. Place Pelleting and Extrusion under shaping.
4. Treat Extrusion as one thermo-mechanical shaping process. Retain lower stable
   `AOM_000833`, deprecate duplicate `AOM_000841`, retire generated
   `AOM_101093`, and give canonical concept Thermal, Mechanical, and Shaping
   parents.
5. Rename `AOM_000838` Flour milling because its governed uses are maize bran,
   pollard, and rice polish. Model both particle reduction and fractionation.
   Generic wet or dry size reduction remains Grinding.
6. Separate material descriptors into three non-exclusive axes:
   - presentation form: whole, block, cake, flake, pellet, mixed, and comminuted,
     with meal and powder narrower than comminuted particle form;
   - bulk consistency: liquid, slurry, and pulp;
   - moisture condition: dried and fresh.
7. Slurry is not treated as a synonym or simple subtype of unqualified liquid.
   It requires solid particles dispersed in a liquid continuous phase. Pulp is a
   moist fibrous or cellular bulk consistency. Exact solids or moisture values
   require quantitative data.
8. Dried condition never parents presentation forms. A pellet, meal, powder, or
   cake may be dried or not; absence of moisture assertion means unknown.
9. Replace broad generated `Comminuted solid form` with `Comminuted particle
   form`. Grinding may result in that presentation but does not entail dry bulk
   state. Hold automatic presentation inference for `AOM_001961` Palm Oil Crude
   Ground, `AOM_002008` Fish Oil Dried Ground Heated, and `AOM_006004` Molasses
   Ground pending material-specific evidence.
10. Add Dried moisture condition where Drying is explicitly governed. Add it to
    `AOM_000536` Blood Ground from Feedipedia blood-meal evidence, not from a
    general logical claim that every ground material is dried. Drying route
    remains unspecified.
11. Keep Maize Bran without presentation or bulk-consistency assertion. Flour
    milling establishes component separation and by-product role, not one final
    form.
12. Keep Rendering on poultry by-product meal because its mapped authority
    explicitly describes rendering, cooking or sterilization, drying, and
    grinding. This remains a material-specific decision, not a lexical inference
    from “meal”.

## Evidence

- EU Catalogue process glossary mirrored by FAOLEX:
  https://faolex.fao.org/docs/pdf/eur119700.pdf
- Feedipedia blood meal: https://www.feedipedia.org/node/11574
- Feedipedia poultry by-product meal: https://www.feedipedia.org/node/214
- FoodOn release, including dried physical quality:
  https://purl.obolibrary.org/obo/foodon.owl
- Governed cohort: `review/livestock-v27/`

## Consequences

Skosmos exposes one process root and parallel mechanism/objective navigation.
Presentation, bulk consistency, and moisture appear as separate predicates and
hierarchies. Old `aom:physicalForm` and `aom:mayResultInPhysicalForm` remain
deprecated compatibility superproperties but receive no governed direct
assertions. Three contradictory ground-fluid cases remain explicit holds rather
than receiving misleading particulate forms.
