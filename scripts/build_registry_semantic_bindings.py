#!/usr/bin/env python3
"""Build and validate ADR 0054 AC-09 registry semantic bindings."""

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "registry-bindings" / "2026.2-rc.1.json"
ACTIVE_SOURCE = ROOT / "data" / "registry-bindings" / "approved_semantic_bindings.csv"
LEDGER_SOURCE = ROOT / "data" / "registry-bindings" / "semantic_binding_id_ledger.csv"
STRUCTURAL_SOURCE = ROOT / "data" / "livestock-staging" / "approved_semantic_bindings.csv"
VALUE_SOURCE = ROOT / "data" / "livestock-staging" / "approved_semantic_value_bindings.csv"
CSVW_SOURCE = ROOT / "schemas" / "csvw" / "registry-semantic-bindings-metadata.json"
SCHEMA_SOURCE = ROOT / "schemas" / "owl" / "registry-semantic-binding.ttl"
SHACL_SOURCE = ROOT / "schemas" / "shacl" / "registry-semantic-bindings.ttl"

AOM_SCHEMA = "https://w3id.org/era-aom/schema/"
AOM_LIVESTOCK = "https://w3id.org/era-aom/livestock/"
BINDING_BASE = "https://w3id.org/era-aom/binding/"
BINDING_RELEASE_BASE = "https://w3id.org/era-aom/binding-release/"
REGISTRY_SUBJECT_BASE = "urn:era-data:registry:"
DCTERMS = "http://purl.org/dc/terms/"
XSD = "http://www.w3.org/2001/XMLSchema#"
OWL_NS = "http://www.w3.org/2002/07/owl#"
SKOS_NS = "http://www.w3.org/2004/02/skos/core#"

PREFIXES = {
    "aom": AOM_SCHEMA,
    "owl": OWL_NS,
    "qudt": "http://qudt.org/schema/qudt/",
    "skos": SKOS_NS,
    "sosa": "http://www.w3.org/ns/sosa/",
    "xsd": XSD,
}

ACTIVE_FIELDS = [
    "semantic_binding_id",
    "registry_release_id",
    "registry_subject_type",
    "registry_subject_id",
    "registry_row_sha256",
    "binding_predicate",
    "target_iri",
    "target_kind",
    "semantic_source_key",
    "semantic_source_file",
    "registry_source_artifact",
    "evidence",
    "lifecycle",
    "reviewer_status",
    "reviewer",
    "review_date",
    "domain_scope",
    "rationale",
]

HOLD_FIELDS = [
    "hold_id",
    "source_kind",
    "semantic_source_key",
    "legacy_concept_id",
    "registry_subject_type",
    "registry_subject_id",
    "registry_row_sha256",
    "registry_source_artifact",
    "target_iri",
    "binding_action",
    "reason_code",
    "reason",
    "evidence",
    "lifecycle",
    "reviewer_status",
    "reviewer",
    "review_date",
    "rationale",
]

