# Feed taxonomy adversarial review recommendations

Status: recommendation package; no ontology hierarchy changes applied yet.

## Scope

Review covers complete affected cohorts rather than reported cards:

- every direct child of `AOM_100850 Feed materials`;
- all 94 descendants of `AOM_000736 Supplement`;
- all 54 descendants of `AOM_000781 Other Ingredients`;
- Organic Acid and its Fumaric Acid child;
- complete component, integrity, composition-state, and separation-process
  branches implicated by `AOM_101019`, `AOM_101085`, `AOM_101109`,
  `AOM_101115`, and `AOM_101130`;
- `AOM_101068 Brewhouse processing` and every concept named in review feedback.

Machine-readable row-level dispositions are in
`feed_taxonomy_adversarial_review.csv`; counts are in
`feed_taxonomy_adversarial_summary.json`.

## Adversarial finding

Current hierarchy is not publication-ready. `Supplement` and `Other Ingredients`
act as residual buckets mixing at least six different semantic roles:

1. feed materials;
2. feed formulations and premixtures;
3. feed additives and additive functional groups;
4. chemical constituents or substances;
5. product, experimental, or feeding roles;
6. unknown commercial products and data placeholders.

One parent cannot repair those differences. Both catch-all branches should
disappear after every child receives an evidence-backed disposition.

## Recommended top-level feed model

Keep three product kinds beside one another:

1. **Feed materials** — substances or products used directly, after processing,
   or in compound feed.
2. **Formulated feeds** — compound, complete, complementary, mineral, premix,
   ration, diet, block, lick, and mix products.
3. **Feed additives** — products intentionally added for technological,
   sensory, nutritional, zootechnical, coccidiostatic, or histomonostatic
   functions.

Keep chemical identity, additive function, feeding role, source taxon,
component, process, presentation, moisture, and product role as independent
facets. Never use `Supplement` or `Other Ingredients` to avoid deciding among
those axes.

## Reported concepts

### AOM_000531, AOM_000532, AOM_000533

These are legacy schema fields, not feed materials. Same defect applies to
`AOM_000534 Ingredient proportion` and `AOM_000535 Ingredient source`.

Recommendation:

- remove all five from browse hierarchy;
- retain IDs as deprecated/searchable compatibility concepts;
- publish replacements through `ingredientName`, source taxon, material
  component, quantity, and material-source properties.

### Organic Acid

`AOM_006389 Organic Acid` should not sit under Feed materials or move under
Other Ingredients. AGROVOC treats organic acids as chemicals. Fumaric acid may
serve as a feed additive, but intended function does not change chemical
identity.

Recommendation:

- move Organic Acid to chemical substances/constituents;
- represent additive product identity and acidity-regulator, preservative, or
  other function separately and only with use evidence.

### Supplement and Other Ingredients

Retire both material superclasses after child migration. Represent supplemental
feeding as a use/role or complementary-feed formulation, not material identity.

Major Supplement splits:

- amino acids, vitamins, urea, trace-element compounds, enzyme preparations,
  and Elancoban candidates move to Feed additives under authority categories;
- blocks, licks, mineral/vitamin mixes, and commercial protein supplements move
  to Formulated feeds;
- calcium carbonate, phosphates, salts, casein, microalgal biomass, protected
  fat products, and other evidenced materials move to source/material branches;
- Protein, Carbohydrate, element names, Pseudovitamin, and Organic Acid move to
  chemical identity/constituent branches;
- unknown brands and underspecified products remain explicit holds.

Major Other Ingredients splits:

- Binder and Digestibility Marker become roles; their bearer substances remain
  independently classified;
- former foodstuffs, food waste, glycerol, water, fungal materials, shells, ash,
  and charcoal move or remain held under evidence-specific material branches;
- Molasses & Urea Block moves to Formulated feeds;
- Free Gossypol moves to undesirable/chemical constituents;
- `Unspecified` retires as a missing-data code;
- ACTIPAL HP 1, Toxynil, Vitalite/Vitalyte, Olaquindox, sand, and activated
  sludge remain holds pending identity, use, safety, or regulatory evidence.

### Protected Fat and Megalac

`AOM_006334 Protected Fat` is too vague and wrongly placed. Manufacturer
evidence identifies Megalac as a calcium-salt rumen-protected fat product made
from palm fatty-acid distillate.

Recommendation:

- rename/reframe `AOM_006334` as `Rumen-protected fat feed materials`;
- move it outside Supplement under fat/oil feed materials;
- retain Megalac as a narrower named feed-material product;
- add explicit calcium-salt/fatty-acid composition and protection-process
  assertions only where product evidence supports them.

### Elancoban

