# AOM identifier policy

AOM concept identifiers are opaque persistent identifiers. Labels, hierarchy,
and scientific classification may change without changing identifier.

## Livestock allocation

- Syntax: `AOM_` followed by at least six decimal digits.
- Allocate strictly above highest numeric identifier found across current public
  release, canonical workbook, and committed registry.
- Never fill gaps, recycle deprecated identifiers, or derive identifiers from
  labels or hierarchy.
- Record allocation in
  `data/livestock-staging/livestock_id_registry.csv` before use.
- One pull request must add registry entry, approved concept record, generated
  artifacts, and validation together.
- Recheck allocation frontier immediately before merge to prevent concurrent
  allocation collision.

On 2026-08-03, public release and canonical workbook both ended at numeric
frontier `AOM_100848`. First governed allocation is `AOM_100849`.
