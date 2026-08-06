#!/usr/bin/env python3
"""Generate reviewable AOM Livestock v2 staging tables and distributions."""

import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

LEVELS = [f"L{i}" for i in range(1, 11)]
MAPPING_FIELDS = {
    "Ontology": "ontology",
    "Agrovoc": "agrovoc",
    "NCBI": "ncbi-taxonomy",
    "WFO": "world-flora-online",
    "Feedipedia": "feedipedia",
    "ilri_code": "ilri-code",
    "CPC_Code_Product": "cpc-product",
    "CPC_Code_Component": "cpc-component",
    "ERA_Code": "era",
}
PROPERTY_FIELDS = [
    "Edge_Value", "Example Units", "Group", "Scientific Name", "Sex",
    "ERA.Field", "C or E", "CPC_Code_Product_Match",
    "CPC_Code_Component_Match", "Ani_Diet_Spp_Syn",
    "Is_Ani_Diet_Ingredient",
]
NON_VALUES = {"", "NA", "#N/A", "No match", "No Match", "New"}
SCHEME_ID = "aom-livestock-v2"
SCHEME_URI = "urn:era-aom:scheme:livestock-v2"
URI_PREFIX = "urn:era-aom:livestock:"
DOI = "https://doi.org/10.7910/DVN/75E7HV"
SOURCE_SHA256 = "a5c6a4873c0ee1aa41a2975ebb2fb74ca3beb867ea3702e227118e5ecce6c17c"


def clean(value):
    value = (value or "").replace("_x000D_", "\n").replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(part.rstrip() for part in value.split("\n")).strip()


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize_mapping(value):
    original = value
    if re.match(r"^https?:/[^/]", value):
        value = value.replace("http:/", "http://", 1).replace("https:/", "https://", 1)
    parsed = urlparse(value)
    uri = value if parsed.scheme in {"http", "https"} and parsed.netloc else ""
    target_id = value.rstrip("/").rsplit("/", 1)[-1] if uri else value
    return target_id, uri, value != original


