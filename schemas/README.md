# Schemas

Source-table schemas, SHACL shapes, CSVW metadata, and generated JSON Schemas
will live here.

Pilot assets:

- `csvw/pilot-metadata.json`
- `json/pilot-concept.schema.json`
- `shacl/concepts.ttl`

Semantic model assets:

- `owl/aom-semantic-model.ttl`: source OWL model for domain records,
  observations, quantities, and governance provenance;
- `shacl/semantic-model.ttl`: SHACL Core constraints for feed materials,
  ingredient components, quantitative observations, QUDT values, and governed
  structural/value semantic bindings.

`dist/livestock-staging/aom-schema.ttl` is generated from the OWL source; do
not edit distribution copy directly. Architecture decision:
[`../docs/decisions/0001-semantic-model-layers.md`](../docs/decisions/0001-semantic-model-layers.md).
Phase-2 binding contract:
[`../docs/decisions/0002-phase-2-structural-migration-contract.md`](../docs/decisions/0002-phase-2-structural-migration-contract.md).
Ingredient-source value decision:
[`../docs/decisions/0003-ingredient-source-value-bindings.md`](../docs/decisions/0003-ingredient-source-value-bindings.md).
