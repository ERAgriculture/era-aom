#!/usr/bin/env python3
"""Build deterministic feed-identity review candidates without merging concepts."""
import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/livestock-staging/legacy_records.csv"
OUT = ROOT / "review/livestock-v4"

EMPTY = {"", "na", "no match", "no match in aom", "false"}
# ILRI feed codes are retained only in private source provenance. That system is
# changing, so its identifiers do not trigger identity review or publication.
EXTERNAL_FIELDS = ("Feedipedia", "CPC_Code_Product")
PROCESS_TERMS = {
    "alkali treated", "autoclaved", "boiled", "chopped", "cracked", "crushed",
    "defatted", "dried", "ensiled", "enzyme treated", "extruded", "fermented",
    "ground", "heated", "hydrolysed", "milled", "molasses treated", "pelleted",
    "pressed", "roasted", "soaked", "sprouted", "urea treated", "wilted",
}
FORM_TERMS = {"block", "cake", "flake", "grain", "hay", "liquid", "meal", "pulp", "whole"}


def normalized(value):
    value = value.casefold().replace("corn", "maize")
    replacements = {
        r"\b(milled|meal|grounded)\b": "ground",
        r"\b(silage|ensilation)\b": "ensiled",
        r"\btoasted\b": "roasted",
        r"\bcooked\b": "heated",
    }
    for pattern, replacement in replacements.items():
        value = re.sub(pattern, replacement, value)
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value)).strip()


def clean_external(value):
    value = value.strip()
    return "" if value.casefold() in EMPTY else value


with SOURCE.open(encoding="utf-8", newline="") as handle:
    source_rows = list(csv.DictReader(handle))
all_rows = [row for row in source_rows if row["AOM"]]
rows = [row for row in all_rows if row["L5"] == "Feed Ingredient"]

by_id = {row["AOM"]: row for row in rows}
lexical = defaultdict(set)
for row in rows:
    for label in [row["Edge_Value"], *row["Synonym"].split(";")]:
        key = normalized(label)
        if key:
            lexical[key].add(row["AOM"])

lexical_rows = []
for key, concept_ids in sorted(lexical.items()):
    if len(concept_ids) < 2:
        continue
    ids = sorted(concept_ids)
    lexical_rows.append({
        "collision_key": key,
        "concept_ids": ";".join(ids),
        "preferred_labels": ";".join(by_id[value]["Edge_Value"] for value in ids),
        "candidate_count": len(ids),
        "status": "review-required",
        "recommended_action": "Compare definitions, hierarchy, occurrences, and external identifiers; retain one ID only when identity is confirmed.",
    })

external = defaultdict(set)
for row in rows:
    for field in EXTERNAL_FIELDS:
        value = clean_external(row[field])
        if value:
            external[(field, value)].add(row["AOM"])

external_rows = []
for (field, value), concept_ids in sorted(external.items()):
    if len(concept_ids) < 2:
        continue
    ids = sorted(concept_ids)
    external_rows.append({
        "mapping_system": field,
        "mapping_value": value,
        "concept_ids": ";".join(ids),
        "preferred_labels": ";".join(by_id[item]["Edge_Value"] for item in ids),
        "candidate_count": len(ids),
        "status": "granularity-review-required",
        "recommended_action": "Determine whether mapping identifies primary feed, component, processed material, or broad source; do not infer concept identity from shared code.",
    })

lexical_by_id = defaultdict(list)
for item in lexical_rows:
    for concept_id in item["concept_ids"].split(";"):
        lexical_by_id[concept_id].append(item["collision_key"])

cereal_rows = []
for row in rows:
    if not any("cereal" in row[field].casefold() for field in ("L6", "L7", "L8")):
        continue
    label = row["Edge_Value"].casefold()
    processes = sorted(term for term in PROCESS_TERMS if re.search(rf"\b{re.escape(term)}\b", label))
    forms = sorted(term for term in FORM_TERMS if re.search(rf"\b{re.escape(term)}\b", label))
    cereal_rows.append({
        "case_id": "CEREAL-" + row["AOM"].removeprefix("AOM_"),
        "concept_id": row["AOM"],
        "preferred_label": row["Edge_Value"],
        "hierarchy_path": row["Derived_Path"],
        "source_context": row["L8"],
        "component_or_form_terms": ";".join(forms),
        "process_terms": ";".join(processes),
        "definition_status": "present" if row["Description"].strip() else "missing",
        "lexical_collision_keys": ";".join(lexical_by_id[row["AOM"]]),
        "feedipedia": clean_external(row["Feedipedia"]),
        "agrovoc": clean_external(row["Agrovoc"]),
        "cpc_product": clean_external(row["CPC_Code_Product"]),
        "review_status": "review-required",
        "proposed_disposition": "",
        "reviewer": "",
        "review_date": "",
        "rationale": "",
    })

