#!/usr/bin/env python3
"""Validate local browser deployment configuration without Docker."""
from pathlib import Path
import rdflib
import yaml

ROOT = Path(__file__).resolve().parents[1]
compose = yaml.safe_load((ROOT / "deploy/local/compose.yaml").read_text())
services = compose["services"]
assert set(services) == {"fuseki", "fuseki-cache", "load-release", "skosmos"}
assert services["fuseki"]["build"]["context"].endswith("#v3.3")
assert services["fuseki"]["build"]["args"]["JENA_VERSION"] == "5.4.0"
assert services["fuseki-cache"]["image"] == "varnish:7.7.3"
assert services["load-release"]["image"] == "curlimages/curl:8.12.1"
assert all(port.startswith("127.0.0.1:") for service in services.values() for port in service.get("ports", []))
for relative in ("config/skosmos/era-aom.ttl", "deploy/local/fuseki.ttl"):
    graph = rdflib.Graph(); graph.parse(ROOT / relative, format="turtle"); assert len(graph) > 0
text = (ROOT / "config/skosmos/era-aom.ttl").read_text()
assert "http://purl.org/net/skosmos#" in text
assert "http://purl.org/net/Skosmos#" not in text
assert "https://w3id.org/era-aom/graph/livestock" in text
print("Deployment bundle validation passed.")
