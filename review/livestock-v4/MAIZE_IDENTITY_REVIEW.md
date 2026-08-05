# Maize feed-material identity review

## Scope and status

Proposal for expert approval. No identifier merge, deprecation, or hierarchy
change is authorized by this document.

Evidence combines canonical workbook `AOM` and `ani_diet` rows with public feed
authorities. ILRI identifiers are excluded from identity decisions because that
system is changing.

## Key finding

Legacy `Whole` is overloaded:

1. `Whole Maize` and `Whole Maize Meal` occur as concentrated feeds. Here
   “whole” most plausibly means whole grain/all grain fractions retained.
2. `Corn Whole||Ensilation` and `Maize Whole||Chopping||Ensilation||Silage`
   describe whole-crop maize silage. Here “whole” means whole plant/crop.

These meanings must not share one uncontrolled `Whole` facet.

Feedipedia defines maize silage as whole ensiled maize plants:
https://feedipedia.review.fao.org/node/13883

FAO separately describes whole-crop maize silage, maize stover silage, and grain
feeds:
https://www.fao.org/4/y1936e/y1936e08.htm
https://www.fao.org/4/x5738e/x5738e09.htm

AGROVOC provides a `whole crop silage` concept:
https://agrovoc.fao.org/browse/agrovoc/en/page/c_24915

## Proposed normalized distinctions

| Dimension | Example | Meaning |
|---|---|---|
| Source crop | Maize | `Zea mays` source context |
| Material/component | Maize grain | Harvested grain |
| Material/component | Whole maize crop | Whole plant including immature/nearly mature cobs |
| Composition/integrity | Whole-grain | Bran, germ, and endosperm retained; not physical particle form |
| Process | Ensiling | Anaerobic preservation process |
| Process | Grinding | Particle-size reduction |
| Quality | Yellow | Colour/classification attribute, not separate crop identity |

`Whole form` must not represent whole-grain integrity or whole-crop material.
Existing facet remains valid only for source values where physical presentation
is genuinely whole and independently evidenced.

## Proposed rules

1. Preserve `AOM_000649 Maize Grain` as canonical grain material.
2. Treat `Maize Ensiled` and `Maize Whole Ensiled` as one likely whole-crop maize
   silage identity; retain one ID only after approval.
3. Do not merge `Maize Grain`, whole-grain maize, and whole-crop maize.
4. Model processing independently from material identity.
5. Treat `Yellow` as quality/variety information; do not mint crop identity from
   colour alone.
6. Shared Feedipedia, AGROVOC, CPC, or taxon mappings trigger review but never
   prove identity.
7. Prefer retained ID using source occurrence count, semantic clarity, public
   mapping quality, and downstream compatibility—not numeric age or ILRI code.
8. Preserve deprecated IDs as searchable aliases with replacement links.

## Strong recommendation

Retain `AOM_001326` for **Whole-crop maize silage** and deprecate
`AOM_006072` with replacement `AOM_001326`:

- `AOM_001326` has three canonical `ani_diet` rows versus two for
  `AOM_006072`;
- its workbook mapping already points to Feedipedia maize silage node 13883;
- both occurrence groups encode ensiling, while `AOM_006072` supplies explicit
  whole-crop evidence;
- retained concept should assert source crop maize, whole-crop material, and
  ensiling process after corresponding component concept is approved.

## Remaining approval questions

1. Approve `AOM_001326` retained / `AOM_006072` deprecated?
2. Approve preferred label `Whole-crop maize silage`?
3. Should `AOM_001313 Maize Whole` become `Whole-grain maize`, or remain held
   until definitions/source publications are reviewed?
4. Should generic ground/cracked/crushed/extruded maize infer grain material when
   workbook component is blank?
5. Should yellow-maize concepts be deprecated into maize/grain plus a future
   colour-quality facet?

Detailed proposals and occurrence counts are in
`maize_identity_review_recommendations.csv`.
