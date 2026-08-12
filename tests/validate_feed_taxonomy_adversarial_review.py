#!/usr/bin/env python3
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review" / "livestock-v29" / "feed_taxonomy_adversarial_review.csv"
SUMMARY = ROOT / "review" / "livestock-v29" / "feed_taxonomy_adversarial_summary.json"

with REVIEW.open(newline="") as handle:
    rows = list(csv.DictReader(handle))
by_id = {row["concept_id"]: row for row in rows}
assert len(by_id) == len(rows)
assert all(row["recommended_action"] and row["recommended_axis"] and row["rationale"] for row in rows)

summary = json.loads(SUMMARY.read_text())
assert summary["reviewed_concepts"] == len(rows)
assert summary["feed_material_direct_children"] == 19
assert summary["supplement_descendants"] == 94
assert summary["other_ingredients_descendants"] == 54
assert summary["organic_acid_descendants"] == 1
assert summary["explicit_holds"] > 0

for concept_id in {
    "AOM_000531", "AOM_000532", "AOM_000533", "AOM_000534", "AOM_000535",
    "AOM_006389", "AOM_000736", "AOM_000781", "AOM_006334", "AOM_001497",
    "AOM_001579", "AOM_101019", "AOM_101068", "AOM_101085", "AOM_101104",
    "AOM_101109", "AOM_101110", "AOM_101115", "AOM_101130",
}:
    assert concept_id in by_id

assert by_id["AOM_000531"]["recommended_action"] == "deprecate-and-remove-from-browse"
assert by_id["AOM_000736"]["recommended_action"] == "retire-and-replace"
assert by_id["AOM_000781"]["recommended_action"] == "retire-after-disposition"
assert by_id["AOM_001579"]["recommended_axis"] == "feed additive"
assert by_id["AOM_001497"]["recommended_target"] == "Megalac under rumen-protected fat feed materials"
assert by_id["AOM_101068"]["recommended_action"] == "retire-from-feed-processes"
assert by_id["AOM_101104"]["recommended_target"] == "Cereal milling fractions under Feed material components"
assert by_id["AOM_101109"]["recommended_action"] == "retire"
assert by_id["AOM_101110"]["recommended_axis"] == "component-retention state"
assert by_id["AOM_101115"]["recommended_target"] == "Native-component retention states under Feed Chemical Composition"
assert by_id["AOM_101130"]["recommended_target"] == "Feed component separation processes"

print(f"Validated {len(rows)} feed-taxonomy adversarial-review dispositions.")
