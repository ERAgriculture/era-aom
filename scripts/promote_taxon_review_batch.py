#!/usr/bin/env python3
"""Promote an explicitly approved taxon review batch into value bindings."""
import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data/livestock-staging/approved_semantic_value_bindings.csv"
FIELDS = [
    "target_property", "source_value", "binding_action", "target_concept_id",
    "target_uri", "target_label", "value_class", "status", "reviewer",
    "review_date", "evidence", "rationale",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("batch", type=Path)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--review-date", required=True)
    parser.add_argument("--approve-all", action="store_true")
    args = parser.parse_args()
    if not args.approve_all:
        raise SystemExit("Refusing promotion without explicit --approve-all")
    batch_path = args.batch if args.batch.is_absolute() else ROOT / args.batch
    with batch_path.open(encoding="utf-8", newline="") as handle:
        batch = list(csv.DictReader(handle))
    with TARGET.open(encoding="utf-8", newline="") as handle:
        approved = list(csv.DictReader(handle))
    assert batch and all(row["status"] == "proposed-for-review" for row in batch)
    assert all(row["proposed_ncbi_taxon_id"] and row["accepted_name"] for row in batch)
    existing = {
        (row["target_property"], row["source_value"].strip().casefold())
        for row in approved
    }
    promoted = []
    for row in batch:
        key = ("aom:sourceTaxon", row["source_name"].strip().casefold())
        if key in existing:
            raise SystemExit(f"Already governed: {row['source_name']}")
        existing.add(key)
        promoted.append({
            "target_property": "aom:sourceTaxon",
            "source_value": row["source_name"],
            "binding_action": "map_to_external",
            "target_concept_id": "",
            "target_uri": "http://purl.obolibrary.org/obo/" + row["proposed_ncbi_taxon_id"],
            "target_label": row["accepted_name"],
            "value_class": "owl:Class",
            "status": "approved",
            "reviewer": args.reviewer,
            "review_date": args.review_date,
            "evidence": row["evidence"],
            "rationale": f"Approved {row['decision_action']}: {row['rationale']}",
        })
    with TARGET.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(approved + promoted)
    print(f"Promoted {len(promoted)} taxon decisions; total value bindings: {len(approved) + len(promoted)}")


if __name__ == "__main__":
    main()
