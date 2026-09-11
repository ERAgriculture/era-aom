# Registry semantic-binding governance

## Purpose

Create reviewable links from stable `era-data` registry subjects to governed
ERA-AOM properties or concepts without copying private registry definitions,
inferring semantics from labels, or erasing unresolved source decisions.

## Inputs

- accepted registry implementation contract under ADR 0054;
- immutable `era-data` candidate manifest and artifact checksums;
- stable registry subject IDs and canonical row checksums;
- approved AOM structural and value-binding decisions; and
- immutable AOM target-release artifacts.

Every input is pinned by commit or SHA-256 before review starts. Private
registry rows may be inspected locally, but only stable IDs, row checksums, and
necessary semantic assertions enter public ERA-AOM source.

## Method

1. Enumerate every prior approved semantic source decision.
2. Match only stable registry subjects supported by exact field purpose and
   existing row-level semantic approval.
3. Allocate append-only `ERA-SBN-*` IDs only to active binding rows.
4. Record registry subject type, ID, row checksum, predicate, target IRI,
   evidence, lifecycle, reviewer state, domain scope, and rationale.
5. Route every decision lacking an active stable registry subject or exact
   target to an explicit versioned hold with a reason code.
6. Validate binding identifiers, source partition completeness, target type,
   predicate compatibility, lifecycle, reviewer evidence, and domain scope.
7. Generate CSV, CSVW, Turtle, JSON-LD, OWL, SHACL, manifest, and checksums from
   governed source.
8. Load release and binding candidate into separate empty-store named graphs;
   verify binding IDs, direct assertions, target graph, and Skosmos behavior.
9. Refresh downstream candidate pins only after AOM candidate review and merge.

## Decision rules

- No inference from labels, lexical similarity, hierarchy, or frequency.
- Field bindings use `aom:mapsToProperty`; value-member bindings use
  `aom:mapsToConcept`.
- Active bindings require active registry subjects and approved row evidence.
- Held registry subjects remain held even when an AOM target has been reviewed.
- Ambiguous amount fields do not imply proportions without unit and basis.
- Missing stable value-member identity produces a hold, not a fuzzy value map.
- Shared-core promotion requires separate cross-domain evidence and approval.
- Retired AOM descriptor cards may remain evidence sources; active bindings
  target current semantic properties or concepts, not their labels.

## Completeness and collision audit

Active source keys and hold source keys must form an exact, non-overlapping
partition of all pinned structural and value decisions. Stable binding IDs,
registry subject/predicate pairs, and direct RDF assertions must be unique.
Targets must exist with expected type in pinned AOM release artifacts.

## Publication boundary

Candidate is immutable, versioned, and not `latest`. Binding graph is separate
from livestock concept graph. Publication does not authorize package/docs
migration, public release cutover, source-workbook correction, or issue closure.

## Rollback

Restore prior registry and AOM release pins. Never delete candidate evidence,
reuse stable binding or registry IDs, mutate an immutable release, or convert a
hold into an active assertion without new review.
