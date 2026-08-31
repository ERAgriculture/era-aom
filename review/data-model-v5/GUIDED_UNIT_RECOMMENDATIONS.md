# ADR 0052 unit-disposition recommendations

Status: recommendation-only; human decision pending.

## Guided decisions

### UD-01 — Raw unit preservation

**Recommendation:** `retain-raw-unit-and-source-row`

Preserve every raw unit label and source-row identity independently from reviewed canonical unit assertions.

**Condition or hold:** Normalization, correction, and mapping never overwrite source evidence.

### UD-02 — Complete held cohort

**Recommendation:** `accept-recommendation-only-hold`

Retain all 64 unresolved rows and both conflicting ZMK/ha rows as holds pending source context.

**Condition or hold:** No row receives canonical unit identity, quantity kind, or conversion from label evidence alone.

### UD-03 — Missing-value sentinels

**Recommendation:** `hold-missing-sentinel-source-correction`

Treat N/A and NA as candidate missing-value sentinels rather than units.

**Condition or hold:** Normalize to null only through approved source correction after confirming source intent.

### UD-04 — Non-unit values and fragments

**Recommendation:** `hold-non-unit-and-fragment-source-correction`

Hold apparent outcomes, statuses, values, and text fragments for field-level source correction.

**Condition or hold:** Lexical classification is triage, not approval to delete, move, or replace a source value.

### UD-05 — Bases and qualifiers

**Recommendation:** `separate-basis-and-qualifier`

Represent material, population, state, and reporting basis independently from physical unit identity.

**Condition or hold:** Terms such as DM, BW, feed, milk, and metabolic require expanded source meaning before modeling.

### UD-06 — Ratio decomposition

**Recommendation:** `decompose-ratio-before-unit-mapping`

Resolve numerator, denominator, scaling, population, area, and time before assigning compound-unit identity.

**Condition or hold:** A slash-containing label does not prove a valid or complete unit expression.

### UD-07 — Symbol case and abbreviation

**Recommendation:** `require-case-sensitive-symbol-review`

Review exact case and expanded meaning before interpreting ambiguous symbols or abbreviations.

**Condition or hold:** Do not silently reinterpret mg as Mg, ms as mS, in as inch, or abbreviations as quantities.

### UD-08 — Quantity kind before unit URI

**Recommendation:** `require-quantity-kind-before-unit-uri`

Establish measured property and quantity kind before selecting a QUDT or other canonical unit identifier.

**Condition or hold:** Same label can occur under different quantities, bases, or contexts.

### UD-09 — UCUM expression validation

**Recommendation:** `use-ucum-validation-not-identity-inference`

Use UCUM to validate approved unit expressions and semantics, not to infer source meaning from malformed labels.

**Condition or hold:** Case-sensitive codes, annotations, and compound expressions require explicit reviewed construction.

### UD-10 — Currency and effective context

**Recommendation:** `require-currency-code-and-effective-context`

Model currency code, denominator or basis, geography, and effective date separately.

**Condition or hold:** Never replace ZMK with ZMW without source date and rebasing context.

### UD-11 — Conversion semantics

**Recommendation:** `require-explicit-conversion-record`

Store conversion factor, offset, formula, direction, basis, applicability, authority, and evidence separately.

**Condition or hold:** Label normalization alone authorizes no numeric conversion.

### UD-12 — Implementation boundary

**Recommendation:** `retain-unit-implementation-gates`

Keep recommendation, human acceptance, source correction, registry implementation, release, and migration as separate gates.

**Condition or hold:** This cohort changes no workbook, schema, unit registry, binding, distribution, or consumer.

## Cohort summary

| Recommended disposition | Cases |
|---|---:|
| `hold-basis-or-qualifier-model` | 11 |
| `hold-currency-and-basis-review` | 3 |
| `hold-currency-effective-context` | 2 |
| `hold-missing-value-source-correction` | 2 |
| `hold-non-unit-source-correction` | 21 |
| `hold-ratio-decomposition` | 16 |
| `hold-source-fragment-correction` | 3 |
| `hold-symbol-case-and-context-review` | 8 |

