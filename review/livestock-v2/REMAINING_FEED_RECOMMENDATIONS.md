# Remaining feed-model hierarchy recommendations

Decision record for 30 cases covering animal feed materials, animal by-products, animal
manures, other ingredients, supplements, feed processes, and diet source.

## Approved disposition

- Mint 17 governed functional/source groupings using `AOM_100976`–`AOM_100992`.
- Apply 13 reparenting decisions where existing categories are sufficient or a
  single-purpose intermediate would only repeat source/part wording.
- Distinguish animal-source feed materials from animal by-products. Fish-processing waste
  and offal belong to Fish by-products, not generic Fish feed materials.
- Attach species-labelled manures directly beneath Animal Manures; avoid redundant Cattle,
  Chicken, Pig, and Poultry containers containing one identically scoped manure concept.
- Keep Feed Process groupings separate from Feed Ingredient hierarchy.

## Terminology safeguards

`Brown Fish`, `Danish Fish`, `Vitalite`, and family-only `Asteraceae` lack enough evidence
for precise, durable preferred terminology. Existing records remain navigable, but explicit
cases in `terminology_review_candidates.csv` require source tracing before label changes or
taxonomic mappings.

## Modeling choices

- Rainbow trout viscera material attaches to existing Rainbow Trout source context; no
  one-child Viscera container is minted.
- Chicken offal joins Chicken feed materials while preserving its narrower label.
- Rumen contents and lard attach directly to Animal by-products.
- Chamomile Flower and reviewed herb/extract records reuse existing `AOM_000811` Herb or
  Extract rather than duplicating that category.
- Diet Source becomes explicit because On-farm and Purchased are reusable provenance
  categories, not ingredient types.

## Controls

Canonical workbook audit found `AOM_100976`–`AOM_100992` unused on 2026-08-03.
Governance records retain reviewer, date, evidence, rationale, and affected child IDs.