OUTPUT_FILES = {
    "semantic_bindings.csv",
    "semantic_binding_id_ledger.csv",
    "semantic_binding_holds.csv",
    "semantic_bindings.csv-metadata.json",
    "semantic_bindings.ttl",
    "semantic_bindings.jsonld",
    "registry-semantic-binding.schema.ttl",
    "registry-semantic-bindings.shacl.ttl",
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def row_sha256(row):
    payload = json.dumps(
        row, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    Path(path).write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def read_csv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows, fieldnames):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def expand(value):
    if not value or value.startswith(("http://", "https://", "urn:")):
        return value
    prefix, local = value.split(":", 1)
    return PREFIXES[prefix] + local


def value_target(row):
    if row["binding_action"] == "map_to_existing":
        return AOM_LIVESTOCK + row["target_concept_id"]
    if row["binding_action"] == "map_to_external":
        return row["target_uri"]
    return ""


def registry_subject_iri(row):
    return (
        REGISTRY_SUBJECT_BASE
        + row["registry_subject_type"]
        + ":"
        + row["registry_subject_id"]
    )


def load_sources(config):
    for relative, expected in config["semantic_sources"].items():
        if sha256(ROOT / relative) != expected:
            raise ValueError(f"Pinned semantic source changed: {relative}")
    return (
        read_csv(ACTIVE_SOURCE),
        read_csv(LEDGER_SOURCE),
        read_csv(STRUCTURAL_SOURCE),
        read_csv(VALUE_SOURCE),
    )


def validate_active_source(config, active, ledger, structural, values):
    expected = config["expected_counts"]
    if len(active) != expected["active_binding_rows"]:
        raise ValueError("Active binding row count differs from accepted contract")
    if len(structural) != expected["structural_source_decisions"]:
        raise ValueError("Structural source count differs from pinned contract")
    if len(values) != expected["value_source_decisions"]:
        raise ValueError("Value source count differs from pinned contract")
    if len(structural) + len(values) != expected["total_source_decisions"]:
        raise ValueError("Semantic source decision total differs from pinned contract")

    if list(active[0]) != ACTIVE_FIELDS:
        raise ValueError("Active binding source header changed")
    ids = [row["semantic_binding_id"] for row in active]
    if len(ids) != len(set(ids)) or any(
        not re.fullmatch(r"ERA-SBN-[0-9]{6}", identifier) for identifier in ids
    ):
        raise ValueError("Semantic binding identifiers are invalid or duplicated")
    subject_keys = [
        (row["registry_subject_type"], row["registry_subject_id"], row["binding_predicate"])
        for row in active
    ]
    if len(subject_keys) != len(set(subject_keys)):
        raise ValueError("Registry subject and predicate pair is duplicated")

    ledger_by_id = {row["semantic_binding_id"]: row for row in ledger}
    if len(ledger_by_id) != len(ledger) or not set(ids).issubset(ledger_by_id):
        raise ValueError("Semantic binding ledger omits or duplicates active IDs")
    for identifier, row in ledger_by_id.items():
        if not re.fullmatch(r"ERA-SBN-[0-9]{6}", identifier):
            raise ValueError(f"Semantic binding ledger ID is invalid: {identifier}")
        if row["registry_subject_type"] not in {"field", "value_member"}:
            raise ValueError(f"Semantic binding ledger subject type is invalid: {identifier}")
        if row["lifecycle"] not in {"active", "deprecated", "retired"}:
            raise ValueError(f"Semantic binding ledger lifecycle is invalid: {identifier}")

    structural_by_key = {row["legacy_concept_id"]: row for row in structural}
    value_by_key = {
        row["target_property"] + "|" + row["source_value"]: row for row in values
    }
    structural_keys = set()
    value_keys = set()
    for row in active:
        identifier = row["semantic_binding_id"]
        ledger_row = ledger_by_id[identifier]
        if (
            ledger_row["registry_subject_type"] != row["registry_subject_type"]
            or ledger_row["registry_subject_id"] != row["registry_subject_id"]
            or ledger_row["first_binding_release"] != config["binding_release_id"]
            or ledger_row["lifecycle"] != row["lifecycle"]
        ):
            raise ValueError(f"Ledger mismatch: {identifier}")
        if row["registry_release_id"] != config["registry"]["release_id"]:
            raise ValueError(f"Registry release mismatch: {identifier}")
        if row["registry_subject_type"] == "field":
            pattern = r"ERA-FLD-[0-9]{6}"
            required_predicate = AOM_SCHEMA + "mapsToProperty"
            required_artifact = "fields.csv"
        elif row["registry_subject_type"] == "value_member":
            pattern = r"ERA-VSM-[0-9]{6}"
            required_predicate = AOM_SCHEMA + "mapsToConcept"
            required_artifact = "value_set_members.csv"
        else:
            raise ValueError(f"Unsupported registry subject type: {identifier}")
        if not re.fullmatch(pattern, row["registry_subject_id"]):
            raise ValueError(f"Registry subject identifier failure: {identifier}")
        if row["binding_predicate"] != required_predicate:
            raise ValueError(f"Binding predicate failure: {identifier}")
        if row["registry_source_artifact"] != required_artifact:
            raise ValueError(f"Registry artifact failure: {identifier}")
        if not re.fullmatch(r"[0-9a-f]{64}", row["registry_row_sha256"]):
            raise ValueError(f"Registry row fingerprint failure: {identifier}")
        if (
            row["lifecycle"] != "active"
            or row["reviewer_status"] != "approved"
            or not row["reviewer"]
            or not row["review_date"]
            or not row["evidence"]
            or not row["rationale"]
        ):
            raise ValueError(f"Review or lifecycle failure: {identifier}")
        if not row["domain_scope"].startswith("livestock-"):
            raise ValueError(f"Unsupported shared-core promotion: {identifier}")

        source_key = row["semantic_source_key"]
        if row["semantic_source_file"] == str(STRUCTURAL_SOURCE.relative_to(ROOT)):
            source = structural_by_key[source_key]
            structural_keys.add(source_key)
            expected_target = expand(source["target_property"])
        elif row["semantic_source_file"] == str(VALUE_SOURCE.relative_to(ROOT)):
            source = value_by_key[source_key]
            value_keys.add(source_key)
            expected_target = value_target(source)
        else:
            raise ValueError(f"Unpinned semantic source: {identifier}")
        if source["status"] != "approved" or source["reviewer"] != row["reviewer"]:
            raise ValueError(f"Source approval mismatch: {identifier}")
        if source["review_date"] != row["review_date"] or expected_target != row["target_iri"]:
            raise ValueError(f"Source target mismatch: {identifier}")

    active_source_decisions = len(structural_keys) + len(value_keys)
    if active_source_decisions != expected["active_source_decisions"]:
        raise ValueError("Active source-decision count differs from contract")
    return structural_keys, value_keys


def build_holds(config, structural, values, active_structural, active_values):
    overrides = config["held_registry_subjects"]
    holds = []

    for row in sorted(structural, key=lambda item: item["legacy_concept_id"]):
        key = row["legacy_concept_id"]
        if key in active_structural:
            continue
        override = overrides.get(key, {})
        reason_code = override.get("reason_code", "registry-field-not-allocated")
        reason = override.get(
            "reason",
            "No stable IW-02 registry field represents this approved legacy semantic contract.",
        )
        holds.append({
            "source_kind": "structural",
            "semantic_source_key": key,
            "legacy_concept_id": key,
            "registry_subject_type": override.get("registry_subject_type", "field"),
            "registry_subject_id": override.get("registry_subject_id", ""),
            "registry_row_sha256": override.get("registry_row_sha256", ""),
            "registry_source_artifact": override.get("registry_source_artifact", "fields.csv"),
            "target_iri": expand(row["target_property"]),
            "binding_action": row["binding_kind"],
            "reason_code": reason_code,
            "reason": reason,
            "evidence": row["evidence"],
            "lifecycle": "held",
            "reviewer_status": row["status"],
            "reviewer": row["reviewer"],
            "review_date": row["review_date"],
            "rationale": row["compatibility_policy"],
        })

    for row in sorted(values, key=lambda item: (item["target_property"], item["source_value"])):
        key = row["target_property"] + "|" + row["source_value"]
        if key in active_values:
            continue
        override = overrides.get(key, {})
        reason_code = override.get("reason_code", "registry-value-member-not-allocated")
        reason = override.get(
            "reason",
            "Approved semantic decision has no stable IW-02 value-member identity.",
        )
        holds.append({
            "source_kind": "value",
            "semantic_source_key": key,
            "legacy_concept_id": "",
            "registry_subject_type": override.get("registry_subject_type", "value_member"),
            "registry_subject_id": override.get("registry_subject_id", ""),
            "registry_row_sha256": override.get("registry_row_sha256", ""),
            "registry_source_artifact": override.get(
                "registry_source_artifact", "value_set_members.csv"
            ),
            "target_iri": value_target(row),
            "binding_action": row["binding_action"],
            "reason_code": reason_code,
            "reason": reason,
            "evidence": row["evidence"],
            "lifecycle": "held",
            "reviewer_status": row["status"],
            "reviewer": row["reviewer"],
            "review_date": row["review_date"],
            "rationale": row["rationale"],
        })

    for position, row in enumerate(holds, 1):
        row["hold_id"] = f"ERA-SBH-{position:06d}"
    if len(holds) != config["expected_counts"]["held_source_decisions"]:
        raise ValueError("Held source-decision count differs from contract")
    return [{field: row[field] for field in HOLD_FIELDS} for row in holds]


def turtle_literal(value):
    return json.dumps(value, ensure_ascii=False)


def write_turtle(path, config, active):
    release_uri = BINDING_RELEASE_BASE + config["binding_release_id"]
    lines = [
        "@prefix aom: <https://w3id.org/era-aom/schema/> .",
        "@prefix dcterms: <http://purl.org/dc/terms/> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "",
    ]
    for row in sorted(active, key=lambda item: item["semantic_binding_id"]):
        binding_uri = BINDING_BASE + row["semantic_binding_id"]
        subject_uri = registry_subject_iri(row)
        source_record = row["semantic_source_file"] + "#" + row["semantic_source_key"]
        terms = [
            "a aom:RegistrySemanticBinding",
            "aom:semanticBindingIdentifier " + turtle_literal(row["semantic_binding_id"]),
            "aom:registryReleaseIdentifier " + turtle_literal(row["registry_release_id"]),
            f"aom:registrySubject <{subject_uri}>",
            "aom:registrySubjectType " + turtle_literal(row["registry_subject_type"]),
            "aom:registrySubjectIdentifier " + turtle_literal(row["registry_subject_id"]),
            "aom:registryRowChecksum " + turtle_literal(row["registry_row_sha256"]),
            f"aom:bindingPredicate <{row['binding_predicate']}>",
            f"aom:bindingTarget <{row['target_iri']}>",
            "aom:evidenceReference " + turtle_literal(row["evidence"]),
            "aom:bindingLifecycle " + turtle_literal(row["lifecycle"]),
            "aom:reviewerStatus " + turtle_literal(row["reviewer_status"]),
            "aom:domainScope " + turtle_literal(row["domain_scope"]),
            "aom:sourceSemanticRecord " + turtle_literal(source_record),
            "aom:sourceRegistryArtifact " + turtle_literal(row["registry_source_artifact"]),
            "aom:bindingRationale " + turtle_literal(row["rationale"]),
            "dcterms:contributor " + turtle_literal(row["reviewer"]),
            f"dcterms:issued {turtle_literal(row['review_date'])}^^xsd:date",
            f"dcterms:isPartOf <{release_uri}>",
        ]
        lines.append(f"<{binding_uri}> " + " ;\n  ".join(terms) + " .\n")
        lines.append(
            f"<{subject_uri}> <{row['binding_predicate']}> <{row['target_iri']}> .\n"
        )
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def write_jsonld(path, config, active):
    release_uri = BINDING_RELEASE_BASE + config["binding_release_id"]
    graph = []
    for row in sorted(active, key=lambda item: item["semantic_binding_id"]):
        subject_uri = registry_subject_iri(row)
        source_record = row["semantic_source_file"] + "#" + row["semantic_source_key"]
        graph.append({
            "@id": BINDING_BASE + row["semantic_binding_id"],
            "@type": AOM_SCHEMA + "RegistrySemanticBinding",
            AOM_SCHEMA + "semanticBindingIdentifier": row["semantic_binding_id"],
            AOM_SCHEMA + "registryReleaseIdentifier": row["registry_release_id"],
            AOM_SCHEMA + "registrySubject": {"@id": subject_uri},
            AOM_SCHEMA + "registrySubjectType": row["registry_subject_type"],
            AOM_SCHEMA + "registrySubjectIdentifier": row["registry_subject_id"],
            AOM_SCHEMA + "registryRowChecksum": row["registry_row_sha256"],
            AOM_SCHEMA + "bindingPredicate": {"@id": row["binding_predicate"]},
            AOM_SCHEMA + "bindingTarget": {"@id": row["target_iri"]},
            AOM_SCHEMA + "evidenceReference": row["evidence"],
            AOM_SCHEMA + "bindingLifecycle": row["lifecycle"],
            AOM_SCHEMA + "reviewerStatus": row["reviewer_status"],
            AOM_SCHEMA + "domainScope": row["domain_scope"],
            AOM_SCHEMA + "sourceSemanticRecord": source_record,
            AOM_SCHEMA + "sourceRegistryArtifact": row["registry_source_artifact"],
            AOM_SCHEMA + "bindingRationale": row["rationale"],
            DCTERMS + "contributor": row["reviewer"],
            DCTERMS + "issued": {"@value": row["review_date"], "@type": XSD + "date"},
            DCTERMS + "isPartOf": {"@id": release_uri},
        })
        graph.append({
            "@id": subject_uri,
            row["binding_predicate"]: {"@id": row["target_iri"]},
        })
    write_json(path, {"@graph": graph})


def build(config_path):
    config = read_json(config_path)
    active, ledger, structural, values = load_sources(config)
    active_structural, active_values = validate_active_source(
        config, active, ledger, structural, values
    )
    holds = build_holds(
        config, structural, values, active_structural, active_values
    )
    output = ROOT / "dist" / "registry-bindings" / f"version={config['binding_release_id']}"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    shutil.copyfile(ACTIVE_SOURCE, output / "semantic_bindings.csv")
    shutil.copyfile(LEDGER_SOURCE, output / "semantic_binding_id_ledger.csv")
    write_csv(output / "semantic_binding_holds.csv", holds, HOLD_FIELDS)
    shutil.copyfile(CSVW_SOURCE, output / "semantic_bindings.csv-metadata.json")
    shutil.copyfile(SCHEMA_SOURCE, output / "registry-semantic-binding.schema.ttl")
    shutil.copyfile(SHACL_SOURCE, output / "registry-semantic-bindings.shacl.ttl")
    write_turtle(output / "semantic_bindings.ttl", config, active)
    write_jsonld(output / "semantic_bindings.jsonld", config, active)

    files = sorted(path for path in output.iterdir() if path.is_file())
    if {path.name for path in files} != OUTPUT_FILES:
        raise ValueError("Generated AC-09 distribution set differs from contract")
    reason_counts = dict(sorted(Counter(row["reason_code"] for row in holds).items()))
    manifest = {
        "manifest_schema_version": "1.0.0",
        "binding_release_id": config["binding_release_id"],
        "status": config["status"],
        "latest": config["latest"],
        "created": config["created"],
        "governing_adr": config["governing_adr"],
        "registry": config["registry"],
        "semantic_governor": config["semantic_governor"],
        "source_fingerprints": {
            **config["semantic_sources"],
            str(ACTIVE_SOURCE.relative_to(ROOT)): sha256(ACTIVE_SOURCE),
            str(LEDGER_SOURCE.relative_to(ROOT)): sha256(LEDGER_SOURCE),
        },
        "counts": {
            **config["expected_counts"],
            "hold_reason_counts": reason_counts,
        },
        "rollback": config["rollback"],
        "distributions": [
            {
                "path": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in files
        ],
    }
    write_json(output / "manifest.json", manifest)
    checksum_files = [*files, output / "manifest.json"]
    (output / "checksums.sha256").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in checksum_files),
        encoding="utf-8",
    )
    return output


