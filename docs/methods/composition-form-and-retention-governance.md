# Composition, form, and retention governance

Status: accepted with ADR 0049.

## Purpose

This method governs feed physical descriptors, processing effects, positive
component retention, chemical identity, and measured composition without
collapsing independent semantic axes.

## Classification questions

Apply questions in order and allow multiple independent assertions:

1. **Is claim measurable or observable as a physical quality?** Use a measured
   physical characteristic such as particle size or water-retention capacity.
2. **Does claim describe visible shape or particle presentation?** Use
   `aom:presentationForm`.
3. **Does claim describe flow, dispersion, or semisolid consistency?** Use
   `aom:bulkConsistency`.
4. **Does claim describe moisture state?** Use `aom:moistureCondition`.
5. **Does claim identify transformation applied?** Use
   `aom:processingMethod`.
6. **Does claim positively identify native component retained?** Use
   `aom:componentRetentionState` plus explicit retained-component relation.
7. **Does claim identify chemical entity?** Use chemical-identity concept and
   external mapping when exact.
8. **Does claim report amount or analytical result?** Use measured composition
   characteristic and observation model.
9. **Does claim identify economic role or product use?** Use independent
   product-role or product-kind relation.

## Inference controls

- Grinding may support comminuted presentation only through an approved rule;
  it never supplies one measured particle-size threshold.
- Meal and Powder never imply Dried unless separate evidence supports moisture
  removal.
- Dried never implies solid, meal, powder, pellet, or block.
- Liquid does not imply absence of solids; Slurry requires governed dispersed
  solids in liquid phase.
- Whole-grain retention survives particle-size reduction when bran, embryo, and
  endosperm remain in characteristic proportions.
- Native-fat retention is positive retained-component evidence, not automatic
  inference from missing defatting process.
- Family-page processing statements are not inherited to mapped materials
  without explicit scope review.
- Bare identity labels are prohibited when they collide with material labels;
  retain role-qualified labels or resolve identity reuse first.

## Evidence procedure

For each changed concept or assertion record:

- stable concept and relation identifiers;
- current hierarchy and every affected material assertion;
- authority, URL, supported claim, limitation, and access date;
- proposed, approved, or held disposition;
- reviewer, date, rationale, and blocking question;
- preferred, alternative, hidden, deprecated, and external-label collision
  result;
- downstream browser and consumer acceptance cases.

Authority comparison must distinguish ontology design guidance, chemical or
biological authority, analytical method, feed-practice evidence, and regulatory
catalogue. No authority is treated as universal outside its scope.

## Implementation procedure

1. Accept ADR and row dispositions.
2. Resolve or preserve every held row.
3. Run global identity and label collision audit.
4. Allocate any accepted new identifier through governed registry.
5. Edit governed source tables only.
6. Rebuild all derived outputs twice and require byte-stable second run.
7. Run hierarchy, binding, RDF, SHACL, mapping, release, and deployment tests.
8. Delete disposable Fuseki volume and reload exact committed checkout.
9. Run guided Skosmos review, notation search, downloads, and deprecated-card
   checks.
10. Record evidence in issue, decision log, implementation register, and
    program handover.

## Review boundary

Recommendation pack does not authorize semantic implementation. Held Lick and
Gluten questions cannot be silently converted into inferred categories.
