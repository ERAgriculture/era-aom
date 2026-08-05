# ERA-AOM production browser

Approved service name: `vocab.era.cgiar.org`. Stack uses automatic TLS through
Caddy, Skosmos 3.3, private Fuseki/Jena Text 5.4.0, Varnish, and persistent
volumes. Only ports 80/443 are public; Fuseki update/query interfaces remain on
internal container network.

## Deployment gates

- CGIAR creates DNS record pointing hostname to managed host.
- Alliance/CGIAR names operational owner, backup location, alert recipient, and
  patch schedule.
- Host permits inbound 80/443 and persistent Docker volumes.
- Formal `2026.1` artifacts replace release-candidate mount before launch.
- Operator records volume backup and restoration test.
- `python scripts/check_live_namespace.py` passes after w3id registration.

Start only after publisher deployment approval:

```sh
docker compose -f deploy/production/compose.yaml config
docker compose -f deploy/production/compose.yaml up --build --detach
curl --fail https://vocab.era.cgiar.org/livestock/en/
```

Production does not expose Fuseki on loopback. Operator must run 2,737-concept
SPARQL count from internal container network or temporary SSH tunnel. Never open port 3030 to
internet. Preserve `fuseki-data`, `caddy-data`, and release manifest/checksums in
backups. Roll back browser by restoring prior graph volume and immutable release.
