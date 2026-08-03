# Final missing-parent hierarchy recommendations

Decision record for the final 37 missing-parent cases spanning farming systems, livestock
management, livestock practices, economic/productivity/social outcomes, and animal species.

## Approved disposition

- Mint 26 governed concepts using `AOM_100993`–`AOM_101018`.
- Apply 11 reparenting decisions where reviewed concepts already express the intended
  hierarchy or the legacy path repeats the child concept.
- Resolve all 86 remaining affected child relations. Successful regeneration should leave
  zero `hierarchy_gaps.csv` records and zero unresolved missing-parent decisions.

## Modernized structure

- Reuse aquatic `reproducers`, terrestrial `barn rearing system`, Feed Management, Crop
  Fodders, Nitrogen Use Efficiency, Variable Cost, and Yield hierarchy concepts.
- Normalize management groupings for housing structure, animal health, abundance, pasture,
  fodder storage, and animal rearing stage.
- Normalize economic branches around opportunity cost, cost-per-asset, input and pest-control
  costs, private benefits, societal benefits, labor outcomes, and milk-fat outcomes.
- Replace adjective-only `Porcine` container with non-rank-asserting `Porcine animals`.

## Reproductive-status caution

Legacy `Parity` combines primiparous/multiparous classes with pregnancy trimesters. Several
descriptions appear shifted by one record: `Mixed` describes first trimester, `First
trimester` describes second, `Second trimester` describes final pregnancy stage, and `Third
trimester` describes postpartum. Batch uses broad `Reproductive status` for navigation and
queues all seven records for source-level correction and later separation into parity and
gestational-stage dimensions. No descriptions are silently rewritten.

## Controls

Canonical workbook audit found `AOM_100993`–`AOM_101018` unused on 2026-08-03.
Governance records retain reviewer, date, evidence, rationale, and affected child IDs.
