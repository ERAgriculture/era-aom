# Feed-process axis governance

## Purpose

This method governs feed-process concepts across operation, mechanism, technical
objective, possible intended benefit, production provenance, and observed
effect. It accompanies [ADR 0047](../decisions/0047-feed-process-objective-benefit-and-effect-model.md)
and preserves row-level evidence from `review/livestock-v35`.

## Required distinctions

1. Record what was done as a process operation.
2. Record how it acts through `aom:processMechanism`.
3. Record direct intended transformation through
   `aom:technicalProcessObjective`.
4. Record contextual rationale through modal `aom:maySupportFeedBenefit`.
5. Record measured outcomes only on a contextual process application through
   `aom:observedProcessEffect`.
6. Record upstream workflows through `aom:productionProcessProvenance`, not
   `aom:processingMethod`.

`aom:processingMethod` may target operation concepts only. Mechanism,
technical-objective, and benefit groupings remain visible browser projections
but are not valid direct material values.

## Evidence procedure

1. Inventory full process closure and every governed material use.
2. Compare local meaning against FoodOn process modelling, EU feed-process
   definitions, OBI process structure, and claim-specific sources.
3. Record source metadata and access date in `evidence_register.csv`.
4. Record each disposition, supporting evidence IDs, rationale, and blocking
   question in `process_axis_review.csv`.
5. Preserve ambiguous cases as explicit holds; never create a permanent
   catch-all process.
6. Treat possible benefits as modal. Never convert a generic process label into
   an achieved digestibility, safety, preservation, or intake claim.

## Identifier and identity gates

Before allocating any axis concept, search normalized preferred, alternative,
hidden, deprecated, retired, and governed external labels. Reuse an existing
identity only when definition and semantic role match. Record every candidate
and collision result in `review/livestock-v36/identity_collision_audit.csv`.

Published identifiers remain stable. Changed modelling roles require a label
history, replacement definition, migration register, and retained search alias.

## Migration rules

- `Defatting` becomes technical objective `Fat removal`. Source wording does
  not identify extraction, pressing, solvent treatment, or another operation.
  Existing material assertions remain held until operation and composition
  evidence are reviewed.
- `Sugar processing` becomes production-process provenance. It identifies an
  upstream workflow through which molasses arises, not a direct treatment
  applied to molasses.
- Observed effects remain unasserted until process-application and observation
  records exist.

## Validation

Implementation acceptance requires deterministic regeneration, second-run
stability, global collision checks, hierarchy and dangling-target checks, OWL
and SHACL validation, release parity and checksum validation, clean Fuseki
reload, and guided Skosmos review of representative process cards.
