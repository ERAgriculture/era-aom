#!/usr/bin/env python3
"""Validate family-level feed-material harmonization review contracts."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "review/livestock-v4/maize_feed_material_harmonization.csv"

with SOURCE.open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))

assert len(rows) == 16
assert len({row["legacy_concept_id"] for row in rows}) == len(rows)
assert {row["feed_primary"] for row in rows} == {"Maize"}
assert all(row["status"] != "approved" for row in rows if row["identity_disposition"] != "retain_primary")

by_id = {row["legacy_concept_id"]: row for row in rows}
assert by_id["AOM_000648"]["identity_disposition"] == "retain_primary"
assert by_id["AOM_001313"]["component"] == "unresolved"
assert by_id["AOM_001313"]["status"] == "held"
assert by_id["AOM_006072"]["component"] == "unresolved"
assert by_id["AOM_006072"]["process_profile"] == "Ensiling"
assert by_id["AOM_000649"]["component"] == "Grain"

print("Feed-material harmonization validation passed: 16 maize review records")
