# Changelog

All notable vocabulary changes will be recorded here.

## Unreleased

- Add 1,239 governed definitions from reviewed scope text and approved semantic
  facets, reducing active definition gaps from 2,127 to 888 without invented
  biological or nutritional claims.

- Govern all 105 historical preferred-label collision groups: retain 98
  context-distinct groups, deprecate six verified duplicates, preserve Cotton
  Seed as explicit hold, and correct audit inputs to use governed active labels.

- Close all 19 ingredient semantic-model exceptions with governed feed-product
  type and composition-state facets; approve seven identity-cluster decisions,
  deprecate duplicate Bothriochloa record `AOM_001898`, retain one explicit
  Cotton Seed identity hold, and publish 1,625 material-facet assertions.

- Build noncanonical `2026.1-rc.1` with proposed HTTPS identifiers, equivalent
  Turtle/JSON-LD/RDF/XML, CSV/Parquet visualization exports, manifest,
  checksums, Skosmos configuration, bulk proposal validation, and explicit
  publication/rollback gates.

- Closed ingredient facet governance across all 83 descriptors with 45 atomic
  mappings, 65 composite assertions, and ten explicit holds.

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
- Govern ingredient-source controlled values: reuse `AOM_000141` On-farm and
  `AOM_000142` Purchased, hold ambiguous Unspecified as semantic null, publish
  RDF/JSON-LD bindings, and enforce mapping decisions with SHACL.
- Correct heterogeneous Ingredient part migration: preserve raw descriptor,
  define typed part/form/process/role/constituent facets, and prohibit automatic
  label-only mappings pending reviewed decomposition.
- Add review-only facet proposals for 83 legacy ingredient-component labels;
  classify atomic, composite, and unresolved cases without source counts,
  automatic mappings, or concept minting.
- Add first ten-taxon NCBI review batch, preserving rank and synonym evidence
  while holding WFO and material-to-taxon assertions for expert approval.
- Approve ten exact source-name to NCBI Taxonomy bindings, including explicit
  genus/family ranks and Pennisetum-to-Cenchrus synonym handling; keep WFO held.
- Add second taxon review batch: flag incorrect Brassica-to-Arecaceae mapping,
  record synonym/rank cases, and hold a chemical string misfiled as taxonomy.
- Approve second source-taxon batch: add 14 NCBI bindings, replace incorrect
  Brassica identifier, and govern known non-taxa with `hold_non_taxon`.
- Add third taxon review batch with 21 live-NCBI-verified species candidates;
  expose wrong legacy targets for Theba pisana and winged bean.
- Approve third source-taxon batch: add 21 NCBI bindings, including corrected
  identifiers for Theba pisana and Psophocarpus tetragonolobus.
- Correct approved Guizotia and Brevoortia NCBI collisions; add pinned snapshot
  plus repeatable offline/live integrity validation for all 45 taxon mappings.
- Add large fourth taxon review batch with 80 live-verified NCBI candidates,
  including five wrong-ID replacements and explicit genus-rank preservation.
- Approve all 80 batch-4 source-taxon decisions; expand live-validated NCBI
  contract to 125 biological mappings and add reusable guarded promotion tool.
- Add final all-remainder taxon review: 146 labels classified into 91
  live-validated mapping candidates and 55 explicit holds.
- Govern all 146 final source-taxon decisions: approve 91 NCBI mappings and
  preserve 55 ambiguous/contextual labels as explicit null-target holds.
- Govern 23 older-release audit labels through 22 corrected or exact NCBI
  bindings and one explicit hold; expand approved taxon mapping contract to 238.
- Govern all 83 profiled ingredient-component descriptors as classification-only
  routes: 52 atomic reviews, 28 decompositions, and three explicit holds.
- Add 55 typed ingredient facet concepts, approve 35 atomic value mappings, and
  publish 39 explicit assertions decomposing 17 compound descriptors.
