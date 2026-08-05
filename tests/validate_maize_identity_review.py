#!/usr/bin/env python3
"""Validate maize identity-review proposal completeness and safety boundaries."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/livestock-v4"
with (REVIEW / "maize_identity_review_recommendations.csv").open(
    encoding="utf-8", newline=""
) as handle:
    rows = list(csv.DictReader(handle))

assert len(rows) == 16
assert len({row["case_id"] for row in rows}) == 16
assert len({row["concept_id"] for row in rows}) == 16
assert all(row["approval_status"] == "proposed" for row in rows)
assert all(row["evidence"] and row["rationale"] for row in rows)
assert all("ilri" not in (row["evidence"] + row["rationale"]).casefold() for row in rows)
by_id = {row["concept_id"]: row for row in rows}
assert by_id["AOM_006072"]["proposed_disposition"] == "deprecate_replace"
assert by_id["AOM_006072"]["replacement_id"] == "AOM_001326"
assert by_id["AOM_001326"]["proposed_label"] == "Whole-crop maize silage"
assert by_id["AOM_001313"]["proposed_disposition"] == "hold"
assert by_id["AOM_000649"]["proposed_disposition"] == "retain_distinct"
assert sum(int(row["canonical_occurrences"]) for row in rows) == 36

text = (REVIEW / "MAIZE_IDENTITY_REVIEW.md").read_text()
assert "No identifier merge" in text
assert "Whole form` must not represent" in text
assert "https://feedipedia.review.fao.org/node/13883" in text
print("Maize identity review validation passed: 16 proposed cases, 36 occurrences")
