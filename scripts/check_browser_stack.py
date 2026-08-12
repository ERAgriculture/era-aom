#!/usr/bin/env python3
"""Smoke-test local Skosmos/Fuseki evaluation stack."""
import argparse
import json
import time
import urllib.parse
import urllib.request

def get(url, accept):
    request = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "era-aom-validator/1"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.status, response.headers.get_content_type(), response.read()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fuseki", default="http://127.0.0.1:9030/skosmos/sparql")
    parser.add_argument("--skosmos", default="http://127.0.0.1:9090")
    parser.add_argument("--attempts", type=int, default=1)
    parser.add_argument("--delay", type=float, default=2)
    args = parser.parse_args()
    last_error = None
    for attempt in range(1, args.attempts + 1):
        try:
            query = "SELECT (COUNT(DISTINCT ?concept) AS ?count) WHERE { ?concept a <http://www.w3.org/2004/02/skos/core#Concept> }"
            url = args.fuseki + "?" + urllib.parse.urlencode({"query": query})
            status, content_type, body = get(url, "application/sparql-results+json")
            assert status == 200 and content_type == "application/sparql-results+json"
            count = int(json.loads(body)["results"]["bindings"][0]["count"]["value"])
            assert count == 2790, count
            status, content_type, _ = get(args.skosmos + "/en/", "text/html")
            assert status == 200 and content_type == "text/html"
            print(json.dumps({"concepts": count, "fuseki": "pass", "skosmos": "pass"}, indent=2))
            return
        except Exception as error:
            last_error = error
            if attempt < args.attempts:
                time.sleep(args.delay)
    raise RuntimeError(f"Browser stack failed after {args.attempts} attempts") from last_error

if __name__ == "__main__": main()
