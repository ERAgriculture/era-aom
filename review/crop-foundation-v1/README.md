# Agricultural practice, outcome, and economic-variable foundation review

Recommendation-only review of canonical `prac`, `out`, and `out_econ`
resources. It does not authorize identifier allocation, source correction,
hierarchy change, mapping promotion, generated-data replacement, or release.

Decision proposal:
[ADR 0053](../../docs/decisions/0053-agricultural-practice-outcome-and-economic-variable-foundation.md).

Method:
[Agricultural practice and outcome foundation governance](../../docs/methods/agricultural-practice-outcome-foundation-governance.md).

## Review scope

- 196 `prac` rows;
- 116 `out` rows;
- 65 `out_econ` rows;
- 109 generated pilot hierarchy nodes;
- 405 generated `skos:broader` edges;
- current pilot and AOM staging identity collisions;
- official authority claim boundaries and exact-label candidates;
- shared-core design candidates and guided human-review gates.

## Files

- [`RECOMMENDATIONS.md`](RECOMMENDATIONS.md): human-readable findings and
  proposed architecture.
- [`source_snapshot.csv`](source_snapshot.csv): governed source counts and
  workbook checksum.
- [`source_row_dispositions.csv`](source_row_dispositions.csv): one disposition
  for every reviewed source row.
- [`hierarchy_node_review.csv`](hierarchy_node_review.csv): review of every
  generated intermediate pilot node.
- [`hierarchy_edge_review.csv`](hierarchy_edge_review.csv): review of every
  generated pilot hierarchy edge.
- [`identity_collision_audit.csv`](identity_collision_audit.csv): pilot-internal
  and source-to-AOM label collision evidence.
- [`source_quality_issues.csv`](source_quality_issues.csv): source, lifecycle,
  notation, sentinel, and definition issues.
- [`pilot_contract_audit.csv`](pilot_contract_audit.csv): promotion blockers in
  current pilot contract.
- [`authority_comparison.csv`](authority_comparison.csv): claim-level authority
  support and limitations.
- [`authority_label_candidates.csv`](authority_label_candidates.csv): exact-label
  AgrO, ENVO, and ChEBI candidates; none approved.
- [`shared_core_candidate_review.csv`](shared_core_candidate_review.csv):
  proposed shared semantic scaffold.
- [`guided_review.csv`](guided_review.csv): ordered human decisions.
- [`evidence_register.csv`](evidence_register.csv): evidence identifiers,
  locators, checksums, support, and claim boundaries.
- [`review_summary.json`](review_summary.json): machine-readable counts and
  implementation authorization flag.

## Rebuild

```bash
python3 scripts/build_crop_foundation_review.py \
  --workbook /path/to/era_master_sheet.xlsx \
  --agro-snapshot /path/to/agro.owl
python3 tests/validate_crop_foundation_review.py
```

AgrO input must be official `agro.owl` snapshot recorded in evidence register.
Committed review uses SHA-256
`d861a6fbf09e01fffcf4312dee29f20a15a1a4a65b2a7012e50c02f65a495b55`.
