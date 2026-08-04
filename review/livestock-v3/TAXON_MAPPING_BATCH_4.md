# Taxon mapping review — batch 4

Status: proposed. No mapping approved here.

Batch expands review to eighty high-impact unresolved source names in one
pass. Every proposed identifier, current name, and rank was checked together
against live NCBI Taxonomy on 2026-08-04 after integrity controls from ADR 0008
were established.

Composition:

- 55 exact current-name bindings;
- 11 explicit synonym/current-name bindings;
- 5 wrong-ID replacements;
- 5 explicit `spp`-to-genus bindings without species inference;
- 3 source misspelling corrections;
- 1 retired-ID replacement;
- 70 species, 8 genera, and 2 subspecies.

Notable collisions include `Coffea`, `Linum usitatissimum`, `Vitellaria
paradoxa`, `Brachiaria ruziziensis`, and `Macadamia integrifolia`. Original
labels remain preserved. Spelling and synonym decisions are enumerated
exceptions, never general fuzzy-matching rules. Algal and animal taxa receive
no WFO assertion; all WFO reconciliation remains deferred.

Approval requires reviewing exception rows and confirming source labels
represent organism identity rather than material text.
