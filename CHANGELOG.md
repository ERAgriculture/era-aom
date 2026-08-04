# Changelog

All notable vocabulary changes will be recorded here.

## Unreleased

- Create repository and Phase 0 workbook inventory.
- Normalize `prac` and `out` into pilot concept, annotation, relation,
  property, registry, and provenance tables.
- Generate pilot SKOS JSON-LD/Turtle, CSVW, JSON Schema, and SHACL.
- Add deterministic regeneration, legacy round-trip, semantic, and CI
  validation.
- Rename repository/product to Agriculture Ontology for Meta-analysis (AOM);
  frame current pilot as crop module and preserve existing livestock AOM
  lineage as separate module.
- Inventory AOM Livestock v2 public release and reconcile against workbook
  AOM-family sheets without publishing restricted linkage data.
- Add normalized AOM Livestock v2 review staging, explicit identity
  quarantine, hierarchy-gap queue, mapping assertions, SKOS distributions,
  OWL schema, and visualization node/edge exports.
- Correct hierarchy derivation for labels containing `/`; add domain-review
  pack for identity collisions and missing explicit parents.
- Add evidence-backed recommendations for two identity blockers and six
  high-impact missing-parent cases.
- Resolve `AOM_006275` collision: retain it for *Panicum antidotale Dried*, map
  *Panicum maximum Dried* to existing `AOM_001676`, correct three species
  mappings, preserve legacy labels as synonyms, and record signed provenance.
- Merge duplicate Brewers Grain concepts: retain `AOM_000564`, deprecate
  `AOM_001884` with replacement link, normalize label to `Brewers grains,
  dehydrated`, and preserve legacy synonyms.
- Establish append-only livestock identifier policy; mint `AOM_100849` Mineral
  content under Feed Chemical Composition and reparent 13 mineral-element
  concepts.
- Mint `AOM_100850` Feed ingredient under Feed Characteristic and reparent 18
  concepts; flag five ingredient-metadata concepts for later schema remodeling.
- Mint `AOM_100851` Maize by-products under Cereal ByProducts, reparent 12
  concepts, and relate grouping to maize crop/product without asserting identity.
- Add bundled priority parents: `AOM_100852` Soybean by-products,
  `AOM_100853` Grazing management, and `AOM_100854` Management activity
  variable cost; resolve 34 hierarchy gaps and queue 10 modeling follow-ups.
- Resolve 14 cereal by-product hierarchy cases in one batch: mint 10 contextual
  groupings, flatten four redundant paths, add five crop/product relations, and
  queue eight classification reviews.
- Resolve 13 legume by-product hierarchy cases: mint 10 contextual groupings,
  normalize Common/Green/Haricot bean ancestry, flatten three paths, add four
  product relations, and queue identity/classification reviews.
- Complete livestock hierarchy reconstruction across crop by-products, crop
  products, forage plants, remaining feed concepts, management, outcomes, and
  species: 234 signed parent decisions, 170 governed identifiers, and zero
  remaining hierarchy gaps.
- Add provenance-aware preferred-label correction overlays; correct six
  high-confidence terms while retaining legacy labels as alternatives.
- Merge duplicate Green Bean Vine/Haricot Bean Vine identities into retained
  `AOM_003960` Common bean vine; deprecate `AOM_004000` with replacement link.
- Accept layered semantic model separating SKOS vocabulary, OWL domain records,
  SOSA/QUDT observations, SHACL validation, and PROV-O provenance; publish
  machine-readable migration dispositions for all 50 deferred modeling cases.
- Publish 13 approved phase-2 structural bindings in CSV, JSON-LD, and Turtle;
  retain legacy URIs, dual-type eight quantitative concepts as SOSA observable
  properties, define QUDT quantity families, and document reversible pipeline
  cutover requirements.
