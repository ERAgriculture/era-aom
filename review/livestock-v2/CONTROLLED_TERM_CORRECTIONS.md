# Controlled-term corrections and identity resolutions

Decision record for six preferred-label corrections and one duplicate identity resolution.
Corrections are governance overlays: immutable legacy rows and paths remain available as
source evidence, while corrected preferred labels publish in normalized artifacts.

## Approved label corrections

- **Bothriochloa dried** replaces misspelled `Bothriocloa Dried`. Existing source mappings
  identify accepted genus Bothriochloa (`wfo-4000005074`, `NCBITaxon_79826`). Kew Plants
  of the World Online accepts Bothriochloa:
  https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:295954-2
- **Ficus exasperata leaves and twigs** replaces `Ficus gnaphalocarpa Leaves and Twigs`.
  Scientific Name, `wfo-0000688290`, and `NCBITaxon_459060` all identify Ficus exasperata.
- **Harrisonia abyssinica leaves** replaces misspelled `Harissonia abyssinica Leaves`.
  Kew accepts Harrisonia abyssinica:
  https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:813729-1
- **Ziziphus jujuba leaves** replaces `Ziziphus jujube Leaves`. Existing mappings identify
  accepted Ziziphus jujuba (`wfo-0000430303`, `NCBITaxon_326968`):
  https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:719213-1
- **Fourth trimester** corrects English ordinal spelling only. Underlying reproductive-stage
  modeling and descriptions remain queued for source-level review.
- **Variable cost—inoculants** corrects `Innoculants` and normalizes label style.

Every former preferred label remains an English `skos:altLabel`.

## Common bean vine identity

`AOM_003960` Green Bean Vine and `AOM_004000` Haricot Bean Vine have no definitions or
distinguishing scope. Both identify Phaseolus vulgaris and share `NCBITaxon_3885` and
`wfo-0000207144`. Retain lower existing identifier `AOM_003960` with preferred label
**Common bean vine**. Deprecate `AOM_004000`, publish `dcterms:isReplacedBy`, and preserve
both legacy labels as alternatives on retained concept.

## Deferred terms

Brown Fish, Danish Fish, Vitalite, and family-only Asteraceae remain pending. Available
evidence cannot support safe replacement labels; this batch does not guess.
