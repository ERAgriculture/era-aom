#!/usr/bin/env python3
"""Generate reviewable AOM Livestock v2 staging tables and distributions."""

import csv
import hashlib
import json
import re
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

    with source.open(encoding="cp1252", newline="") as handle:
        reader = csv.DictReader(handle)
        source_fields = reader.fieldnames[:38]
        records = [{field: clean(row.get(field)) for field in source_fields} for row in reader]

    for number, record in enumerate(records, 2):
        levels = [record[level] for level in LEVELS if record[level]]
        record["_source_row"] = str(number)
        record["_path"] = "/".join(levels)
        record["_label"] = levels[-1] if levels else ""
        record["_level"] = str(len(levels))

    id_counts = Counter(row["AOM"] for row in records if row["AOM"])
    path_counts = Counter(row["_path"] for row in records if row["_path"])
    duplicate_ids = {key for key, count in id_counts.items() if count > 1}
    duplicate_paths = {key for key, count in path_counts.items() if count > 1}
    excluded = {row["_source_row"] for row in records if row["AOM"] in duplicate_ids}

    quarantine = []
    for row in records:
        reasons = []
        if row["AOM"] in duplicate_ids:
            reasons.append("duplicate_concept_id")
        if row["_path"] in duplicate_paths:
            reasons.append("duplicate_derived_path")
        for reason in reasons:
            quarantine.append({
                "source_row": row["_source_row"], "concept_id": row["AOM"],
                "preferred_label": row["_label"], "derived_path": row["_path"],
                "reason": reason, "disposition": "domain_review_required",
            })

    eligible = [
        row for row in records
        if row["_source_row"] not in excluded and row["AOM"] and row["_label"]
    ]
    by_path = defaultdict(list)
    for row in eligible:
        by_path[row["_path"]].append(row)

    concepts, labels, definitions, notes = [], [], [], []
    relations, gaps, mappings, properties, sources = [], [], [], [], []
    for row in eligible:
        concept_id = row["AOM"]
        concepts.append({
            "concept_id": concept_id, "scheme_id": SCHEME_ID,
            "module": "aom-livestock", "concept_type": "legacy_aom_concept",
            "notation": concept_id, "status": "staging",
            "hierarchy_level": row["_level"], "derived_path": row["_path"],
            "source_row": row["_source_row"],
        })
        labels.append({
            "concept_id": concept_id, "language": "en", "label_type": "pref",
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
        segments = row["_path"].split("/")
        if len(segments) > 1:
            parent_path = "/".join(segments[:-1])
            parents = by_path.get(parent_path, [])
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
                mappings.append({
                    "subject_id": concept_id, "mapping_relation": "relatedMatch",
                    "target_scheme": scheme, "target_id": target_id,
                    "target_uri": target_uri, "original_value": value,
                    "normalization_applied": "malformed_http_repair" if repaired else "",
                    "evidence": DOI, "status": "legacy-unreviewed",
                    "source_release": "AOM Livestock v2.0", "reviewer": "",
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

    schemes = [{
        "scheme_id": SCHEME_ID, "module": "aom-livestock",
        "preferred_label": "AOM Livestock v2 staging", "language": "en",
        "status": "staging-not-canonical", "source_doi": DOI,
    }]
    legacy = [{
        "source_row": row["_source_row"],
        **{field: row[field] for field in source_fields},
        "Derived_Path": row["_path"],
    } for row in records]
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
    broader = {row["subject_id"]: row["object_id"] for row in relations}
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
            "@id": URI_PREFIX + concept_id, "@type": "skos:Concept",
            "skos:inScheme": {"@id": SCHEME_URI}, "skos:notation": concept_id,
            "skos:prefLabel": {"@value": pref[concept_id], "@language": "en"},
            "era:conceptType": "legacy_aom_concept", "era:status": "unknown",
        }
        if alt[concept_id]:
            item["skos:altLabel"] = [{"@value": x, "@language": "en"} for x in alt[concept_id]]
        if concept_id in defs:
            item["skos:definition"] = {"@value": defs[concept_id], "@language": "en"}
        if concept_id in broader:
            item["skos:broader"] = {"@id": URI_PREFIX + broader[concept_id]}
        if mapped[concept_id]:
            item["skos:relatedMatch"] = [{"@id": x} for x in sorted(set(mapped[concept_id]))]
        graph.append(item)
    dist_dir.mkdir(parents=True, exist_ok=True)
    jsonld = {
        "@context": {"skos": "http://www.w3.org/2004/02/skos/core#",
                     "dcterms": "http://purl.org/dc/terms/",
                     "era": "urn:era:property:"},
        "@graph": graph,
    }
    (dist_dir / "aom-livestock.jsonld").write_text(
        json.dumps(jsonld, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    ttl = [
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix dcterms: <http://purl.org/dc/terms/> .", "",
        "@prefix era: <urn:era:property:> .", "",
        f"<{SCHEME_URI}> a skos:ConceptScheme ;",
        '  skos:prefLabel "AOM Livestock v2 staging"@en ;',
        f"  dcterms:source <{DOI}> .", "",
    ]
    for concept_id in sorted(pref):
        terms = [
            "a skos:Concept", f"skos:inScheme <{SCHEME_URI}>",
            f"skos:notation {json.dumps(concept_id)}",
            f"skos:prefLabel {json.dumps(pref[concept_id], ensure_ascii=False)}@en",
            'era:conceptType "legacy_aom_concept"', 'era:status "unknown"',
        ]
        terms += [f"skos:altLabel {json.dumps(x, ensure_ascii=False)}@en" for x in alt[concept_id]]
        if concept_id in defs:
            terms.append(f"skos:definition {json.dumps(defs[concept_id], ensure_ascii=False)}@en")
        if concept_id in broader:
            terms.append(f"skos:broader <{URI_PREFIX + broader[concept_id]}>")
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
        "edge_type": "broader", "status": row["status"],
    } for row in relations]
    write_csv(dist_dir / "nodes.csv", list(nodes[0]), nodes)
    write_csv(dist_dir / "edges.csv", list(edges[0]), edges)
    (dist_dir / "aom-schema.ttl").write_text("""@prefix aom: <urn:era-aom:schema:> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
<urn:era-aom:schema> a owl:Ontology ; rdfs:label "AOM schema"@en .
aom:Module a owl:Class ; rdfs:label "Module"@en .
aom:MappingAssertion a owl:Class ; rdfs:label "Mapping assertion"@en .
aom:ChangeProposal a owl:Class ; rdfs:label "Change proposal"@en .
aom:Release a owl:Class ; rdfs:label "Release"@en .
aom:Evidence a owl:Class ; rdfs:label "Evidence"@en .
aom:Reviewer a owl:Class ; rdfs:label "Reviewer"@en .
aom:inModule a owl:ObjectProperty ; rdfs:range aom:Module .
aom:supportedBy a owl:ObjectProperty ; rdfs:range aom:Evidence .
aom:reviewedBy a owl:ObjectProperty ; rdfs:range aom:Reviewer .
aom:releasedIn a owl:ObjectProperty ; rdfs:range aom:Release .
""", encoding="utf-8")

    files = sorted(
        path for path in [*data_dir.glob("*.csv"), *dist_dir.glob("*")]
        if path.name != "manifest.json"
    )
    manifest = {
        "manifest_schema_version": "1.0.0", "status": "staging-not-canonical",
        "source": {"doi": "10.7910/DVN/75E7HV", "version": "2.0",
                   "sha256": hashlib.sha256(source.read_bytes()).hexdigest()},
        "counts": {
            "source_records": len(records), "published_staging_concepts": len(concepts),
            "excluded_duplicate_id_records": len(excluded),
            "quarantine_assertions": len(quarantine),
            "hierarchy_relations": len(relations), "hierarchy_gaps": len(gaps),
            "mapping_assertions": len(mappings),
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
