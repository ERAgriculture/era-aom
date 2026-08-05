#!/usr/bin/env python3
"""Validate deterministic feed identity audit and critical candidate coverage."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/livestock-v4"


def read(name):
    with (REVIEW / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


lexical = read("feed_lexical_identity_candidates.csv")
external = read("feed_external_granularity_candidates.csv")
assert len(lexical) == 16
assert len(external) == 345
assert all(row["status"] == "review-required" for row in lexical)
assert all(row["status"] == "granularity-review-required" for row in external)
assert any({"AOM_000564", "AOM_001884"} <= set(row["concept_ids"].split(";"))
           for row in lexical)
assert any(row["mapping_system"] == "ilri_code" and row["mapping_value"] == "FEED0023"
           and {"AOM_000648", "AOM_000649"} <= set(row["concept_ids"].split(";"))
           for row in external)
assert any(row["mapping_system"] == "Feedipedia" and "AOM_001313" in row["concept_ids"].split(";")
           for row in external)
release = json.loads((ROOT / "config/releases/2026.1-rc.1.json").read_text())
baseline = release["content_baseline"]
assert baseline["era_workbook_snapshot_modified"] == "2026-07-09T11:29:11+03:00"
assert baseline["era_workbook_rows"] == 2503
assert baseline["aom_id_mismatches"] == 0
assert baseline["hierarchy_level_mismatches"] == 0
assert baseline["private_workbook_fingerprint_published"] is False
print(f"Feed identity audit validation passed: {len(lexical)} lexical and {len(external)} external groups")
