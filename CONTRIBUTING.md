# Contributing to AOM

AOM welcomes corrections, new concepts, synonyms, translations, hierarchy
changes, mappings, and evidence from all agricultural domains.

## Before proposing a change

1. Search existing labels and synonyms.
2. Identify affected AOM concept and release where possible.
3. Gather an authoritative source: DOI, standard, dataset documentation, or
   stable institutional page.
4. Submit unrelated concepts separately. Use a bulk proposal for a coherent
   term set.

Use GitHub issue forms:

- **New concept** — concept absent from AOM;
- **Correct concept** — label, definition, synonym, hierarchy, lifecycle, or
  provenance change;
- **Mapping proposal** — relation to another controlled vocabulary.

Contributors unable to use GitHub may contact repository maintainers. Friendly
web form remains planned; it will create same structured proposal record.

## Review workflow

```text
proposal → completeness/duplicate checks → domain review
         → accept, revise, or reject with rationale
         → pull request and automated validation
         → versioned release
```

Proposal does not change published AOM directly. Reviewer verifies identity,
meaning, scope, evidence, hierarchy, and mapping relation. Cross-module changes
require relevant crop and livestock review. Permanent reviewer remains TBD;
pilot/cutover approver is Pete Steward.

AI may help detect duplicates, normalize syntax, draft text, or suggest
mappings. AI output must be identified as a proposal and supported by evidence.
Human reviewer owns semantic decision.

## Stable identifiers

- Never request reassignment or reuse of published ID.
- Incorrect or superseded concept becomes deprecated with replacement link.
- Duplicate concepts require explicit merge/deprecation decision and
  crosswalk.
- New IDs are minted only after approval.

## Bulk proposals

Open issue describing scope before preparing more than five related concepts.
Normalized bulk template and validator will be published before canonical
cutover. Never submit restricted source data or copyrighted full text.

