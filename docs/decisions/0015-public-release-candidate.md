# Decision 0015 — package first public release candidate without cutover

**Status:** accepted
**Date:** 2026-08-05
**Approver:** Pete Steward for candidate build; permanent reviewer TBD

## Decision

Build `2026.1-rc.1` as immutable-style, noncanonical candidate using proposed
`https://w3id.org/era-aom/` identifiers. Generate semantic, analyst, citation,
licence, checksum, provenance, Skosmos, and visualization artifacts from
governed staging sources. Keep every external publication and canonical gate
false until independently completed and approved.

## Rationale

Candidate proves packaging and interoperability without claiming live URI
resolution or replacing workbook authority. Proposed w3id namespace decouples
concept identity from repository, browser, and hosting implementation. Dual
publication preserves rollback while reviewers inspect remaining operational
gates.

## Consequences

- Candidate IRIs are test identities, not live promises yet.
- No GitHub release, w3id registration, Skosmos deployment, or AgroPortal
  submission occurs through this decision alone.
- Permanent reviewer appointment and canonical cutover remain separate human
  decisions.
