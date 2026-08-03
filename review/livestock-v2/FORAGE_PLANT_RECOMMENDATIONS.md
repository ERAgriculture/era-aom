# Forage-plant hierarchy recommendations

Decision record for 47 missing-parent cases across cereal/grass forages, forage trees,
legume forages, and other forage plants.

## Approved disposition

- Mint 31 governed forage-material groupings using `AOM_100945`–`AOM_100975`.
- Apply 16 reparenting decisions where source concepts already exist or plant-part-only
  intermediate nodes add no semantic value.
- Keep feed-material groupings distinct from botanical taxon concepts. Use `skos:related`
  for the existing Trifolium quartinianum taxon rather than cross-hierarchy `skos:broader`.
- Retain useful Jatropha press-cake and Mucuna protein-product groupings because each
  classifies several materially related processed feeds.

## Taxonomic normalization

- Normalize misspelled `Bothriocloa` to accepted genus **Bothriochloa**. Kew Plants of
  the World Online treats Bothriochloa as an accepted genus:
  https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:295954-2
- Normalize `Harissonia abyssinica` to accepted **Harrisonia abyssinica**:
  https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:813729-1
- Normalize `Ziziphus jujube` to accepted **Ziziphus jujuba**:
  https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:719213-1
- Preserve existing WFO/NCBI mappings on source records; new contextual groups do not
  claim taxon identity.

## Deferred identity review

`AOM_006373` is labelled Ficus gnaphalocarpa Leaves and Twigs, while its scientific-name,
WFO, and NCBI fields identify Ficus exasperata. It is attached only to Forage Trees and
queued in `identity_review_candidates.csv`; no false source grouping is minted.

## Controls

Canonical workbook audit found `AOM_100945`–`AOM_100975` unused on 2026-08-03.
Governance records retain reviewer, date, evidence, rationale, and affected child IDs.