def validate_registry(config, active, holds, registry_root):
    registry_root = Path(registry_root).resolve()
    merge_commit = config["registry"]["merge_commit"]
    subprocess.run(
        ["git", "-C", str(registry_root), "merge-base", "--is-ancestor", merge_commit, "HEAD"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    version_dir = registry_root / "registry" / f"version={config['registry']['version']}"
    if sha256(version_dir / "publication_manifest.json") != config["registry"]["publication_manifest_sha256"]:
        raise ValueError("Pinned IW-02 publication manifest changed")
    artifact_dir = version_dir / "artifacts"
    for name, expected in config["registry"]["artifacts"].items():
        if sha256(artifact_dir / name) != expected:
            raise ValueError(f"Pinned IW-02 registry artifact changed: {name}")

    rows_by_artifact = {}
    for artifact in {row["registry_source_artifact"] for row in active} | {
        row["registry_source_artifact"] for row in holds if row["registry_subject_id"]
    }:
        rows = read_csv(artifact_dir / artifact)
        key = "field_id" if artifact == "fields.csv" else "value_member_id"
        rows_by_artifact[artifact] = {row[key]: row for row in rows}

    for row in [*active, *(item for item in holds if item["registry_subject_id"])]:
        source = rows_by_artifact[row["registry_source_artifact"]].get(
            row["registry_subject_id"]
        )
        if not source or row_sha256(source) != row["registry_row_sha256"]:
            raise ValueError(f"Registry subject fingerprint mismatch: {row['registry_subject_id']}")
        if row in active and source["lifecycle"] != "active":
            raise ValueError(f"Active binding points to held registry subject: {row['registry_subject_id']}")


def validate(config_path, registry_root=None):
    from pyshacl import validate as shacl_validate
    from rdflib import Graph, OWL, RDF, SKOS, URIRef

    config = read_json(config_path)
    active, ledger, structural, values = load_sources(config)
    active_structural, active_values = validate_active_source(
        config, active, ledger, structural, values
    )
    expected_holds = build_holds(
        config, structural, values, active_structural, active_values
    )
    output = ROOT / "dist" / "registry-bindings" / f"version={config['binding_release_id']}"
    manifest = read_json(output / "manifest.json")
    holds = read_csv(output / "semantic_binding_holds.csv")
    if read_csv(output / "semantic_bindings.csv") != active:
        raise ValueError("Published active bindings differ from governed source")
    if read_csv(output / "semantic_binding_id_ledger.csv") != ledger:
        raise ValueError("Published identifier ledger differs from governed source")
    if holds != expected_holds:
        raise ValueError("Published hold register differs from source partition")
    if manifest["status"] != "candidate" or manifest["latest"]:
        raise ValueError("Binding candidate status or latest pointer is invalid")
    if manifest["counts"]["held_source_decisions"] != len(holds):
        raise ValueError("Binding hold count differs from manifest")
    if manifest["counts"]["hold_reason_counts"] != dict(
        sorted(Counter(row["reason_code"] for row in holds).items())
    ):
        raise ValueError("Binding hold reasons differ from manifest")
    if config["rollback"]["latest_pointer_change"]:
        raise ValueError("Candidate rollback contract advances latest pointer")

    distributions = {item["path"]: item for item in manifest["distributions"]}
    if set(distributions) != OUTPUT_FILES:
        raise ValueError("Manifest distribution set differs from AC-09 contract")
    for name, record in distributions.items():
        path = output / name
        if path.stat().st_size != record["bytes"] or sha256(path) != record["sha256"]:
            raise ValueError(f"Distribution fingerprint mismatch: {name}")
    expected_checksums = "".join(
        f"{sha256(output / name)}  {name}\n"
        for name in sorted(OUTPUT_FILES)
    ) + f"{sha256(output / 'manifest.json')}  manifest.json\n"
    if (output / "checksums.sha256").read_text(encoding="utf-8") != expected_checksums:
        raise ValueError("Binding checksum file differs from distributions")

    csvw = read_json(output / "semantic_bindings.csv-metadata.json")
    csvw_names = [column["name"] for column in csvw["tableSchema"]["columns"]]
    if csvw_names != ACTIVE_FIELDS or csvw["tableSchema"]["primaryKey"] != "semantic_binding_id":
        raise ValueError("CSVW descriptor differs from active binding source")

    ttl_graph = Graph().parse(output / "semantic_bindings.ttl")
    jsonld_graph = Graph().parse(output / "semantic_bindings.jsonld")
    if set(ttl_graph) != set(jsonld_graph):
        raise ValueError("Turtle and JSON-LD semantic binding graphs differ")
    binding_class = URIRef(AOM_SCHEMA + "RegistrySemanticBinding")
    binding_nodes = set(ttl_graph.subjects(RDF.type, binding_class))
    if len(binding_nodes) != len(active):
        raise ValueError("RDF semantic binding identity count differs from source")
    conforms, _, report = shacl_validate(
        ttl_graph,
        shacl_graph=Graph().parse(output / "registry-semantic-bindings.shacl.ttl"),
        ont_graph=Graph().parse(output / "registry-semantic-binding.schema.ttl"),
    )
    if not conforms:
        raise ValueError(f"Registry semantic binding SHACL failure: {report}")

    target_release = ROOT / "dist" / "releases" / config["semantic_governor"]["target_release"]
    target_graph = Graph()
    for name, expected in config["semantic_governor"]["target_artifacts"].items():
        path = target_release / name
        if sha256(path) != expected:
            raise ValueError(f"Pinned AOM target artifact changed: {name}")
        target_graph += Graph().parse(path)
    expected_types = {
        "owl:DatatypeProperty": OWL.DatatypeProperty,
        "owl:ObjectProperty": OWL.ObjectProperty,
        "skos:Concept": SKOS.Concept,
    }
    for row in active:
        target = URIRef(row["target_iri"])
        expected_type = expected_types[row["target_kind"]]
        if (target, RDF.type, expected_type) not in target_graph:
            raise ValueError(f"Dangling or mistyped AOM target: {row['semantic_binding_id']}")
        subject = URIRef(registry_subject_iri(row))
        predicate = URIRef(row["binding_predicate"])
        if (subject, predicate, target) not in ttl_graph:
            raise ValueError(f"Direct semantic assertion missing: {row['semantic_binding_id']}")
        if row["target_iri"].startswith("https://w3id.org/era-aom/core/"):
            raise ValueError(f"Unsupported shared-core promotion: {row['semantic_binding_id']}")

    if registry_root:
        validate_registry(config, active, holds, registry_root)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "validate"))
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--registry-root")
    args = parser.parse_args()
    config_path = Path(args.config).resolve()
    if args.command == "build":
        output = build(config_path)
        print(f"Built registry semantic binding candidate: {output}")
    else:
        validate(config_path, args.registry_root)
        print("Registry semantic binding validation passed")


if __name__ == "__main__":
    main()
