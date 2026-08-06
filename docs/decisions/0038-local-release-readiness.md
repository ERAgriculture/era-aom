# ADR 0038: Local release readiness

- Status: accepted
- Date: 2026-08-06
- Owner: Alliance of Bioversity International and CIAT
- Reviewer: TBD

## Decision

Treat `2026.1-rc.1` as technically ready for local evaluation when automated
browser/API, hierarchy, content-negotiation, serialization, accessibility-hook,
stylesheet, performance, and representative-semantic checks pass. Keep manual
visual acceptance, permanent reviewer appointment, hosting, persistent URI
activation, DOI, registry submission, and canonical cutover as separate gates.

Recreate Skosmos after configuration/CSS changes because APC may retain parsed
configuration across process restarts. Patch pinned Skosmos 3.3 skip-link target
from nonexistent `#maincontent` to `#main-content`. Route browser contribution
navigation to governed GitHub issue forms instead of an unconfigured mail form.
