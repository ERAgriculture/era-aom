# Ingredient rule quality gate

This packet audits reusable rules before bulk semantic promotion.

```bash
python scripts/build_ingredient_rule_quality_gate.py
```

- `ingredient_rule_quality_assessment.csv` provides occurrence counts,
  cross-family coverage, deterministic samples, risk, recommendation, and guard
  for every rule.
- `ingredient_family_rollout_plan.csv` quantifies rollout work by ingredient
  family.
- `ingredient_rule_quality_summary.json` records promotion gates.

No recommendation changes ontology data. Reviewer approval must be recorded in
the assessment before a separate promotion step can generate semantic assertions.
