# ERA-AOM publication and rollback runbook

## Safety boundary

Building a candidate is local and reversible. Creating a GitHub release,
registering `w3id.org`, deploying Skosmos, registering AgroPortal, or uploading
public objects changes external state and requires explicit publisher approval.
Canonical cutover requires separate approval.

## Build and validate

```sh
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python scripts/build_release_candidate.py \
  --config=config/releases/2026.1-rc.1.json
.venv/bin/python scripts/validate_release_candidate.py --release=2026.1-rc.1
```

Review `manifest.json`, `checksums.sha256`, release notes, licence, citation,
counts, and open gates. Rebuild from clean checkout; candidate tree and
checksums must match.

## Semantic-tool evaluation

Local browser stack is defined in `deploy/local/`. It pins Skosmos 3.3 and
Jena/Fuseki 5.4.0, loads release candidate into one named graph, and exposes
services on loopback only. Validate configuration in CI, then run where Docker
is available:

```sh
docker compose -f deploy/local/compose.yaml up --build
python scripts/check_browser_stack.py
```

1. Load `aom-livestock.ttl`, `aom-schema.ttl`, and semantic bindings into
   Apache Jena/Fuseki named graphs.
2. Point Skosmos vocabulary configuration at graph and verify search, hierarchy,
   labels, definitions, mappings, deprecated/replacement links, and concept
   neighbourhoods.
3. Open `aom-schema.ttl` in Protégé and WebVOWL. Inspect schema only; do not
   remodel SKOS concepts as OWL classes.
4. Import release into temporary AgroPortal submission only after namespace
   resolution works.

## Persistent namespace and content negotiation

Proposed namespace is `https://w3id.org/era-aom/`. Register only after
institutional owner accepts redirect targets and maintenance responsibility.
Generate registration files through `scripts/build_w3id_proposal.py`; see
`docs/W3ID_REGISTRATION.md`. Generator rejects unapproved/example targets.
Required representations:

- `text/html`: public concept page;
- `text/turtle`: Turtle distribution or concept response;
- `application/ld+json`: JSON-LD;
- `application/rdf+xml`: RDF/XML.

After deployment:

```sh
python scripts/check_live_namespace.py
```

Do not mark `namespace_registered` or `live_content_negotiation` true before
live tests pass.

## Approval and publication

Named reviewer signs semantic content; publisher verifies ownership/licence,
provenance, accessibility, privacy wording, checksums, and rollback package.
Tag and release immutable version only after all non-cutover publication gates
pass. Keep `canonical_cutover=false` and `dual_publish` until separate cutover
approval.

## Rollback

1. Stop downstream consumers from selecting failed version.
2. Restore prior immutable release pointer and Skosmos graph.
3. Preserve failed release/tag and incident evidence; never rewrite it.
4. Revert namespace redirects only to prior stable release, never to temporary
   or branch URLs.
5. Continue legacy workbook/pipeline path while correction goes through normal
   proposal, review, validation, and release process.
