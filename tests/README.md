# Tests

Automated source-schema, referential-integrity, semantic, SHACL, and
round-trip tests will be added with normalized pilot data.

- `validate_pilot.R`: self-contained normalized-table integrity checks.
- `check_roundtrip.R`: private-workbook comparison; runs locally because
  workbook is not published.
- GitHub Actions parses JSON-LD/Turtle and executes SHACL against both schemes.
- `validate_livestock_inventory.py`: pins public AOM v2 identity and verifies
  private/restricted data remain excluded.
- `validate_livestock_staging.py`: validates normalized public-v2 staging,
  identity quarantine, hierarchy review queue, mappings, and manifest.
