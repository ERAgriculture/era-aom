# ADR 0040: global legacy identity-collision cohort

Status: accepted  
Date: 2026-08-10  
Reviewer: Pete Steward

## Context

The clean-graph Skosmos review showed that the earlier preferred-label
governance allowed duplicate identifiers when only hierarchy or property
context differed. That is not an identity distinction. The global audit now
contains 93 normalized preferred-label groups spanning 214 concepts, including
deprecated identifiers so replacement history remains reviewable.

Every current group was reviewed against its public AOM Livestock v2 source
record, definition, external mappings, model class, and governed semantic use.
The row-level evidence is retained in
`review/livestock-v25/global_identity_collision_detail.csv`; governed
dispositions are retained in
`data/livestock-staging/approved_ontology_collision_decisions.csv`.

## Decision

Classify all 93 groups as follows:

- Retain 66 groups where definitions establish a real distinction: taxon versus
  feed material, measured constituent versus supplement, intervention addition
  versus substitution, outcome or measurement versus material, or
  taxon-scoped rearing-stage values.
- Deprecate 25 verified duplicates with replacement crosswalks. This includes
  six prior pesticide and grazing duplicates, corrected Bothriochloa dried,
  duplicate Enzyme Treatment and Fermentation process concepts, and 16
  aquatic/terrestrial farming-system clones whose definitions or EOL mappings
  coincide.
- Keep Cotton Seed and Extrusion as explicit holds. Cotton needs product-role
  and CPC granularity review. Extrusion needs domain review to distinguish its
  legacy thermal and mechanical concepts from the governed processing facet.

ADR 0042 subsequently resolves Extrusion as one thermo-mechanical shaping
process. Cotton Seed remains the sole identity hold.

For every deprecated duplicate, retain its stable identifier, source record,
legacy labels, and `dcterms:isReplacedBy` crosswalk. Do not mint replacement
identifiers.

Where deprecating a duplicate would otherwise remove useful navigation,
canonical concepts receive a second `skos:broader` relation. This preserves
both aquatic and terrestrial farming-system branches, and both legacy
biological-processing and governed process branches, without duplicating
concept identity.

## Consequences

The identity audit must reconcile every current collision exactly to one
governed decision. It reports approved, held, and unreviewed group counts and
fails release readiness whenever an unreviewed group remains. A hold is a
reviewed outcome, not permission to infer a canonical identity.

ADR 0021 remains historical evidence for the initial collision inventory. Its
blanket retention of production-system and process-context duplicates is
superseded by this decision.

Canonical cutover, public hosting, W3ID registration, DOI, and AgroPortal
publication remain deferred until full validation, clean reload, and visual
acceptance pass.
