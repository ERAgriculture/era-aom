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

Livestock release reconciliation:

- [`AOM_LIVESTOCK_RECONCILIATION.md`](AOM_LIVESTOCK_RECONCILIATION.md)
- `livestock_release_manifest.csv`
- `livestock_reconciliation.json`

Regenerate reconciliation from separately downloaded public AOM v2 CSV and
private workbook:

```sh
Rscript scripts/reconcile_livestock_release.R \
  /path/to/AOM-v2.csv /path/to/era_master_sheet.xlsx
```
