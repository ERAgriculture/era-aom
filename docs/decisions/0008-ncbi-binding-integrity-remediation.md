# ADR 0008: NCBI binding integrity remediation

- Status: Accepted
- Date: 2026-08-04
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: Pete Steward

## Decision

Supersede two approved bindings inherited from incorrect legacy identifiers.
Bind `Guizotia abyssinica` to `NCBITaxon_4230`; `NCBITaxon_4146` identifies
`Olea europaea`. Bind genus `Brevoortia` to `NCBITaxon_224706`;
`NCBITaxon_55119` identifies subfamily `Alosinae`.

Require every approved NCBI binding to match a pinned current-name/rank
snapshot. Validate snapshot offline in CI. Run live NCBI validation before any
future approval batch or snapshot refresh. Live validation rejects redirected
identifiers and accepted-name mismatches.

## Consequences

Existing pipeline contract must be repinned after merge. Future approval PRs
cannot rely on inherited identifier labels alone. Snapshot records evidence and
verification date but remains a derived validation artifact, not independent
taxonomy authority.
