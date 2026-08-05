# Ingredient-component value facet recommendations

## Status

Classification outcomes approved through ADR 0012. No row is approved concept
mapping governance. No concept IRI, new identifier, or canonical assertion is
created by this review pack.

## Evidence boundary

Aggregate-only pipeline profiling supplied 83 distinct normalized descriptors.
Committed candidate table contains labels only. Source counts, records, study
codes, treatment identifiers, and private ingredient rows are excluded.

## Result

| Proposed primary disposition | Values |
|---|---:|
| Anatomical part | 30 |
| Composite descriptor | 28 |
| Product role | 11 |
| Physical form | 6 |
| Chemical constituent | 5 |
| Unresolved | 3 |
| Processing method as sole primary facet | 0 |

Processing appears as secondary facet in derived-product descriptors rather
than as a standalone operation label. This supports preserving raw source text
and decomposing compounds instead of forcing each value into one property.

Confidence records classification clarity, not mapping confidence: 53 high, 26
medium, and 4 low. Exact AOM label matches do not increase confidence because
existing matches may occupy incompatible hierarchy branches.

## Review rules

- `review_single`: verify facet, definition, hierarchy, material context, and
  candidate identity before any mapping.
- `decompose`: create two or more reviewed facet assertions; never map compound
  string as one opaque part concept.
- `hold`: retain `aom:legacyComponentDescriptor` only until source evidence
  establishes meaning.
- Material identity remains separate from facets. A label naming whole feed
  material must not be converted into anatomical part merely because source
  column was called Ingredient part.
- Chemical measurements remain SOSA/QUDT observations. Constituent facet states
  identity only, never concentration.

## Approval path

1. Reviewer confirms or changes proposed facet/disposition.
2. Reviewer records evidence and rationale for each approved decision.
3. AOM governance maps only unambiguous atomic values to reviewed concepts.
4. Composite values receive explicit decompositions.
5. Pipeline pins approved contract and validates source-value coverage.

Machine-readable proposals:
`ingredient_component_value_candidates.csv`. Validation schema:
`../../schemas/json/ingredient-component-value-candidate.schema.json`.
Approved classification contract:
`../../data/livestock-staging/approved_ingredient_component_classifications.csv`.
