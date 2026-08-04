#!/usr/bin/env python3
"""Validate approved source-taxon bindings against a pinned NCBI snapshot."""
import argparse
import csv
import datetime as dt
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/livestock-staging/approved_semantic_value_bindings.csv"
SNAPSHOT = ROOT / "data/reference/ncbi_taxonomy_snapshot.csv"
NCBI = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
FIELDS = ["source_value", "target_uri", "target_label", "rank", "verified_on", "evidence"]


def approved_rows():
    with CONTRACT.open(encoding="utf-8", newline="") as handle:
        rows = [
            row for row in csv.DictReader(handle)
            if row["target_property"] == "aom:sourceTaxon"
            and row["binding_action"] == "map_to_external"
        ]
    assert len(rows) == 45
    assert not any(row["target_uri"] == "http://purl.obolibrary.org/obo/NCBITaxon_4146" for row in rows)
    assert not any(row["target_uri"] == "http://purl.obolibrary.org/obo/NCBITaxon_55119" for row in rows)
    assert len({row["source_value"].strip().casefold() for row in rows}) == len(rows)
    return rows


def live_snapshot(rows):
    ids = [row["target_uri"].rsplit("_", 1)[1] for row in rows]
    url = NCBI + "?db=taxonomy&id=" + ",".join(ids) + "&retmode=xml"
    with urllib.request.urlopen(url, timeout=30) as response:
        taxa = ET.fromstring(response.read()).findall("Taxon")
    assert len(taxa) == len(rows), "NCBI response does not preserve contract cardinality"
    today = dt.date.today().isoformat()
    result = []
    for row, requested_id, taxon in zip(rows, ids, taxa):
        returned_id = taxon.findtext("TaxId")
        current_name = taxon.findtext("ScientificName")
        rank = taxon.findtext("Rank")
        assert returned_id == requested_id, f"retired or redirected NCBI ID: {requested_id} -> {returned_id}"
        assert current_name == row["target_label"], (
            f"NCBI name mismatch for {row['source_value']}: "
            f"contract={row['target_label']!r}, live={current_name!r}"
        )
        result.append({
            "source_value": row["source_value"],
            "target_uri": row["target_uri"],
            "target_label": current_name,
            "rank": rank,
            "verified_on": today,
            "evidence": f"https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id={requested_id}",
        })
    return result


def validate_snapshot(rows):
    with SNAPSHOT.open(encoding="utf-8", newline="") as handle:
        snapshot = list(csv.DictReader(handle))
    assert list(snapshot[0]) == FIELDS
    assert len(snapshot) == len(rows)
    by_source = {row["source_value"]: row for row in snapshot}
    assert len(by_source) == len(snapshot)
    for row in rows:
        pinned = by_source[row["source_value"]]
        assert pinned["target_uri"] == row["target_uri"]
        assert pinned["target_label"] == row["target_label"]
        assert pinned["rank"] and pinned["verified_on"] and pinned["evidence"]
    return snapshot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="check current NCBI records")
    parser.add_argument("--refresh", action="store_true", help="replace snapshot after live validation")
    args = parser.parse_args()
    if args.refresh:
        args.live = True
    rows = approved_rows()
    pinned = validate_snapshot(rows) if SNAPSHOT.exists() and not args.refresh else None
    if args.live:
        current = live_snapshot(rows)
        if pinned is not None:
            for old, new in zip(pinned, current):
                assert (old["source_value"], old["target_uri"], old["target_label"], old["rank"]) == (
                    new["source_value"], new["target_uri"], new["target_label"], new["rank"]
                )
        if args.refresh:
            SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
            with SNAPSHOT.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
                writer.writeheader()
                writer.writerows(current)
    validate_snapshot(rows)
    print(f"NCBI taxon binding validation passed: {len(rows)} approved mappings")


if __name__ == "__main__":
    main()
