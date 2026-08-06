# Tests

Automated source-schema, referential-integrity, semantic, SHACL, and
round-trip tests will be added with normalized pilot data.

- `validate_pilot.R`: self-contained normalized-table integrity checks.
- `check_roundtrip.R`: private-workbook comparison; runs locally because
  workbook is not published.
- GitHub Actions parses JSON-LD/Turtle and executes SHACL against both schemes.
- `validate_livestock_inventory.py`: pins public AOM v2 identity and verifies
  private/restricted data remain excluded.
- `validate_livestock_staging.py`: validates normalized public-v2 staging,
  identity quarantine, hierarchy review queue, mappings, and manifest.
- `validate_livestock_review_pack.py`: verifies complete review coverage and
  signed-decision preservation while unapproved cases remain untouched.
- `validate_priority_recommendations.py`: pins eight evidence-backed priority
  proposals and validates signed approvals.
- `validate_ingredient_harmonization_workbench.py`: checks complete governed
  ingredient coverage, reusable-rule routing, resolved-decision awareness,
  exception isolation, and prohibition of automatic changes or ILRI evidence.
- `validate_ingredient_rule_quality_gate.py`: checks every reusable rule has
  evidence counts, samples, risk, guard, recommendation, and a blocked promotion
  state until named review approval.
- `validate_approved_ingredient_rule_promotion.py`: checks signed rule approval,
  held-rule exclusion, generated assertion uniqueness, guard enforcement,
  family coverage, and critical ambiguous/deprecated cases.
- `validate_ingredient_model_gap_review.py`: checks all remaining exceptions are
  covered once by six model families, cluster recommendations remain proposed,
  and governed-label overrides replace stale edge-label input.
- `validate_whole_grain_integrity.py`: checks reviewed maize, wheat, and rice
  integrity decisions, labels, RDF assertions, independent grinding, and absence
  of false physical-form or generic-grain inference.
- `validate_feed_material_source_overrides.py`: checks governed Blood, Shell,
  and Oil identities suppress false component/form extraction while preserving
  independent process assertions.
- `validate_semantic_model.py`: parses OWL/SHACL, checks complete disposition
  and phase-2 binding coverage, validates RDF/JSON-LD equivalence, and proves
  valid/invalid semantic-model fixtures behave correctly.
