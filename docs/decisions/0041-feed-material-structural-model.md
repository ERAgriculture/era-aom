# ADR 0041: Feed-material source, role, process, and form structure

## Status

Accepted — 2026-08-11

## Context

Manual Skosmos review exposed linked structural defects across feed materials:
external mappings were hidden; mapped page names were absent; biological source
links were incomplete; product/by-product role remained encoded mainly in legacy
hierarchy; grinding lacked a safe result-form model; and generic poultry
by-products carried processed meal and chicken-specific synonyms.

Review covers all 1,643 legacy feed materials, 342 approved Grinding assertions,
466 concepts in legacy animal/crop by-product branches, all 335 mapped Feedipedia
resources, and affected poultry, chicken, blood, and maize examples. This is one
governed structural cohort, not isolated card repair.

## Decision

1. Keep biological source, product role, process, and physical form independent.
   Source-oriented feed groupings may link to biological AOM concepts with
   `skos:related`; reviewed species mappings use `aom:sourceTaxon`.
2. Translate legacy `Animal Byproduct` and `Crop Byproduct` branch membership to
   explicit `aom:productRole` where no reviewed role exists. Preserve compatibility
   hierarchy pending later source-axis migration.
3. Govern blood, blood ground, and dried-ground-heated blood as animal
   by-products. Form remains independent.
4. Add `Comminuted solid form`, with `Meal form` and existing `Powder form` as
   narrower forms. Grinding may result in comminuted solid material; it does not
   establish meal, powder, or particle size.
5. Add `aom:mayResultInPhysicalForm` between processing methods and possible result
   forms. Assert broad comminuted form on materials with approved Grinding unless
   stronger concept-specific form evidence exists.
6. Do not promote `meal` lexically across all materials. Named compound feeds remain
   product identities. Poultry by-product meal receives a dedicated narrower
   feed-material concept because Feedipedia directly establishes ground/rendered
   parts and drying during its defined processing. This source-specific decision
   does not make drying an entailment of the word “meal”.
7. Rename generic `Poultry byproduct` to `Poultry by-products`. Suppress processed
   meal and chicken-specific alternate labels from that generic concept. Keep
   `Chicken Offal Dried Ground` distinct, with reviewed Meal form and chicken taxon.
8. Publish mapping predicates in Skosmos and load frozen external-resource page
   headings. Mapping relation remains explicit; source page names never become AOM
   synonyms automatically.

## Evidence

- Feedipedia poultry by-product meal: https://www.feedipedia.org/node/214
- Feedipedia poultry offal meal: https://www.feedipedia.org/node/12474
- Feedipedia high-protein poultry by-product meal: https://www.feedipedia.org/node/12911
- Feedipedia blood meal: https://www.feedipedia.org/node/221
- Feedipedia maize bran: https://www.feedipedia.org/node/12280
- Legacy and governed staging tables under `data/livestock-staging/`

## Consequences

Feed cards show reviewed biological source and product role without forcing identity
under role hierarchy. Ground materials can use a broad form when particle size is
unknown. Meal/powder browse as narrower forms. Poultry by-products and poultry
by-product meal no longer collapse into one card. Uncached Feedipedia page headings
remain visible as URIs and stay recorded holds rather than triggering live build-time
network access.
