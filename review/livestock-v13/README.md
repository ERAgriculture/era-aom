# Canonical-workbook source cohort

Frozen cohort contains all 200 definition gaps routed to source-workbook review.
Evidence is ERA `era_master_sheet.xlsx`, AOM sheet, SHA-256
`f834c4f7837927774499eff4340c912784a3db10c2e19bd5d75a7f753df41438`.
Workbook has 2,503 rows and 2,501 identifiers. All cohort descriptions are blank;
definitions therefore state only governed identity or hierarchy role.

Current workbook paths differ from normalized queue paths for two concepts. Both
paths remain in frozen cohort for audit. No hierarchy mutation follows from this
definition review. Commercial names, ambiguous local labels, contradictory
categories, and compound component/process terms remain held until citable
evidence and structured assertions exist. No ILRI code participates.

Rebuild decisions with:

```sh
python scripts/build_workbook_source_scope_review.py
```

Do not run `--snapshot` after approval; option exists only to freeze a newly
reviewed cohort from an explicit AOM-sheet CSV export.
