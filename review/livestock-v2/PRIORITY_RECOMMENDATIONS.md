# AOM Livestock v2 priority recommendations

Evidence brief for two identity blockers and six high-impact missing-parent
cases. Recommendations remain proposals. No identifier, mapping, hierarchy, or
label change has been applied.

## Recommended decisions

| Case | Recommendation | Confidence |
|---|---|---|
| `ID-AOM-006275` | Split two species concepts; choose ID survivor only after provenance review; correct species mappings | high |
| `PATH-BREWERS-GRAIN` | Merge; provisionally retain `AOM_000564`, deprecate `AOM_001884` | high |
| `PARENT-006` | Mint `Mineral content` intermediate concept | high |
| `PARENT-007` | Mint `Feed ingredient` intermediate concept | high |
| `PARENT-036` | Mint `Maize by-products`; do not reuse product concept | high |
| `PARENT-078` | Mint `Soybean by-products`; do not reuse product concept | medium |
| `PARENT-200` | Mint `Grazing management` intermediate concept | high |
| `PARENT-227` | Mint `Management-activity variable cost` intermediate concept | medium |

Confidence measures evidence supporting disposition, not authority to approve.

## Identity blocker: `AOM_006275`

Two rows represent different species-derived dried feeds:

- *Panicum antidotale* dried;
- *Panicum maximum* dried, now commonly treated as *Megathyrsus maximus*.

Current shared mappings are not species mappings:

- NCBI `4539` identifies genus *Panicum*, not either species;
- WFO `wfo-4000027882` identifies genus *Panicum*;
- both therefore lose required species distinction.

Authoritative candidates:

| Legacy label | NCBI | WFO | Feedipedia |
|---|---|---|---|
| *Panicum antidotale* | `NCBITaxon:3031383` — current NCBI name *Janochloa antidotale* | `wfo-0000883036` — *Panicum antidotale* | `413` — Blue panic |
| *Panicum maximum* | `NCBITaxon:59788` — *Megathyrsus maximus*, with *Panicum maximum* as synonym | `wfo-0000885123` — *Panicum maximum* | `416` — Guinea grass (*Megathyrsus maximus*) |

Sources: [NCBI *Janochloa antidotale*](https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=206011),
[NCBI *Megathyrsus maximus*](https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=59788),
[WFO *Panicum antidotale*](https://www.worldfloraonline.org/taxon/wfo-0000883036),
[WFO *Panicum maximum*](https://www.worldfloraonline.org/taxon/wfo-0000885123),
[Feedipedia Blue panic](https://www.feedipedia.org/node/413), and
[Feedipedia Guinea grass](https://www.feedipedia.org/node/416).

Recommendation:

1. Preserve both meanings as distinct AOM concepts.
2. Retain `AOM_006275` for one concept only after reviewer checks original
   assignment provenance; row order is insufficient evidence.
3. Mint one replacement ID for other concept.
4. Add explicit legacy crosswalk documenting collision.
5. Replace shared genus mappings with species-level mappings above.
6. Normalize preferred label for *Panicum maximum* concept to current accepted
   name only if livestock reviewer accepts nomenclature policy; otherwise keep
   legacy preferred label and add current name as synonym.

Downstream structural audit found two `ani_diet` references: one corresponds to
each species. No survivor can be selected from usage frequency.

## Identity blocker: Brewers Grain

`AOM_000564` and `AOM_001884` share:

- preferred label;
- full hierarchy path;
- Feedipedia target `11893`;
- no documented distinguishing definition.

[Feedipedia `11893`](https://www.feedipedia.org/node/11893) specifically
represents dehydrated brewers grains. Feedipedia separately models
[general brewers grains](https://www.feedipedia.org/node/74),
[ensiled](https://www.feedipedia.org/node/11894), and
[fresh](https://www.feedipedia.org/node/11895) forms.

Recommendation: merge duplicate records. Provisionally retain `AOM_000564`
because structural audit found two downstream references versus one for
`AOM_001884`. Deprecate `AOM_001884` with replacement link. Preferred label
should become `Brewers grains, dehydrated` if Feedipedia mapping remains
intended; otherwise remove overly specific mapping and retain broader label.

## High-impact missing parents

### `PARENT-006` — Mineral content

Thirteen children are chemical elements under Feed Chemical Composition.
FAO identifies minerals as major feed components and explicitly includes most
listed children among major and trace elements.
[FAO feed composition guidance](https://www.fao.org/4/s4314e/s4314e04.htm).

Recommendation: mint `Mineral content`, broader Feed Chemical Composition.
Use scope note: measured mineral-element content of feed material. This avoids
confusion with mineral feed supplements.

### `PARENT-007` — Feed ingredient

Eighteen children cover ingredient identity, part, species, proportion, source,
and ingredient branches. Codex defines feed ingredient as component or
constituent making up feed, including plant, animal, aquatic, organic, and
inorganic sources.
[Codex Code of Practice on Good Animal Feeding](https://www.fao.org/4/i1111e/i1111e02.pdf).

Recommendation: mint `Feed ingredient`, broader Feed Characteristic. Reviewer
should separately decide whether ingredient metadata fields belong in concept
hierarchy or data schema.

### `PARENT-036` — Maize by-products

Twelve children include cob, offal, straw, gluten, germ, and other derivative
materials. Existing `AOM_000648` represents Maize under Crop Product/Cereal
Products and carries species/product mappings. Reusing it as by-product parent
would conflate crop/product identity with contextual material grouping.

FAO documents maize germ, seed-coat, gluten, and germ meal as processing
by-products used for animal feed.
[FAO maize processing](https://www.fao.org/4/t0395e/T0395E02.htm).
AGROVOC defines [by-products](https://agrovoc.fao.org/browse/agrovoc/en/page/c_1172)
as secondary/incidental products.

Recommendation: mint `Maize by-products`. Relate to `AOM_000648`, but do not
assert identity. Longer-term model should separate source taxon from processed
feed material.

### `PARENT-078` — Soybean by-products

Same modeling issue as Maize: 12 derivative materials currently need grouping,
while `AOM_001582` represents Soybean under Crop Product/Legume Products.

Recommendation: mint `Soybean by-products`; relate to `AOM_001582` without
identity. Confidence medium because child set mixes cake, dried material,
residue, straw, and other processing states needing curator review.

### `PARENT-200` — Grazing management

Ten children cover grazing intensity, field dimensions, sward-height targets,
and related controls. FAO describes grazing management through livestock kind,
class, stocking rate, season, and intensity.
[FAO grazing management](https://www.fao.org/4/X9137E/x9137e06.htm).

Recommendation: mint `Grazing management`, broader Livestock Management.

### `PARENT-227` — Management-activity variable cost

Twelve children represent variable costs of tillage, weeding, harvesting,
threshing, planting, and related operations. FAO farm-budget examples group
soil preparation, planting, inputs, labour, harvesting, and commercialization
within variable-cost accounting.
[FAO variable-cost example](https://www.fao.org/4/al309e/al309e.pdf).

Recommendation: mint `Management-activity variable cost`, broader Economics.
Label avoids ambiguous generic `Management Activities` and states children
measure costs, not activities themselves.

## Approval gate

Reviewer must record decision, evidence, rationale, identity, and date in
`03_review_decisions.csv`. Approved changes belong in separate implementation
PR with minted-ID registry update, deprecation crosswalk, regenerated graph,
and downstream parity checks.

