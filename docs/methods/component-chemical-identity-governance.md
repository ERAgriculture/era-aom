# Component and chemical-identity governance method

## Purpose

This method implements accepted [ADR 0048](../decisions/0048-chemical-identity-composition-and-component-model.md) while preserving chemical identity, measured composition, material component, component retention, feed-product use, and processing as independent assertions.

## Governing rules

1. Chemical identity answers what entity is present. Measured composition answers what quantity or characteristic is observed.
2. `aom:primaryConstituent` supplies constituent role. Target labels do not need role suffixes.
3. `aom:ingredientPart` remains a scoped subproperty for source-anatomy assertions. `aom:materialComponent` remains broad query property.
4. `aom:componentRetentionState` represents positive whole-crop or whole-grain retention independently of measured composition.
5. Plant and animal anatomy receive separate navigation groups. Ambiguous vernacular component labels remain directly under anatomical root as explicit holds.
6. Process-defined Bran remains outside anatomy. Germ anatomy becomes Plant embryo; commercial germ materials retain separate feed-material identities.
7. Straw and Stover component assertions are removed. Published component IDs are retired without replacement while generic material identity remains held.
8. Stable duplicate concepts use governed deprecation and `dcterms:isReplacedBy`; published IDs are never deleted.

## External mapping gate

Mappings require concept-level definition comparison against pinned authority source, not label equality alone.

- Plant Ontology source: commit `94750e01c897da6955c2fef97379f4d99cb333a8`.
- FoodOn source: commit `c5035015de540ba4f4210fd0e24d3909d6fb2037`.
- Uberon source: commit `1d91869610a93335203dc931a224302f42e8c530`.
- ChEBI entity and substance records: accessed 2026-08-20.

Exact mappings are limited to definitions whose biological scope matches AOM use. Germ retains `relatedMatch` to Plant embryo because legacy search wording is only a related synonym. Bran retains `closeMatch` to FoodOn seed bran because cereal milling scope differs.

## Deterministic implementation

Run:

```bash
python scripts/build_process_axis_implementation.py
python scripts/build_component_chemical_identity_implementation.py
python scripts/normalize_livestock_release.py data/livestock-staging/legacy_records.csv .
python scripts/build_semantic_bindings.py
python scripts/build_release_candidate.py --config=config/releases/2026.1-rc.1.json
python tests/validate_component_chemical_identity_implementation.py
```

`build_definition_enrichment.py` must run before process-axis and Cohort D
implementation. Running it afterward would overwrite governed replacement
definitions produced by those implementation steps.

Second run must produce no diff. Distribution files remain generated outputs; only governed sources are edited directly.

## Consumer behavior

Consumers needing all material components must query `aom:materialComponent` with subproperty reasoning or union it with `aom:ingredientPart`. Consumers needing only positive whole-material retention must query `aom:componentRetentionState`; `aom:compositionState` remains for held Cohort E composition cases.

## Holds

Held rows remain in implementation register. No exact mapping, replacement, material-identity reuse, or Composition/Form inference is published for held cases.