## Complete row cohort

### `hold-basis-or-qualifier-model`

| Case | Raw unit | Current correction | Required evidence |
|---|---|---|---|
| `UNIT-0156` | `body` | `—` | Identify measured quantity and model material, population, state, or basis separately from unit. |
| `UNIT-0223` | `concentrate` | `—` | Identify measured quantity and model material, population, state, or basis separately from unit. |
| `UNIT-0270` | `excreta` | `—` | Identify measured quantity and model material, population, state, or basis separately from unit. |
| `UNIT-0276` | `feed` | `—` | Identify measured quantity and model material, population, state, or basis separately from unit. |
| `UNIT-0277` | `forage` | `—` | Identify measured quantity and model material, population, state, or basis separately from unit. |
| `UNIT-0666` | `metabolic` | `—` | Identify measured quantity and model material, population, state, or basis separately from unit. |
| `UNIT-0727` | `milk` | `—` | Identify measured quantity and model material, population, state, or basis separately from unit. |
| `UNIT-0892` | `organic` | `—` | Identify measured quantity and model material, population, state, or basis separately from unit. |
| `UNIT-1072` | `weight` | `—` | Identify measured quantity and model material, population, state, or basis separately from unit. |
| `UNIT-1073` | `wool` | `—` | Identify measured quantity and model material, population, state, or basis separately from unit. |
| `UNIT-1074` | `Wool` | `—` | Identify measured quantity and model material, population, state, or basis separately from unit. |

### `hold-currency-and-basis-review`

| Case | Raw unit | Current correction | Required evidence |
|---|---|---|---|
| `UNIT-0138` | `3k/NGN/individual` | `—` | Confirm currency code, numerator meaning, denominator or basis, geography, and effective date. |
| `UNIT-0893` | `per USD` | `—` | Confirm currency code, numerator meaning, denominator or basis, geography, and effective date. |
| `UNIT-1060` | `USD/tonne` | `—` | Confirm currency code, numerator meaning, denominator or basis, geography, and effective date. |

### `hold-currency-effective-context`

| Case | Raw unit | Current correction | Required evidence |
|---|---|---|---|
| `UNIT-1096` | `ZMK/ha` | `ZMK/ha` | Resolve source record date and intended pre-2013 ZMK or post-rebasing ZMW identity before correction. |
| `UNIT-1097` | `ZMK/ha` | `ZMW/ha` | Resolve source record date and intended pre-2013 ZMK or post-rebasing ZMW identity before correction. |

### `hold-missing-value-source-correction`

| Case | Raw unit | Current correction | Required evidence |
|---|---|---|---|
| `UNIT-0852` | `N/A` | `—` | Confirm sentinel use and replace with governed null through approved source correction. |
| `UNIT-0860` | `NA` | `—` | Confirm sentinel use and replace with governed null through approved source correction. |

### `hold-non-unit-source-correction`