`AOM_001579 Elancoban` is a monensin-sodium coccidiostatic feed additive. Its
current OWL type is correct, but browse path remains wrong because
`AOM_004433 Anti-coccidia` is under Supplement.

Recommendation:

- move and rename parent to `Coccidiostatic feed additives` under Feed additives;
- retain Elancoban beneath that category;
- keep animal category, dose, authorization, and safety conditions outside
  timeless concept identity unless represented with dated regulatory evidence.

### Brewhouse processing and process separation

`AOM_101068 Brewhouse processing` currently has no active material assertion.
It also contradicts `Feed processes`, whose definition says a process is applied
to feed material. Brewing is an upstream beverage-manufacturing process whose
stages produce possible feed by-products.

Recommendation:

- remove and retire AOM_101068 from active Feed processes for now;
- if source-production provenance is later needed, use a precise `Beer brewing`
  process under manufacturing processes and connect brewer's grains or yeast
  with `derivedFromProcess`/`output of`, not `processingMethod`;
- do not place the whole brewing process under Thermal or Separation merely
  because some stages heat or separate material.

Rename `AOM_101130 Feed separation processes` to `Feed component separation
processes`, following FoodOn's clearer objective definition. Keep only processes
whose definition removes or recovers a component/fraction. Remove Brewhouse
processing. Remove generic Rendering unless a material-specific rendering stage
explicitly includes component recovery. Keep reviewed multi-parent placement for
defatting, extraction, distillation, pressing, decortication, threshing, and
fractionating flour milling.

### Component hierarchy and Bran

Bran should not be forced under anatomical parts. Feed bran commonly denotes a
milling fraction that may contain several outer grain tissues and variable
endosperm. Current parallel top-level roots are still poor architecture.

Recommendation:

- retain `AOM_101085 Feed material components` as one component root;
- move/rename `AOM_101019` beneath it as `Anatomical components`;
- add a sibling `Processed material fractions` branch;
- place `AOM_101104 Bran` under `Cereal milling fractions` there;
- move Blood to body substances;
- move Straw and Stover from anatomy to crop-residue material/product-role
  modelling;
- move Whole crop out of component hierarchy into component-retention scope.

### Whole grain and composition states

`AOM_101109 Material integrity` is misleading. Ground whole-grain maize remains
whole-grain because bran, germ, and endosperm are retained, not because particle
integrity remains.

Recommendation:

- retire AOM_101109;
- rename AOM_101110 to `Whole-grain composition`;
- move it under a renamed AOM_101115 `Native-component retention states` branch
  beneath Feed Chemical Composition;
- retain Full-fat and Whole-milk shorthand only with positive
  `retainsNativeComponent` semantics.

Do not model Full-fat as inferred `does not have Defatting`. Missing process
assertions do not prove non-occurrence in an open-world graph. If source evidence
states Full-fat, assert positive retention of native fat; preserve Defatting as
an independent process when present.

## Authority comparison

- EU Regulation 767/2009 separates feed materials from compound, complete, and
  complementary feeds.
- EU Regulation 1831/2003 separates feed additives into technological, sensory,
  nutritional, zootechnical, and coccidiostat/histomonostat categories.
- EU Regulation 68/2013 lists feed materials and process definitions, including
  mineral materials, glycerine, brewers' grains, extraction, and distillation.
- AGROVOC separates feed additives, supplements, and organic acids and defines
  supplement by use with another feed.
- FoodOn separates product, anatomy, chemical, quality, and process facets;
  models products as outputs of processes; uses `food component separation
  process`; and recognizes cereal grain milling fractions and whole-grain
  component retention.

## Evidence

- https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009R0767
- https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32003R1831
- https://eur-lex.europa.eu/eli/reg/2013/68/oj/eng
- https://food.ec.europa.eu/food-safety/animal-feed/feed-additives_en
- https://agrovoc.fao.org/browse/agrovoc/en/page/c_2827
- https://agrovoc.fao.org/browse/agrovoc/en/page/c_33996
- https://agrovoc.fao.org/browse/agrovoc/en/page/c_5383
- https://foodon.org/food-facets/
- https://foodon.org/food-facets/food-transformation-process/
- https://foodon.org/design/foodon-relations/
- https://foodon.org/foodon-and-anatomy/
- https://www.megalac.com/resources-advice/fats-advice/64-rumenprotected-fats-calcium-salt-supplements
- https://efsa.onlinelibrary.wiley.com/doi/10.2903/j.efsa.2026.10123
- https://www.w3.org/TR/owl-syntax/#Negative_Object_Property_Assertions

## Implementation boundary

Do not patch reported cards alone. Next semantic PR should migrate complete
approved disposition groups, preserve unresolved rows as holds, deprecate rather
than delete stable IDs, regenerate all release artifacts, rebuild empty Fuseki
storage, and repeat Skosmos review.
