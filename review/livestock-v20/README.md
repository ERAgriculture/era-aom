# Final definition-tail remediation register

This register covers every definition still held after authority/model
consolidation. It converts a flat backlog into review lanes with explicit
evidence gates, semantic risk, related-ID candidates, and required actions.

All 109 concepts remain held. `automation_eligible=false` is deliberate:
remaining cases concern identity, granularity, unsafe source inference,
commercial formulations, local terminology, or ontology structure. Reviewers
record decisions in the register; approved changes require a later governed
promotion with evidence and tests.

Regenerate deterministically:

```sh
python scripts/build_final_definition_tail_register.py
python tests/validate_final_definition_tail_register.py
```
