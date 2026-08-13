# Cohort B recommendations: ingredient descriptors

Status: accepted by Pete Steward on 2026-08-13 under
[era-program #53](https://github.com/ERAgriculture/era-program/issues/53).

## Snapshot

All five reported IDs are already approved retirements and already have
machine-readable semantic bindings. Yet every ID remains a direct child of
`AOM_100850 Feed materials`, and generated livestock RDF expresses only custom
`era:status "deprecated"`; it emits no `owl:deprecated true`.

Result: Skosmos treats fields as normal feed-material browse concepts. Current
retirement decision and browser output contradict each other.

## Authority comparison

| Authority | Supported conclusion | Boundary |
|---|---|---|
| [W3C SKOS Reference](https://www.w3.org/TR/skos-reference/) | SKOS concepts carry labels, notations, notes, and informal hierarchy; `skos:broader` is a navigation relationship between concepts. | SKOS defines no concept-retirement predicate and does not turn metadata fields into domain concepts. |
| [W3C OWL 2 Syntax](https://www.w3.org/TR/owl2-syntax/#Annotation_Properties) | `owl:deprecated "true"^^xsd:boolean` states that an IRI is deprecated. | Flag does not itself remove hierarchy edges or define a replacement. |
| [Skosmos 3.3 configuration](https://github.com/NatLibFi/Skosmos/blob/v3.3/src/model/VocabularyConfig.php) | `skosmos:showDeprecated` defaults to false and is driven by `owl:deprecated`. | ERA custom `era:status` is not read as deprecation. |
| [Skosmos 3.3 SPARQL model](https://github.com/NatLibFi/Skosmos/blob/v3.3/src/model/sparql/GenericSparql.php) | Search and index queries can filter `owl:deprecated`; concept pages show a deprecation alert. | Narrower/hierarchy query does not filter deprecated children, so browse edges must also be governed. |
| [QUDT QuantityValue](https://qudt.org/schema/qudt/QuantityValue) | Ingredient proportion belongs in a structured quantity representation. | Proportion still needs explicit unit and basis; a number alone is insufficient. |
| ERA ADR 0044 and phase-2 pipeline contract | Five legacy IDs are field identities; pipeline already dual-publishes semantic component data and preserves source values. | Pipeline remains pre-cutover and exposes target-class/domain mismatches requiring reviewed migration. |

## Evidence

Generated inventories prove:

- five of five concepts have `status=deprecated`;
- five of five have approved retirement decisions;
- five of five have approved semantic bindings;
- five of five still have `skos:broader AOM_100850` in deployed RDF;
- zero of five have `owl:deprecated true`;
- only `era-data-pipeline` among audited implementation consumers uses these IDs
  and properties; it uses them as pinned contract keys, not hierarchy nodes;
- no exact references occur in audited `era-data`, `eragri`, `era-docs`, LTE,
  or analysis repositories;
- GitHub organization-wide code search was rate-limited, so local named-repo
  audit is strong evidence, not proof of every external consumer.

Full citations, limitations, dates, and local snapshot commits are recorded in
`evidence_register.csv` and `ingredient_descriptor_consumer_audit.csv`.

## Findings

### No active Ingredient descriptors branch

Do not mint or restore an active `Ingredient descriptors`, `Ingredient details`,
or `Ingredient modifiers` concept branch. Such branch would preserve category
error: schema fields would still appear as kinds of feed characteristic.

Keep five stable IDs resolvable as deprecated legacy schema identifiers. Remove
their active Feed-material browse edges. Add `owl:deprecated true` plus explicit
history notes explaining canonical representation. Preserve notation, labels,
definitions, source mappings, and governance provenance.

`AOM_101156 Ingredient descriptors` observed in local Skosmos was rejected
pre-revert residue, absent from merged source and clean release files. Clean
reload removed it. It is not valid precedent or an allocatable ID.

### Search versus navigation

Desired behavior differs by surface:

- active hierarchy: exclude retired field concepts;
- exact notation/label search: retain during compatibility window;
- direct URI: resolve permanently;
- concept card: show clear deprecated warning and migration history;
- feed-material card: show normalized semantic properties, not legacy field
  concepts.

Implement both standard deprecation and hierarchy suppression. `owl:deprecated`
alone fixes search/status recognition but Skosmos 3.3 hierarchy queries still
return deprecated children. Removing hierarchy alone loses visible retirement
status and may harm other consumers.

Set and test an explicit `skosmos:showDeprecated` policy. Compatibility promise
currently says stable IDs remain searchable, so proposed initial value is
`true`; deprecated cards must then show warning. Reconsider after documented
consumer cutover. Do not depend on Skosmos default.

### AOM_000531 Ingredient name

Canonical feed-material name is already `skos:prefLabel`; duplicate name field
must not appear on vocabulary cards. Pipeline value is source-record text on a
specific ingredient component, not a canonical property of every FeedMaterial.

Retire browse concept. Preserve row-local text as provenance on
`aom:IngredientComponent`. Preferred implementation: introduce a clearly named
source-label property and deprecate `aom:ingredientName` after dual-publish.
Lower-change alternative: retain predicate URI but redefine label, domain, and
scope as source-record ingredient label. Human choice required.

### AOM_000532 Ingredient part

Legacy `D.Item.Comp` mixes anatomy, form, process, role, constituent, and
compound descriptions. Existing pipeline decomposition is correct direction.

Retire browse concept. Show reviewed `materialComponent`, `physicalForm`,
`processingMethod`, `productRole`, and constituent relations. Keep
`aom:legacyComponentDescriptor` only on `aom:IngredientComponent` as exact
source provenance while unresolved; current FeedMaterial domain is wrong.
Display raw descriptor only in migration/review view.

### AOM_000533 Ingredient species

"Species" is too narrow: approved values include genus and family. Retire browse
concept and relabel `aom:sourceTaxon` as "has source taxon"; card label should be
"Biological source".

Canonical reviewed taxon belongs on FeedMaterial. Pipeline row-local taxon label
and provisional IRI require provenance until ingredient material identity is
resolved. Do not silently assert every row-level taxon against canonical
material.

### AOM_000534 Ingredient proportion

Proportion describes ingredient component within formulation/diet, never feed
material identity. Existing `aom:IngredientComponent` target is correct.

Use `aom:ingredientProportion` with `qudt:QuantityValue`, numeric value, explicit
unit, and denominator/basis. Review `Dimensionless` versus more specific
`DimensionlessRatio`; reject source values whose basis cannot be established.
Display only on formulation-component cards.

### AOM_000535 Ingredient source

Pipeline values are `On-farm` and `Purchased`: acquisition/procurement source,
not biological source. Current FeedMaterial domain and "ingredient source"
label create ambiguity with `sourceTaxon`.

Retire browse concept. Retain `aom:ingredientSource` URI during compatibility,
relabel it "has acquisition source", redefine domain to IngredientComponent or
an explicit procurement assertion, and label card field "Acquisition source".
Do not attach purchased/on-farm status to canonical material identity.

## Generator correction

Root cause sits in `normalize_livestock_release.py`:

1. source hierarchy generates broader edges;
2. retirement changes concept status only;
3. normalizer never removes retired browse edges;
4. livestock serializer emits custom status only;
5. tests reject active children under retired parents, but not retired children
   under active parents.

Implementation should make approved retirement navigation explicit. Recommended
rule: approved concept retirement suppresses active incoming `skos:broader`
edges unless a separately approved archival-navigation exception exists.
Deprecated duplicate replacement remains separate governance and may retain
context when justified.

Add tests for:

- every deprecated concept emits boolean `owl:deprecated true` in Turtle,
  RDF/XML, and JSON-LD;
- every approved retirement has no active browse edge unless governed exception;
- all five direct URIs resolve with warning and history note;
- exact notation search follows explicit compatibility policy;
- `AOM_100850` narrower list excludes all five;
- clean-load graph equals generated union and contains no rejected IDs.

## Alternatives rejected

1. **Reparent under Ingredient descriptors:** tidy appearance, wrong semantic
   category, preserves obsolete browse concepts.
2. **Delete records:** breaks stable published identifiers and evidence trail.
3. **Emit only `owl:deprecated`:** search/card improves, hierarchy remains wrong.
4. **Remove only broader edges:** hierarchy improves, deprecation remains
   invisible to interoperable consumers.
5. **Keep current output:** directly contradicts approved retirement rationale.

## Accepted decisions

1. Permanent retirement of five browse concepts; reject active
   Ingredient descriptors branch.
2. Dual browser policy: searchable/resolvable deprecated IDs, absent
   from active hierarchy.
3. `owl:deprecated` plus history-note serialization.
4. Resolve AOM_000531 source-label property strategy during implementation
   without reactivating legacy concept.
5. Target-scope corrections for component descriptor, source taxon,
   proportion, and acquisition source.
6. Implementation and pipeline-contract work proceed as separate reviewed PRs.

All five row dispositions are approved. No identifier allocation or ontology
implementation occurs in this cohort.
