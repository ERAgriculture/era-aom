#!/usr/bin/env python3
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/livestock-v11/feedipedia_source_scope_review.csv"
DATA = ROOT / "data/livestock-staging"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


rows = read(REVIEW)
definitions = read(DATA / "approved_definition_enrichments.csv")
assert len(rows) == 193 and len({row["concept_id"] for row in rows}) == 193
assert Counter(row["status"] for row in rows) == {"approved": 101, "held": 92}
assert Counter(row["decision"] for row in rows) == {
    "approve_source_scope_definition": 101,
    "hold_identity_or_alias_review": 43,
    "hold_shared_page": 32,
    "hold_source_warning": 10,
    "hold_category_page": 5,
    "hold_retrieval_failure": 2,
}
approved = {row["concept_id"] for row in rows if row["status"] == "approved"}
generated = {
    row["concept_id"] for row in definitions
    if row["definition_method"] == "composed_from_reviewed_feedipedia_source_scope"
}
assert generated == approved
assert not any("ilri" in value.casefold() for row in rows for value in row.values())
print("Feedipedia source-scope validation passed: 101 approved; 92 held")
