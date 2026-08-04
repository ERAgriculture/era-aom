# Final taxon mapping review

Status: proposed. No mapping or hold approved here.

This pass covers every source label remaining after approved batches 1–4:
146 labels in one review artifact. Ninety-one labels have live-validated NCBI
candidate mappings; fifty-five remain explicit holds. Aggregate-only source
profiling indicates proposed mappings cover 150 source rows and holds cover 113
rows. Counts document review impact only and no source records are published.

Candidate composition:

- 75 exact current-name matches;
- 6 explicit synonym/current-name bindings;
- 6 explicit unspecified-species-to-genus bindings;
- 4 inherited wrong-ID replacements;
- 50 unresolved-name holds;
- 5 contextual/rank-syntax holds.

All 91 proposed identifiers, current names, and ranks were bulk-checked against
live NCBI Taxonomy on 2026-08-04. Generator first checks inherited IDs against
NCBI primary and secondary names, then uses exact NCBI name-status suggestions.
It never uses fuzzy matching and never approves decisions.

Holds include ambiguous common names, malformed names, misspellings without a
unique exact NCBI record, conflicting legacy IDs, and context-bearing labels
such as `Zea mays (baby)`. These require source correction or expert review;
they must not receive guessed IRIs.

WFO remains deferred. Approval should treat mapping candidates and holds as
separate governed outcomes.
