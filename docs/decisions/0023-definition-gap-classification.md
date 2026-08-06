# ADR 0023: definition-gap classification

Status: accepted  
Date: 2026-08-06  
Reviewer: Pete Steward

## Context

ADR 0022 reduced active definition gaps from 2,127 to 888. Remaining concepts span distinct evidence needs: 643 feed materials, 80 outcomes, 67 rearing stages, 45 taxa, 35 management concepts, 16 farming-system concepts, and two core roots.

## Decision

Add 243 model-level definitions for outcomes, rearing stages, taxa, management concepts, and farming-system classifications. Definitions state only governed hierarchy context and semantic role. They do not infer scientific rank, measurement protocol, biological properties, or management effects.

Classify every prior gap in `definition_gap_queue.csv`:

- 199 feed materials route to Feedipedia research;
- 26 route to public ontology/AGROVOC research;
- 218 have taxon mappings insufficient to define material identity;
- 200 require source-workbook research;
- two core roots require manual definitions.

Exclude ILRI codes from routing and published evidence. External mappings remain candidates for research, not copied definitions or identity proof.

## Consequences

Approved definition enrichments rise to 1,482. Active gaps fall from 888 to 645. Remaining work is bounded, domain-routed, and evidence-dependent rather than an undifferentiated missing-definition count.
