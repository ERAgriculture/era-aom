#!/usr/bin/env python3
"""Validate complete, bounded material-scope closure."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


register = [r for r in read(ROOT / "review/livestock-v20/final_definition_tail_register.csv")
            if r["remediation_track"] == "material_scope"]
review = read(ROOT / "review/livestock-v21/material_scope_review.csv")
assert len(register) == len(review) == 40
assert {r["concept_id"] for r in register} == {r["concept_id"] for r in review}
assert all(r["decision"] == "approve_bounded_workbook_material_scope" and r["status"] == "approved" for r in review)
assert all(r["component_scope"] == r["process_scope"] == "unspecified" for r in review)
assert all(r["governed_source_identity"] and r["evidence"] and r["rationale"] for r in review)
print("Material-scope closure passed: 40/40 approved with bounded semantics")
