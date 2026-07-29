# Workbook inventory

Phase 0 records sheet dimensions, column types, blank counts, duplicate header
positions, and candidate keys. It does not publish workbook cell values.

Source checksum, modification time, and file size are written only to ignored
local output. Keep that private fingerprint with migration records.

Regenerate:

```sh
Rscript scripts/inventory_workbook.R /path/to/era_master_sheet.xlsx inventory/generated
```

`sheet_disposition.csv` contains proposed classifications. Review required
before any sheet export.
