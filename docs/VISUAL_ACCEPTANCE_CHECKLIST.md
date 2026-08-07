# ERA-AOM visual acceptance checklist

Use local Skosmos at `http://127.0.0.1:9090/livestock/en/` after recreating the
Skosmos container. Capture desktop screenshots at normal browser zoom.

## Required views

1. Vocabulary home — hierarchy shows four roots and expands beyond Management.
2. `AOM_001313` — Whole-grain maize: definition, broader/narrower concepts,
   alternate labels, URI, and three downloads are readable.
3. `AOM_001326` — Whole-crop maize silage: component is Whole crop and process
   is Ensiling; neither is represented only through label nesting.
4. `AOM_003206` — Poultry byproduct: By-product role visible in definition.
5. `AOM_000748` — named commercial product: composition and efficacy remain
   unspecified.
6. `AOM_000638` — Cassava Shaft: no invented definition or stem facet.
7. `AOM_006072` — deprecated Maize Whole Ensiled: replacement link points to
   `AOM_001326`.
8. Concept with multiple external mappings — each URI wraps on its own line;
   labels/domains do not overlap.
9. Header — `Contribute` opens governed GitHub issue chooser.
10. Keyboard — skip link moves focus to main content; search, hierarchy, and
    downloads remain reachable.
11. Semantic relationships — applicable concept cards show explicit directional
    predicate labels such as “has biological species”, “has processing method”,
    and “has product role”; unrelated cards do not show feed-material predicates.

Record pass/fail and screenshot filenames in release review. Any semantic
disagreement becomes a governed proposal, not an ad hoc RDF edit.
