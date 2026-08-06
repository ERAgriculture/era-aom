#!/usr/bin/env python3
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
REVIEW = ROOT / "review/livestock-v15"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


concepts = read(REVIEW / "authority_mapping_concepts.csv")
cohort = read(REVIEW / "authority_mapping_assertions.csv")
reviews = read(DATA / "approved_mapping_reviews.csv")
mappings = read(DATA / "mappings.csv")
assert len(concepts) == 105 and len(cohort) == len(reviews) == 383
assert Counter(row["decision"] for row in reviews) == {
    "retain_related_nondefinitional": 344,
    "remove_contradictory_mapping": 27,
    "retain_related_evidence_hold": 12,
}
assert Counter(row["target_scheme"] for row in reviews if row["publish"] == "false") == {
    "agrovoc": 11, "feedipedia": 8, "ncbi-taxonomy": 8,
}
published_keys = {(row["subject_id"], row["target_scheme"], row["target_uri"] or row["target_id"]) for row in mappings}
removed_keys = {(row["subject_id"], row["target_scheme"], row["target_uri"] or row["target_id"]) for row in reviews if row["publish"] == "false"}
assert not (published_keys & removed_keys)
retained = [row for row in reviews if row["publish"] == "true"]
assert all((row["subject_id"], row["target_scheme"], row["target_uri"] or row["target_id"]) in published_keys for row in retained)
assert all(row["definition_evidence_grade"] == "insufficient" and row["mapping_relation"] == "relatedMatch" for row in reviews)
assert not any("ilri" in value.casefold() for row in reviews for value in row.values())
print("Authority mapping review passed: 383 reviewed; 27 removed; 356 non-definitional related mappings retained")
