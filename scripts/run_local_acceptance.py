#!/usr/bin/env python3
"""Exercise local ERA-AOM browser, API, graph backup, and redirect behavior."""

import argparse
import json
import statistics
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from rdflib import Graph


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request(url, accept="application/json", follow=True):
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "era-aom-acceptance/1"})
    started = time.perf_counter()
    try:
        response = opener.open(req, timeout=20)
    except urllib.error.HTTPError as error:
        if follow or error.code not in (301, 302, 303, 307, 308):
            raise
        response = error
    body = response.read()
    return response.status, response.headers, body, time.perf_counter() - started


def json_get(url, timings):
    status, headers, body, elapsed = request(url)
    timings.append(elapsed)
    assert status == 200, (url, status)
    assert "json" in headers.get_content_type(), (url, headers.get_content_type())
    return json.loads(body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/local-acceptance.json")
    parser.add_argument("--fuseki", default="http://127.0.0.1:9030/skosmos")
    parser.add_argument("--skosmos", default="http://127.0.0.1:9090")
    parser.add_argument("--w3id", default="http://127.0.0.1:9080/era-aom/")
    parser.add_argument("--output", default="acceptance-results")
    args = parser.parse_args()
    profile = json.loads(Path(args.config).read_text())
    timings = []
    results = {}
    vocid = profile["vocabulary_id"]
    concept_id = profile["representative_concept"]
    concept_uri = f"https://w3id.org/era-aom/livestock/{concept_id}"

    query = "SELECT (COUNT(DISTINCT ?c) AS ?count) WHERE { ?c a <http://www.w3.org/2004/02/skos/core#Concept> }"
    sparql_url = args.fuseki + "/sparql?" + urllib.parse.urlencode({"query": query})
    sparql = json_get(sparql_url, timings)
    count = int(sparql["results"]["bindings"][0]["count"]["value"])
    assert count == profile["expected_concepts"], count
    results["concept_count"] = count

    hierarchy_query = "SELECT (COUNT(?broader) AS ?broaderCount) (COUNT(?narrower) AS ?narrowerCount) WHERE { { ?child <http://www.w3.org/2004/02/skos/core#broader> ?parent . BIND(?parent AS ?broader) } UNION { ?parent <http://www.w3.org/2004/02/skos/core#narrower> ?child . BIND(?child AS ?narrower) } }"
    hierarchy_url = args.fuseki + "/sparql?" + urllib.parse.urlencode({"query": hierarchy_query})
    hierarchy = json_get(hierarchy_url, timings)["results"]["bindings"][0]
    broader_count = int(hierarchy["broaderCount"]["value"])
    narrower_count = int(hierarchy["narrowerCount"]["value"])
    assert broader_count == narrower_count == 2733, hierarchy

    api = args.skosmos.rstrip("/") + "/rest/v1"
    vocabularies = json_get(api + "/vocabularies?lang=en", timings)
    assert vocid in json.dumps(vocabularies), vocabularies
    search = json_get(api + f"/{vocid}/search?" + urllib.parse.urlencode({"query": profile["search_query"], "lang": "en", "maxhits": 20}), timings)
    assert profile["search_query"].lower() in json.dumps(search).lower(), search
    broader = json_get(api + f"/{vocid}/broader?" + urllib.parse.urlencode({"uri": concept_uri, "lang": "en"}), timings)
    assert broader is not None
    stats = json_get(api + f"/{vocid}/vocabularyStatistics?lang=en", timings)
    assert str(count) in json.dumps(stats), stats
    top_concepts = json_get(api + f"/{vocid}/topConcepts?lang=en", timings)
    top_text = json.dumps(top_concepts)
    assert all(item in top_text for item in profile["expected_top_concepts"]), top_concepts
    results["api"] = {"vocabularies": "pass", "search": "pass", "broader": "pass", "top_concepts": "pass", "statistics": "pass"}
    results["hierarchy"] = {"roots": len(profile["expected_top_concepts"]), "broader": broader_count, "narrower": narrower_count}

    page = args.skosmos.rstrip("/") + f"/{vocid}/en/page/{concept_id}"
    status, headers, body, elapsed = request(page, "text/html")
    timings.append(elapsed)
    html = body.decode("utf-8", errors="replace")
    assert status == 200 and headers.get_content_type() == "text/html"
    assert profile["representative_label"] in html
    assert 'application/ld+json' in html
    results["concept_page"] = {"id": concept_id, "label": profile["representative_label"], "embedded_jsonld": True}

    graph_url = args.fuseki + "/get?" + urllib.parse.urlencode({"graph": "https://w3id.org/era-aom/graph/livestock"})
    status, _, graph_body, elapsed = request(graph_url, "text/turtle")
    timings.append(elapsed)
    assert status == 200
    backup = Graph().parse(data=graph_body, format="turtle")
    assert len(backup) >= 26850, len(backup)
    results["graph_backup"] = {"triples": len(backup), "parse": "pass"}

    redirect_expectations = {
        "text/turtle": "aom-livestock.ttl",
        "application/ld+json": "aom-livestock.jsonld",
        "application/rdf+xml": "aom-livestock.rdf",
        "text/html": f"/livestock/en/page/{concept_id}",
    }
    for accept, suffix in redirect_expectations.items():
        status, headers, _, elapsed = request(args.w3id.rstrip("/") + f"/livestock/{concept_id}", accept, follow=False)
        timings.append(elapsed)
        assert status == 303, (accept, status)
        assert headers["Location"].endswith(suffix), (accept, headers["Location"])
    results["content_negotiation"] = {key: "pass" for key in redirect_expectations}

    results["performance"] = {
        "requests": len(timings),
        "maximum_seconds": round(max(timings), 4),
        "median_seconds": round(statistics.median(timings), 4),
        "threshold_seconds": profile["maximum_response_seconds"],
    }
    assert max(timings) <= profile["maximum_response_seconds"], results["performance"]
    results["status"] = "pass"

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "acceptance.json").write_text(json.dumps(results, indent=2) + "\n")
    lines = ["# ERA-AOM local acceptance", "", "Status: **PASS**", "", f"- Concepts: {count:,}", f"- Top concepts: {len(profile['expected_top_concepts'])}", f"- Broader/narrower pairs: {broader_count:,}/{narrower_count:,}", f"- Backup graph triples: {len(backup):,}", f"- Requests: {len(timings)}", f"- Maximum response: {max(timings):.4f}s", f"- Median response: {statistics.median(timings):.4f}s", "- Skosmos API/search/hierarchy/statistics: pass", "- Concept HTML + embedded JSON-LD: pass", "- Turtle/JSON-LD/RDF/XML/HTML redirects: pass", ""]
    (output / "acceptance.md").write_text("\n".join(lines))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
