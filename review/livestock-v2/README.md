# AOM Livestock v2 domain-review pack

Review input generated from public normalized staging. No decision in this
directory changes AOM.

## Review order

1. Resolve two blocking identity cases in `01_identity_collisions.csv`.
2. Review 234 missing-parent candidates in
   `02_missing_parent_candidates.csv`, grouped into batches below.
3. Record signed decisions in `03_review_decisions.csv`.
4. Apply approved decisions through separate validated pull request.

Evidence-backed recommendations for eight priority cases:
[`PRIORITY_RECOMMENDATIONS.md`](PRIORITY_RECOMMENDATIONS.md). Structured copy:
`04_priority_recommendations.csv`.

Deferred concept-to-schema remodeling candidates:
`schema_remodeling_candidates.csv`.

## Missing-parent batches

| Batch | Candidate parents |
|---|---:|
| Farming System / livestock system | 4 |
| Management / Livestock Management | 205 |
| Management / Livestock Practices | 2 |
| Outcomes / Efficiency | 1 |
| Outcomes / Productivity | 16 |
| Outcomes / Social | 1 |
| Species / Animal | 2 |

454 child relations depend on these 234 candidate
parents. High priority means at least 10 affected children; medium means 3–9.
Priority measures impact, not semantic confidence.

## High-impact parent cases

| Case | Children | Candidate path | Same-label existing ID |
|---|---:|---|---|
| PARENT-078 | 12 | Management/Livestock Management/Feed Characteristic/Feed Composition/Feed Ingredient/Crop Byproduct/Legume ByProducts/Soybean | AOM_001582 |
| PARENT-200 | 10 | Management/Livestock Management/Grazing Management | — |
| PARENT-227 | 12 | Outcomes/Productivity/Economics/Variable Cost/Management Activities | — |

## Allowed decisions

Identity collision:

- retain one ID and mint replacement;
- confirm distinct concepts and distinguish paths;
- merge/deprecate with replacement link;
- request more evidence.

Missing parent:

- mint explicit intermediate concept;
- map to existing concept;
- reparent affected children;
- reject proposed hierarchy;
- request more evidence.

Reviewer must supply identity, date, evidence, and rationale. Empty decision
fields are intentional. AI may summarize evidence but cannot approve.

## Safety

- identifiers minted: 3;
- hierarchy changes applied: 46;
- semantic decisions applied: 5;
- private workbook content used: 0.
