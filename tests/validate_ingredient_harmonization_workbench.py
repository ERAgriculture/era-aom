#!/usr/bin/env python3
"""Validate full-inventory ingredient rule-workbench contracts."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/livestock-v5"


def read(name):
    with (REVIEW / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


inventory = read("ingredient_harmonization_inventory.csv")
rules = read("ingredient_rule_catalog.csv")
clusters = read("ingredient_signature_clusters.csv")
exceptions = read("ingredient_exception_queue.csv")
summary = json.loads((REVIEW / "ingredient_harmonization_summary.json").read_text())

assert len(inventory) == summary["ingredient_concepts"] == 1643
assert len({row["concept_id"] for row in inventory}) == 1643
assert len(rules) == summary["rules"] == 68
assert len({row["rule_id"] for row in rules}) == 68
assert len(clusters) == 7 and summary["unresolved_signature_clusters"] == 7
assert len(exceptions) == summary["unresolved_expert_exceptions"] == 19
assert summary["routes"] == {
    "batch_review": 10,
    "expert_exception": 25,
    "retain_atomic_candidate": 624,
    "rule_application_candidate": 984,
}
assert summary["safety"] == {
    "automatic_ontology_changes": 0,
    "legacy_ids_preserved": True,
    "ilri_identifiers_used": False,
}
assert all(row["status"] == "proposed-not-applied" for row in inventory)
assert all(row["approval_state"] in {"proposed", "held"} for row in rules)
assert not any("ilri" in field.casefold() for row in inventory for field in row)
assert not any("ilri" in value.casefold() for row in inventory for value in row.values())

by_id = {row["concept_id"]: row for row in inventory}
assert by_id["AOM_001326"]["process_candidates"] == "Ensiling"
assert by_id["AOM_006072"]["governance_state"] == "approved_deprecated"
assert by_id["AOM_001313"]["review_route"] == "expert_exception"
assert "whole may mean" in by_id["AOM_001313"]["exception_reason"]
assert not any(
    {"AOM_001326", "AOM_006072"} <= set(row["concept_ids"].split(";"))
    for row in clusters
)
assert "AOM_006072" not in {row["concept_id"] for row in exceptions}
assert by_id["AOM_006500"]["process_candidates"] == "Boiling;Drying;Grinding;Dehulling;Soaking"
assert by_id["AOM_006108"]["source_identity_candidate"] == "common bean"
assert by_id["AOM_001313"]["governance_state"] == "approved_model_resolution"
assert by_id["AOM_001616"]["source_identity_candidate"] == "blood"
assert not by_id["AOM_001616"]["component_candidates"]
assert by_id["AOM_001333"]["source_identity_candidate"] == "oil"
assert not by_id["AOM_001333"]["form_candidates"]
print(
    f"Ingredient harmonization workbench validation passed: {len(inventory)} concepts, "
    f"{len(rules)} rules, {len(exceptions)} unresolved exceptions"
)