exact_labels = defaultdict(set)
for row in all_rows:
    key = normalized(row["Edge_Value"])
    if key:
        exact_labels[key].add(row["AOM"])
all_by_id = {row["AOM"]: row for row in all_rows}
preferred_collision_rows = []
for key, ids_set in sorted(exact_labels.items()):
    if len(ids_set) < 2:
        continue
    ids = sorted(ids_set)
    preferred_collision_rows.append({
        "collision_key": key,
        "concept_ids": ";".join(ids),
        "preferred_labels": ";".join(all_by_id[item]["Edge_Value"] for item in ids),
        "hierarchy_paths": " | ".join(all_by_id[item]["Derived_Path"] for item in ids),
        "candidate_count": len(ids),
        "status": "review-required",
        "recommended_action": "Confirm duplicate, contextual distinction, relabel, or hold; never merge automatically.",
    })
duplicate_label_groups = len(preferred_collision_rows)
summary_rows = [
    {"scope": "all AOM", "quality_signal": "source rows", "count": len(source_rows), "severity": "baseline", "interpretation": "Canonical-workbook-aligned source records audited.", "next_action": "Preserve baseline."},
    {"scope": "all AOM", "quality_signal": "identified source rows", "count": len(all_rows), "severity": "high", "interpretation": "One source record lacks an AOM identifier.", "next_action": "Review unidentified source record before cutover."},
    {"scope": "all AOM", "quality_signal": "missing definitions", "count": sum(not row["Description"].strip() for row in all_rows), "severity": "high", "interpretation": "Identity and scope cannot be reviewed reliably from labels alone.", "next_action": "Author or source definitions by domain."},
    {"scope": "all AOM", "quality_signal": "normalized preferred-label collisions", "count": duplicate_label_groups, "severity": "high", "interpretation": "Potential duplicates, contextual variants, or over-normalized labels.", "next_action": "Review identity; never merge automatically."},
    {"scope": "feed ingredients", "quality_signal": "concepts", "count": len(rows), "severity": "baseline", "interpretation": "Feed-material review scope.", "next_action": "Review in domain batches."},
    {"scope": "feed ingredients", "quality_signal": "lexical collision groups", "count": len(lexical_rows), "severity": "high", "interpretation": "Preferred and alternate labels collide after documented terminology normalization.", "next_action": "Compare hierarchy, definitions, source occurrences, and public mappings."},
    {"scope": "feed ingredients", "quality_signal": "shared public-identifier groups", "count": len(external_rows), "severity": "medium", "interpretation": "Feedipedia or CPC mappings span multiple semantic levels.", "next_action": "Review mapping granularity; shared mapping does not prove identity."},
    {"scope": "cereal feed materials", "quality_signal": "review candidates", "count": len(cereal_rows), "severity": "high", "interpretation": "Coherent first expert-review batch with extracted process/form signals.", "next_action": "Complete disposition, reviewer, date, and rationale."},
    {"scope": "cereal feed materials", "quality_signal": "missing definitions", "count": sum(row["definition_status"] == "missing" for row in cereal_rows), "severity": "high", "interpretation": "Nearly all cereal identities lack explicit scope definitions.", "next_action": "Prioritize ambiguous whole/grain/component concepts."},
]

OUT.mkdir(parents=True, exist_ok=True)
for name, records in {
    "feed_lexical_identity_candidates.csv": lexical_rows,
    "feed_external_granularity_candidates.csv": external_rows,
    "cereal_feed_material_review.csv": cereal_rows,
    "ontology_quality_summary.csv": summary_rows,
    "ontology_pref_label_collision_candidates.csv": preferred_collision_rows,
}.items():
    path = OUT / name
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)

print(
    f"Audited {len(rows)} feed concepts: {len(lexical_rows)} lexical collision "
    f"groups; {len(external_rows)} shared-public-identifier groups; "
    f"{len(cereal_rows)} cereal review candidates."
)
