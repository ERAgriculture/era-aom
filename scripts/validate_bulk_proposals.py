#!/usr/bin/env python3
"""Validate normalized public bulk-change proposal CSV files."""

import argparse
import csv
from pathlib import Path
from urllib.parse import urlparse

FIELDS = [
    "proposal_id", "change_type", "affected_concept_id", "preferred_label",
    "language", "module", "parent_concept_id", "target_uri",
    "mapping_relation", "rationale", "evidence_uri", "contributor_name",
    "contributor_affiliation",
]
CHANGE_TYPES = {
    "new_concept", "correction", "synonym", "translation", "hierarchy",
    "mapping", "duplicate", "deprecation",
}
MODULES = {"aom-crop", "aom-livestock", "aom-core", "uncertain"}
MAPPINGS = {"", "exactMatch", "closeMatch", "broadMatch", "narrowMatch", "relatedMatch"}


def is_http_uri(value):
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("--allow-empty", action="store_true")
    args = parser.parse_args()
    path = Path(args.csv_file)
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == FIELDS, "Bulk proposal columns/order differ from template"
        rows = list(reader)
    if not rows and not args.allow_empty:
        raise ValueError("Bulk proposal contains no rows")
    ids = [row["proposal_id"].strip() for row in rows]
    assert all(ids) and len(ids) == len(set(ids)), "proposal_id must be present and unique"
    for line, row in enumerate(rows, 2):
        assert row["change_type"] in CHANGE_TYPES, f"line {line}: invalid change_type"
        assert row["module"] in MODULES, f"line {line}: invalid module"
        assert row["mapping_relation"] in MAPPINGS, f"line {line}: invalid mapping_relation"
        assert row["preferred_label"].strip(), f"line {line}: preferred_label required"
        assert row["language"].strip(), f"line {line}: language required"
        assert row["rationale"].strip(), f"line {line}: rationale required"
        assert is_http_uri(row["evidence_uri"]), f"line {line}: HTTP(S) evidence_uri required"
        assert row["contributor_name"].strip(), f"line {line}: contributor_name required"
        assert row["contributor_affiliation"].strip(), f"line {line}: affiliation required"
        if row["change_type"] != "new_concept":
            assert row["affected_concept_id"].startswith("AOM_"), f"line {line}: affected AOM ID required"
        if row["change_type"] == "mapping":
            assert is_http_uri(row["target_uri"]), f"line {line}: target_uri required for mapping"
            assert row["mapping_relation"], f"line {line}: mapping_relation required"
    print(f"Validated {len(rows)} bulk proposals from {path}.")


if __name__ == "__main__":
    main()
