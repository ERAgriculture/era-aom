# Decision 0001: Separate vocabulary, domain data, observations, and provenance

- Status: accepted for staged migration
- Date: 2026-08-04
- Owner: Alliance of Bioversity International and CIAT
- Approver: Pete Steward
- Migration: non-destructive, phased, backward-compatible

## Context

AOM Livestock inherited SKOS-like hierarchy nodes that mix five different things:
controlled terms, feed-material records, ingredient metadata, quantitative variables, and
reproductive-state dimensions. Treating every item as one `skos:Concept` makes labels
navigable but cannot express values, units, source taxa, processing methods, formulation
proportions, or validation rules precisely.

Fifty concepts were therefore deferred during hierarchy reconstruction. This decision
assigns every case a target semantic layer without changing released identifiers yet.

## Decision

Use four coordinated layers:

1. **Knowledge organization — SKOS.** Stable AOM identifiers, multilingual preferred and
   alternative labels, definitions, broader/related relations, and external mappings remain
   SKOS concepts. SKOS is designed for concepts, lexical labels, schemes, relations, and
   mappings: https://www.w3.org/TR/skos-reference/
2. **Domain semantics — OWL 2.** Feed materials, formulations, ingredient components,
   product roles, and explicit properties use OWL classes and properties:
   https://www.w3.org/TR/owl-overview/
3. **Observations and quantities — SOSA/SSN + QUDT.** Measured variables become
   `sosa:observedProperty` targets; values use `qudt:QuantityValue`, numeric value, and unit.
   Sources: https://www.w3.org/TR/vocab-ssn-2023/ and
   https://www.qudt.org/doc/2026/01/DOC_SCHEMA-QUDT.html
4. **Validation and provenance — SHACL + PROV-O.** SHACL validates required structure,
   datatypes, and units; PROV-O identifies evidence, agents, and derivation. Sources:
   https://www.w3.org/TR/shacl/ and https://www.w3.org/TR/prov-o/

JSON-LD 1.1 and Turtle remain serializations of one RDF graph. JSON-LD provides web/API
compatibility without creating a second semantic model:
https://www.w3.org/TR/json-ld11/

## Core patterns

### Feed material

`aom:FeedMaterial` represents material identity. Source taxon, plant/animal part,
processing method, and economic product role are separate facets. A processed feed may
remain an AOM SKOS concept while also identifying or classifying a feed-material instance.

### Formulation component

`aom:IngredientComponent` links one feed material to one formulation. Proportion is a QUDT
quantity value, not a vocabulary node. Ingredient name/source metadata become properties.

### Quantitative observation

`aom:QuantitativeObservation` specializes `sosa:Observation`. It requires one observed
property and one QUDT result carrying decimal numeric value and unit IRI.

### Reproductive dimensions

Parity and gestational stage become separate concept dimensions. Existing AOM identifiers
remain resolvable. Ambiguous `Mixed` and nonstandard `Fourth trimester` stay on hold until
source evidence supports placement and corrected definitions.

## AI compatibility

- Stable IRIs and explicit types support knowledge-graph retrieval and tool calling.
- Language-tagged SKOS labels support multilingual search and embedding generation.
- SHACL gives deterministic constraints that AI suggestions must pass.
- PROV-O distinguishes evidence, reviewer, and generated artifacts.
- Embeddings, inferred links, and model suggestions remain derived artifacts, never
  canonical assertions.
- Machine-readable dispositions make migration decisions inspectable by humans and agents.

## Backward compatibility

- No identifier deletion or reuse.
- Existing provisional `urn:era-aom:schema:` namespace remains unchanged. HTTP PURL
  migration requires registered redirect ownership and a separate compatibility decision.
- No hierarchy change in this design PR.
- Legacy concepts remain resolvable through consumer cutover.
- Properties replace concept usage only after pipeline and data-schema migration.
- Product/by-product and reproductive reclassification require separate reviewed decisions.
- Release manifests classify later migrations as compatible or potentially breaking.

## Migration phases

1. **Design (this decision):** publish OWL, SHACL, examples, tests, and 50 dispositions.
2. **Structural migration:** introduce ingredient properties and SOSA/QUDT observations;
   dual-publish old columns/concepts during pipeline cutover.
3. **Reviewed classification:** facet feed materials, separate reproductive dimensions,
   then deprecate obsolete concept-as-field usage only after consumer verification.

## Consequences

Model becomes more precise and interoperable, but ingestion pipeline must construct typed
records rather than place every field in one hierarchy. Short-term mapping work is accepted
to avoid long-term ambiguity and brittle AI-only interpretation.
