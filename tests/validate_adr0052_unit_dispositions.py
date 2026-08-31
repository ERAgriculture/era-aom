#!/usr/bin/env python3
"""Validate recommendation-only ADR 0052 unit dispositions."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "review/data-model-v1/unit_mapping_audit.csv"
REVIEW = ROOT / "review/data-model-v5"
SOURCE_SHA256 = "29fbec8fc3fb2b2153532bcbfdaea8f32b1918b3b397e445f33aa1c192063b8c"
EXPECTED_COUNTS = {
    "hold-basis-or-qualifier-model": 11,
    "hold-currency-and-basis-review": 3,
    "hold-currency-effective-context": 2,
    "hold-missing-value-source-correction": 2,
    "hold-non-unit-source-correction": 21,
    "hold-ratio-decomposition": 16,
    "hold-source-fragment-correction": 3,
    "hold-symbol-case-and-context-review": 8,
}


def read_json(name: str) -> object:
    path = REVIEW / name
    assert path.is_file(), f"Missing {path}"
    return json.loads(path.read_text(encoding="utf-8"))


assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256
with SOURCE.open(encoding="utf-8", newline="") as handle:
    source_rows = list(csv.DictReader(handle))
held_source = [
    row
    for row in source_rows
    if row["mapping_status"] in {"unresolved", "conflicting-canonical-label"}
]

cases = read_json("unit_disposition_recommendations.json")
guided = read_json("guided_decision_recommendations.json")
authorities = read_json("authority_comparison.json")
evidence = read_json("evidence_register.json")
summary = read_json("disposition_summary.json")
assert isinstance(cases, list)
assert isinstance(guided, list)
assert isinstance(authorities, list)
assert isinstance(evidence, list)
assert isinstance(summary, dict)

assert len(held_source) == len(cases) == 66
assert Counter(row["mapping_status"] for row in held_source) == {
    "conflicting-canonical-label": 2,
    "unresolved": 64,
}
assert {
    (int(row["source_row"]), row["raw_unit"], row["canonical_label"], row["mapping_status"])
    for row in held_source
} == {
    (
        int(case["source_row"]),
        case["raw_unit"],
        case["canonical_label"],
        case["source_mapping_status"],
    )
    for case in cases
}
assert Counter(case["recommended_disposition"] for case in cases) == EXPECTED_COUNTS
assert all(case["recommendation_status"] == "proposed" for case in cases)
assert all(case["required_evidence"] and case["authority_route"] for case in cases)
for field in (
    "canonical_unit_uri",
    "quantity_kind_uri",
    "conversion_rule",
    "human_decision",
    "reviewer",
    "review_date",
    "decision_note",
):
    assert all(not case[field] for case in cases)

assert len(guided) == 12
assert {decision["review_id"] for decision in guided} == {
    f"UD-{number:02d}" for number in range(1, 13)
}
assert all(decision["conditions_or_holds"] for decision in guided)
assert len(authorities) == 5
assert {row["authority"] for row in authorities} == {
    "Bank of Zambia 2012 rebasing guidance",
    "ERA ADR 0007 canonical workbook policy",
    "ISO 4217",
    "QUDT 3.1.10",
    "UCUM 2.2",
}
assert all(row["url"] and row["supports"] and row["limitation"] for row in authorities)
assert len(evidence) == 6
assert all(row["supports"] and row["claim_boundary"] for row in evidence)

assert summary["status"] == "recommendation-only"
assert summary["review_date"] == "2026-08-29"
assert summary["source_audit_sha256"] == SOURCE_SHA256
assert summary["guided_decision_count"] == 12
assert summary["held_case_count"] == 66
assert summary["unresolved_case_count"] == 64
assert summary["conflicting_case_count"] == 2
assert summary["disposition_counts"] == EXPECTED_COUNTS
assert summary["human_decision_recorded"] is False
for key in (
    "canonical_unit_mappings_created",
    "quantity_kind_mappings_created",
    "conversion_rules_created",
    "source_workbook_modified",
    "schema_regeneration_authorized",
    "release_authorized",
    "consumer_migration_authorized",
    "spreadsheet_artifact_authored",
):
    assert summary[key] is False

readme = (REVIEW / "README.md").read_text(encoding="utf-8")
method = (REVIEW / "METHOD.md").read_text(encoding="utf-8")
guided_markdown = (REVIEW / "GUIDED_UNIT_RECOMMENDATIONS.md").read_text(encoding="utf-8")
assert "Every row remains held" in readme
assert SOURCE_SHA256 in method
assert "human decision pending" in guided_markdown
assert guided_markdown.count("| `UNIT-") == 66

adr = (ROOT / "docs/decisions/0052-data-model-registry-and-shared-core-contract.md").read_text(encoding="utf-8")
assert "data-model-v5/README.md" in adr
assert "64 unresolved unit rows and both conflicting" in " ".join(adr.split())

print("Validated ADR 0052 unit dispositions: 12 decisions and 66 held cases")
