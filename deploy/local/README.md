# Local ERA-AOM browser

Reproducible evaluation stack: Skosmos 3.3, Apache Jena/Fuseki 5.4.0, Jena
Text, and Varnish. Services bind to loopback only. Release loader imports
`2026.1-rc.1` into named graph `https://w3id.org/era-aom/graph/livestock`.

```sh
docker compose -f deploy/local/compose.yaml up --build
python scripts/check_browser_stack.py --attempts=90 --delay=2
docker compose -f deploy/local/compose.yaml down
```

Use `down --volumes` only when deliberately discarding local evaluation data.
This is not public hosting: no TLS, authentication, backups, monitoring,
institutional domain, or w3id registration. Passing local checks does not
authorize external deployment or canonical cutover. Pins follow Skosmos 3.3
upstream Docker configuration; update pins through dependency PRs.

GitHub Actions repeats full container build, graph load, SPARQL count, and
Skosmos HTTP checks on every pull request. Logs are captured before teardown
when runtime validation fails.
