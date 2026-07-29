# Governance

## Roles

- Institutional custodian and publisher: Alliance of Bioversity International
  and CIAT.
- Product: Agriculture Ontology for Meta-analysis, preserving published
  livestock AOM and collaborative ERA crop lineage.
- Pilot and canonical-cutover approver: Pete Steward.
- Permanent vocabulary reviewer: TBD.
- Creators, contributors, reviewers, rights holders, and funders: recorded as
  distinct roles.

## Change control

- Pull requests expose every canonical source change.
- Stable identifiers are never reused.
- Released versions are immutable.
- AI may propose labels, mappings, and classifications.
- Automated validation checks proposals.
- Human reviewer approves semantic changes.
- Embeddings and retrieval indexes remain generated artifacts, never canonical
  sources.

## Release classification

Each release manifest classifies change as one of:

- `metadata-only`
- `compatible`
- `potentially-breaking`
- `breaking`

Calendar release identifiers use `YYYY.N`.
