# ADR 0052 unit-disposition method

## Inputs

- `review/data-model-v1/unit_mapping_audit.csv`
- source SHA-256: `29fbec8fc3fb2b2153532bcbfdaea8f32b1918b3b397e445f33aa1c192063b8c`
- only rows with `unresolved` or `conflicting-canonical-label` status

## Method

1. Preserve source row, raw label, canonical correction, occurrence count, and
   source audit status unchanged.
2. Select all 64 unresolved rows and both conflicting rows; fail validation if
   source membership changes.
3. Assign one exact lexical triage class from explicit label sets and slash
   structure. Triage determines required evidence, not semantic identity.
4. Leave canonical unit URI, quantity-kind URI, conversion rule, and human
   decision blank for every case.
5. Compare QUDT, UCUM, ISO 4217, Bank of Zambia guidance, and ERA source
   authority with explicit limitations.
6. Generate JSON and Markdown byte-deterministically; validate counts,
   fingerprints, classifications, blank decisions, and implementation gates.

## Interpretation boundary

Current repository evidence does not connect these unit-harmonization rows to
specific outcome fields or observations. Terms such as `DM`, `BW`, `FCM`,
`in`, `mg C / ha`, and `ms/cm` therefore remain ambiguous. Slash syntax does
not prove a complete ratio. Case variants do not prove equivalence. Apparent
sentinels or fragments require governed source correction rather than silent
normalization.
