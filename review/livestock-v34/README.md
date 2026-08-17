# Cohort A feed product-kind implementation

Status: implementation candidate under accepted
[ADR 0045](../../docs/decisions/0045-feed-product-kind-and-source-navigation.md).

Tracking: [era-program #52](https://github.com/ERAgriculture/era-program/issues/52).

This cohort implements every accepted or held row from `livestock-v31` without
restoring reverted work:

- Feed materials expose four direct editorial navigation branches: Forage
  materials, Plant products and by-products, Feeds of animal origin, and Other
  feeds;
- Glycerol enters temporary governed Unclassified feed materials;
- Unspecified Yeast and microalgal materials enter Other biological feed
  materials;
- Water, Animal Manures, Pleurotus ostreatus, Pseudovitamin, and Chromium Oxide
  Ground move to explicit classification holds rather than inheriting
  FeedMaterial status by browse placement;
- Chemical substances loses product-kind wording, while source, product role,
  chemical identity, process, and composition remain independent;
- `AOM_101156` through `AOM_101158` remain reserved and absent because they
  originated only in reverted unapproved work.

## Evidence trail

- `feed_product_kind_implementation_register.csv` joins all 32 reviewed rows to
  implementation status, target, evidence, ADR, method, reviewer, and date;
- `identity_collision_audit.csv` records preferred/alternative/hidden/
  deprecated/external-label checks before allocation;
- `temporary_unclassified_register.csv` records reason, evidence gap, owner,
  target cohort, review date, and one-release-cycle resolution boundary;
- `evidence_register.csv` carries authority claims and limitations forward from
  v31 and adds decision, collision, and rejected-ID governance evidence;
- `feed_product_kind_implementation_summary.json` records deterministic counts.
- `local_acceptance_summary.json` records clean-volume Fuseki/Skosmos evidence:
  2,794 concepts, 2,801 inverse hierarchy pairs, 37,979 graph triples, exact
  four-branch Feed-material navigation, 13 nested-parent checks, 31 concept
  cards, notation search, RDF downloads, and content negotiation.

Implementation approval remains separate from public release, namespace,
AgroPortal, DOI, and canonical cutover approval.
