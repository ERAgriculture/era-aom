# ERA-AOM local quality acceptance

Hosting is deferred. Current objective is proving release quality through
ephemeral local containers and CI before requesting CGIAR infrastructure.

Acceptance harness exercises:

- exact 2,737-concept SPARQL count;
- exact four-root hierarchy and 2,733 symmetric broader/narrower pairs;
- Skosmos vocabulary discovery, search, hierarchy, and statistics APIs;
- representative concept page and embedded JSON-LD;
- named-graph Turtle export as parseable backup evidence;
- local Apache execution of proposed w3id HTML/Turtle/JSON-LD/RDF/XML rules;
- bounded response-time threshold;
- machine-readable JSON and human-readable Markdown reports.

Run on Docker-capable machine:

```sh
docker compose -f deploy/local/compose.yaml up --build --detach
python scripts/check_browser_stack.py --attempts=90 --delay=2
python scripts/run_local_acceptance.py --output=acceptance-results
docker compose -f deploy/local/compose.yaml down --volumes
```

Use `--force-recreate skosmos` after configuration or stylesheet changes.
Skosmos caches parsed configuration in APC; a process restart does not reliably
invalidate a bind-mounted file whose modification key is unchanged.

GitHub Actions uploads report from every run. Visual screenshots and manual
interaction remain separate because current development machine lacks Docker and
browser connection. Hosting-only DNS/TLS, public uptime, w3id, AgroPortal, and
DOI gates remain deferred.
