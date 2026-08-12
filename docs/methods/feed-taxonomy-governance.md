# Feed taxonomy governance method

- Method version: 1.0
- Approved: 2026-08-12
- Decision record: [ADR 0044](../decisions/0044-feed-taxonomy-axis-reclassification.md)
- Review cohort: [livestock-v29 recommendations](../../review/livestock-v29/RECOMMENDATIONS.md)
- Implementation cohort: [livestock-v30 register](../../review/livestock-v30/feed_taxonomy_implementation_register.csv)

## Purpose

This method governs classification of feed-related AOM concepts while preserving
source identity, stable identifiers, decision provenance, and unresolved cases.
It prevents residual categories such as `Supplement` or `Other Ingredients`
from mixing product kind, chemical identity, role, process, component, and
composition state.

## Unit of review

Review complete semantic cohorts, not reported cards. Cohort selection must
include:

1. reported concepts;
2. every descendant of implicated grouping concepts;
3. every concept using implicated semantic predicates or value classes;
4. same-label and normalized-label matches across active, alternative, hidden,
   deprecated, generated, and external-mapping labels;
5. upstream and downstream hierarchy impact.

Each reviewed concept receives one row in a machine-readable register. Holds
remain inside cohort and do not reduce denominator.

## Classification sequence

Apply axes in this order. Never answer a later question by changing an earlier
axis.

1. **Source identity** — What substance, organism-derived material, named
   product, formulation, or source term is represented?
2. **Feed product kind** — Is evidence sufficient for Feed material, Formulated
   feed, Feed additive, or only broad Feed?
3. **Chemical identity** — Is a chemical substance or constituent represented
   independently of product kind?
4. **Role** — Does evidence establish product, functional, or experimental role?
5. **Component** — Is value anatomical structure, body substance, processed
   fraction, or composite material scope?
6. **Process** — Was process intentionally applied to represented feed, or is it
   upstream production provenance?
7. **State** — Does evidence support presentation, bulk consistency, moisture,
   or positive native-component retention?

One concept may participate in several axes through explicit RDF properties.
Hierarchy must not carry all semantics.

## Evidence classes

| Evidence class | Permitted use | Prohibited inference |
|---|---|---|
| Regulation or official catalogue | Product-kind definitions, authorized category structure, catalogue-listed material identity | Authorization for ambiguous brand, compound, species, dose, or jurisdiction |
| Regulatory assessment | Named product identity and assessed use | Timeless global authorization |
| Authority vocabulary | Broad identity and terminology structure | Product-specific legal status |
| Reference ontology | Reusable axis, relation, anatomy, fraction, or process pattern | Automatic equivalence or occurrence in AOM |
| Manufacturer evidence | Named product composition or production claim | Generalization to all products in category |
| Source workbook | Source label, hierarchy, synonym, and occurrence provenance | Biological, chemical, regulatory, or process entailment absent from source |
| Editorial model evidence | Separation of orthogonal axes and compatibility policy | New empirical fact about material or product |

Evidence record must state both supported claim and limitation. URI alone is
insufficient provenance.

## Decision states

- `implemented` — evidence supports semantic class and placement.
- `implemented-structural` — evidence supports architecture, label, relation, or
  retirement without asserting uncertain product identity.
- `hold` — source identity remains active but only broad `aom:Feed`, chemical
  identity, role, or no semantic class is safe.
- `outside-scope` — row included for cohort completeness but receives no new
  disposition.

Hold is governed outcome, not failed review. Hold records must name missing
evidence type and must not inherit Feed material, Formulated feed, or Feed
additive class from administrative browse placement.

## Retirement and compatibility

Published source identifiers are never deleted or reassigned.

- Same-meaning legacy concept: deprecate with `dcterms:isReplacedBy` and retain
  searchable labels.
- Schema field misrepresented as concept: retire without replacement concept;
  retain semantic-binding record pointing to replacement property.
- Split catch-all: migrate every child first; route unresolved children to
  explicit hold grouping; retire empty legacy grouping without claiming one
  false replacement.
- Generated identifier rejected before publication: remove from active concept
  set, mark registry `retired-before-publication`, and never reassign.

## Identifier allocation

Before allocating an ID:

1. search all AOM label types and deprecated records;
2. search external mapping labels;
3. compare definitions and semantic use, not labels alone;
4. record collision result and allocation basis;
5. allocate next sequential unused ID;
6. add registry row in same change.

## Authority comparison

- Regulation 767/2009 distinguishes feed materials and compound,
  complete, and complementary feeds.
- Regulation 1831/2003 separates additive categories by principal function and
  requires authorization under specific conditions.
- Regulation 68/2013 provides feed-material and process catalogue evidence.
- AGROVOC distinguishes feed additives, supplements as use with another feed,
  and organic acids as chemical compounds.
- FoodOn separates material, anatomy, chemical, quality, and process facets and
  distinguishes process output/provenance from treatment applied to product.
- OWL open-world semantics requires explicit negative assertions; missing
  processing assertions cannot mean “not defatted” or another negative fact.

Authority comparison guides model architecture. It does not replace
concept-specific evidence.

## Evidence trail

Implementation publishes:

- [source recommendation register](../../review/livestock-v29/feed_taxonomy_adversarial_review.csv);
- [implementation register](../../review/livestock-v30/feed_taxonomy_implementation_register.csv);
- [evidence register](../../review/livestock-v30/evidence_register.csv);
- [implementation summary](../../review/livestock-v30/feed_taxonomy_implementation_summary.json);
- governed staging CSVs under `data/livestock-staging/`;
- generated semantic RDF under `dist/livestock-staging/`;
- accepted ADR and changelog entry.

Every implementation row carries reviewer, date, evidence state, decision
record, method record, target class or parent where applicable, and rationale.

## Reproducibility

Run generators in this order:

```bash
python scripts/build_feed_formulation_structural_review.py
python scripts/build_feed_taxonomy_adversarial_review.py
python scripts/build_feed_taxonomy_axis_implementation.py
python scripts/build_definition_enrichment.py
python scripts/normalize_livestock_release.py data/livestock-staging/legacy_records.csv .
python scripts/build_semantic_bindings.py
```

Then run implementation validator, full semantic validators, collision audit,
RDF parsing, SHACL, release checksum validation, and clean-volume
Fuseki/Skosmos acceptance. Incremental graph loading is not acceptance evidence.

## Change control

1. Recommendation PR records adversarial review and proposed ADR.
2. Reviewer approves, amends, or holds dispositions.
3. Implementation PR changes governed sources and generated artifacts.
4. Independent implementation and evidence review checks cohort counts and
   exceptions.
5. Empty Fuseki reload and Skosmos review may reopen decision.
6. Publication remains separate explicit approval.
