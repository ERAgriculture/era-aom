# ADR 0052 source-disposition recommendations

Status: recommendation-only; human decision pending.

## Guided decisions

### SD-01 — Non-overlapping duplicate logical fields

**Recommendation:** `accept-profile-consolidation`

Represent 13 duplicate table-field keys with disjoint extraction-round coverage as one stable logical field plus round-specific profiles.

**Condition or hold:** Preserve every canonical source row and round-specific property; allocate stable keys only during separately approved registry implementation.

### SD-02 — Overlapping duplicate logical fields

**Recommendation:** `hold-source-row-comparison`

Hold three duplicate keys whose source rows overlap in the same extraction round.

**Condition or hold:** Compare full row properties and source intent before merge, retirement, or profile assignment; overlap prevents automatic consolidation.

### SD-03 — Irrigation date-key conflict

**Recommendation:** `hold-source-key-correction`

Hold duplicate Irrig.Out.I.Date.Start rows because one carries Date End display identity in the same round.

**Condition or hold:** Source owner must confirm whether row 406 is an end-date key; never rename from display label alone.

### SD-04 — Blank field rows

**Recommendation:** `hold-metadata-or-removal-classification`

Hold three rows without field identity until classified as table metadata, intentional separator, or removable source artifact.

**Condition or hold:** Do not mint blank field identities or silently drop rows without reviewed source disposition.

### SD-05 — Missing table identity

**Recommendation:** `hold-table-assignment-or-retirement`

Hold source row 480 because populated field Time has no table identity and current generation drops it.

**Condition or hold:** Assign table only from source evidence or explicitly retire row; field label alone cannot establish table membership.

### SD-06 — Lookup pairs without registry candidates

**Recommendation:** `hold-add-field-or-retire-lookup`

Hold 39 lookup pairs with no candidate field key in the current registry.

**Condition or hold:** For each pair, add or restore a governed field definition from source evidence, or retire the lookup pair; never create a fuzzy binding.

### SD-07 — Lookup table-key candidates

**Recommendation:** `hold-table-key-realignment-review`

Hold Fert.Method.M.Source and Res.Out.M.Process despite one same-field candidate each in Res.Method.

**Condition or hold:** Confirm source table identity, value scope, and consumer use before key correction; candidate similarity is not approval.

### SD-08 — Stable field-to-value-set relationship

**Recommendation:** `accept-explicit-binding-policy`

Bind every approved value set to a stable field key and stable value-set key rather than table/field label coincidence.

**Condition or hold:** No unmatched pair is approved by this policy; all 41 remain held until source disposition.

## Disposition summary

| Cohort | Disposition | Cases |
|---|---|---:|
| Field keys | `consolidate-logical-field-with-round-profiles` | 13 |
| Field keys | `hold-assign-table-or-retire` | 1 |
| Field keys | `hold-classify-metadata-or-remove` | 3 |
| Field keys | `hold-overlapping-duplicate-source-rows` | 3 |
| Field keys | `hold-source-key-correction` | 1 |
| Lookup pairs | `hold-add-field-or-retire-lookup` | 39 |
| Lookup pairs | `hold-table-key-realignment-review` | 2 |

Complete row-level recommendations:

- [`field_key_disposition_recommendations.csv`](field_key_disposition_recommendations.csv)
- [`lookup_binding_disposition_recommendations.csv`](lookup_binding_disposition_recommendations.csv)

## Decision boundary

Accepting this cohort would approve 13 profile consolidations and retain
49 source-edit cases as holds. It would not edit source, allocate keys,
create bindings, regenerate schemas, publish releases, or migrate consumers.
