# ADR 0050: Reproducible release artifact contract

- Status: Proposed
- Date: 2026-08-23
- Owners: ERA-AOM release governance
- Tracking: [era-aom #99](https://github.com/ERAgriculture/era-aom/issues/99)

## Context

Post-merge ADR 0048 acceptance found semantically equivalent JSON-LD, RDF/XML,
and Parquet artifacts with different bytes after rebuilding on another supported
environment. One derived identity-review file was also stale until a final-state
builder reran. Existing validation proved graph and table meaning but did not
reject stale committed outputs.

Reproduction at merged commit `8fb207ffb974891d59f58d7e9a1b90fcf44796ce`
showed that the allowed PyArrow 18.1.0 writer changed all five Parquet files
produced by PyArrow 24.0.0. Rebuilding with RDFLib 7.6.0 and PyArrow 24.0.0
produced identical bytes on macOS and Linux.

## Decision

1. Require Python 3.12 and exact release-writer dependency versions.
2. Require byte identity for every tracked generated release and review output
   after a clean rebuild with the supported runtime.
3. Generate release JSON-LD and RDF/XML from sorted ground graphs. Blank nodes
   are rejected until assigned stable resource identifiers.
4. Write Parquet with explicit format, compression, dictionary, statistics, and
   schema options; validate complete row/value parity with companion CSV files.
5. Continue graph-equivalence checks across Turtle, JSON-LD, and RDF/XML in
   addition to byte checks.
6. Run a repository-cleanliness gate after all builders and validators. Any
   tracked or untracked difference fails CI as stale or nondeterministic output.
7. Treat unsupported writer versions as outside the reproducible release
   contract even when their outputs remain semantically equivalent.

## Consequences

- Dependency upgrades become reviewed release changes with regenerated artifacts
  and cross-platform evidence.
- Release diffs are large once while canonical serializers replace unordered
  RDFLib output.
- CI detects stale review files and distributions instead of silently validating
  them.
- Semantic equivalence remains mandatory and is not replaced by byte comparison.
- This decision changes packaging only; no ontology concept, relationship, or
  publication status changes.

## Evidence

- [`review/rebuild-v1/reproducibility_evidence.json`](../../review/rebuild-v1/reproducibility_evidence.json)
- [`docs/REBUILD_CONTRACT.md`](../REBUILD_CONTRACT.md)

## Approval record

Awaiting human decision. Implementation remains a non-semantic release candidate
until this ADR and its evidence are reviewed.
