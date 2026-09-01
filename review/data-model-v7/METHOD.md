# ADR 0052 product-contract review method

## Inputs

- Agronomy schema SHA-256: `a06d2b18da35d5a56004e1abf918df42be1b9d0f0cffe8b4aec53a878794507f`
- Livestock schema SHA-256: `6979df8efd8c673e41a75cf0ab847d28cda1ab81b4b19eba3cd7a0d78e525507`
- Package data SHA-256: `00318de7341cad728e991ab0bf536fe68aeaeff4f732b7fde0b06e5f68e92091`
- Package dictionary SHA-256: `85ff22c5c595888899b0c3c5cbfaab3fe1b377dfedcb52fdb0dd44d322aaffd9`
- Consumer differences SHA-256: `09638c0baf86e4231c2f8778c298df9bdf9bb45b075d210fd858fa2a36cc014f`
- Consumer comparison SHA-256: `78059447ba5c4cdea497b6012f66fd5187ed3f22b02fe9e7bc43f82779c8203f`

Source snapshot was extracted from clean, pinned `era-data` and `eragri`
commits with:

```sh
Rscript scripts/extract_adr0052_product_contract_sources.R \
  /path/to/era-data /path/to/eragri review/data-model-v7/source_snapshot.json
```

CI uses committed snapshot, not mutable sibling repositories.

## Method

1. Preserve both ordered 138-field schema lists and physical types exactly.
2. Compare field-name sets, physical types, positions, and blank descriptions.
3. Compare package data and dictionary using exact names only.
4. Record two explicit lexical alias candidates without asserting identity.
5. Record `C1:Cn` and `T1:Tn` as pattern candidates without expansion approval.
6. Override `C14` and `T14` as published-only release-lineage holds.
7. Preserve every v1 consumer difference and classify one evidence hold.
8. Leave all approved content and human-decision fields blank.
9. Validate counts, source hashes, membership, boundaries, and deterministic rebuild.

## Decision rule

No lexical match, position, datatype label, pattern, or absence proves identity,
meaning, derivation, compatibility, or retirement. Human review must resolve
each proposed policy and row. Unsupported cases remain holds.