def main():
    if len(sys.argv) not in {2, 3}:
        raise SystemExit("Usage: normalize_livestock_release.py PUBLIC_CSV [ROOT]")
    source = Path(sys.argv[1]).resolve()
    root = Path(sys.argv[2] if len(sys.argv) == 3 else ".").resolve()
    data_dir = root / "data/livestock-staging"
    dist_dir = root / "dist/livestock-staging"

    def read_governance(name):
        path = data_dir / name
        if not path.exists():
            return []
        with path.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    identity_resolutions = read_governance("approved_identity_resolutions.csv")
    mapping_replacements = read_governance("approved_mapping_replacements.csv")
    deprecations = read_governance("approved_deprecations.csv")
    label_corrections = read_governance("approved_label_corrections.csv")
    new_concepts = read_governance("approved_new_concepts.csv")
    id_registry = read_governance("livestock_id_registry.csv")
    semantic_relations = read_governance("approved_semantic_relations.csv")
    reparentings = read_governance("approved_reparentings.csv")
    facet_concepts = read_governance("approved_ingredient_facet_concepts.csv")
    resolution_by_row = {row["source_row"]: row for row in identity_resolutions}
    replacement_by_key = {
        (row["source_row"], row["source_column"]): row
        for row in mapping_replacements
    }
    deprecation_by_id = {row["deprecated_id"]: row for row in deprecations}
    retained_by_id = {row["replacement_id"]: row for row in deprecations}
    label_correction_by_id = {
        row["concept_id"]: row for row in label_corrections
    }
    resolved_path_ids = set(deprecation_by_id) | set(retained_by_id)

    raw_source = source.read_bytes()
    try:
        source_text = raw_source.decode("utf-8")
    except UnicodeDecodeError:
        source_text = raw_source.decode("cp1252")
    reader = csv.DictReader(io.StringIO(source_text, newline=""))
    repository_snapshot = "source_row" in reader.fieldnames
    source_fields = [
        field for field in reader.fieldnames
        if field not in {"source_row", "Derived_Path"}
    ][:38]
    records = []
    for number, raw in enumerate(reader, 2):
        record = {field: clean(raw.get(field)) for field in source_fields}
        record["_source_row"] = clean(raw.get("source_row")) if repository_snapshot else str(number)
        records.append(record)

    for record in records:
        levels = [record[level] for level in LEVELS if record[level]]
        record["_path_key"] = tuple(levels)
        record["_path"] = "/".join(levels)
        record["_parent_path"] = "/".join(levels[:-1])
        record["_label"] = levels[-1] if levels else ""
        record["_level"] = str(len(levels))

    legacy = [{
        "source_row": row["_source_row"],
        **{field: row[field] for field in source_fields},
        "Derived_Path": row["_path"],
    } for row in records]

    source_rows = {row["_source_row"] for row in records}
    if not set(resolution_by_row) <= source_rows:
        raise ValueError("Approved identity resolution references unknown source row")
    if not {key[0] for key in replacement_by_key} <= source_rows:
        raise ValueError("Approved mapping replacement references unknown source row")
    source_ids = {row["AOM"] for row in records}
    if not (set(deprecation_by_id) | set(retained_by_id)) <= source_ids:
        raise ValueError("Approved deprecation references unknown concept ID")
    if len(label_correction_by_id) != len(label_corrections):
        raise ValueError("Approved label corrections must have unique concept IDs")
    if not set(label_correction_by_id) <= source_ids:
        raise ValueError("Approved label correction references unknown concept ID")
    registered_ids = {row["concept_id"] for row in id_registry}
    new_ids = {row["concept_id"] for row in new_concepts}
    if len(new_ids) != len(new_concepts) or not new_ids <= registered_ids:
        raise ValueError("Every new concept must have one registered unique identifier")
    if new_ids & source_ids:
        raise ValueError("New concept identifier collides with legacy source")

    resolved_to_existing = {
        source_row for source_row, resolution in resolution_by_row.items()
        if resolution["action"] == "map_to_existing"
    }

    id_counts = Counter(
        row["AOM"] for row in records
        if row["AOM"] and row["_source_row"] not in resolved_to_existing
    )
    path_counts = Counter(row["_path_key"] for row in records if row["_path_key"])
    duplicate_ids = {key for key, count in id_counts.items() if count > 1}
    duplicate_paths = {key for key, count in path_counts.items() if count > 1}
    unresolved_duplicate_rows = {
        row["_source_row"] for row in records if row["AOM"] in duplicate_ids
    }
    excluded = resolved_to_existing | unresolved_duplicate_rows

    quarantine = []
    for row in records:
        reasons = []
        if row["AOM"] in duplicate_ids and row["_source_row"] not in resolved_to_existing:
            reasons.append("duplicate_concept_id")
        if row["_path_key"] in duplicate_paths:
            reasons.append("duplicate_derived_path")
        for reason in reasons:
            quarantine.append({
                "source_row": row["_source_row"], "concept_id": row["AOM"],
                "preferred_label": row["_label"], "derived_path": row["_path"],
                "reason": reason,
                "disposition": (
                    "resolved_deprecation"
                    if reason == "duplicate_derived_path" and row["AOM"] in resolved_path_ids
                    else "domain_review_required"
                ),
            })

    eligible = [
        row for row in records
        if row["_source_row"] not in excluded and row["AOM"] and row["_label"]
    ]

    for row in eligible:
        for column in MAPPING_FIELDS:
            replacement = replacement_by_key.get((row["_source_row"], column))
            if replacement:
                if row[column] != replacement["old_value"]:
                    raise ValueError(
                        f"Mapping replacement source mismatch at row {row['_source_row']} {column}"
                    )
                row[column] = replacement["new_value"]
    by_path = defaultdict(list)
    for row in eligible:
        by_path[row["_path_key"]].append(row)

    concepts, labels, definitions, notes = [], [], [], []
    relations, gaps, mappings, properties, sources = [], [], [], [], []
    for row in eligible:
        concept_id = row["AOM"]
        deprecation = deprecation_by_id.get(concept_id)
        retained = retained_by_id.get(concept_id)
        label_correction = label_correction_by_id.get(concept_id)
        if label_correction and label_correction["old_label"] != row["_label"]:
            raise ValueError(f"Label correction source mismatch for {concept_id}")
        preferred_label = (
            retained["preferred_label"] if retained else
            label_correction["new_label"] if label_correction else
            row["_label"]
        )
        concepts.append({
            "concept_id": concept_id, "scheme_id": SCHEME_ID,
            "module": "aom-livestock", "concept_type": "legacy_aom_concept",
            "notation": concept_id, "status": "deprecated" if deprecation else "staging",
            "hierarchy_level": row["_level"], "derived_path": row["_path"],
            "source_row": row["_source_row"],
        })
        labels.append({
            "concept_id": concept_id, "language": "en", "label_type": "pref",
            "label": preferred_label,
            "source_column": (
                "approved_deprecation" if retained else
                "approved_label_correction" if label_correction else
                f"L{row['_level']}"
            ),
        })
        if preferred_label.casefold() != row["_label"].casefold():
            labels.append({
                "concept_id": concept_id, "language": "en", "label_type": "alt",
                "label": row["_label"], "source_column": f"L{row['_level']}",
            })
        seen = set()
        for synonym in map(clean, row["Synonym"].split(";")):
            key = synonym.casefold()
            if synonym and key != row["_label"].casefold() and key not in seen:
                seen.add(key)
                labels.append({
                    "concept_id": concept_id, "language": "en",
                    "label_type": "alt", "label": synonym,
                    "source_column": "Synonym",
                })
        if row["Description"]:
            definitions.append({
                "concept_id": concept_id, "language": "en",
                "definition": row["Description"], "source_column": "Description",
            })
        if row["Notes"]:
            notes.append({
                "concept_id": concept_id, "language": "en",
                "note_type": "scope_note", "note": row["Notes"],
                "source_column": "Notes",
            })
        if int(row["_level"]) > 1:
            parent_key = row["_path_key"][:-1]
            parent_path = row["_parent_path"]
            parents = by_path.get(parent_key, [])
            if len(parents) == 1:
                relations.append({
                    "subject_id": concept_id, "relation_type": "broader",
                    "object_id": parents[0]["AOM"], "status": "derived-from-levels",
                })
            else:
                gaps.append({
                    "child_id": concept_id, "child_path": row["_path"],
                    "missing_parent_path": parent_path,
                    "reason": "parent_path_has_no_explicit_concept" if not parents
                    else "parent_path_is_ambiguous",
                    "disposition": "review_and_mint_or_map_parent",
                })
        for column, scheme in MAPPING_FIELDS.items():
            for value in map(clean, row[column].split(";")):
                if value in NON_VALUES:
                    continue
                target_id, target_uri, repaired = normalize_mapping(value)
                replacement = replacement_by_key.get((row["_source_row"], column))
                mappings.append({
                    "subject_id": concept_id, "mapping_relation": "relatedMatch",
                    "target_scheme": scheme, "target_id": target_id,
                    "target_uri": target_uri, "original_value": value,
                    "normalization_applied": "malformed_http_repair" if repaired else "",
                    "evidence": replacement["evidence"] if replacement else DOI,
                    "status": "reviewed" if replacement else "legacy-unreviewed",
                    "source_release": "AOM Livestock v2.0",
                    "reviewer": replacement["reviewer"] if replacement else "",
                })
        for column in PROPERTY_FIELDS:
            if row[column]:
                properties.append({
                    "concept_id": concept_id, "property": column,
                    "value": row[column], "source_column": column,
                    "status": "legacy-unreviewed",
                })
        sources.append({
            "concept_id": concept_id, "source_release": "AOM Livestock v2.0",
            "source_row": row["_source_row"], "source_doi": DOI,
        })

    for deprecation in deprecations:
        relations.append({
            "subject_id": deprecation["deprecated_id"],
            "relation_type": "replaced_by",
            "object_id": deprecation["replacement_id"],
            "status": "reviewed",
        })

    records_by_source = {row["_source_row"]: row for row in records}
    label_keys = {
        (row["concept_id"], row["language"], row["label"].casefold())
        for row in labels
    }
    for resolution in identity_resolutions:
        if resolution["action"] != "map_to_existing":
            continue
        source_row = records_by_source[resolution["source_row"]]
        target_id = resolution["resolved_concept_id"]
        alias_values = [source_row["_label"], *map(clean, source_row["Synonym"].split(";"))]
        for alias in alias_values:
            key = (target_id, "en", alias.casefold())
            if alias and key not in label_keys:
                label_keys.add(key)
                labels.append({
                    "concept_id": target_id, "language": "en",
                    "label_type": "alt", "label": alias,
                    "source_column": "approved_identity_resolution",
                })

    concept_ids = {row["concept_id"] for row in concepts}
    for new_concept in new_concepts:
        concept_id = new_concept["concept_id"]
        parent_id = new_concept["broader_id"]
        if parent_id not in concept_ids:
            raise ValueError(f"New concept parent is unknown: {parent_id}")
        concepts.append({
            "concept_id": concept_id, "scheme_id": SCHEME_ID,
            "module": "aom-livestock", "concept_type": "aom_concept",
            "notation": concept_id, "status": "staging",
            "hierarchy_level": new_concept["hierarchy_level"],
            "derived_path": new_concept["derived_path"], "source_row": "",
        })
        labels.append({
            "concept_id": concept_id, "language": "en", "label_type": "pref",
            "label": new_concept["preferred_label"],
            "source_column": "approved_new_concept",
        })
        if new_concept["scope_note"]:
            notes.append({
                "concept_id": concept_id, "language": "en",
                "note_type": "scope_note", "note": new_concept["scope_note"],
                "source_column": "approved_new_concept",
            })
        relations.append({
            "subject_id": concept_id, "relation_type": "broader",
            "object_id": parent_id, "status": "reviewed",
        })
        child_ids = set(filter(None, new_concept["child_ids"].split(";")))
        unknown_children = child_ids - concept_ids
        if unknown_children:
            raise ValueError(f"New concept has unknown children: {sorted(unknown_children)}")
        gaps = [
            gap for gap in gaps
            if gap["child_id"] not in child_ids
        ]
        for child_id in sorted(child_ids):
            relations.append({
                "subject_id": child_id, "relation_type": "broader",
                "object_id": concept_id, "status": "reviewed",
            })
        sources.append({
            "concept_id": concept_id, "source_release": "AOM curation",
            "source_row": "", "source_doi": new_concept["evidence"],
        })
        concept_ids.add(concept_id)

    for reparenting in reparentings:
        target_id = reparenting["target_parent_id"]
        child_ids = set(filter(None, reparenting["child_ids"].split(";")))
        if target_id not in concept_ids or not child_ids <= concept_ids:
            raise ValueError("Approved reparenting references unknown concept")
        already_parented = {
            row["subject_id"] for row in relations
            if row["relation_type"] == "broader"
        }
        if child_ids & already_parented:
            raise ValueError("Approved reparenting child already has broader relation")
        gaps = [gap for gap in gaps if gap["child_id"] not in child_ids]
        for child_id in sorted(child_ids):
            relations.append({
                "subject_id": child_id, "relation_type": "broader",
                "object_id": target_id, "status": "reviewed",
            })

    for semantic_relation in semantic_relations:
        if semantic_relation["relation_type"] not in {"related"}:
            raise ValueError("Unsupported approved semantic relation type")
        if not {
            semantic_relation["subject_id"], semantic_relation["object_id"]
        } <= concept_ids:
            raise ValueError("Approved semantic relation references unknown concept")
        relations.append({
            "subject_id": semantic_relation["subject_id"],
            "relation_type": semantic_relation["relation_type"],
            "object_id": semantic_relation["object_id"],
            "status": "reviewed",
        })

    for deprecation in deprecations:
        deprecated_id = deprecation["deprecated_id"]
        replacement_id = deprecation["replacement_id"]
        source = next(row for row in records if row["AOM"] == deprecated_id)
        aliases = [source["_label"], *map(clean, source["Synonym"].split(";"))]
        for alias in aliases:
            key = (replacement_id, "en", alias.casefold())
            if alias and key not in label_keys:
                label_keys.add(key)
                labels.append({
                    "concept_id": replacement_id, "language": "en",
                    "label_type": "alt", "label": alias,
                    "source_column": "approved_deprecation",
                })

    schemes = [{
        "scheme_id": SCHEME_ID, "module": "aom-livestock",
        "preferred_label": "AOM Livestock v2 staging", "language": "en",
        "status": "staging-not-canonical", "source_doi": DOI,
    }]
    tables = {
        "schemes": schemes, "concepts": concepts, "labels": labels,
        "definitions": definitions, "notes": notes, "relations": relations,
        "mappings": mappings, "properties": properties,
        "source_records": sources, "quarantine": quarantine,
        "hierarchy_gaps": gaps, "legacy_records": legacy,
    }
    for name, rows in tables.items():
        fields = list(rows[0]) if rows else ["empty"]
        write_csv(data_dir / f"{name}.csv", fields, rows)

    pref = {row["concept_id"]: row["label"] for row in labels if row["label_type"] == "pref"}
    alt = defaultdict(list)
    for row in labels:
        if row["label_type"] == "alt":
            alt[row["concept_id"]].append(row["label"])
    defs = {row["concept_id"]: row["definition"] for row in definitions}
    broader = {
        row["subject_id"]: row["object_id"]
        for row in relations if row["relation_type"] == "broader"
    }
    replaced_by = {
        row["subject_id"]: row["object_id"]
        for row in relations if row["relation_type"] == "replaced_by"
    }
    related = defaultdict(list)
    for row in relations:
        if row["relation_type"] == "related":
            related[row["subject_id"]].append(row["object_id"])
    concept_status = {
        row["concept_id"]: "deprecated" if row["status"] == "deprecated" else "unknown"
        for row in concepts
    }
    concept_type = {row["concept_id"]: row["concept_type"] for row in concepts}
    facet_value_class = {row["concept_id"]: row["value_class"] for row in facet_concepts}
    mapped = defaultdict(list)
    for row in mappings:
        if row["target_uri"]:
            mapped[row["subject_id"]].append(row["target_uri"])

    graph = [{
        "@id": SCHEME_URI, "@type": "skos:ConceptScheme",
        "skos:prefLabel": {"@value": "AOM Livestock v2 staging", "@language": "en"},
        "dcterms:source": {"@id": DOI},
    }]
    for concept_id in sorted(pref):
        item = {
            "@id": URI_PREFIX + concept_id,
            "@type": (["skos:Concept", facet_value_class[concept_id]]
                      if concept_id in facet_value_class else "skos:Concept"),
            "skos:inScheme": {"@id": SCHEME_URI}, "skos:notation": concept_id,
            "skos:prefLabel": {"@value": pref[concept_id], "@language": "en"},
            "era:conceptType": concept_type[concept_id],
            "era:status": concept_status[concept_id],
        }
        if alt[concept_id]:
            item["skos:altLabel"] = [{"@value": x, "@language": "en"} for x in alt[concept_id]]
        if concept_id in defs:
            item["skos:definition"] = {"@value": defs[concept_id], "@language": "en"}
        if concept_id in broader:
            item["skos:broader"] = {"@id": URI_PREFIX + broader[concept_id]}
        if concept_id in replaced_by:
            item["dcterms:isReplacedBy"] = {"@id": URI_PREFIX + replaced_by[concept_id]}
        if related[concept_id]:
            item["skos:related"] = [
                {"@id": URI_PREFIX + target_id}
                for target_id in sorted(set(related[concept_id]))
            ]
        if mapped[concept_id]:
            item["skos:relatedMatch"] = [{"@id": x} for x in sorted(set(mapped[concept_id]))]
        graph.append(item)
    dist_dir.mkdir(parents=True, exist_ok=True)
    jsonld = {
        "@context": {"skos": "http://www.w3.org/2004/02/skos/core#",
                     "dcterms": "http://purl.org/dc/terms/",
                     "aom": "urn:era-aom:schema:",
                     "era": "urn:era:property:"},
        "@graph": graph,
    }
    (dist_dir / "aom-livestock.jsonld").write_text(
        json.dumps(jsonld, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    ttl = [
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix dcterms: <http://purl.org/dc/terms/> .", "",
        "@prefix aom: <urn:era-aom:schema:> .", "",
        "@prefix era: <urn:era:property:> .", "",
        f"<{SCHEME_URI}> a skos:ConceptScheme ;",
        '  skos:prefLabel "AOM Livestock v2 staging"@en ;',
        f"  dcterms:source <{DOI}> .", "",
    ]
    for concept_id in sorted(pref):
        terms = [
            (f"a skos:Concept, {facet_value_class[concept_id]}"
             if concept_id in facet_value_class else "a skos:Concept"),
            f"skos:inScheme <{SCHEME_URI}>",
            f"skos:notation {json.dumps(concept_id)}",
            f"skos:prefLabel {json.dumps(pref[concept_id], ensure_ascii=False)}@en",
            f'era:conceptType {json.dumps(concept_type[concept_id])}',
            f'era:status {json.dumps(concept_status[concept_id])}',
        ]
        terms += [f"skos:altLabel {json.dumps(x, ensure_ascii=False)}@en" for x in alt[concept_id]]
        if concept_id in defs:
            terms.append(f"skos:definition {json.dumps(defs[concept_id], ensure_ascii=False)}@en")
        if concept_id in broader:
            terms.append(f"skos:broader <{URI_PREFIX + broader[concept_id]}>")
        if concept_id in replaced_by:
            terms.append(f"dcterms:isReplacedBy <{URI_PREFIX + replaced_by[concept_id]}>")
        terms += [
            f"skos:related <{URI_PREFIX + target_id}>"
            for target_id in sorted(set(related[concept_id]))
        ]
        terms += [f"skos:relatedMatch <{x}>" for x in sorted(set(mapped[concept_id]))]
        ttl.append(f"<{URI_PREFIX + concept_id}> " + " ;\n  ".join(terms) + " .\n")
    (dist_dir / "aom-livestock.ttl").write_text("\n".join(ttl), encoding="utf-8")

    nodes = [{
        "node_id": row["concept_id"], "label": pref[row["concept_id"]],
        "node_type": "aom-concept", "module": "aom-livestock",
        "status": row["status"],
    } for row in concepts]
    edges = [{
        "source": row["subject_id"], "target": row["object_id"],
        "edge_type": row["relation_type"], "status": row["status"],
    } for row in relations]
    write_csv(dist_dir / "nodes.csv", list(nodes[0]), nodes)
    write_csv(dist_dir / "edges.csv", list(edges[0]), edges)
    schema_source = root / "schemas/owl/aom-semantic-model.ttl"
    (dist_dir / "aom-schema.ttl").write_text(
        schema_source.read_text(encoding="utf-8"), encoding="utf-8"
    )
    subprocess.run(
        [sys.executable, str(root / "scripts/build_semantic_bindings.py")],
        cwd=root, check=True,
    )

    files = sorted(
        path for path in [*data_dir.glob("*.csv"), *dist_dir.glob("*")]
        if path.name != "manifest.json"
    )
    manifest = {
        "manifest_schema_version": "1.0.0", "status": "staging-not-canonical",
        "source": {"doi": "10.7910/DVN/75E7HV", "version": "2.0",
                   "sha256": SOURCE_SHA256},
        "generation_input": {
            "type": "repository-legacy-snapshot" if repository_snapshot else "doi-release-csv",
            "sha256": hashlib.sha256(raw_source).hexdigest(),
        },
        "counts": {
            "source_records": len(records), "published_staging_concepts": len(concepts),
            "excluded_duplicate_id_records": len(unresolved_duplicate_rows),
            "resolved_to_existing_records": len(resolved_to_existing),
            "quarantine_assertions": len(quarantine),
            "hierarchy_relations": sum(
                row["relation_type"] == "broader" for row in relations
            ),
            "replacement_relations": sum(
                row["relation_type"] == "replaced_by" for row in relations
            ),
            "semantic_relations": sum(
                row["relation_type"] == "related" for row in relations
            ),
            "hierarchy_gaps": len(gaps),
            "mapping_assertions": len(mappings),
            "approved_identity_resolutions": len(identity_resolutions),
            "approved_mapping_replacements": len(mapping_replacements),
            "approved_deprecations": len(deprecations),
            "approved_label_corrections": len(label_corrections),
            "approved_new_concepts": len(new_concepts),
            "registered_livestock_ids": len(id_registry),
            "approved_semantic_relations": len(semantic_relations),
            "approved_reparentings": len(reparentings),
            "approved_semantic_bindings": len(
                read_governance("approved_semantic_bindings.csv")
            ),
            "approved_semantic_value_bindings": len(
                read_governance("approved_semantic_value_bindings.csv")
            ),
            "approved_ingredient_component_classifications": len(
                read_governance("approved_ingredient_component_classifications.csv")
            ),
            "approved_ingredient_facet_concepts": len(facet_concepts),
            "approved_ingredient_harmonization_rules": len(
                read_governance("approved_ingredient_harmonization_rules.csv")
            ),
            "approved_generated_feed_material_facets": len(
                read_governance("approved_generated_feed_material_facets.csv")
            ),
            "approved_whole_grain_integrity_decisions": len(
                read_governance("approved_whole_grain_integrity_decisions.csv")
            ),
            "approved_feed_material_source_overrides": len(
                read_governance("approved_feed_material_source_overrides.csv")
            ),
            "approved_ingredient_semantic_closure_decisions": len(
                read_governance("approved_ingredient_semantic_closure_decisions.csv")
            ),
            "approved_ingredient_cluster_decisions": len(
                read_governance("approved_ingredient_cluster_decisions.csv")
            ),
            "approved_ingredient_component_value_mappings": len(
                read_governance("approved_ingredient_component_value_mappings.csv")
            ),
            "approved_ingredient_component_decompositions": len(
                read_governance("approved_ingredient_component_decompositions.csv")
            ),
            "approved_ingredient_component_value_holds": len(
                read_governance("approved_ingredient_component_value_holds.csv")
            ),
        },
        "identifier_policy": {
            "concept_ids_preserved": True, "rdf_uri_base": URI_PREFIX,
            "rdf_uri_status": "provisional-staging-only",
        },
        "files": [{
            "path": str(path.relative_to(root)), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        } for path in files if path.is_file()],
    }
    (dist_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Normalized {len(records)} records: {len(concepts)} concepts, "
          f"{len(gaps)} hierarchy gaps, {len(mappings)} mappings.")


if __name__ == "__main__":
    main()
