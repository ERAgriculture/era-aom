# Decision 0016: split persistent identity from hosting

Status: proposed — hosting targets and maintainers await approval.

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

1. Production Skosmos HTTPS base URL and operational owner.
2. Immutable release asset base URL and formal `2026.1` publication.
3. Individual w3id maintainer(s); organization alone is insufficient continuity.
4. External PR to `perma-id/w3id.org`.

Generator refuses example domains and unapproved target configuration. No w3id
files should be submitted until generated output passes local validation and all
destinations resolve.
