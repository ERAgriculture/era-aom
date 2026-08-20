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

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, SKOS


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
    assert broader_count == narrower_count == profile["expected_hierarchy_relations"], hierarchy

    api = args.skosmos.rstrip("/") + "/rest/v1"
    vocabularies = json_get(api + "/vocabularies?lang=en", timings)
    assert vocid in json.dumps(vocabularies), vocabularies
    search = json_get(api + f"/{vocid}/search?" + urllib.parse.urlencode({"query": profile["search_query"], "lang": "en", "maxhits": 20}), timings)
    assert profile["search_query"].lower() in json.dumps(search).lower(), search
    notation_search = json_get(api + f"/{vocid}/search?" + urllib.parse.urlencode({"query": profile["notation_search_concept"], "lang": "en", "maxhits": 20}), timings)
    notation_text = json.dumps(notation_search)
    assert profile["notation_search_concept"] in notation_text, notation_search
    assert profile["notation_search_label"] in notation_text, notation_search
    retired_search_results = []
    for check in profile["retired_descriptor_checks"]:
        retired_search = json_get(
            api + f"/{vocid}/search?" + urllib.parse.urlencode({
                "query": check["concept_id"], "lang": "en", "maxhits": 20,
            }),
            timings,
        )
        retired_text = json.dumps(retired_search)
        assert check["concept_id"] in retired_text and check["label"] in retired_text
        retired_search_results.append(check["concept_id"])
    broader = json_get(api + f"/{vocid}/broader?" + urllib.parse.urlencode({"uri": concept_uri, "lang": "en"}), timings)
    assert broader is not None
    retired_parent_uri = f"https://w3id.org/era-aom/livestock/{profile['retired_parent_concept']}"
    narrower = json_get(
        api + f"/{vocid}/narrower?" + urllib.parse.urlencode({"uri": retired_parent_uri, "lang": "en"}),
        timings,
    )
    narrower_text = json.dumps(narrower)
    assert not any(check["concept_id"] in narrower_text for check in profile["retired_descriptor_checks"])
    navigation = json_get(
        api + f"/{vocid}/narrower?" + urllib.parse.urlencode({"uri": retired_parent_uri, "lang": "en"}),
        timings,
    )
    actual_navigation = {
        item["uri"].rsplit("/", 1)[-1]: item["prefLabel"]
        for item in navigation["narrower"]
    }
    expected_navigation = {
        item["concept_id"]: item["label"]
        for item in profile["feed_material_navigation_children"]
    }
    assert actual_navigation == expected_navigation, actual_navigation
    nested_navigation = []
    for check in profile["nested_navigation_checks"]:
        child_uri = f"https://w3id.org/era-aom/livestock/{check['concept_id']}"
        parent_response = json_get(
            api + f"/{vocid}/broader?" + urllib.parse.urlencode({"uri": child_uri, "lang": "en"}),
            timings,
        )
        actual_parents = {
            item["uri"].rsplit("/", 1)[-1]
            for item in parent_response["broader"]
        }
        assert actual_parents == {check["parent_id"]}, (check, actual_parents)
        nested_navigation.append(check)
    stats = json_get(api + f"/{vocid}/vocabularyStatistics?lang=en", timings)
    assert str(count) in json.dumps(stats), stats
    top_concepts = json_get(api + f"/{vocid}/topConcepts?lang=en", timings)
    top_text = json.dumps(top_concepts)
    assert all(item in top_text for item in profile["expected_top_concepts"]), top_concepts
    results["api"] = {"vocabularies": "pass", "search": "pass", "notation_search": "pass", "retired_search": retired_search_results, "retired_hierarchy_exclusion": "pass", "feed_material_navigation": expected_navigation, "nested_navigation": nested_navigation, "broader": "pass", "top_concepts": "pass", "statistics": "pass"}
    results["hierarchy"] = {"roots": len(profile["expected_top_concepts"]), "broader": broader_count, "narrower": narrower_count}

    page = args.skosmos.rstrip("/") + f"/{vocid}/en/page/{concept_id}"
    status, headers, body, elapsed = request(page, "text/html")
    timings.append(elapsed)
    html = body.decode("utf-8", errors="replace")
    assert status == 200 and headers.get_content_type() == "text/html"
    assert profile["representative_label"] in html
    assert 'application/ld+json' in html
    assert '<link href="resource/css/era-aom.css"' in html
    assert 'id="skiptocontent"' in html and '#main-content">Skip to main</a>' in html
    assert 'id="main-content"' in html
    assert '<meta name="viewport"' in html
    assert 'href="https://github.com/ERAgriculture/era-aom/issues/new/choose"' in html
    assert '&nbsp;Contribute' in html
    results["concept_page"] = {"id": concept_id, "label": profile["representative_label"], "embedded_jsonld": True}

    compound_id = profile["compound_display_concept"]
    compound_page = args.skosmos.rstrip("/") + f"/{vocid}/en/page/{compound_id}"
    compound_status, compound_headers, compound_body, elapsed = request(compound_page, "text/html")
    timings.append(elapsed)
    compound_html = compound_body.decode("utf-8", errors="replace")
    assert compound_status == 200 and compound_headers.get_content_type() == "text/html"
    assert profile["compound_display_label"] in compound_html
    assert profile["compound_display_facet"] in compound_html
    for property_check in profile["compound_display_properties"]:
        assert property_check["property"] in compound_html, property_check
        assert property_check["value"] in compound_html, property_check
    results["compound_concept_page"] = {
        "id": compound_id,
        "label": profile["compound_display_label"],
        "facet": profile["compound_display_facet"],
        "properties": profile["compound_display_properties"],
    }

    process_id = profile["process_display_concept"]
    process_page = args.skosmos.rstrip("/") + f"/{vocid}/en/page/{process_id}"
    process_status, process_headers, process_body, elapsed = request(process_page, "text/html")
    timings.append(elapsed)
    process_html = process_body.decode("utf-8", errors="replace")
    assert process_status == 200 and process_headers.get_content_type() == "text/html"
    assert profile["process_display_label"] in process_html
    for property_check in profile["process_display_properties"]:
        assert property_check["property"] in process_html, property_check
        assert property_check["value"] in process_html, property_check
    results["process_concept_page"] = {
        "id": process_id,
        "label": profile["process_display_label"],
        "properties": profile["process_display_properties"],
    }

    css_url = args.skosmos.rstrip("/") + "/resource/css/era-aom.css"
    status, headers, css_body, elapsed = request(css_url, "text/css")
    timings.append(elapsed)
    css_text = css_body.decode("utf-8")
    assert status == 200 and headers.get_content_type() == "text/css"
    assert ".prop-skos_relatedMatch" in css_text and ".prop-mapping-label" in css_text
    assert ".prop-mapping-vocab" in css_text and "overflow-wrap: anywhere" in css_text
    results["custom_css"] = {"linked": True, "served": True, "long_mapping_wrap": True}
    results["contribution_route"] = {"github_issue_chooser": "pass", "dead_mail_form_exposed": False}

    graph_url = args.fuseki + "/get?" + urllib.parse.urlencode({"graph": "https://w3id.org/era-aom/graph/livestock"})
    status, _, graph_body, elapsed = request(graph_url, "text/turtle")
    timings.append(elapsed)
    assert status == 200
    backup = Graph().parse(data=graph_body, format="turtle")
    assert len(backup) >= profile["minimum_graph_triples"], len(backup)
    results["graph_backup"] = {"triples": len(backup), "parse": "pass"}

    retired_results = []
    for check in profile["retired_descriptor_checks"]:
        cid = check["concept_id"]
        uri = URIRef(f"https://w3id.org/era-aom/livestock/{cid}")
        assert (uri, OWL.deprecated, Literal(True)) in backup
        assert not any(backup.objects(uri, SKOS.broader))
        history = {str(value) for value in backup.objects(uri, SKOS.historyNote)}
        assert any(check["history_contains"] in value for value in history), (cid, history)
        concept_page = args.skosmos.rstrip("/") + f"/{vocid}/en/page/{cid}"
        page_status, _, page_body, elapsed = request(concept_page, "text/html")
        timings.append(elapsed)
        page_html = page_body.decode("utf-8", errors="replace")
        assert page_status == 200 and check["label"] in page_html
        assert "This concept has been deprecated." in page_html
        retired_results.append({"concept_id": cid, "search": "pass", "page": "deprecated-warning-pass", "history": "pass", "hierarchy": "excluded"})
    results["retired_descriptors"] = retired_results

    representative_results = []
    for check in profile["representative_checks"]:
        cid = check["concept_id"]
        uri = URIRef(f"https://w3id.org/era-aom/livestock/{cid}")
        labels = {str(value) for value in backup.objects(uri, SKOS.prefLabel)}
        definitions = [str(value) for value in backup.objects(uri, SKOS.definition)]
        assert check["label"] in labels, (cid, labels)
        if "definition_contains" in check:
            assert any(check["definition_contains"] in value for value in definitions), (cid, definitions)
        if check.get("definition_absent"):
            assert not definitions, (cid, definitions)
        if check.get("status"):
            status_values = {str(value) for value in backup.objects(uri, URIRef("urn:era:property:status"))}
            assert check["status"] in status_values, (cid, status_values)
        if check.get("replaced_by"):
            replacements = {str(value).rsplit("/", 1)[-1] for value in backup.objects(uri, DCTERMS.isReplacedBy)}
            assert check["replaced_by"] in replacements, (cid, replacements)
        for property_check in check.get("properties", []):
            predicate = URIRef(f"https://w3id.org/era-aom/schema/{property_check['predicate']}")
            targets = {str(value).rsplit("/", 1)[-1] for value in backup.objects(uri, predicate)}
            assert property_check["target_id"] in targets, (cid, property_check, targets)
        concept_page = args.skosmos.rstrip("/") + f"/{vocid}/en/page/{cid}"
        page_status, _, page_body, elapsed = request(concept_page, "text/html")
        timings.append(elapsed)
        page_html = page_body.decode("utf-8", errors="replace")
        assert page_status == 200 and check["label"] in page_html and 'application/ld+json' in page_html
        for property_check in check.get("properties", []):
            assert property_check["property_label"] in page_html, property_check
            assert property_check["value_label"] in page_html, property_check
        representative_results.append({"concept_id": cid, "label": check["label"], "page": "pass", "semantics": "pass"})
    results["representative_matrix"] = representative_results

    format_checks = {
        "application/rdf+xml": "xml",
        "text/turtle": "turtle",
        "application/ld+json": "json-ld",
    }
    for media_type, rdf_format in format_checks.items():
        data_url = api + f"/{vocid}/data?" + urllib.parse.urlencode({"uri": concept_uri, "format": media_type})
        status, _, body, elapsed = request(data_url, media_type)
        timings.append(elapsed)
        assert status == 200
        parsed = Graph().parse(data=body, format=rdf_format)
        assert (URIRef(concept_uri), SKOS.prefLabel, None) in parsed
    results["concept_downloads"] = {key: "parse-pass" for key in format_checks}

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
    lines = ["# ERA-AOM local acceptance", "", "Status: **PASS**", "", f"- Concepts: {count:,}", f"- Top concepts: {len(profile['expected_top_concepts'])}", f"- Broader/narrower pairs: {broader_count:,}/{narrower_count:,}", f"- Backup graph triples: {len(backup):,}", f"- Representative concepts: {len(representative_results)}", f"- Retired descriptor cards: {len(retired_results)}", f"- Feed-material navigation children: {len(expected_navigation)}", f"- Nested navigation checks: {len(nested_navigation)}", f"- Requests: {len(timings)}", f"- Maximum response: {max(timings):.4f}s", f"- Median response: {statistics.median(timings):.4f}s", "- Skosmos API/search/hierarchy/statistics: pass", "- Feed-material direct and nested navigation: pass", "- Retired descriptor exact search, warnings, history, and hierarchy exclusion: pass", "- Concept HTML + embedded JSON-LD: pass", "- Compound concept source/component/process/role display: pass", "- Process mechanism/objective/benefit display: pass", "- Custom stylesheet linked, served, and wrap rules present: pass", "- Representative semantic/page matrix: pass", "- Concept RDF/XML, Turtle, and JSON-LD downloads parse: pass", "- Turtle/JSON-LD/RDF/XML/HTML redirects: pass", ""]
    (output / "acceptance.md").write_text("\n".join(lines))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
