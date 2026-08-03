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
