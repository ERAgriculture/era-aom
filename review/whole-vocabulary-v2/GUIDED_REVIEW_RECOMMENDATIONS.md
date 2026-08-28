# ADR 0051 guided-review recommendations

Status: recommendation-only; human decision pending.

## Guided decisions

### GV-01 — AOM product and module boundary

**Recommendation:** `accept`

Retain AOM as the umbrella product and preserve separately governed core, crop, livestock, and mapping products.

**Condition or hold:** No concept enters shared core from lexical overlap, convenience, or one-domain use; require reviewed crop-and-livestock identity and scope evidence.

### GV-02 — Function-first resource routing

**Recommendation:** `accept`

Route domain concepts, schemas, code lists, mappings, catalog metadata, operational resources, and excluded evidence to distinct governed products.

**Condition or hold:** Approval of a sheet route does not approve row identity, hierarchy, mapping, publication, or one-row-one-concept conversion; revise prac, out, and out_econ from crop-only routing to cross-domain row routing under accepted ADR 0053.

### GV-03 — Data-model and semantic-binding boundary

**Recommendation:** `accept-with-conditions`

Route field, profile, value-set, unit, product-schema, and compatibility contracts through their governed registries with explicit AOM bindings.

**Condition or hold:** Apply accepted ADR 0052 boundaries; field records and lookup values do not become aom-core concepts by default, and implementation remains separately gated.

### GV-04 — Supporting livestock workbook resources

**Recommendation:** `accept-with-conditions`

Use the three sheets as governed evidence and mappings into stable livestock identities and relationships.

**Condition or hold:** Preserve source lineage and reviewed corrections; promote any independent identity only through row-level evidence and global collision review.

### GV-05 — Migration waves and dependency order

**Recommendation:** `accept-with-revision`

Retain eight bounded waves and explicit dependencies; treat wave labels 0 through 7 as identifiers and narrative positions 1 through 8 as ordinals, and revise the practice/outcome wave from crop-only to cross-domain row routing.

**Condition or hold:** ADR 0049 remains a separate livestock visual-acceptance gate and must not block unrelated data-model, crop, reference, or mapping reviews; no long-running branch combines all waves.

### GV-06 — Whole-vocabulary coverage contract

**Recommendation:** `accept`

Report canonical-resource denominator, target product, owner, source-row coverage, semantic state, holds, exclusions, and consumer dependencies.

**Condition or hold:** Source-row counts and deep completion of one module never establish whole-AOM semantic completeness.

### GV-07 — Source and identifier continuity

**Recommendation:** `accept`

Preserve source rows, stable identifiers, labels, provenance, lifecycle, and review status while decomposing compound rows through reviewed relationships.

**Condition or hold:** Never infer one row equals one concept, reuse identity from labels alone, delete published IDs, or hand-edit generated distributions.

### GV-08 — Publication, privacy, and exclusion boundaries

**Recommendation:** `accept-with-holds`

Retain explicit exclusions and provenance while publishing only rights-safe governed derivatives through the correct owner repository.

**Condition or hold:** Keep site_list on sensitivity review, ssa_feedsdb excluded, and scio - Custom Terms on provenance review; no acceptance implies public release.

## Resource-route summary

| Recommended decision | Resources |
|---|---:|
| `accept-exclusion-with-retained-provenance` | 7 |
| `accept-proposed-route-with-row-review` | 17 |
| `accept-supporting-evidence-route` | 3 |
| `hold-provenance-review` | 1 |
| `hold-publication-review` | 1 |
| `retain-confirmed-restricted-exclusion` | 1 |
| `revise-to-cross-domain-row-routing` | 3 |

All 33 row-level recommendations are in
[`resource_routing_recommendations.csv`](resource_routing_recommendations.csv).

## Decision boundary

Accepting this recommendation cohort would approve resource-routing policy
and stated holds only. It would not approve row identities, hierarchy,
mappings, source edits, publication, implementation, release, consumer
migration, or canonical cutover.
