# Decision 0016: split persistent identity from hosting

Status: accepted — identity and target names approved 2026-08-05; deployment
remains gated on DNS, live hosting, release publication, and external approval.

## Context

`w3id.org` is a permanent HTTPS redirect service, not ontology hosting. ERA-AOM
needs stable concept identities while retaining freedom to replace browser or
artifact infrastructure. No ERA repository currently has GitHub Pages enabled,
and no approved production Skosmos hostname exists.

## Proposed decision

- Keep public identity at `https://w3id.org/era-aom/`.
- Route HTML requests to version-independent Skosmos concept pages.
- Route Turtle, JSON-LD, and RDF/XML requests to immutable release assets.
- Use HTTP 303 and `Vary: Accept` for content negotiation.
- Keep browser hosting, immutable artifact hosting, and canonical pipeline
  cutover as separate operational concerns.
- Name at least one individual GitHub maintainer plus organizational contact in
  w3id registration. Avoid person-dependent destination URLs.

This split is future-proof: browser host can move without changing concept
identifiers, machine clients receive standard RDF formats, and AI/search systems
can dereference stable IRIs into explicit SKOS graphs.

## Required approvals

Approved configuration:

- Skosmos target: `https://vocab.era.cgiar.org/livestock`;
- immutable artifact target: GitHub Release `2026.1`;
- individual maintainer: Pete Steward (`peetmate`);
- organizational continuity: `ERAgriculture`;
- owner attribution: Alliance of Bioversity International and CIAT, within
  CGIAR.

Still required:

1. CGIAR DNS delegation and operational hosting owner confirmation.
2. Live Skosmos deployment and immutable `2026.1` publication.
3. Destination/content-negotiation tests.
4. Explicit approval for external PR to `perma-id/w3id.org`.

Generator refuses example domains and unapproved target configuration. Approved
target names authorize generating review files, not DNS changes, deployment,
release publication, or external submission. No w3id files should be submitted
until generated output passes validation and all destinations resolve.
