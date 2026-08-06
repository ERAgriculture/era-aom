# ADR 0021: preferred-label collision governance

Status: accepted  
Date: 2026-08-06  
Reviewer: Pete Steward

## Context

Whole-ontology audit originally reported 95 normalized preferred-label collision groups from legacy workbook labels. That report ignored governed preferred labels and deprecated status. Corrected audit against normalized `concepts.csv` and `labels.csv` exposes 105 historical groups: additional collisions arise intentionally where governed semantic facet values share ordinary domain words such as `Drying`, `Hay`, and `Blood`.

SKOS does not require globally unique preferred labels. Equality of labels does not establish concept identity. Species-specific rearing stages, taxa and derived feed materials, measured constituents and supplements, aquatic and terrestrial system values, intervention roles, and semantic facet values occupy different modeled contexts.

## Decision

Record one governed disposition for every historical group:

- retain 98 groups as context-distinct;
- deprecate six verified duplicate concepts with replacement links;
- retain Cotton Seed as one explicit identity hold.

Five pesticide-branch concepts duplicate antimicrobial-branch concepts exactly: labels, definitions, and ChEBI mappings coincide, while definitions explicitly describe antimicrobial drugs. Retain AOM_000350–AOM_000354 and deprecate AOM_000338–AOM_000342 respectively.

Two Strip grazing records share label/synonym and EOL_0001945. Retain AOM_000935, which has lower ID and source definition; deprecate AOM_000949.

Do not mass-qualify preferred labels. Qualifiers such as “taxon” or “feed material” would alter established terminology merely to satisfy a UI uniqueness preference. Hierarchy, RDF types, scope notes, identifiers, and governed dispositions carry semantic distinction.

## Consequences

Active normalized vocabulary contains 99 collision groups: 98 approved retain-distinct decisions and one approved hold. No group remains unattended. Deprecated concepts remain resolvable and point to retained identifiers. Future audit runs use governed labels, exclude deprecated concepts, and report unresolved collision count separately.
