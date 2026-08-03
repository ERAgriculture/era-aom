# AOM Livestock v2 domain-review pack

Review queues and signed governance records generated from public normalized
staging. Approved decisions affect generated AOM only through normalized
governance tables and validated pull requests. Blank decisions remain pending.

## Review order

1. Inspect signed identity and hierarchy decisions already applied.
2. Review unresolved candidates in
   `02_missing_parent_candidates.csv`, grouped into batches below.
3. Record signed decisions in `03_review_decisions.csv`.
4. Apply approved decisions through separate validated pull request.

Evidence-backed recommendations for eight priority cases:
[`PRIORITY_RECOMMENDATIONS.md`](PRIORITY_RECOMMENDATIONS.md). Structured copy:
`04_priority_recommendations.csv`.

Approved cereal by-product batch evidence:
[`CEREAL_BYPRODUCT_RECOMMENDATIONS.md`](CEREAL_BYPRODUCT_RECOMMENDATIONS.md).

Approved legume by-product batch evidence:
[`LEGUME_BYPRODUCT_RECOMMENDATIONS.md`](LEGUME_BYPRODUCT_RECOMMENDATIONS.md).

Deferred concept-to-schema remodeling candidates:
`schema_remodeling_candidates.csv`.

Pending identity investigations: `identity_review_candidates.csv`.

## Missing-parent batches

| Batch | Candidate parents |
|---|---:|
| Farming System / livestock system | 4 |
| Management / Livestock Management | 89 |
| Management / Livestock Practices | 2 |
| Outcomes / Efficiency | 1 |
| Outcomes / Productivity | 15 |
| Outcomes / Social | 1 |
| Species / Animal | 2 |

196 child relations depend on these 234 candidate
parents. High priority means at least 10 affected children; medium means 3–9.
Priority measures impact, not semantic confidence.

## High-impact parent cases

| Case | Children | Candidate path | Same-label existing ID |
|---|---:|---|---|


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

- identifiers minted: 96;
- hierarchy changes applied: 397;
- semantic decisions applied: 122;
- private workbook content used: 0.
