# Source-taxon governance addendum

Status: approved through ADR 0011.

Pipeline audit against an older private livestock release exposed 106 rows
across 23 source labels absent from the governed value contract. This addendum
records source-value decisions without publishing row-level evidence or private
counts by label.

Twenty-two labels receive NCBI Taxonomy bindings. Five replace unsafe legacy
identifiers: one wrong species, two genus-to-species rank errors, one
species-to-genus rank error, and one corrected misspelling. `Cynodon` binds to
plant genus `NCBITaxon_15437`; NCBI also contains a vertebrate homonym, rejected
because source field describes feed taxa.

`Pennisetum petiolare` remains `hold_ambiguous`. No exact NCBI record exists,
and mapping to genus would erase its explicit species epithet. Fuzzy matching
and target-label inference remain forbidden.
