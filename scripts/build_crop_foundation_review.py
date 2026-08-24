#!/usr/bin/env python3
"""Build recommendation-only crop-foundation governance artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "review/crop-foundation-v1"
PILOT = ROOT / "data/pilot"
LIVESTOCK = ROOT / "data/livestock-staging"
REVIEW_DATE = "2026-08-24"

EXPECTED_COLUMNS = {
    "prac": [
        "Code", "Theme", "Theme.Code", "Practice", "Practice.Code",
        "Subpractice", "Subpractice.Code", "Subpractice.S",
        "Subpractice.Suffix", "Definition", "Notes", "Linked.Tab",
        "Linked.Col", "Depreciated",
    ],
    "out": [
        "Code", "Pillar", "Pillar.Code", "Subpillar", "Subpillar.Code",
        "Indicator", "Indicator.Code", "Subindicator", "Subindicator.Short",
        "Subindicator.Code", "Definition", "Notes", "Example units",
        "Original.Outcome", "Negative Values", "Sign", "TC.Ratio",
        "Not.Perc", "Depreciated", "Previous.Names",
    ],
    "out_econ": ["AOM", "Category", "Variable", "Definition"],
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        if not rows:
            raise ValueError(f"Cannot infer columns for empty output: {path}")
        fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    return " ".join(value.casefold().split())


def normalize_code_artifact(value: str) -> str:
    if not re.fullmatch(r"\d+\.\d+", value or ""):
        return value
    if "999999999" not in value and "000000000" not in value:
        return value
    number = float(value)
    rounded = round(number, 8)
    return f"{rounded:.8f}".rstrip("0").rstrip(".")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_workbook(workbook: Path, output_dir: Path) -> None:
    r_code = r'''
args <- commandArgs(trailingOnly = TRUE)
workbook <- args[[1]]
out_dir <- args[[2]]
sheets <- c("prac", "out", "out_econ")
for (sheet in sheets) {
  value <- readxl::read_excel(workbook, sheet = sheet, .name_repair = "minimal")
  value <- data.frame(source_row = seq_len(nrow(value)) + 1L, value, check.names = FALSE)
  write.table(
    value,
    file.path(out_dir, paste0(sheet, ".tsv")),
    sep = "\t",
    quote = TRUE,
    qmethod = "double",
    row.names = FALSE,
    na = "",
    fileEncoding = "UTF-8"
  )
}
'''
    subprocess.run(
        ["Rscript", "-e", r_code, str(workbook), str(output_dir)],
        check=True,
        text=True,
    )


def read_source_tables(workbook: Path) -> dict[str, list[dict[str, str]]]:
    with tempfile.TemporaryDirectory(prefix="era-crop-foundation-") as tmp:
        tmp_path = Path(tmp)
        extract_workbook(workbook, tmp_path)
        tables = {}
        for sheet, expected in EXPECTED_COLUMNS.items():
            with (tmp_path / f"{sheet}.tsv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            actual = list(rows[0]) if rows else []
            required = ["source_row", *expected]
            if actual != required:
                raise ValueError(f"Unexpected {sheet} columns: {actual}")
            tables[sheet] = rows
        return tables


def source_identity(sheet: str, row: dict[str, str]) -> str:
    if sheet == "prac":
        return f"prac:{row['Code']}"
    if sheet == "out":
        return f"out:{row['Code']}"
    return f"out_econ:row:{row['source_row']}"


def source_label(sheet: str, row: dict[str, str]) -> str:
    return row[{"prac": "Subpractice", "out": "Subindicator", "out_econ": "Variable"}[sheet]]


def source_definition(sheet: str, row: dict[str, str]) -> str:
    return row.get("Definition", "")


def source_code(sheet: str, row: dict[str, str]) -> str:
    return row.get("Code", row.get("AOM", ""))


def classify_domain(sheet: str, row: dict[str, str]) -> str:
    if sheet == "out_econ":
        return "cross-domain-economics"
    if sheet == "prac":
        theme = row["Theme"]
        if theme == "Animals":
            return "livestock"
        if theme == "Energy":
            return "energy"
        if theme == "Non-CSA":
            return "cross-domain"
        return "crop"
    if row["Subpillar"] == "Cookstove":
        return "energy"
    if row["Subpillar"] == "Livestock Diet":
        return "livestock"
    label = normalize_text(row["Subindicator"])
    animal_terms = (
        "animal", "milk", "meat", "egg", "feed ", "weight gain",
        "reproductive yield", "protein conversion",
    )
    if any(term in label for term in animal_terms):
        return "livestock"
    if row["Subpillar"] in {"Economics", "Social"}:
        return "cross-domain"
    if row["Subpillar"] in {"Carbon Stocks", "Emissions", "Efficiency", "Physical"}:
        return "cross-domain-environment"
    return "crop"


def recommended_resource(domain: str) -> str:
    if domain == "crop":
        return "aom-crop"
    if domain == "livestock":
        return "aom-livestock"
    if domain == "energy":
        return "module-unassigned"
    if domain == "cross-domain-economics":
        return "aom-core-model-plus-domain-variable"
    return "module-review"


def load_pilot() -> dict[str, object]:
    concepts = {row["concept_id"]: row for row in read_csv(PILOT / "concepts.csv")}
    labels = read_csv(PILOT / "labels.csv")
    pref = {
        row["concept_id"]: row["label"]
        for row in labels if row["label_type"] == "pref" and row["language"] == "en"
    }
    relations = read_csv(PILOT / "relations.csv")
    parent = {row["subject_id"]: row["object_id"] for row in relations if row["relation_type"] == "broader"}
    source_records = {
        (row["source_sheet"], row["source_row"]): row["concept_id"]
        for row in read_csv(PILOT / "source_records.csv")
    }

    def concept_path(concept_id: str) -> str:
        values = []
        seen = set()
        current = concept_id
        while current and current not in seen:
            seen.add(current)
            values.append(pref.get(current, current))
            current = parent.get(current, "")
        return " / ".join(reversed(values))

    return {
        "concepts": concepts,
        "labels": labels,
        "pref": pref,
        "relations": relations,
        "parent": parent,
        "source_records": source_records,
        "paths": {concept_id: concept_path(concept_id) for concept_id in concepts},
        "id_registry": read_csv(PILOT / "id_registry.csv"),
        "properties": read_csv(PILOT / "properties.csv"),
    }


def load_aom() -> dict[str, object]:
    labels = read_csv(LIVESTOCK / "labels.csv")
    definitions = read_csv(LIVESTOCK / "definitions.csv")
    concepts = {row["concept_id"]: row for row in read_csv(LIVESTOCK / "concepts.csv")}
    mappings = [row for row in read_csv(LIVESTOCK / "mappings.csv") if row["target_scheme"] == "era"]
    pref = {
        row["concept_id"]: row["label"]
        for row in labels if row["label_type"] == "pref" and row["language"] == "en"
    }
    definition_by_id = defaultdict(list)
    for row in definitions:
        if row["language"] == "en" and row["definition"]:
            definition_by_id[row["concept_id"]].append(row["definition"])
    labels_by_normalized = defaultdict(list)
    for row in labels:
        if row["language"] == "en" and row["label"]:
            labels_by_normalized[normalize_text(row["label"])].append(row)
    mappings_by_code = defaultdict(list)
    for row in mappings:
        mappings_by_code[row["target_id"]].append(row)
    return {
        "labels": labels,
        "pref": pref,
        "definitions": definition_by_id,
        "concepts": concepts,
        "labels_by_normalized": labels_by_normalized,
        "mappings_by_code": mappings_by_code,
    }


def parse_agro(agro_snapshot: Path) -> tuple[dict[str, list[dict[str, str]]], str]:
    rdf = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
    rdfs = "{http://www.w3.org/2000/01/rdf-schema#}"
    labels = defaultdict(list)
    root = ET.parse(agro_snapshot).getroot()
    for element in root:
        about = element.attrib.get(rdf + "about", "")
        if not about:
            continue
        for child in element:
            if child.tag == rdfs + "label" and child.text:
                label = " ".join(child.text.split())
                labels[normalize_text(label)].append({"uri": about, "label": label})
    return labels, sha256(agro_snapshot)


def authority_name(uri: str) -> str:
    local = uri.rstrip("/").rsplit("/", 1)[-1]
    prefix = local.split("_", 1)[0]
    return {
        "AGRO": "AgrO",
        "ENVO": "ENVO imported through AgrO",
        "CHEBI": "ChEBI imported through AgrO",
    }.get(prefix, "AgrO imported authority")


def build_authority_candidates(
    tables: dict[str, list[dict[str, str]]], agro_labels: dict[str, list[dict[str, str]]]
) -> tuple[list[dict[str, object]], dict[tuple[str, str], list[str]]]:
    rows = []
    by_source = defaultdict(list)
    for sheet in ("prac", "out", "out_econ"):
        for row in tables[sheet]:
            label = source_label(sheet, row)
            for match in agro_labels.get(normalize_text(label), []):
                authority_id = match["uri"].rstrip("/").rsplit("/", 1)[-1]
                rows.append({
                    "source_sheet": sheet,
                    "source_row": row["source_row"],
                    "source_id": source_identity(sheet, row),
                    "source_label": label,
                    "authority": authority_name(match["uri"]),
                    "authority_id": authority_id,
                    "authority_uri": match["uri"],
                    "authority_label": match["label"],
                    "match_signal": "normalized-exact-label",
                    "recommended_disposition": "identity-mapping-review-required",
                    "status": "held",
                    "claim_boundary": "Exact label is candidate evidence only; scope, definition, and entity type remain unverified.",
                    "evidence_id": "E-AUTH-AGRO-SNAPSHOT",
                })
                by_source[(sheet, row["source_row"])].append(authority_id)
    rows.sort(key=lambda item: (item["source_sheet"], int(item["source_row"]), item["authority_id"]))
    return rows, by_source


def source_aom_signals(sheet: str, row: dict[str, str], aom: dict[str, object]) -> dict[str, object]:
    label = source_label(sheet, row)
    definition = source_definition(sheet, row)
    corrected_code = normalize_code_artifact(source_code(sheet, row))
    mapping_rows = aom["mappings_by_code"].get(corrected_code, []) if sheet != "out_econ" else []
    mapping_ids = sorted({item["subject_id"] for item in mapping_rows})
    label_rows = aom["labels_by_normalized"].get(normalize_text(label), [])
    label_ids = sorted({item["concept_id"] for item in label_rows})
    exact_definition_ids = []
    if definition:
        normalized_definition = normalize_text(definition)
        for concept_id in label_ids:
            if any(normalize_text(value) == normalized_definition for value in aom["definitions"].get(concept_id, [])):
                exact_definition_ids.append(concept_id)
    return {
        "mapping_ids": mapping_ids,
        "label_ids": label_ids,
        "exact_definition_ids": sorted(exact_definition_ids),
        "corrected_code": corrected_code,
    }


def practice_model(row: dict[str, str]) -> str:
    label = row["Subpractice"]
    notes = normalize_text(row["Notes"])
    if row["Code"] == "h16":
        return "source-field-or-context-descriptor"
    if "automatically generated" in notes:
        return "derived-comparison-record"
    if (
        re.search(r"(^|\b)(control|experiment|baseline|basal|conventional|unimproved|unspecified)(\b|$)", normalize_text(label))
        or normalize_text(label).startswith("no ")
    ):
        return "practice-or-condition-plus-experimental-role"
    return "agricultural-practice-concept"


def disposition_for_row(
    sheet: str,
    row: dict[str, str],
    signals: dict[str, object],
) -> tuple[str, str, str]:
    deprecated = row.get("Depreciated", "").upper() == "TRUE"
    missing_definition = not source_definition(sheet, row).strip()
    unknown_status = sheet in {"prac", "out"} and not row.get("Depreciated", "").strip()
    label = source_label(sheet, row)
    distinct_context = sheet == "prac" and normalize_text(label) in {
        "urea", "ash", "heat tolerance", "unspecified",
    }
    if sheet == "out_econ":
        if missing_definition:
            return "hold-source-correction-before-id-allocation", "held", "Economic row lacks definition and all rows still carry placeholder AOM identifiers."
        return "hold-id-allocation-pending-economic-decomposition", "held", "Economic variable needs measure, cost/benefit class, object, basis, and valuation review before identity allocation."
    if deprecated:
        return "hold-deprecated-source-record", "held", "Deprecated source row requires replacement or lifecycle decision; it must not become a new active identity."
    if missing_definition or unknown_status:
        return "hold-source-quality-correction", "held", "Definition or lifecycle status is incomplete."
    if sheet == "prac" and row["Code"] == "h16":
        return "move-to-source-schema-review", "held", "Predominant biodigester model is a descriptor field, not a practice identity."
    if distinct_context:
        return "retain-distinct-context-pending-identity-review", "held", "Same label exists in AOM with different feed, animal, or generic scope; label equality cannot merge identities."
    if len(signals["mapping_ids"]) > 1:
        return "hold-ambiguous-legacy-code-mapping", "held", "Legacy ERA code points to multiple AOM identifiers."
    if len(signals["exact_definition_ids"]) == 1:
        return "reuse-existing-aom-id-candidate", "proposed", "Normalized label and definition match one existing AOM concept; module placement still needs approval."
    if len(signals["mapping_ids"]) == 1:
        return "hold-existing-aom-code-mapping-review", "held", "One legacy code mapping exists but exact identity is not established by definition."
    return "retain-source-candidate-pending-row-review", "proposed", "No approved existing identity found; retain source record without allocating a public identifier."


def build_source_dispositions(
    tables: dict[str, list[dict[str, str]]],
    pilot: dict[str, object],
    aom: dict[str, object],
    authority_by_source: dict[tuple[str, str], list[str]],
) -> tuple[list[dict[str, object]], dict[tuple[str, str], dict[str, object]]]:
    rows = []
    signals_by_source = {}
    for sheet in ("prac", "out", "out_econ"):
        for row in tables[sheet]:
            key = (sheet, row["source_row"])
            signals = source_aom_signals(sheet, row, aom)
            signals_by_source[key] = signals
            domain = classify_domain(sheet, row)
            current_id = pilot["source_records"].get(key, "")
            if sheet == "prac":
                model = practice_model(row)
                issue = "Current pilot conflates source hierarchy, concept identity, and experimental comparison context."
            elif sheet == "out":
                model = "sosa-property-plus-procedure-quantity-and-basis"
                issue = "Current pilot treats reporting hierarchy and analytical metadata as one SKOS concept tree."
                if signals["corrected_code"] != row["Code"]:
                    issue += " Source code also contains a binary numeric artifact."
                if current_id and pilot["concepts"].get(current_id, {}).get("notation") != row["Code"]:
                    issue += " Pilot notation differs from source lexical code."
            else:
                model = "economic-observable-plus-accounting-context"
                issue = "Source is absent from pilot, uses placeholder identifiers, and treats accounting category as intrinsic hierarchy."
            action, status, rationale = disposition_for_row(sheet, row, signals)
            rows.append({
                "source_sheet": sheet,
                "source_row": row["source_row"],
                "source_id": source_identity(sheet, row),
                "source_code_lexical": source_code(sheet, row),
                "proposed_governed_code": signals["corrected_code"],
                "source_label": source_label(sheet, row),
                "source_status": row.get("Depreciated", "not-applicable") or "unknown",
                "domain": domain,
                "current_pilot_id": current_id,
                "current_pilot_path": pilot["paths"].get(current_id, ""),
                "current_model_issue": issue,
                "recommended_resource": recommended_resource(domain),
                "recommended_model": model,
                "recommended_action": action,
                "decision_status": status,
                "legacy_code_mapping_candidates": ";".join(signals["mapping_ids"]),
                "same_label_aom_candidates": ";".join(signals["label_ids"]),
                "exact_definition_aom_candidates": ";".join(signals["exact_definition_ids"]),
                "authority_label_candidates": ";".join(sorted(set(authority_by_source.get(key, [])))),
                "evidence_ids": "E-SRC-WORKBOOK;E-PILOT;E-AOM-STAGING",
                "reviewer": "",
                "review_date": "",
                "rationale": rationale,
            })
    return rows, signals_by_source


def build_hierarchy_node_review(pilot: dict[str, object]) -> list[dict[str, object]]:
    children = defaultdict(list)
    for row in pilot["relations"]:
        if row["relation_type"] == "broader":
            children[row["object_id"]].append(row["subject_id"])
    pref_collision_count = Counter(normalize_text(value) for value in pilot["pref"].values())
    rows = []
    for item in pilot["id_registry"]:
        concept_id = item["concept_id"]
        label = pilot["pref"].get(concept_id, item["source_label"])
        child_ids = children.get(concept_id, [])
        same_label_children = [
            child_id for child_id in child_ids
            if normalize_text(pilot["pref"].get(child_id, "")) == normalize_text(label)
        ]
        concept_type = pilot["concepts"].get(concept_id, {}).get("concept_type", item["concept_type"])
        if concept_type in {"theme", "pillar", "subpillar", "indicator"}:
            role = "editorial-navigation"
            representation = "skos:Collection"
            rationale = "Source level organizes reporting or browsing; it does not establish inherent broader meaning."
        elif same_label_children:
            role = "duplicate-group-and-leaf"
            representation = "collapse-or-reuse-leaf-after-identity-review"
            rationale = "Generated parent repeats a child label and creates parallel identity without evidence."
        else:
            role = "candidate-practice-group"
            representation = "skos:Concept-or-Collection-after-extensional-review"
            rationale = "Practice grouping may be a true broader practice or only an editorial grouping; source structure alone cannot decide."
        rows.append({
            "concept_id": concept_id,
            "scheme_id": item["scheme_id"],
            "concept_type": concept_type,
            "preferred_label": label,
            "source_notation": item["source_notation"],
            "parent_id": item["parent_id"],
            "direct_child_count": len(child_ids),
            "same_label_child_ids": ";".join(sorted(same_label_children)),
            "normalized_pref_label_collision_count": pref_collision_count[normalize_text(label)],
            "reviewed_role": role,
            "recommended_representation": representation,
            "recommended_action": "do-not-promote-current-node-as-is",
            "status": "held",
            "evidence_ids": "E-PILOT;E-SKOS",
            "rationale": rationale,
        })
    rows.sort(key=lambda item: item["concept_id"])
    return rows


def build_hierarchy_edge_review(pilot: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for index, item in enumerate(pilot["relations"], start=1):
        subject_id = item["subject_id"]
        object_id = item["object_id"]
        subject_label = pilot["pref"].get(subject_id, subject_id)
        object_label = pilot["pref"].get(object_id, object_id)
        object_type = pilot["concepts"].get(object_id, {}).get("concept_type", "")
        same_label = normalize_text(subject_label) == normalize_text(object_label)
        if same_label:
            disposition = "reject-broader-collapse-identity"
            proposed_relation = "none-pending-identity-resolution"
            rationale = "Subject and object have same normalized preferred label; broader assertion manufactures duplicate identity."
        elif object_type in {"theme", "pillar", "subpillar", "indicator"}:
            disposition = "replace-with-navigation-membership"
            proposed_relation = "member-of-reporting-collection"
            rationale = "Object is an editorial source level; membership preserves navigation without asserting inherent broader meaning."
        else:
            disposition = "hold-specialization-review"
            proposed_relation = "skos:broader-candidate"
            rationale = "Practice-group relation may express specialization, but parent identity and extension require review."
        rows.append({
            "edge_id": f"HIER-{index:04d}",
            "subject_id": subject_id,
            "subject_label": subject_label,
            "subject_type": pilot["concepts"].get(subject_id, {}).get("concept_type", ""),
            "current_relation": item["relation_type"],
            "object_id": object_id,
            "object_label": object_label,
            "object_type": object_type,
            "recommended_disposition": disposition,
            "proposed_relation": proposed_relation,
            "status": "held",
            "evidence_ids": "E-PILOT;E-SKOS",
            "rationale": rationale,
        })
    return rows


def build_collisions(
    tables: dict[str, list[dict[str, str]]],
    pilot: dict[str, object],
    aom: dict[str, object],
    signals_by_source: dict[tuple[str, str], dict[str, object]],
) -> list[dict[str, object]]:
    rows = []
    labels_by_normalized = defaultdict(list)
    for item in pilot["labels"]:
        if item["language"] == "en" and item["label"]:
            labels_by_normalized[normalize_text(item["label"])].append(item)
    group_number = 0
    for normalized, entries in sorted(labels_by_normalized.items()):
        concept_ids = sorted({entry["concept_id"] for entry in entries})
        if len(concept_ids) < 2:
            continue
        group_number += 1
        for concept_id in concept_ids:
            own = [entry for entry in entries if entry["concept_id"] == concept_id]
            rows.append({
                "collision_group_id": f"PILOT-{group_number:03d}",
                "collision_scope": "pilot-internal",
                "normalized_label": normalized,
                "source_or_pilot_id": concept_id,
                "source_label_types": ";".join(sorted({entry["label_type"] for entry in own})),
                "source_concept_type": pilot["concepts"].get(concept_id, {}).get("concept_type", ""),
                "other_concept_id": ";".join(item for item in concept_ids if item != concept_id),
                "other_label_types": "",
                "definition_match": "not-assessed",
                "code_mapping_match": "not-applicable",
                "recommended_disposition": "global-identity-review-before-promotion",
                "status": "held",
                "rationale": "Same normalized English label appears on multiple pilot concepts or generated hierarchy nodes.",
            })
    global_number = 0
    for sheet in ("prac", "out", "out_econ"):
        for source in tables[sheet]:
            normalized = normalize_text(source_label(sheet, source))
            aom_entries = aom["labels_by_normalized"].get(normalized, [])
            for concept_id in sorted({entry["concept_id"] for entry in aom_entries}):
                global_number += 1
                signal = signals_by_source[(sheet, source["source_row"])]
                exact = concept_id in signal["exact_definition_ids"]
                code_match = concept_id in signal["mapping_ids"]
                if exact:
                    disposition = "reuse-existing-aom-id-candidate"
                    rationale = "Normalized preferred label and definition match; stable AOM identity has priority pending module review."
                elif sheet == "prac" and normalized in {"urea", "ash", "heat tolerance", "unspecified"}:
                    disposition = "retain-distinct-context-pending-scope-definition"
                    rationale = "Same label names a different feed, animal, generic, or field-application entity; do not merge by label."
                else:
                    disposition = "identity-review-required"
                    rationale = "Label collision lacks enough evidence for equivalence or distinction."
                label_types = sorted({
                    entry["label_type"] for entry in aom_entries if entry["concept_id"] == concept_id
                })
                rows.append({
                    "collision_group_id": f"AOM-{global_number:03d}",
                    "collision_scope": "source-to-aom",
                    "normalized_label": normalized,
                    "source_or_pilot_id": source_identity(sheet, source),
                    "source_label_types": "preferred-source-label",
                    "source_concept_type": sheet,
                    "other_concept_id": concept_id,
                    "other_label_types": ";".join(label_types),
                    "definition_match": "exact-normalized" if exact else "not-exact-or-missing",
                    "code_mapping_match": "yes" if code_match else "no",
                    "recommended_disposition": disposition,
                    "status": "proposed" if exact else "held",
                    "rationale": rationale,
                })
    return rows


def build_source_quality_issues(
    tables: dict[str, list[dict[str, str]]], pilot: dict[str, object]
) -> list[dict[str, object]]:
    issues = []

    def add(sheet: str, row: dict[str, str], issue_type: str, field: str, value: str, severity: str, action: str, rationale: str) -> None:
        issues.append({
            "issue_id": f"SQ-{len(issues) + 1:04d}",
            "source_sheet": sheet,
            "source_row": row["source_row"],
            "source_id": source_identity(sheet, row),
            "source_label": source_label(sheet, row),
            "issue_type": issue_type,
            "field": field,
            "current_value": value,
            "severity": severity,
            "recommended_action": action,
            "status": "open",
            "rationale": rationale,
        })

    practice_code_counts = Counter(row["Subpractice.Code"] for row in tables["prac"] if row["Subpractice.Code"])
    for row in tables["prac"]:
        if not row["Definition"].strip():
            add("prac", row, "missing-definition", "Definition", "", "high", "correct-source-before-promotion", "Public concept identity lacks a definition.")
        if not row["Depreciated"].strip():
            add("prac", row, "unknown-lifecycle-status", "Depreciated", "", "high", "resolve-active-or-deprecated", "Blank lifecycle value is neither active nor deprecated.")
        if row["Depreciated"].upper() == "TRUE":
            add("prac", row, "deprecated-source-record", "Depreciated", row["Depreciated"], "information", "record-replacement-or-retirement", "Deprecated record requires explicit lifecycle treatment.")
        for field in ("Subpractice.Suffix", "Linked.Tab", "Linked.Col"):
            if row[field] == "NA":
                add("prac", row, "literal-na-sentinel", field, "NA", "medium", "normalize-to-null-with-raw-provenance", "Literal NA is missing-value syntax, not semantic content.")
        code = row["Subpractice.Code"]
        if code and practice_code_counts[code] > 1:
            add("prac", row, "duplicate-subpractice-code", "Subpractice.Code", code, "high", "resolve-code-scope-and-uniqueness", "One compact code is assigned to multiple source labels.")

    indicator_codes_by_label = defaultdict(set)
    for row in tables["out"]:
        indicator_codes_by_label[normalize_text(row["Indicator"])].add(row["Indicator.Code"])
    for row in tables["out"]:
        corrected = normalize_code_artifact(row["Code"])
        if corrected != row["Code"]:
            add("out", row, "binary-numeric-code-artifact", "Code", row["Code"], "high", "approve-lexical-code-correction-crosswalk", f"Proposed governed code is {corrected}; source lexical value must remain in provenance.")
        key = ("out", row["source_row"])
        current_id = pilot["source_records"].get(key, "")
        notation = pilot["concepts"].get(current_id, {}).get("notation", "")
        if notation and notation != row["Code"]:
            add("out", row, "pilot-notation-mutation", "notation", notation, "high", "stop-vector-wide-numeric-formatting", "Pilot notation silently differs from canonical source code.")
        if row["Sign"] not in {"p", "n"}:
            add("out", row, "invalid-sign-code", "Sign", row["Sign"], "medium", "normalize-controlled-code", "Sign field is not encoded consistently as p or n.")
        if row["Not.Perc"] not in {"Y", "N"}:
            add("out", row, "non-boolean-not-percentage", "Not.Perc", row["Not.Perc"], "medium", "replace-with-reviewed-analytical-rule", "Field contains uncertain or parenthetical values and is not a Boolean contract.")
        if row["Depreciated"].upper() == "TRUE":
            add("out", row, "deprecated-source-record", "Depreciated", row["Depreciated"], "information", "record-replacement-or-retirement", "Deprecated outcome requires explicit lifecycle treatment.")
        if len(indicator_codes_by_label[normalize_text(row["Indicator"])]) > 1:
            add("out", row, "indicator-label-code-collision", "Indicator", row["Indicator"], "high", "separate-label-from-reporting-node-identity", "Same indicator label carries more than one source code.")

    econ_label_counts = Counter(normalize_text(row["Variable"]) for row in tables["out_econ"])
    defect_actions = {
        "family labor cost (female)": "correct-sex-reference-in-definition",
        "hired labor cost": "replace-family-labour-definition",
        "nutrient/soil management": "replace-example-with-variable-definition",
        "loans": "clarify-interest-or-financing-cost-identity",
    }
    for row in tables["out_econ"]:
        if row["AOM"] == "AOM_will_add_unique_value":
            add("out_econ", row, "placeholder-identifier", "AOM", row["AOM"], "high", "hold-id-allocation", "Placeholder is repeated across all rows and cannot identify a public concept.")
        if not row["Definition"].strip():
            add("out_econ", row, "missing-definition", "Definition", "", "high", "correct-source-before-id-allocation", "Economic variable lacks a definition.")
        if econ_label_counts[normalize_text(row["Variable"])] > 1:
            add("out_econ", row, "duplicate-contextual-variable-label", "Variable", row["Variable"], "high", "model-cost-context-or-rename-scoped-variables", "Same label is used for fixed acquisition/depreciation and variable rental/maintenance contexts.")
        normalized = normalize_text(row["Variable"])
        if normalized in defect_actions:
            add("out_econ", row, "definition-content-defect", "Definition", row["Definition"], "high", defect_actions[normalized], "Definition does not reliably describe named economic variable.")
    return issues


def authority_comparison() -> list[dict[str, str]]:
    return [
        {
            "authority": "W3C SKOS Reference",
            "authority_url": "https://www.w3.org/TR/skos-reference/",
            "supports": "Concept schemes, labels, notations, semantic relations, mappings, and labeled or ordered collections.",
            "does_not_support": "Workbook reporting levels as automatic broader meaning, field schemas, or observation procedure semantics.",
            "use_in_review": "Treat source navigation as collections unless inherent semantic hierarchy is reviewed.",
            "evidence_id": "E-SKOS",
            "access_date": REVIEW_DATE,
        },
        {
            "authority": "W3C SOSA/SSN 2023",
            "authority_url": "https://www.w3.org/TR/vocab-ssn-2023/",
            "supports": "Observations, sosa:Property, features of interest, procedures, results, and observation context.",
            "does_not_support": "ERA reporting pillars, economic-accounting classification, or row identity by itself.",
            "use_in_review": "Represent outcome variables as property specifications bound to procedure, result, and feature context.",
            "evidence_id": "E-SOSA",
            "access_date": REVIEW_DATE,
        },
        {
            "authority": "Crop Ontology",
            "authority_url": "https://cropontology.org/about",
            "supports": "Crop phenotypic variables decomposed into trait, method, and scale.",
            "does_not_support": "All management, livestock, social, energy, and economic outcome identities.",
            "use_in_review": "Use trait-method-scale pattern where crop phenotype variables fit its scope.",
            "evidence_id": "E-CROP-ONTOLOGY",
            "access_date": REVIEW_DATE,
        },
        {
            "authority": "AgrO",
            "authority_url": "https://github.com/AgriculturalSemantics/agro",
            "supports": "Agronomic practices, techniques, experimental variables, and reuse of OBO authorities.",
            "does_not_support": "Identity equivalence from exact label alone or ERA-specific reporting and economic rows.",
            "use_in_review": "Generate external candidate matches only; require definition, scope, and entity-type review.",
            "evidence_id": "E-AUTH-AGRO-SNAPSHOT",
            "access_date": REVIEW_DATE,
        },
        {
            "authority": "FAO AGROVOC",
            "authority_url": "https://agrovoc.fao.org/",
            "supports": "Broad multilingual agricultural terminology and external lexical or broad mapping candidates.",
            "does_not_support": "ERA source-row identity, experiment roles, variable derivations, or automatic hierarchy adoption.",
            "use_in_review": "Use in later row-level external mapping review after internal identities stabilize.",
            "evidence_id": "E-AGROVOC",
            "access_date": REVIEW_DATE,
        },
        {
            "authority": "FoodOn transformation process facet",
            "authority_url": "https://foodon.org/food-facets/food-transformation-process/",
            "supports": "Processes transforming food source or product into derived material and process-output relations.",
            "does_not_support": "Field management, experimental comparator roles, or economic variables.",
            "use_in_review": "Constrain postharvest and food-processing mappings without forcing field practices into FoodOn.",
            "evidence_id": "E-FOODON",
            "access_date": REVIEW_DATE,
        },
        {
            "authority": "QUDT",
            "authority_url": "https://www.qudt.org/catalog/qudt-catalog.html",
            "supports": "Quantity kinds, units, dimensions, and quantity values.",
            "does_not_support": "Agricultural variable identity, procedure, reporting hierarchy, or interpretation direction.",
            "use_in_review": "Bind reviewed outcome and economic measures to quantity kinds, units, and denominator bases.",
            "evidence_id": "E-QUDT",
            "access_date": REVIEW_DATE,
        },
        {
            "authority": "EU Farm Sustainability Data Network",
            "authority_url": "https://agriculture.ec.europa.eu/data-and-analysis/farm-structures-and-economics/fsdn_en",
            "supports": "Harmonized farm bookkeeping and microeconomic outputs, costs, inputs, and assets.",
            "does_not_support": "Ontology identity for each ERA economic variable or experimental outcome semantics.",
            "use_in_review": "Reference farm-accounting scope and cost classification boundaries.",
            "evidence_id": "E-FSDN",
            "access_date": REVIEW_DATE,
        },
        {
            "authority": "FAO SEEA Agriculture Forestry and Fisheries",
            "authority_url": "https://www.fao.org/fileadmin/templates/ess/ess_test_folder/Publications/Agrienvironmental/SEEA_AFF_FINAL_Clean_03.pdf",
            "supports": "Output, intermediate consumption, fixed-capital formation, inventories, and income-account boundaries.",
            "does_not_support": "Study-level variable identity or direct SKOS parentage for ERA rows.",
            "use_in_review": "Check accounting-category boundaries and asset-versus-expense context.",
            "evidence_id": "E-SEEA-AFF",
            "access_date": REVIEW_DATE,
        },
        {
            "authority": "UN System of National Accounts",
            "authority_url": "https://unstats.un.org/unsd/Nationalaccount/sna.asp",
            "supports": "International economic-accounting concepts and category boundaries.",
            "does_not_support": "Farm-trial variable granularity or agricultural semantic identity.",
            "use_in_review": "Secondary boundary check only; prefer farm-level sources for detailed modeling.",
            "evidence_id": "E-SNA",
            "access_date": REVIEW_DATE,
        },
    ]


def shared_core_candidates() -> list[dict[str, str]]:
    values = [
        ("SC-01", "Agricultural practice concept", "Reusable intervention type identity", "aom-core-candidate", "AgrO candidate", "proposed", "Compare crop and livestock practice identity before promotion."),
        ("SC-02", "Practice application", "Occurrence applying a practice to a managed system", "aom-core-candidate", "PROV/SOSA alignment review", "proposed", "Define actor, target, time, location, and applied practice."),
        ("SC-03", "Experimental role", "Role borne by study arms or applied conditions", "aom-core-candidate", "OBI alignment review", "proposed", "Generalize beyond feed-specific ExperimentalFeedRole."),
        ("SC-04", "Treatment role", "Intervention role in a comparison", "aom-core-candidate", "OBI alignment review", "proposed", "Keep separate from agricultural practice identity."),
        ("SC-05", "Comparator or control role", "Comparator, control, or reference role in a study", "aom-core-candidate", "OBI alignment review", "proposed", "Do not encode role into preferred practice label."),
        ("SC-06", "Baseline condition", "Observed or assigned pre-intervention condition", "aom-core-candidate", "SOSA/OBI alignment review", "held", "Distinguish absence, conventional management, and measured baseline."),
        ("SC-07", "Outcome property specification", "Observable or derived property being estimated", "aom-core-candidate", "sosa:Property", "proposed", "Use current SOSA Property rather than deprecated ObservableProperty."),
        ("SC-08", "Observation procedure", "Method or protocol used to obtain result", "aom-core-candidate", "sosa:Procedure", "proposed", "Needed to distinguish same property measured by different methods."),
        ("SC-09", "Derived measure specification", "Formula combining measured or supplied quantities", "aom-core-candidate", "SOSA plus ERA derivation model", "proposed", "Record numerator, denominator, formula, and interpretation."),
        ("SC-10", "Feature of interest", "Entity whose property is observed", "aom-core-candidate", "sosa:FeatureOfInterest", "proposed", "Keep crop, animal, soil, farm, plot, product, and household context explicit."),
        ("SC-11", "Quantity and unit profile", "Quantity kind, unit, scale, and denominator basis", "aom-core-candidate", "QUDT", "proposed", "Example-unit strings are evidence, not final bindings."),
        ("SC-12", "Reporting collection", "Editorial pillar, subpillar, indicator, or theme grouping", "aom-core-candidate", "skos:Collection", "proposed", "Membership must not imply inherent semantic broader relation."),
        ("SC-13", "Economic measure specification", "Economic property such as cost, income, or value", "aom-core-candidate", "SOSA/QUDT plus accounting authorities", "proposed", "Bind currency, time, object, transaction, basis, and valuation method."),
        ("SC-14", "Cost or benefit classification", "Accounting or analytical classification borne in context", "aom-core-candidate", "FSDN/SEEA-AFF", "held", "Category may vary by accounting treatment and must not become intrinsic identity automatically."),
        ("SC-15", "Module assignment", "Governed placement of identity in crop, livestock, core, or other product", "mappings-or-governance", "ERA ADR 0051", "proposed", "Energy and genuinely cross-domain rows require explicit routing."),
    ]
    return [
        {
            "candidate_id": candidate_id,
            "candidate_label": label,
            "semantic_role": role,
            "proposed_owner": owner,
            "external_alignment": alignment,
            "status": status,
            "prerequisite_or_boundary": boundary,
            "evidence_ids": "E-SKOS;E-SOSA;E-CROP-ONTOLOGY;E-AUTH-AGRO-SNAPSHOT;E-QUDT",
        }
        for candidate_id, label, role, owner, alignment, status, boundary in values
    ]


def pilot_contract_audit() -> list[dict[str, str]]:
    values = [
        ("PC-01", "Scheme scope", "Pilot labels both registries as crop-only.", "block-public-promotion", "Rename and route rows by governed module because sources include crop, livestock, energy, social, and economic content."),
        ("PC-02", "Source coverage", "out_econ has no pilot representation.", "block-completeness-claim", "Integrate 65 economic rows only after variable decomposition and source correction."),
        ("PC-03", "Source codes", "Outcome vector formatting changes 58 integer codes to .0 and treats numeric spreadsheet cells as identifier numbers.", "block-public-identifiers", "Govern codes as lexical identifiers, preserve displayed source notation, and prohibit vector-wide numeric formatting."),
        ("PC-04", "Missing-value syntax", "Literal NA is emitted as semantic property values.", "fix-generator-before-rebuild", "Normalize source sentinels to null while preserving raw provenance."),
        ("PC-05", "Hierarchy semantics", "All 405 source hierarchy edges become skos:broader.", "block-hierarchy-promotion", "Use collections for navigation and approve broader only after extensional identity review."),
        ("PC-06", "Generated parent identity", "Parent nodes are minted from label plus parent and sometimes duplicate child labels.", "block-generated-parent-promotion", "Collapse duplicates and review remaining groups as concepts versus collections."),
        ("PC-07", "Global identity", "Pilot mints parallel identities despite legacy ERA mappings and exact AOM label-definition matches.", "block-id-allocation", "Reuse stable AOM IDs only after row-level identity and module review."),
        ("PC-08", "Practice study context", "Practice identity, absence, baseline, comparator, and treatment semantics share one hierarchy.", "model-separation-required", "Separate practice concepts, application occurrences, conditions, and experimental roles."),
        ("PC-09", "Outcome semantics", "Reporting levels, property identity, units, derivation flags, and interpretation metadata share one concept tree.", "model-separation-required", "Use SOSA Property, procedure, quantity/unit/basis, derivation, and reporting collections."),
        ("PC-10", "Operational linkage", "Linked.Tab and Linked.Col are published without a field-key contract.", "hold-semantic-promotion", "Keep as source provenance until ADR 0052 field registry and binding rules are accepted."),
        ("PC-11", "Lifecycle", "One practice status is blank and deprecated rows can still receive pilot concepts.", "fix-source-and-lifecycle", "Resolve unknown status and require replacement or retirement decisions before activation."),
        ("PC-12", "Economic classification", "Fixed, variable, private, societal, and opportunity categories are treated as intrinsic row identity.", "model-separation-required", "Represent accounting category as contextual classification with object, basis, and valuation method."),
    ]
    return [
        {
            "audit_id": audit_id,
            "contract_area": area,
            "finding": finding,
            "gate": gate,
            "recommendation": recommendation,
            "status": "open",
            "evidence_ids": "E-SRC-WORKBOOK;E-PILOT;E-AOM-STAGING",
        }
        for audit_id, area, finding, gate, recommendation in values
    ]


def guided_review() -> list[dict[str, str]]:
    values = [
        ("GR-01", "1", "Approve cross-domain scope and module routing", "Are prac and out accepted as cross-domain source registries rather than crop-only schemes?", "pilot_contract_audit.csv#PC-01", "Approve route-by-row and rename pilot schemes.", "yes"),
        ("GR-02", "1", "Approve source-code contract", "Should source codes remain lexical with eight governed artifact corrections and no automatic .0 suffixes?", "source_quality_issues.csv", "Approve lexical preservation plus explicit crosswalks.", "yes"),
        ("GR-03", "1", "Approve navigation model", "Should theme, pillar, subpillar, and indicator levels become reporting collections by default?", "hierarchy_node_review.csv", "Approve collection membership; require evidence for skos:broader.", "yes"),
        ("GR-04", "1", "Approve identity reuse rule", "Should exact label-definition matches prefer existing stable AOM IDs after module review?", "identity_collision_audit.csv", "Approve stable-ID reuse candidates; keep ambiguous mappings held.", "yes"),
        ("GR-05", "1", "Approve practice-context split", "Should practice identity be separate from application, absence, baseline, treatment, and comparator role?", "source_row_dispositions.csv", "Approve shared core candidates SC-01 through SC-06.", "yes"),
        ("GR-06", "1", "Approve outcome-variable model", "Should outcomes use sosa:Property plus procedure, feature, quantity, unit/basis, and derivation?", "shared_core_candidate_review.csv", "Approve SC-07 through SC-11 as implementation design inputs.", "yes"),
        ("GR-07", "2", "Review practice parent groups", "Which generated practice parents are true broader concepts versus editorial collections or duplicates?", "hierarchy_node_review.csv", "Start with rows carrying same_label_child_ids.", "yes"),
        ("GR-08", "2", "Review same-label distinct identities", "Confirm field Urea, Ash, crop Heat Tolerance, and generic Unspecified remain distinct from AOM feed or animal concepts.", "identity_collision_audit.csv", "Approve contextual distinction or improve definitions.", "yes"),
        ("GR-09", "2", "Review economic source defects", "Correct missing, swapped, example-only, and ambiguous definitions before identifier allocation.", "source_quality_issues.csv", "Correct canonical workbook; rerun review.", "yes"),
        ("GR-10", "2", "Review economic decomposition", "Should cost/benefit category, object, transaction, actor, time/basis, currency, and valuation method be explicit facets?", "source_row_dispositions.csv", "Approve SC-13 and refine SC-14.", "yes"),
        ("GR-11", "3", "Review external mapping candidates", "Do AgrO, ENVO, and ChEBI exact-label candidates match source definitions and entity types?", "authority_label_candidates.csv", "Approve individually; no bulk exactMatch.", "no"),
        ("GR-12", "3", "Resolve energy module boundary", "Where should cookstove, biodigester, and energy-management identities live?", "source_row_dispositions.csv", "Approve new module or explicit cross-domain routing before promotion.", "yes"),
    ]
    return [
        {
            "review_id": review_id,
            "priority": priority,
            "review_topic": topic,
            "review_question": question,
            "primary_evidence": evidence,
            "recommended_starting_decision": decision,
            "blocks_promotion": blocks,
            "review_status": "pending",
            "reviewer": "",
            "review_date": "",
            "decision_note": "",
        }
        for review_id, priority, topic, question, evidence, decision, blocks in values
    ]


def evidence_register(workbook_hash: str, agro_hash: str) -> list[dict[str, str]]:
    return [
        {"evidence_id": "E-SRC-WORKBOOK", "evidence_type": "canonical-source", "title": "ERA master workbook: prac, out, and out_econ sheets", "locator": "governed local canonical workbook", "version_or_date": "snapshot reviewed 2026-08-24", "sha256": workbook_hash, "supports": "Source rows, labels, definitions, source hierarchy, flags, codes, and operational fields.", "claim_boundary": "Workbook layout and codes do not by themselves establish ontology identity or public hierarchy."},
        {"evidence_id": "E-PILOT", "evidence_type": "repository-snapshot", "title": "Current prac/out pilot normalized data", "locator": "../../data/pilot/", "version_or_date": "branch base 2026-08-24", "sha256": "", "supports": "Current generated IDs, labels, properties, hierarchy, and source-row links.", "claim_boundary": "Pilot status is provisional and does not authorize public identity or semantics."},
        {"evidence_id": "E-AOM-STAGING", "evidence_type": "repository-snapshot", "title": "AOM livestock staging labels, definitions, concepts, and mappings", "locator": "../../data/livestock-staging/", "version_or_date": "branch base 2026-08-24", "sha256": "", "supports": "Published or staged AOM identity candidates and legacy ERA code mappings.", "claim_boundary": "legacy-unreviewed mappings and same labels are evidence candidates, not approved equivalence."},
        {"evidence_id": "E-SKOS", "evidence_type": "standard", "title": "W3C SKOS Simple Knowledge Organization System Reference", "locator": "https://www.w3.org/TR/skos-reference/", "version_or_date": "W3C Recommendation", "sha256": "", "supports": "Concept, scheme, semantic relation, mapping, and collection semantics.", "claim_boundary": "Does not establish domain identity, field schema, or observation procedure."},
        {"evidence_id": "E-SOSA", "evidence_type": "standard", "title": "W3C SOSA/SSN 2023", "locator": "https://www.w3.org/TR/vocab-ssn-2023/", "version_or_date": "2023 specification", "sha256": "", "supports": "Property, observation, feature of interest, procedure, and result model.", "claim_boundary": "Does not establish ERA row identity or reporting hierarchy."},
        {"evidence_id": "E-CROP-ONTOLOGY", "evidence_type": "domain-authority", "title": "Crop Ontology", "locator": "https://cropontology.org/about", "version_or_date": "accessed 2026-08-24", "sha256": "", "supports": "Crop phenotypic variable trait-method-scale pattern.", "claim_boundary": "Does not cover all practice, livestock, social, energy, and economic variables."},
        {"evidence_id": "E-AUTH-AGRO-SNAPSHOT", "evidence_type": "ontology-snapshot", "title": "AgrO official repository agro.owl snapshot", "locator": "https://raw.githubusercontent.com/AgriculturalSemantics/agro/master/agro.owl", "version_or_date": "downloaded 2026-08-24; ontology version IRI reports 2022-11-02", "sha256": agro_hash, "supports": "Exact-label authority candidates for agronomic practices and imported OBO terms.", "claim_boundary": "Exact labels and imported terms do not prove identity equivalence."},
        {"evidence_id": "E-AGROVOC", "evidence_type": "domain-authority", "title": "FAO AGROVOC", "locator": "https://agrovoc.fao.org/", "version_or_date": "accessed 2026-08-24", "sha256": "", "supports": "Broad multilingual agricultural terminology and later mapping candidates.", "claim_boundary": "Does not establish ERA experiment-variable identity or automatic parentage."},
        {"evidence_id": "E-FOODON", "evidence_type": "domain-authority", "title": "FoodOn food transformation process facet", "locator": "https://foodon.org/food-facets/food-transformation-process/", "version_or_date": "accessed 2026-08-24", "sha256": "", "supports": "Postharvest and food-process transformation and output modeling.", "claim_boundary": "Does not cover field management, study roles, or accounting variables."},
        {"evidence_id": "E-QUDT", "evidence_type": "standard-vocabulary", "title": "QUDT catalog", "locator": "https://www.qudt.org/catalog/qudt-catalog.html", "version_or_date": "accessed 2026-08-24", "sha256": "", "supports": "Quantities, units, dimensions, and quantity kinds.", "claim_boundary": "Does not establish agricultural property identity or derivation procedure."},
        {"evidence_id": "E-FSDN", "evidence_type": "accounting-authority", "title": "EU Farm Sustainability Data Network", "locator": "https://agriculture.ec.europa.eu/data-and-analysis/farm-structures-and-economics/fsdn_en", "version_or_date": "accessed 2026-08-24", "sha256": "", "supports": "Farm bookkeeping, output, cost, input, and asset scope.", "claim_boundary": "Does not directly identify ERA study variables."},
        {"evidence_id": "E-SEEA-AFF", "evidence_type": "accounting-standard", "title": "FAO SEEA Agriculture Forestry and Fisheries", "locator": "https://www.fao.org/fileadmin/templates/ess/ess_test_folder/Publications/Agrienvironmental/SEEA_AFF_FINAL_Clean_03.pdf", "version_or_date": "official publication", "sha256": "", "supports": "Output, consumption, capital, inventories, and income-account boundaries.", "claim_boundary": "Macro and sector accounting scope does not determine experiment-variable identity."},
        {"evidence_id": "E-SNA", "evidence_type": "accounting-standard", "title": "UN System of National Accounts", "locator": "https://unstats.un.org/unsd/Nationalaccount/sna.asp", "version_or_date": "accessed 2026-08-24", "sha256": "", "supports": "International economic-accounting concept boundaries.", "claim_boundary": "Too broad for direct ERA farm-trial row mapping."},
    ]


def source_snapshot(tables: dict[str, list[dict[str, str]]], workbook_hash: str) -> list[dict[str, object]]:
    return [
        {
            "source_sheet": sheet,
            "row_count": len(tables[sheet]),
            "unique_source_code_count": len({source_code(sheet, row) for row in tables[sheet]}),
            "unique_preferred_label_count": len({normalize_text(source_label(sheet, row)) for row in tables[sheet]}),
            "definition_missing_count": sum(not source_definition(sheet, row).strip() for row in tables[sheet]),
            "active_count": sum(row.get("Depreciated", "").upper() == "FALSE" for row in tables[sheet]),
            "deprecated_count": sum(row.get("Depreciated", "").upper() == "TRUE" for row in tables[sheet]),
            "unknown_status_count": sum(not row.get("Depreciated", "").strip() for row in tables[sheet]) if sheet != "out_econ" else 0,
            "workbook_sha256": workbook_hash,
        }
        for sheet in ("prac", "out", "out_econ")
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", required=True, type=Path)
    parser.add_argument("--agro-snapshot", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if not args.workbook.is_file():
        raise SystemExit(f"Workbook not found: {args.workbook}")
    if not args.agro_snapshot.is_file():
        raise SystemExit(f"AgrO snapshot not found: {args.agro_snapshot}")

    tables = read_source_tables(args.workbook)
    pilot = load_pilot()
    aom = load_aom()
    agro_labels, agro_hash = parse_agro(args.agro_snapshot)
    authority_candidates, authority_by_source = build_authority_candidates(tables, agro_labels)
    dispositions, signals = build_source_dispositions(tables, pilot, aom, authority_by_source)
    nodes = build_hierarchy_node_review(pilot)
    edges = build_hierarchy_edge_review(pilot)
    collisions = build_collisions(tables, pilot, aom, signals)
    quality = build_source_quality_issues(tables, pilot)
    authorities = authority_comparison()
    core = shared_core_candidates()
    contracts = pilot_contract_audit()
    guided = guided_review()
    workbook_hash = sha256(args.workbook)
    evidence = evidence_register(workbook_hash, agro_hash)
    snapshot = source_snapshot(tables, workbook_hash)

    outputs = {
        "source_snapshot.csv": snapshot,
        "source_row_dispositions.csv": dispositions,
        "hierarchy_node_review.csv": nodes,
        "hierarchy_edge_review.csv": edges,
        "identity_collision_audit.csv": collisions,
        "source_quality_issues.csv": quality,
        "pilot_contract_audit.csv": contracts,
        "authority_comparison.csv": authorities,
        "authority_label_candidates.csv": authority_candidates,
        "shared_core_candidate_review.csv": core,
        "guided_review.csv": guided,
        "evidence_register.csv": evidence,
    }
    for filename, rows in outputs.items():
        write_csv(args.output_dir / filename, rows)

    disposition_status = Counter(row["decision_status"] for row in dispositions)
    disposition_actions = Counter(row["recommended_action"] for row in dispositions)
    collision_scopes = Counter(row["collision_scope"] for row in collisions)
    issue_types = Counter(row["issue_type"] for row in quality)
    summary = {
        "review_version": "crop-foundation-v1",
        "review_date": REVIEW_DATE,
        "status": "recommendation-only",
        "source_workbook_sha256": workbook_hash,
        "agro_snapshot_sha256": agro_hash,
        "source_rows": {sheet: len(tables[sheet]) for sheet in ("prac", "out", "out_econ")},
        "source_row_total": sum(len(tables[sheet]) for sheet in tables),
        "source_disposition_status": dict(sorted(disposition_status.items())),
        "source_disposition_actions": dict(sorted(disposition_actions.items())),
        "pilot_intermediate_nodes_reviewed": len(nodes),
        "pilot_hierarchy_edges_reviewed": len(edges),
        "identity_collision_records": len(collisions),
        "identity_collision_scopes": dict(sorted(collision_scopes.items())),
        "source_quality_issue_count": len(quality),
        "source_quality_issue_types": dict(sorted(issue_types.items())),
        "authority_label_candidate_count": len(authority_candidates),
        "shared_core_candidate_count": len(core),
        "guided_review_item_count": len(guided),
        "implementation_authorized": False,
    }
    with (args.output_dir / "review_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
