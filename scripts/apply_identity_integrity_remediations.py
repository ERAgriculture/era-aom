#!/usr/bin/env python3
"""Apply approved identity-integrity remediations to governed source tables."""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/livestock-staging"
DECISIONS = DATA / "approved_identity_integrity_remediations.csv"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def fields(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return csv.DictReader(handle).fieldnames


def write(path, rows, fieldnames):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


decisions = read(DECISIONS)
replacement = {
    row["generated_id"]: row["canonical_id"]
    for row in decisions
    if row["status"] == "approved" and row["action"] == "reuse_existing"
}
renames = {
    row["generated_id"]: row["replacement_label"]
    for row in decisions
    if row["status"] == "approved" and row["action"] == "rename_distinct"
}
original_labels = {row["generated_id"]: row["generated_label"] for row in decisions}
assert len(replacement) == 14
assert len(renames) == 3
assert not (set(replacement) & set(replacement.values()))

# Tables where concept identifiers are references, not entity definitions.
reference_tables = [
    "approved_feed_material_facets.csv",
    "approved_generated_feed_material_facets.csv",
    "approved_hard_tail_feed_material_facets.csv",
    "approved_structural_feed_material_facets.csv",
    "approved_ingredient_component_decompositions.csv",
    "approved_ingredient_component_value_mappings.csv",
    "approved_ingredient_semantic_closure_decisions.csv",
    "approved_process_state_relations.csv",
]
replacement_count = 0
for name in reference_tables:
    path = DATA / name
    rows = read(path)
    for row in rows:
        if row.get("target_concept_id") in renames and "target_label" in row:
            row["target_label"] = renames[row["target_concept_id"]]
        for key, value in row.items():
            if value in replacement:
                row[key] = replacement[value]
                replacement_count += 1
    write(path, rows, fields(path))

# Reuse canonical legacy concepts as governed facet values.
facet_path = DATA / "approved_ingredient_facet_concepts.csv"
facet_rows = read(facet_path)
for row in facet_rows:
    if row["concept_id"] in replacement:
        row["concept_id"] = replacement[row["concept_id"]]
    if row["concept_id"] in renames:
        row["preferred_label"] = renames[row["concept_id"]]
write(facet_path, facet_rows, fields(facet_path))
assert len({row["concept_id"] for row in facet_rows}) == len(facet_rows)

new_concept_path = DATA / "approved_new_concepts.csv"
new_concept_rows = read(new_concept_path)
for row in new_concept_rows:
    if row["broader_id"] in replacement:
        row["broader_id"] = replacement[row["broader_id"]]
    if "/Feed processes" not in row["derived_path"]:
        row["derived_path"] = row["derived_path"].replace(
            "/Ingredient processing methods", "/Feed processes"
        )
    if row["concept_id"] in renames:
        row["preferred_label"] = renames[row["concept_id"]]
        row["derived_path"] = row["derived_path"].rsplit("/", 1)[0] + "/" + row["preferred_label"]
        row["scope_note"] = (
            f"Governed {row['preferred_label'].casefold()} value used for feed-material semantics; "
            f"distinguished from the feed-material concept labeled {original_labels[row['concept_id']]}."
        )
write(new_concept_path, new_concept_rows, fields(new_concept_path))

# Never-published duplicate definitions cease being ontology entities.
for name in ["approved_new_concepts.csv", "approved_definition_enrichments.csv"]:
    path = DATA / name
    rows = read(path)
    kept = [row for row in rows if row["concept_id"] not in replacement]
    assert 0 <= len(rows) - len(kept) <= len(replacement)
    write(path, kept, fields(path))

# Superseded collision decisions encoded invalid identity logic; current
# remediation table becomes governing record for these groups.
collision_path = DATA / "approved_ontology_collision_decisions.csv"
collision_rows = read(collision_path)
kept = [
    row for row in collision_rows
    if not any(identifier in replacement for identifier in row["concept_ids"].split(";"))
]
assert 0 <= len(collision_rows) - len(kept) <= len(replacement)
write(collision_path, kept, fields(collision_path))

# Registry remains immutable history, but retired IDs cannot be reused.
registry_path = DATA / "livestock_id_registry.csv"
registry_rows = read(registry_path)
seen = set()
for row in registry_rows:
    if row["concept_id"] in replacement:
        seen.add(row["concept_id"])
        row["status"] = "retired-before-publication"
        row["allocation_basis"] = (
            "Retired by approved identity-integrity remediation; reuse existing "
            + replacement[row["concept_id"]]
            + ". Identifier must not be reassigned."
        )
    if row["concept_id"] in renames:
        row["preferred_label"] = renames[row["concept_id"]]
        row["allocation_basis"] = (
            "Renamed by approved identity-integrity remediation to distinguish "
            "facet meaning from same-label feed-material concept."
        )
assert seen == set(replacement)
write(registry_path, registry_rows, fields(registry_path))

print(
    f"Applied {len(replacement)} canonical replacements across "
    f"{replacement_count} governed references."
)
