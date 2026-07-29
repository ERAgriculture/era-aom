#!/usr/bin/env python3

import json
import sys
from pathlib import Path


path = Path(sys.argv[1] if len(sys.argv) > 1 else "inventory/livestock_reconciliation.json")
report = json.loads(path.read_text(encoding="utf-8"))


def expect(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


public = report["public_release"]
alignment = report["alignment"]
identity = report["identity_integrity"]
privacy = report["privacy"]

expect(public["doi"] == "10.7910/DVN/75E7HV", "Unexpected DOI")
expect(public["version"] == "2.0", "Unexpected release version")
expect(
    public["md5"] == "9dd9b11879805f22c18ec7e0173f80ba",
    "Public file checksum changed",
)
expect(public["rows"] == 2503, "Public row count changed")
expect(public["meaningful_columns"] == 38, "Column count changed")
expect(alignment["aom_id_mismatches"] == 0, "AOM IDs drifted")
expect(alignment["hierarchy_level_mismatches"] == 0, "Hierarchy drifted")
expect(identity["duplicate_aom_ids"] == "AOM_006275", "Duplicate-ID case changed")
expect(not privacy["workbook_path_published"], "Private workbook path exposed")
expect(
    not privacy["workbook_fingerprint_published"],
    "Private workbook fingerprint exposed",
)
expect(not privacy["ssa_feedsdb_values_published"], "Restricted SSA Feeds values exposed")

print("Livestock inventory validation passed")
