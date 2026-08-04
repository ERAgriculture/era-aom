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
  ingredient components, quantitative observations, and QUDT values.

`dist/livestock-staging/aom-schema.ttl` is generated from the OWL source; do
not edit distribution copy directly. Architecture decision:
[`../docs/decisions/0001-semantic-model-layers.md`](../docs/decisions/0001-semantic-model-layers.md).
