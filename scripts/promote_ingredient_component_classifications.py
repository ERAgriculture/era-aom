#!/usr/bin/env python3
"""Promote reviewed ingredient-component classifications without minting mappings."""
import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data/livestock-staging/approved_ingredient_component_classifications.csv"
FIELDS = [
    "source_value", "normalized_value", "primary_facet", "secondary_facets",
    "disposition", "confidence", "status", "reviewer", "review_date",
    "evidence", "rationale",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--review-date", required=True)
    parser.add_argument("--approve-all", action="store_true")
    args = parser.parse_args()
    if not args.approve_all:
        raise SystemExit("Refusing promotion without explicit --approve-all")
    source = args.source if args.source.is_absolute() else ROOT / args.source
    with source.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 83
    assert all(row["status"] == "proposed-for-review" for row in rows)
    assert all(not row["reviewer"] and not row["review_date"] for row in rows)
    assert len({row["normalized_value"] for row in rows}) == len(rows)
    promoted = [{
        "source_value": row["source_value"],
        "normalized_value": row["normalized_value"],
        "primary_facet": row["proposed_facet"],
        "secondary_facets": row["secondary_facets"],
        "disposition": row["disposition"],
        "confidence": row["confidence"],
        "status": "approved-classification",
        "reviewer": args.reviewer,
        "review_date": args.review_date,
        "evidence": row["evidence"],
        "rationale": row["rationale"],
    } for row in rows]
    with TARGET.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(promoted)
    print(f"Promoted {len(promoted)} ingredient-component classifications; zero mappings minted")


if __name__ == "__main__":
    main()
