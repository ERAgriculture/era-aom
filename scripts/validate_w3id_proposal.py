#!/usr/bin/env python3
"""Validate generated w3id.org proposal files and redirect invariants."""

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    root = Path(args.path)
    htaccess = (root / ".htaccess").read_text()
    readme = (root / "README.md").read_text()
    required = (
        "Options -MultiViews",
        'Header always set Vary "Accept"',
        "text/turtle",
        r"application/ld\+json",
        r"application/rdf\+xml",
        "[R=303",
        "https://w3id.org/era-aom/",
        "https://github.com/ERAgriculture/era-aom",
    )
    combined = htaccess + readme
    missing = [value for value in required if value not in combined]
    if missing:
        raise ValueError("Missing w3id requirements: " + ", ".join(missing))
    if "example.org" in combined or "${" in combined:
        raise ValueError("Proposal contains placeholder target")
    if htaccess.count("[R=303") < 7:
        raise ValueError("Expected content-negotiation, concept, release, and fallback redirects")
    print("w3id proposal validation passed.")


if __name__ == "__main__":
    main()
