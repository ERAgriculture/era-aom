#!/usr/bin/env python3
"""Build deterministic feed-identity review candidates without merging concepts."""
import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/livestock-staging/legacy_records.csv"
OUT = ROOT / "review/livestock-v4"

EMPTY = {"", "na", "no match", "no match in aom", "false"}
EXTERNAL_FIELDS = ("ilri_code", "Feedipedia", "CPC_Code_Product")


def normalized(value):
    value = value.casefold().replace("corn", "maize")
    replacements = {
        r"\b(milled|meal|grounded)\b": "ground",
        r"\b(silage|ensilation)\b": "ensiled",
        r"\btoasted\b": "roasted",
        r"\bcooked\b": "heated",
    }
    for pattern, replacement in replacements.items():
        value = re.sub(pattern, replacement, value)
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value)).strip()


def clean_external(value):
    value = value.strip()
    return "" if value.casefold() in EMPTY else value


with SOURCE.open(encoding="utf-8", newline="") as handle:
    rows = [row for row in csv.DictReader(handle)
            if row["AOM"] and row["L5"] == "Feed Ingredient"]

by_id = {row["AOM"]: row for row in rows}
lexical = defaultdict(set)
for row in rows:
    for label in [row["Edge_Value"], *row["Synonym"].split(";")]:
        key = normalized(label)
        if key:
            lexical[key].add(row["AOM"])

lexical_rows = []
for key, concept_ids in sorted(lexical.items()):
    if len(concept_ids) < 2:
        continue
    ids = sorted(concept_ids)
    lexical_rows.append({
        "collision_key": key,
        "concept_ids": ";".join(ids),
        "preferred_labels": ";".join(by_id[value]["Edge_Value"] for value in ids),
        "candidate_count": len(ids),
        "status": "review-required",
        "recommended_action": "Compare definitions, hierarchy, occurrences, and external identifiers; retain one ID only when identity is confirmed.",
    })

external = defaultdict(set)
for row in rows:
    for field in EXTERNAL_FIELDS:
        value = clean_external(row[field])
        if value:
            external[(field, value)].add(row["AOM"])

external_rows = []
for (field, value), concept_ids in sorted(external.items()):
    if len(concept_ids) < 2:
        continue
    ids = sorted(concept_ids)
    external_rows.append({
        "mapping_system": field,
        "mapping_value": value,
        "concept_ids": ";".join(ids),
        "preferred_labels": ";".join(by_id[item]["Edge_Value"] for item in ids),
        "candidate_count": len(ids),
        "status": "granularity-review-required",
        "recommended_action": "Determine whether mapping identifies primary feed, component, processed material, or broad source; do not infer concept identity from shared code.",
    })

OUT.mkdir(parents=True, exist_ok=True)
for name, records in {
    "feed_lexical_identity_candidates.csv": lexical_rows,
    "feed_external_granularity_candidates.csv": external_rows,
}.items():
    path = OUT / name
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)

print(
    f"Audited {len(rows)} feed concepts: {len(lexical_rows)} lexical collision "
    f"groups; {len(external_rows)} shared-identifier groups."
)