| Case | Raw unit | Current correction | Required evidence |
|---|---|---|---|
| `UNIT-0002` | `0.04` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0154` | `Biomass Carbon` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0165` | `Calving` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0172` | `clean` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0232` | `degraded` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0275` | `Fecundity` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0377` | `gained` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0406` | `Index` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0413` | `intake` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0570` | `kidding` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0571` | `kids` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0605` | `Live` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0648` | `Macrofauna group No.` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0665` | `Mesofauna group No.` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0777` | `Mortality` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0905` | `production` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0906` | `Prolificacy` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0913` | `rate` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0914` | `Rate` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0919` | `replicate` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |
| `UNIT-0958` | `survival` | `—` | Trace outcome field and source row to determine correct unit, count, score, status, or misplaced value. |

### `hold-ratio-decomposition`

| Case | Raw unit | Current correction | Required evidence |
|---|---|---|---|
| `UNIT-0114` | `/individual/day` | `—` | Identify numerator unit, denominator unit or basis, population, time, area, and scaling factor explicitly. |
| `UNIT-0234` | `DM/day` | `—` | Identify numerator unit, denominator unit or basis, population, time, area, and scaling factor explicitly. |
| `UNIT-0235` | `DM/ha` | `—` | Identify numerator unit, denominator unit or basis, population, time, area, and scaling factor explicitly. |
| `UNIT-0306` | `g g/N` | `—` | Identify numerator unit, denominator unit or basis, population, time, area, and scaling factor explicitly. |
| `UNIT-0329` | `g/234` | `—` | Identify numerator unit, denominator unit or basis, population, time, area, and scaling factor explicitly. |
| `UNIT-0354` | `g/ka` | `—` | Identify numerator unit, denominator unit or basis, population, time, area, and scaling factor explicitly. |
| `UNIT-0375` | `gain/feed` | `—` | Identify numerator unit, denominator unit or basis, population, time, area, and scaling factor explicitly. |
| `UNIT-0376` | `gain/protein` | `—` | Identify numerator unit, denominator unit or basis, population, time, area, and scaling factor explicitly. |
| `UNIT-0568` | `kgt/individual` | `—` | Identify numerator unit, denominator unit or basis, population, time, area, and scaling factor explicitly. |
| `UNIT-0572` | `kids/all` | `—` | Identify numerator unit, denominator unit or basis, population, time, area, and scaling factor explicitly. |
| `UNIT-0655` | `manure/day` | `—` | Identify numerator unit, denominator unit or basis, population, time, area, and scaling factor explicitly. |
| `UNIT-0656` | `matter/day` | `—` | Identify numerator unit, denominator unit or basis, population, time, area, and scaling factor explicitly. |
| `UNIT-0693` | `mg/100` | `—` | Identify numerator unit, denominator unit or basis, population, time, area, and scaling factor explicitly. |
| `UNIT-0696` | `mg/234` | `—` | Identify numerator unit, denominator unit or basis, population, time, area, and scaling factor explicitly. |
| `UNIT-1011` | `urine/day` | `—` | Identify numerator unit, denominator unit or basis, population, time, area, and scaling factor explicitly. |
| `UNIT-1012` | `urine/day` | `—` | Identify numerator unit, denominator unit or basis, population, time, area, and scaling factor explicitly. |

### `hold-source-fragment-correction`

| Case | Raw unit | Current correction | Required evidence |
|---|---|---|---|
| `UNIT-0891` | `of` | `—` | Recover complete source value or confirm removal; fragment cannot identify a unit. |
| `UNIT-0993` | `the` | `—` | Recover complete source value or confirm removal; fragment cannot identify a unit. |
| `UNIT-1002` | `truly` | `—` | Recover complete source value or confirm removal; fragment cannot identify a unit. |

### `hold-symbol-case-and-context-review`

| Case | Raw unit | Current correction | Required evidence |
|---|---|---|---|
| `UNIT-0162` | `BW` | `—` | Confirm expanded meaning, exact case, measured quantity, and contextual basis from source field evidence. |
| `UNIT-0233` | `DM` | `—` | Confirm expanded meaning, exact case, measured quantity, and contextual basis from source field evidence. |
| `UNIT-0256` | `ETA/ha` | `—` | Confirm expanded meaning, exact case, measured quantity, and contextual basis from source field evidence. |
| `UNIT-0265` | `ETH/ha` | `—` | Confirm expanded meaning, exact case, measured quantity, and contextual basis from source field evidence. |
| `UNIT-0274` | `FCM` | `—` | Confirm expanded meaning, exact case, measured quantity, and contextual basis from source field evidence. |
| `UNIT-0405` | `in` | `—` | Confirm expanded meaning, exact case, measured quantity, and contextual basis from source field evidence. |
| `UNIT-0667` | `mg C / ha` | `—` | Confirm expanded meaning, exact case, measured quantity, and contextual basis from source field evidence. |
| `UNIT-0779` | `ms/cm` | `—` | Confirm expanded meaning, exact case, measured quantity, and contextual basis from source field evidence. |

## Decision boundary

Accepting this recommendation cohort would accept review policy and
retain all 66 rows as explicit holds. It would not correct source, assign
unit or quantity-kind identity, define conversion, create registry records,
regenerate schemas, publish releases, or migrate consumers.
