# ADR 0019: Preserve standalone feed-material identity during decomposition

- Status: Accepted
- Date: 2026-08-06
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Context

Lexical decomposition normally removes component and form tokens to recover a
source identity. This fails when the apparent component is itself the complete
feed-material identity. `Blood`, `Shell`, and `Oil` then leave an empty source,
while processed variants lose the material they describe.

## Decision

Add reviewed, concept-specific source-identity overrides for six affected
materials. Preserve Blood, Shell, or Oil as material identity. Suppress matching
component/form extraction for those concepts. Continue extracting independently
evidenced processes such as Drying, Grinding, and Heating.

Overrides are governed data, not general lexical rules. They must name exact
concept IDs, suppressed values, reviewer, date, evidence, and rationale. Future
source taxon or material refinements may replace an override through normal
review without changing legacy identity.

## Consequences

- Six expert exceptions become deterministic governed cases.
- Blood and Shell are not falsely asserted as parts of an unknown source.
- Oil is not falsely asserted as physical form.
- Process assertions remain queryable and reproducible.
