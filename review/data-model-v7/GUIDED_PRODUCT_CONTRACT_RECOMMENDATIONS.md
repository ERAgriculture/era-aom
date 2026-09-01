# Guided product-contract recommendations

Status: **human decision pending**.

| ID | Recommendation | Conditions / holds |
|---|---|---|
| `PC-01` | Govern extraction schemas separately from released analytical product schemas. | No extraction or product schema changes until producer ownership and compatibility profiles are approved. |
| `PC-02` | Use one reviewed 138-field logical set with separate agronomy and livestock ordered product profiles. | Do not call current schema files identical or reorder either product without migration evidence. |
| `PC-03` | Require reviewed documentation or explicit deferral for every public product field. | Each field remains held until description, logical type, derivation, unit or basis, values, applicability, and lifecycle are reviewed. |
| `PC-04` | Review exact-name package dictionary rows as candidates, not authoritative mappings. | No description or datatype may be copied into product contracts without field-level review. |
| `PC-05` | Review trailing-space and punctuation variants through explicit governed aliases. | No automatic trim, punctuation normalization, rename, or identity assertion. |
| `PC-06` | Replace C1:Cn and T1:Tn patterns with explicit governed field aliases only after scope review. | C1-C14 and T1-T14 remain separately reviewable; no generated aliases are approved here. |
| `PC-07` | Publish release provenance and compatibility profile for each package data snapshot and dictionary. | No package snapshot may be treated as current release without a pinned producer release and checksum. |
| `PC-08` | Retain C14 and T14 as published-only holds pending release and derivation lineage. | No removal, package addition, or pattern mapping is approved. |
| `PC-09` | Retain B.Code as package-only hold pending provenance and compatibility or retirement decision. | No schema addition or package removal is approved. |
| `PC-10` | Review Irrig.Meth.T as dictionary-only legacy or retirement case. | No alias target or retirement is inferred from absence. |
| `PC-11` | Record physical and logical type, nullability, derivation, unit or basis, controlled values, applicability, lifecycle, and evidence per field. | Unknown properties remain explicit reviewed deferrals rather than guessed values. |
| `PC-12` | Require schema, data, package, dictionary, and documentation compatibility report before closure. | No release, migration, source edit, package edit, documentation edit, or issue closure is approved here. |

## Product-field cohort

- Total fields: 138
- Dispositions: `{"hold-author-missing-product-documentation": 7, "hold-published-only-release-lineage": 2, "hold-review-exact-dictionary-candidate": 101, "hold-review-explicit-alias-candidate": 2, "hold-review-pattern-expansion-candidate": 26}`
- Review artifact: `product_field_recommendations.json`

## Consumer-difference cohort

- Total differences: 44
- Dispositions: `{"hold-dictionary-only-retirement-review": 1, "hold-explicit-alias-definition-review": 2, "hold-package-only-release-provenance": 1, "hold-pattern-alias-definition-review": 2, "hold-published-only-release-provenance": 2, "hold-review-explicit-alias-candidate": 2, "hold-review-pattern-expansion-candidate": 26, "hold-undocumented-package-field": 8}`
- Review artifact: `consumer_difference_recommendations.json`
