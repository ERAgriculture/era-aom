# Ingredient descriptor lifecycle implementation

Status: implementation of accepted [ADR 0046](../../docs/decisions/0046-ingredient-descriptor-lifecycle-and-browser-deprecation.md).

This cohort implements five accepted row dispositions from
[`review/livestock-v32`](../livestock-v32/RECOMMENDATIONS.md). It changes no
published identifier and mints no concept. It:

- removes approved retirements from active browse hierarchy while preserving
  stable cards, labels, notation, definitions, mappings, and evidence;
- emits both custom lifecycle status and boolean `owl:deprecated true`;
- serializes governed `skos:historyNote` values;
- sets explicit searchable-deprecated browser policy;
- corrects ingredient source-label, component-descriptor, taxon, proportion,
  and acquisition-source contracts;
- leaves `era-data-pipeline` contract migration to its separately reviewed PR.

## Authority comparison

| Authority | Implementation use | Boundary |
|---|---|---|
| W3C OWL 2 | `owl:deprecated true` for interoperable retirement. | Does not govern browse-edge removal. |
| W3C SKOS | Stable labels, notation, definitions, mappings, and history notes. | Does not define lifecycle state. |
| Skosmos 3.3 | Explicit `skosmos:showDeprecated true` preserves exact-search compatibility and card warning. | Hierarchy query still requires governed edge suppression. |
| QUDT 3.5 | `DimensionlessRatio`, ratio units, and quantity-kind metadata for ingredient proportion. | ERA still must declare diet-composition denominator basis. |
| ADR 0046 | Governs lifecycle, browser behavior, and property scope. | Pipeline migration remains separate. |

## Evidence

See [`evidence_register.csv`](evidence_register.csv) and
[`ingredient_descriptor_implementation_register.csv`](ingredient_descriptor_implementation_register.csv).
Machine acceptance lives in
[`tests/validate_ingredient_descriptor_lifecycle_implementation.py`](../../tests/validate_ingredient_descriptor_lifecycle_implementation.py).
