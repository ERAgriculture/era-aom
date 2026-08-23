# ERA-AOM reproducible rebuild contract

## Scope

Release and review builders must reproduce every tracked generated artifact from
a clean checkout. Semantic equivalence alone does not permit stale committed
outputs.

## Supported writer runtime

Byte reproducibility is supported with:

- Python 3.12;
- RDFLib 7.6.0;
- PyArrow 24.0.0;
- pySHACL 0.40.1;
- PyYAML 6.0.2.

`requirements-dev.txt` pins this runtime exactly. Unsupported writer versions
may produce semantically equivalent files, but their bytes are not accepted as
release artifacts.

## Artifact requirements

- Tracked CSV, Turtle, JSON-LD, RDF/XML, Parquet, manifest, checksum, and review
  outputs require byte identity after a clean rebuild with the supported runtime.
- JSON-LD and RDF/XML use sorted ground-graph writers. Release graphs containing
  blank nodes fail until stable resource identifiers are assigned.
- RDF serializations must also parse to equal triple sets.
- Parquet files use explicit writer options and must also equal their CSV source
  tables by schema, row order, and values.
- Manifest checksums cover every release distribution and the manifest itself.

## Build order

1. Run source audits and governed review builders.
2. Apply accepted semantic cohort builders.
3. Run final definition enrichment and normalize livestock staging.
4. Refresh final-state derived identity review outputs.
5. Build semantic bindings and validate RDF/SHACL.
6. Build and validate the release candidate.
7. Run `python tests/validate_release_reproducibility.py`.
8. Run `python scripts/validate_clean_rebuild.py` last.

The final clean gate examines tracked and untracked repository state. Any change
means committed generated output is stale or a builder is nondeterministic.

## Cross-platform evidence

ERA-AOM issue 99 reproduced Parquet byte drift when the previously allowed
PyArrow 18.1.0 writer rebuilt artifacts committed by PyArrow 24.0.0. The same
merged commit rebuilt byte-identically on macOS and Linux with the pinned
runtime. Canonical RDF writers and clean-worktree CI prevent recurrence from
unordered serialization or stale derived reviews.
