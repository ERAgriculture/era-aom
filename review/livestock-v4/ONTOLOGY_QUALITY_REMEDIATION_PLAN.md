# AOM livestock ontology quality-remediation plan

## Purpose

Treat browser visualization as a semantic-quality acceptance surface, not proof
that valid RDF has correct identities. Review concepts in coherent domain batches;
do not merge, reparent, or decompose from lexical similarity alone.

## Evidence baseline

- Canonical transition source: ERA `era_master_sheet.xlsx`, AOM sheet, modified
  2026-07-09; 2,503 source rows.
- Reproducible public evidence: AOM Livestock Prototype v2 and normalized source
  snapshot aligned to current workbook identifiers and L1-L10 hierarchy.
- Public identity evidence: definitions, source occurrences, hierarchy,
  Feedipedia, AGROVOC, NCBI Taxonomy, WFO, and CPC at their documented scope.
- Deferred evidence: ILRI feed identifiers. Preserve privately; exclude from
  identity scoring because that system is changing.
- Never-publish evidence: `ssa_feedsdb`, restricted feed databases, and closed
  source material.

## Decision vocabulary

Every reviewed case receives exactly one disposition:

1. `retain_distinct` — scientific distinction established;
2. `deprecate_replace` — identity duplicate; one persistent ID retained;
3. `relabel` — identity valid, preferred label misleading;
4. `reparent` — identity valid, hierarchy wrong;
5. `decompose` — compound material represented through reviewed facets;
6. `map_related` — overlap without identity;
7. `hold` — evidence insufficient;
8. `exclude` — scratch, restricted, or non-public record.

Each decision requires evidence, rationale, reviewer, review date, compatibility
effect, and retained/replacement ID where applicable.

## Work packages

### WP1 — cereal feed materials

Review all 369 rows in `cereal_feed_material_review.csv` as one batch. Start with
high-risk families: maize, wheat, rice, barley, sorghum, millet, and oat. Resolve:

- grain versus whole grain versus whole crop;
- material/component identity;
- processing methods versus resulting materials;
- compound process chains;
- product versus by-product role;
- mapping granularity;
- missing definitions.

`Maize Grain`, `Maize Whole`, `Maize Ensiled`, and `Maize Whole Ensiled` remain
unmerged until source-use and scope review establishes identity.

### WP2 — remaining crop feed materials

Apply approved WP1 patterns to legumes, oil crops, roots/tubers, fruit products,
crop residues, and forage plants. Re-review lexical collisions rather than
automatically extending cereal decisions.

### WP3 — animal feeds and non-crop materials

Review animal products/by-products, manures, minerals, supplements, mixtures,
and formulation concepts. Separate feed-material identity from ingredient use in
a formulation.

### WP4 — non-feed AOM branches

Audit animals/breeds/stages, management processes, feed composition,
digestibility, outcomes, and remaining hierarchy. Use same decision contract.

## Implementation batch

After domain approval, implement one substantial PR per work package:

- governed decision tables;
- deprecated/replacement links and migration crosswalks;
- normalized labels and hierarchy;
- reviewed semantic facets only;
- regenerated CSV, Parquet, Turtle, JSON-LD, and RDF/XML;
- SHACL and regression validation;
- semantic changelog and consumer-impact report.

No concept-by-concept PR sequence.

## Acceptance gates

1. Review table complete: no blank disposition, reviewer, date, or rationale.
2. No automatic merge based only on labels or shared mappings.
3. Deprecated IDs resolve to retained IDs and remain searchable.
4. Public/private evidence boundary passes validation.
5. SKOS hierarchy has no gaps, cycles, or unintended duplicate siblings.
6. Semantic facets pass SHACL and match reviewed decisions.
7. Skosmos visual review covers roots, retained concepts, deprecated concepts,
   processed materials, mappings, search synonyms, and downloads.
8. Ingestion compatibility crosswalk passes consumer regression tests.
9. Release rebuilds deterministically from clean checkout.
10. Pete Steward approves domain batch before merge.

## Current gate

Audit only. No WP1 identity decision is approved by these generated candidates.
Next human-review action: triage maize and other cereal root/material concepts,
then approve review rules before processing all 369 rows.
