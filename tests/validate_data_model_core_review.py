#!/usr/bin/env python3

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review" / "data-model-v1"


def read_csv(name):
    with (REVIEW / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def expect(value, message):
    if not value:
        raise AssertionError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


required_files = {
    "RECOMMENDATIONS.md",
    "authority_comparison.csv",
    "consumer_contract_comparison.csv",
    "consumer_contract_diffs.csv",
    "evidence_register.csv",
    "field_key_issues.csv",
    "field_quality_metrics.csv",
    "lookup_binding_audit.csv",
    "recommendation_register.csv",
    "review_summary.json",
    "semantic_binding_scope.csv",
    "shared_core_boundary.csv",
    "source_contracts.csv",
    "unit_mapping_audit.csv",
}
expect(required_files.issubset({path.name for path in REVIEW.iterdir()}), "Data-model review files missing")

summary = json.loads((REVIEW / "review_summary.json").read_text(encoding="utf-8"))
sources = read_csv("source_contracts.csv")
issues = read_csv("field_key_issues.csv")
metrics = read_csv("field_quality_metrics.csv")
lookups = read_csv("lookup_binding_audit.csv")
units = read_csv("unit_mapping_audit.csv")
consumers = read_csv("consumer_contract_comparison.csv")
diffs = read_csv("consumer_contract_diffs.csv")
bindings = read_csv("semantic_binding_scope.csv")
boundaries = read_csv("shared_core_boundary.csv")
recommendations = read_csv("recommendation_register.csv")
authorities = read_csv("authority_comparison.csv")
evidence = read_csv("evidence_register.csv")

expect(summary["review"] == "data-model-v1", "Unexpected review identifier")
expect(summary["status"] == "recommendation-only", "Review must remain recommendation-only")
expect(summary["semantic_changes"] == 0, "Review must authorize no semantic change")
expect(summary["allocated_identifiers"] == 0, "Review must allocate no identifiers")
expect(summary["source_workbook_md5"] == "cb5d54c4bce97e23832b782cdebd8931", "Canonical workbook fingerprint changed")
expect(summary["published_vocab_workbook_md5"] == "dfb9129e4001227ca85d566f913aacee", "Published v2026.1 workbook fingerprint changed")

field_summary = summary["field_registry"]
expect(field_summary["workbook_rows"] == 754, "Workbook field-sheet count changed")
expect(field_summary["populated_field_rows"] == 751, "Populated field-row count changed")
expect(field_summary["valid_field_rows"] == 750, "Valid table-field row count changed")
expect(field_summary["unique_field_keys"] == 733, "Unique field-key count changed")
expect(field_summary["duplicate_field_keys"] == 17, "Duplicate field-key count changed")
expect(field_summary["issue_rows"] == 21, "Field issue count changed")
expect(field_summary["missing_descriptions"] == 270, "Missing-description count changed")
expect(field_summary["missing_datatypes"] == 117, "Missing-datatype count changed")
expect(field_summary["courageous_camel_fields"] == 324, "Fourth-round field count changed")

expect(len(sources) == len({row["source_id"] for row in sources}) == 12, "Source contract inventory changed")
expect(all(row["source_version"] for row in sources), "Every source contract needs version or checksum")

issue_counts = Counter(row["issue_type"] for row in issues)
expect(len(issues) == 21, "Field-key issue register changed")
expect(issue_counts["blank-field-row"] == 3, "Blank-field issue count changed")
expect(issue_counts["missing-table-key"] == 1, "Missing-table issue count changed")
expect(issue_counts["duplicate-logical-field-key"] == 16, "Duplicate logical-key count changed")
expect(issue_counts["duplicate-key-label-conflict"] == 1, "Key-label conflict count changed")
irrigation = [row for row in issues if row["issue_type"] == "duplicate-key-label-conflict"]
expect(irrigation[0]["Table"] == "Irrig.Out" and irrigation[0]["Field"] == "I.Date.Start", "Irrigation source conflict changed")
expect(all(row["source_rows"] and row["recommended_disposition"] for row in issues), "Every field issue needs traceable disposition")

metric_by_name = {row["metric"]: int(row["value"]) for row in metrics}
expect(metric_by_name["declared_extraction_rounds"] == 4, "Canonical extraction-round count changed")
expect(metric_by_name["published_model_extraction_rounds"] == 3, "Published extraction-round count changed")
expect(metric_by_name["published_model_allowed_value_fields"] == 43, "Published allowed-value field count changed")
expect(metric_by_name["published_model_allowed_values"] == 399, "Published allowed-value count changed")

lookup_counts = Counter(row["exact_match"] for row in lookups)
expect(len(lookups) == 83, "Lookup pair count changed")
expect(lookup_counts == {"yes": 42, "no": 41}, "Lookup exact-match coverage changed")
expect(all(row["source_rows"] and row["recommended_disposition"] for row in lookups), "Every lookup pair needs evidence and disposition")
expect(all(row["generator_disposition"] == "omitted-by-exact-key-join" for row in lookups if row["exact_match"] == "no"), "Unmatched lookup pairs must remain visible")

unit_counts = Counter(row["mapping_status"] for row in units)
expect(len(units) == 1105, "Unit mapping row count changed")
expect(unit_counts == {
    "conflicting-canonical-label": 2,
    "identity-label": 404,
    "normalized-label": 635,
    "unresolved": 64,
}, "Unit mapping status counts changed")
conflicting_units = [row for row in units if row["mapping_status"] == "conflicting-canonical-label"]
expect({row["raw_unit"] for row in conflicting_units} == {"ZMK/ha"}, "Unexpected conflicting raw unit")
expect({row["canonical_label"] for row in conflicting_units} == {"ZMK/ha", "ZMW/ha"}, "Currency-unit conflict changed")
expect(all(not row["canonical_unit_uri"] for row in units), "Review must not infer canonical unit URIs")
expect(all(row["external_mapping_status"] == "not-reviewed" for row in units), "Unit mappings must remain unreviewed")

expect(len(consumers) == 6, "Consumer contract comparison changed")
consumer_by_contract = {row["contract"]: row for row in consumers}
expect(int(consumer_by_contract["published-era-compiled-schema-2026.1"]["field_entries"]) == 138, "Agronomy product schema count changed")
expect(int(consumer_by_contract["published-era-compiled-ls-schema-2026.1"]["field_entries"]) == 138, "Livestock product schema count changed")
expect(int(consumer_by_contract["eragri-era-compiled-snapshot"]["field_entries"]) == 137, "Package data column count changed")
expect(int(consumer_by_contract["eragri-era-compiled-dictionary"]["field_entries"]) == 106, "Package dictionary field count changed")
expect(int(consumer_by_contract["published-era-compiled-schema-2026.1"]["populated_descriptions"]) == 0, "Agronomy schema descriptions changed")
expect(len(diffs) == 44, "Recorded consumer-difference count changed")
published_only = {row["identifier"] for row in diffs if row["comparison"] == "published-agronomy-schema-vs-eragri-data" and row["side"] == "published-only"}
package_only = {row["identifier"] for row in diffs if row["comparison"] == "published-agronomy-schema-vs-eragri-data" and row["side"] == "package-only"}
expect(published_only == {"C14", "T14"}, "Published-only product fields changed")
expect(package_only == {"B.Code"}, "Package-only product fields changed")

expect(len(bindings) == 13, "Structural semantic-binding count changed")
expect({row["domain_scope"] for row in bindings} == {"livestock-feed", "livestock-grazing-observation"}, "Unexpected binding scope")
expect(all(row["shared_core_disposition"] for row in bindings), "Every semantic binding needs core disposition")
expect(len(boundaries) == 8, "Shared-core boundary register changed")
expect(any(row["target_module"] == "aom-livestock" for row in boundaries), "Feed model must remain livestock scoped")

expect(len(recommendations) == 12, "Recommendation register changed")
expect(all(row["semantic_change_authorized"] == "no" for row in recommendations), "Recommendations must authorize no semantic changes")
expect(all(row["owner_repository"] and row["acceptance_evidence"] for row in recommendations), "Recommendations need owners and acceptance evidence")
expect(len(authorities) == 8, "Authority comparison changed")
expect(all(row["supports"] and row["does_not_support"] and row["evidence"] for row in authorities), "Authorities need explicit support and limitations")
expect(len(evidence) == 14, "Evidence register changed")
expect(all(row["claim"] and row["evidence"] and row["limitation"] for row in evidence), "Evidence claims need sources and limitations")

output_names = {
    "source_contracts": "source_contracts.csv",
    "field_key_issues": "field_key_issues.csv",
    "field_quality_metrics": "field_quality_metrics.csv",
    "lookup_binding_audit": "lookup_binding_audit.csv",
    "unit_mapping_audit": "unit_mapping_audit.csv",
    "consumer_contract_comparison": "consumer_contract_comparison.csv",
    "consumer_contract_diffs": "consumer_contract_diffs.csv",
    "semantic_binding_scope": "semantic_binding_scope.csv",
    "shared_core_boundary": "shared_core_boundary.csv",
    "recommendation_register": "recommendation_register.csv",
    "authority_comparison": "authority_comparison.csv",
    "evidence_register": "evidence_register.csv",
}
for key, filename in output_names.items():
    expect(summary["outputs"][f"{key}_sha256"] == sha256(REVIEW / filename), f"Output hash drifted: {filename}")

recommendation_text = (REVIEW / "RECOMMENDATIONS.md").read_text(encoding="utf-8")
adr_text = (ROOT / "docs" / "decisions" / "0052-data-model-registry-and-shared-core-contract.md").read_text(encoding="utf-8")
method_text = (ROOT / "docs" / "methods" / "data-model-and-shared-core-contract-review.md").read_text(encoding="utf-8")
for heading in ("## Authority comparison", "## Evidence"):
    expect(heading in recommendation_text, f"Recommendations missing {heading}")
    expect(heading in adr_text, f"ADR missing {heading}")
expect("Status: Proposed" in adr_text, "ADR must remain proposed")
expect("semantic_changes = 0L" in (ROOT / "scripts" / "build_data_model_core_review.R").read_text(encoding="utf-8"), "Builder must retain no-change declaration")
expect("Never infer dimensions" in method_text, "Method must prohibit inferred unit semantics")

print("Data-model and shared-core review validation passed")
