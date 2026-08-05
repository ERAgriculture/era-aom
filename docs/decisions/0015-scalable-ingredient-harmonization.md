# ADR 0015: Scale ingredient harmonization through governed rules

- Status: Accepted for proposal generation
- Date: 2026-08-05
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Context

Livestock source contains 1,644 feed-ingredient occurrences representing 1,643
governed concepts. Manual concept-by-concept
review would be slow, inconsistent, and difficult to repeat when source data
changes. Maize review established reusable distinctions between source identity,
material component, processing method, physical form, and quality.

## Decision

Use a deterministic rule workbench across the complete ingredient inventory.
Rules extract proposed semantic dimensions, create normalized signatures, group
possible duplicates, assign confidence and review routes, and isolate true
exceptions. Review and approve reusable rules or families rather than individual
concepts wherever evidence permits.

Generated proposals never change ontology identity, labels, mappings, hierarchy,
or status. A signature is a review aid, not proof of equivalence. Every merge or
deprecation still requires explicit governance data. Existing approved decisions
are recognized so resolved cases do not return to the unresolved queue.

Review routes are:

1. `rule_application_candidate` — clear typed decomposition suitable for bulk
   rule approval;
2. `retain_atomic_candidate` — no compound signal detected; retain in bulk unless
   collision or other evidence intervenes;
3. `batch_review` — structurally complex but reusable family pattern;
4. `expert_exception` — ambiguity, lost source identity, or metadata concept.

Unqualified `Whole` remains ambiguous. ILRI feed identifiers remain excluded
from rule evidence and scoring while that external system changes.

## Consequences

- Human work shifts from 1,643 individual concept reviews to rule families, signature
  clusters, and a small exception queue.
- Results are deterministic, reproducible, traceable to rule version, and usable
  by both tabular pipelines and RDF/AI systems.
- Legacy identifiers remain stable and searchable.
- Rule promotion requires separate approval and validation before normalized
  semantic assertions enter a release.
