#!/usr/bin/env python3
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "review/livestock-v9/feedipedia_definition_evidence.csv"

with PATH.open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))

assert len(rows) == 199
assert len({row["concept_id"] for row in rows}) == 199
assert len({row["feedipedia_url"] for row in rows}) == 182
assert all(row["feedipedia_url"].startswith(("https://www.feedipedia.org/", "https://feedipedia.org/")) for row in rows)
assert Counter(row["evidence_disposition"] for row in rows) == {
    "hold_scope_and_facet_review": 142,
    "hold_shared_page_scope_review": 32,
    "hold_source_warning": 10,
    "candidate_manual_definition_review": 8,
    "hold_category_not_concept": 5,
    "hold_retrieval_failed": 2,
}
assert all(
    row["evidence_disposition"] != "candidate_manual_definition_review"
    or row["lexical_relation"] == "lexically_exact"
    for row in rows
)
assert all(
    row["shared_mapping_count"] == "1"
    for row in rows if row["evidence_disposition"] == "candidate_manual_definition_review"
)
print("Feedipedia definition evidence validation passed")
