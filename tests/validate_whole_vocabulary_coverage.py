#!/usr/bin/env python3

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review" / "whole-vocabulary-v1"


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def expect(value, message):
    if not value:
        raise AssertionError(message)


inventory = read_csv(ROOT / "inventory" / "workbook_sheets.csv")
coverage = read_csv(REVIEW / "resource_coverage.csv")
waves = read_csv(REVIEW / "migration_waves.csv")
authorities = read_csv(REVIEW / "authority_comparison.csv")
evidence = read_csv(REVIEW / "evidence_register.csv")
summary = json.loads((REVIEW / "coverage_summary.json").read_text(encoding="utf-8"))

inventory_sheets = [row["sheet"] for row in inventory]
coverage_sheets = [row["sheet"] for row in coverage]
expect(coverage_sheets == inventory_sheets, "Coverage must preserve every workbook sheet in source order")
expect(len(coverage_sheets) == len(set(coverage_sheets)) == 33, "Coverage must contain 33 unique sheets")

for row in coverage:
    expect(row["target_product"], f"Missing target product for {row['sheet']}")
    expect(row["owner_repository"], f"Missing owner repository for {row['sheet']}")
    expect(row["recommended_treatment"], f"Missing treatment for {row['sheet']}")
    expect(row["current_coverage_state"], f"Missing coverage state for {row['sheet']}")
    expect(row["migration_wave"], f"Missing migration wave for {row['sheet']}")
    expect(row["next_action"], f"Missing next action for {row['sheet']}")

by_sheet = {row["sheet"]: row for row in coverage}
expect(by_sheet["ssa_feedsdb"]["publication_disposition"] == "exclude", "Restricted SSA Feeds source must stay excluded")
expect(by_sheet["ssa_feedsdb"]["target_product"] == "excluded-restricted", "Restricted SSA Feeds source must have no public target")
expect(by_sheet["site_list"]["publication_disposition"] == "review", "Site list must remain under publication review")
expect(by_sheet["era_fields_v2"]["recommended_treatment"] == "schema-with-semantic-bindings", "Current field registry must remain schema, not concept scheme")
expect(by_sheet["AOM_diets"]["recommended_treatment"] == "working-subset-crosswalk", "AOM diets must not become an independent scheme")
expect(by_sheet["ani_diet"]["recommended_treatment"] == "operational-crosswalk-evidence", "Diet assignments must remain crosswalk evidence")
expect(by_sheet["vars_animals"]["current_coverage_state"] == "reconciled-not-normalized", "Animal varieties must remain visible as incomplete")
expect(by_sheet["AOM"]["current_coverage_state"] == "release-normalized-partially-reviewed", "Livestock release must not imply complete domain review")

normalized_sheets = [row["sheet"] for row in coverage if int(row["normalized_source_rows"]) > 0]
expect(normalized_sheets == ["prac", "out", "AOM"], "Normalized source-sheet coverage changed")
expect(summary["normalized_source_sheets"] == normalized_sheets, "Summary normalized-sheet list drifted")
expect(summary["normalized_source_rows"] == 2815, "Normalized source-row count changed")
expect(summary["workbook_sheets"] == 33, "Summary sheet count changed")
expect(summary["public_or_review_sheets"] == 24, "Public or review sheet count changed")
expect(summary["concept_scheme_sheets"] == 14, "Concept-scheme inventory count changed")
expect(summary["semantic_changes"] == 0, "Coverage review must remain recommendation-only")
expect(summary["allocated_identifiers"] == 0, "Coverage review must allocate no identifiers")
expect(summary["module_coverage"]["aom-core"]["normalized_source_sheet_count"] == 0, "Shared core must remain visibly unmigrated")
expect(summary["module_coverage"]["aom-crop"]["normalized_source_sheets"] == ["prac", "out"], "Crop pilot coverage changed")
expect(summary["module_coverage"]["aom-livestock"]["normalized_source_sheets"] == ["AOM"], "Livestock source coverage changed")

wave_ids = [row["wave"] for row in waves]
expect(wave_ids == sorted(wave_ids, key=lambda value: int(value.split("-", 1)[0])), "Migration waves must be ordered")
expect(len(wave_ids) == len(set(wave_ids)) == 8, "Migration waves must be unique")
expect({row["migration_wave"] for row in coverage if row["migration_wave"] != "hold"}.issubset(set(wave_ids)), "Coverage references unknown migration wave")
expect(len(authorities) == 7, "Authority comparison must retain seven boundaries")
expect(len(evidence) == 9, "Evidence register must retain nine claims")
expect(all(row["limitation"] for row in evidence), "Every evidence claim requires a limitation")

print("Whole-vocabulary coverage validation passed")
