#!/usr/bin/env python3
"""Validate ADR 0052 human acceptance record."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECOMMENDATIONS = ROOT / "review/data-model-v1"
ACCEPTANCE = ROOT / "review/data-model-v2"


def read_csv(directory: Path, name: str) -> list[dict[str, str]]:
    path = directory / name
    assert path.is_file(), f"Missing {path}"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


summary = json.loads((ACCEPTANCE / "acceptance_summary.json").read_text(encoding="utf-8"))
recommendations = read_csv(RECOMMENDATIONS, "recommendation_register.csv")
approvals = read_csv(ACCEPTANCE, "decision_approvals.csv")
field_issues = read_csv(RECOMMENDATIONS, "field_key_issues.csv")
lookups = read_csv(RECOMMENDATIONS, "lookup_binding_audit.csv")
units = read_csv(RECOMMENDATIONS, "unit_mapping_audit.csv")
consumer_differences = read_csv(RECOMMENDATIONS, "consumer_contract_diffs.csv")
consumers = read_csv(RECOMMENDATIONS, "consumer_contract_comparison.csv")
evidence = read_csv(ACCEPTANCE, "evidence_register.csv")

expected_ids = {f"DM-{number:02d}" for number in range(1, 13)}
assert len(approvals) == len(recommendations) == 12
assert {row["recommendation_id"] for row in approvals} == expected_ids
assert {row["recommendation_id"] for row in recommendations} == expected_ids
assert all(row["approval_status"] == "accepted" for row in approvals)
assert all(row["reviewer"] == "P. Steward" for row in approvals)
assert all(row["review_date"] == "2026-08-28" for row in approvals)
assert all(row["conditions_or_holds"] for row in approvals)
assert all(row["semantic_change_authorized"] == "no" for row in recommendations)

assert len(field_issues) == 21
assert Counter(row["exact_match"] for row in lookups) == {"yes": 42, "no": 41}
assert Counter(row["mapping_status"] for row in units) == {
    "conflicting-canonical-label": 2,
    "identity-label": 404,
    "normalized-label": 635,
    "unresolved": 64,
}
assert len(consumer_differences) == 44
product_contracts = {
    row["contract"]: row for row in consumers
    if row["contract"].startswith("published-era-compiled-")
}
assert len(product_contracts) == 2
assert {int(row["field_entries"]) for row in product_contracts.values()} == {138}

assert summary["adr_status"] == "Accepted"
assert summary["decision_count"] == summary["decisions_accepted"] == len(approvals)
assert summary["field_key_holds"] == len(field_issues)
assert summary["unmatched_lookup_holds"] == 41
assert summary["unresolved_unit_holds"] == 64
assert summary["conflicting_unit_rows"] == 2
assert summary["product_schema_columns_per_product"] == 138
assert summary["consumer_difference_records"] == len(consumer_differences)
assert summary["architecture_accepted"] is True
assert summary["source_disposition_authorized"] is True
assert summary["canonical_workbook_modified"] is False
assert summary["stable_keys_allocated"] is False
assert summary["registry_implementation_authorized"] is False
assert summary["shared_core_promotion_authorized"] is False
assert summary["existing_release_mutation_authorized"] is False
assert summary["new_release_authorized"] is False
assert summary["consumer_migration_authorized"] is False
assert summary["programme_issue_closure_authorized"] is False
assert len(evidence) == 5
assert all(row["claim_boundary"] for row in evidence)

print(
    "Validated ADR 0052 acceptance: 12 decisions, 21 field-key holds, "
    "41 lookup holds, 64 unresolved unit holds, and 44 consumer differences"
)
