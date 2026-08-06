#!/usr/bin/env python3
"""Validate local browser deployment configuration without Docker."""
from pathlib import Path
import rdflib
import yaml

ROOT = Path(__file__).resolve().parents[1]
compose = yaml.safe_load((ROOT / "deploy/local/compose.yaml").read_text())
services = compose["services"]
assert set(services) == {"fuseki", "fuseki-cache", "load-release", "skosmos", "w3id-mock"}
assert services["fuseki"]["build"]["context"].endswith("#v3.3:dockerfiles/jena-fuseki2-docker")
assert services["fuseki"]["build"]["args"]["JENA_VERSION"] == "5.4.0"
assert services["fuseki-cache"]["image"] == "varnish:7.7.3"
assert services["load-release"]["image"] == "curlimages/curl:8.12.1"
assert services["w3id-mock"]["image"] == "httpd:2.4.68-alpine"
assert all(port.startswith("127.0.0.1:") for service in services.values() for port in service.get("ports", []))
for relative in ("config/skosmos/era-aom.ttl", "deploy/local/fuseki.ttl"):
    graph = rdflib.Graph(); graph.parse(ROOT / relative, format="turtle"); assert len(graph) > 0
text = (ROOT / "config/skosmos/era-aom.ttl").read_text()
assert "http://purl.org/net/skosmos#" in text
assert "http://purl.org/net/Skosmos#" not in text
assert "https://w3id.org/era-aom/graph/livestock" in text
assert 'skosmos:customCss "resource/css/era-aom.css"' in text
css = ROOT / "config/skosmos/era-aom.css"
assert css.is_file() and ".prop-skos_relatedMatch" in css.read_text()
assert "overflow-wrap: anywhere" in css.read_text()
assert any("era-aom.css:/var/www/html/resource/css/era-aom.css:ro" in volume
           for volume in services["skosmos"]["volumes"])
assert "#maincontent/#main-content" in " ".join(services["skosmos"]["command"])
assert "issues/new/choose" in " ".join(services["skosmos"]["command"])

production = yaml.safe_load((ROOT / "deploy/production/compose.yaml").read_text())
production_services = production["services"]
assert set(production_services) == {"fuseki", "fuseki-cache", "load-release", "skosmos", "proxy"}
assert production_services["proxy"]["image"] == "caddy:2.11.4-alpine"
assert "ports" not in production_services["fuseki"]
assert "ports" not in production_services["skosmos"]
assert production_services["proxy"]["ports"] == ["80:80", "443:443", "443:443/udp"]
graph = rdflib.Graph(); graph.parse(ROOT / "config/skosmos/era-aom-production.ttl", format="turtle")
assert len(graph) > 0
assert any("era-aom.css:/var/www/html/resource/css/era-aom.css:ro" in volume
           for volume in production_services["skosmos"]["volumes"])
assert "#maincontent/#main-content" in " ".join(production_services["skosmos"]["command"])
assert "issues/new/choose" in " ".join(production_services["skosmos"]["command"])
assert "vocab.era.cgiar.org" in (ROOT / "deploy/production/Caddyfile").read_text()
print("Deployment bundle validation passed.")
