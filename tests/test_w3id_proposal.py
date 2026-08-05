#!/usr/bin/env python3
"""Test safe w3id proposal generation without external submission."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_w3id_proposal import build


CONFIG = {
    "approved": True,
    "namespace": "https://w3id.org/era-aom/",
    "html_base": "https://vocab.test.invalid/livestock",
    "artifact_base": "https://releases.test.invalid/era-aom/2026.1",
    "release": "2026.1",
    "maintainer_name": "ERA-AOM maintainers",
    "maintainer_github": "ERAgriculture",
}


htaccess, readme = build(CONFIG)
assert "R=303" in htaccess
assert 'Vary "Accept"' in htaccess
assert "aom-livestock.ttl" in htaccess
assert "aom-livestock.jsonld" in htaccess
assert "aom-livestock.rdf" in htaccess
assert "livestock/(.+)" in htaccess
assert "ERAgriculture" in readme

unsafe = dict(CONFIG, approved=False)
try:
    build(unsafe)
except ValueError as error:
    assert "approved=true" in str(error)
else:
    raise AssertionError("Unapproved configuration generated submission files")

placeholder = dict(CONFIG, html_base="https://vocab.example.org/livestock")
try:
    build(placeholder)
except ValueError as error:
    assert "example.org" in str(error)
else:
    raise AssertionError("Placeholder target generated submission files")

print("w3id proposal tests passed.")
