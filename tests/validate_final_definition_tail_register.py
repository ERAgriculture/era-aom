#!/usr/bin/env python3
"""Validate complete unresolved-tail coverage and safe routing."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/livestock-v20"


def read(name):
    with (REVIEW / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


cohort = read("final_definition_tail_cohort.csv")
rows = read("final_definition_tail_register.csv")
summary = json.loads((REVIEW / "final_definition_tail_summary.json").read_text())
assert len(cohort) == len(rows) == summary["cohort_size"] == 109
assert {r["concept_id"] for r in cohort} == {r["concept_id"] for r in rows}
assert len({r["concept_id"] for r in rows}) == 109
assert all(r["automation_eligible"] == "false" and r["proposed_status"] == "held" for r in rows)
assert all(r["resolution_gate"] and r["required_action"] and r["review_lane"] for r in rows)
assert set(summary["by_remediation_track"]) == {
    "authority_repair", "commercial_product", "identity_consolidation",
    "identity_repair", "local_term", "material_scope", "semantic_model",
}
assert sum(summary["by_remediation_track"].values()) == 109
assert summary["automation_eligible"] == 0 and summary["proposed_held"] == 109
assert any(r["candidate_related_ids"] for r in rows if r["remediation_track"] == "identity_consolidation")
print("Final definition-tail register passed: 109/109 routed; zero unsafe auto-approvals")
