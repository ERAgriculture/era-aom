#!/usr/bin/env python3
"""Post-deployment content-negotiation smoke test for persistent AOM IRIs."""

import argparse
import urllib.request


def fetch(url, accept):
    request = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "era-aom-validator/1"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.status, response.headers.get_content_type(), response.geturl()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="https://w3id.org/era-aom/")
    parser.add_argument("--concept", default="livestock/AOM_000001")
    args = parser.parse_args()
    url = args.base.rstrip("/") + "/" + args.concept
    expectations = {
        "text/html": "text/html",
        "text/turtle": "text/turtle",
        "application/ld+json": "application/ld+json",
        "application/rdf+xml": "application/rdf+xml",
    }
    for accept, expected in expectations.items():
        status, content_type, final_url = fetch(url, accept)
        assert status == 200, (accept, status, final_url)
        assert content_type == expected, (accept, content_type, final_url)
        print(accept, "->", content_type, final_url)


if __name__ == "__main__":
    main()
