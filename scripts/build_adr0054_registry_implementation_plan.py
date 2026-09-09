#!/usr/bin/env python3
"""Build recommendation-only ADR 0054 cross-repository implementation plan."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/data-model-v9"
SNAPSHOT = REVIEW / "source_snapshot.json"


REPOSITORIES = [
    {
        "repository_id": "RP-01",
        "repository": "ERAgriculture/era-data-pipeline",
        "role": "producer",
        "input_contract": "Canonical workbook snapshot, accepted disposition cohorts, pinned AOM binding release",
        "output_contract": "Deterministic normalized registry candidate, validation report, source fingerprints",
        "implementation_boundary": "May generate candidates; may not mutate canonical workbook or publish a release",
        "completion_evidence": "Clean rebuild equality, schema validation, row-preservation report, four-round coverage",
    },
    {
        "repository_id": "RP-02",
        "repository": "ERAgriculture/era-data",
        "role": "publisher",
        "input_contract": "Hash-pinned pipeline candidate and consumer compatibility reports",
        "output_contract": "Immutable release candidate, CSVW descriptors, product profiles, manifest, catalog entry",
        "implementation_boundary": "Must not overwrite v2026.1 or advance latest pointer before cutover gate",
        "completion_evidence": "Artifact hashes, foreign-key validation, catalog validation, migration report",
    },
    {
        "repository_id": "RP-03",
        "repository": "ERAgriculture/era-aom",
        "role": "semantic-governor",
        "input_contract": "Stable registry candidate IDs and accepted row-level semantic evidence",
        "output_contract": "Reviewed semantic-binding registry, SHACL constraints, versioned RDF distributions",
        "implementation_boundary": "No identity inference, unreviewed mapping, or shared-core promotion",
        "completion_evidence": "Binding completeness, target integrity, global identity audit, clean-store graph validation",
    },
    {
        "repository_id": "RP-04",
        "repository": "ERAgriculture/eragri",
        "role": "package-consumer",
        "input_contract": "Pinned era-data release candidate and compatibility profile",
        "output_contract": "Release-pinned package data and dictionary with compatibility tests",
        "implementation_boundary": "Must retain old supported contract until explicit package migration",
        "completion_evidence": "Column, type, order, documentation, release, and checksum compatibility report",
    },
    {
        "repository_id": "RP-05",
        "repository": "ERAgriculture/era-docs",
        "role": "documentation-consumer",
        "input_contract": "Pinned released registry and product dictionaries",
        "output_contract": "Generated human guidance carrying release identity and explicit limitations",
        "implementation_boundary": "Must not claim unresolved units, fields, or lookups are formalized",
        "completion_evidence": "Generated-page drift test, link validation, release and limitation visibility",
    },
    {
        "repository_id": "RP-06",
        "repository": "ERAgriculture/era-program",
        "role": "programme-governor",
        "input_contract": "Accepted ADR, repository PR evidence, release and compatibility reports",
        "output_contract": "Cross-repository issue map, cutover decision, durable closure record",
        "implementation_boundary": "May not close programme issues from producer-only completion",
        "completion_evidence": "All repository gates linked, residual holds explicit, rollback window complete",
    },
]


ARTIFACTS = [
    {
        "artifact_id": "AC-01",
        "artifact": "source_snapshot",
        "contract_layer": "canonical authoring provenance",
        "producer": "era-data-pipeline",
        "publisher": "era-data",
        "format": "JSON plus checksums",
        "primary_key": "source_snapshot_id",
        "foreign_keys": "release_manifest.source_snapshot_id",
        "required_content": "Workbook checksum, sheet names, extraction timestamp, producer commit, accepted cohort hashes",
        "release_gate": "Canonical source read-only capture succeeds; no source rows silently omitted",
    },
    {
        "artifact_id": "AC-02",
        "artifact": "tables",
        "contract_layer": "normalized logical registry",
        "producer": "era-data-pipeline",
        "publisher": "era-data",
        "format": "CSV plus CSVW",
        "primary_key": "table_id",
        "foreign_keys": "fields.table_id",
        "required_content": "Opaque stable ID, current label, lifecycle, source lineage, evidence status",
        "release_gate": "Unique IDs and labels; no dangling field references",
    },
    {
        "artifact_id": "AC-03",
        "artifact": "fields",
        "contract_layer": "normalized logical registry",
        "producer": "era-data-pipeline",
        "publisher": "era-data",
        "format": "CSV plus CSVW",
        "primary_key": "field_id",
        "foreign_keys": "table_id -> tables.table_id",
        "required_content": "Opaque stable ID, table ID, governed name, definition, lifecycle, replacement, lineage",
        "release_gate": "Logical identity unique; eight unresolved field cases remain explicit holds",
    },
    {
        "artifact_id": "AC-04",
        "artifact": "field_profiles",
        "contract_layer": "extraction-round profiles",
        "producer": "era-data-pipeline",
        "publisher": "era-data",
        "format": "CSV plus CSVW",
        "primary_key": "field_profile_id",
        "foreign_keys": "field_id -> fields.field_id",
        "required_content": "Round, source name, order, datatype, format, requiredness, validation, source presence",
        "release_gate": "Four rounds represented; 13 accepted consolidations applied without collapsing source provenance",
    },
    {
        "artifact_id": "AC-05",
        "artifact": "value_sets",
        "contract_layer": "field-scoped value sets",
        "producer": "era-data-pipeline",
        "publisher": "era-data",
        "format": "CSV plus CSVW",
        "primary_key": "value_set_id",
        "foreign_keys": "value_set_members.value_set_id; field_value_sets.value_set_id",
        "required_content": "Stable ID, title, publication function, lifecycle, source lineage, review status",
        "release_gate": "All lookup groups represented; 41 unmatched pairs remain unbound holds",
    },
    {
        "artifact_id": "AC-06",
        "artifact": "value_set_members",
        "contract_layer": "field-scoped value sets",
        "producer": "era-data-pipeline",
        "publisher": "era-data",
        "format": "CSV plus CSVW",
        "primary_key": "value_member_id",
        "foreign_keys": "value_set_id -> value_sets.value_set_id",
        "required_content": "Stable member ID, raw code, preferred label, lifecycle, source row, evidence status",
        "release_gate": "Raw values preserved; no fuzzy binding or automatic semantic promotion",
    },
    {
        "artifact_id": "AC-07",
        "artifact": "field_value_sets",
        "contract_layer": "field-scoped value sets",
        "producer": "era-data-pipeline",
        "publisher": "era-data",
        "format": "CSV plus CSVW",
        "primary_key": "field_value_set_binding_id",
        "foreign_keys": "field_id -> fields.field_id; value_set_id -> value_sets.value_set_id",
        "required_content": "Stable binding ID, field and value-set IDs, scope, lifecycle, evidence status",
        "release_gate": "Only reviewed exact identity bindings active; 41 unmatched pairs retained as holds",
    },
    {
        "artifact_id": "AC-08",
        "artifact": "unit_mappings",
        "contract_layer": "raw-to-canonical unit mappings",
        "producer": "era-data-pipeline",
        "publisher": "era-data",
        "format": "CSV plus CSVW",
        "primary_key": "unit_mapping_id",
        "foreign_keys": "field_id -> fields.field_id when field scope is known",
        "required_content": "Raw string, context, quantity kind, canonical IRI, factor, offset, basis, evidence, status",
        "release_gate": "All 66 accepted cases represented as holds; no inferred mapping or conversion",
    },
    {
        "artifact_id": "AC-09",
        "artifact": "semantic_bindings",
        "contract_layer": "AOM semantic bindings",
        "producer": "era-aom",
        "publisher": "era-aom",
        "format": "CSV source, SHACL, JSON-LD, Turtle",
        "primary_key": "semantic_binding_id",
        "foreign_keys": "Registry subject ID; governed AOM target IRI",
        "required_content": "Subject type and ID, predicate, target IRI, evidence, lifecycle, reviewer status",
        "release_gate": "Reviewed target identity, valid predicate, no dangling IRI, crop-and-livestock evidence for core",
    },
    {
        "artifact_id": "AC-10",
        "artifact": "product_profiles",
        "contract_layer": "released product schemas",
        "producer": "era-data-pipeline",
        "publisher": "era-data",
        "format": "CSV plus CSVW and JSON Table Schema",
        "primary_key": "product_profile_id",
        "foreign_keys": "product_fields.product_profile_id",
        "required_content": "Product identity, release, ordered field profile, applicability, lifecycle",
        "release_gate": "Agronomy and livestock profiles remain separate and preserve reviewed order",
    },
    {
        "artifact_id": "AC-11",
        "artifact": "product_fields",
        "contract_layer": "released product schemas",
        "producer": "era-data-pipeline",
        "publisher": "era-data",
        "format": "CSV plus CSVW and JSON Table Schema",
        "primary_key": "product_field_id",
        "foreign_keys": "product_profile_id -> product_profiles; field_id -> fields when source field exists",
        "required_content": "Order, physical and logical type, description, derivation, unit or basis, values, lifecycle",
        "release_gate": "Each 138-column product has reviewed documentation or explicit deferral",
    },
    {
        "artifact_id": "AC-12",
        "artifact": "consumer_compatibility",
        "contract_layer": "release compatibility views",
        "producer": "pipeline, AOM, eragri, and docs consumers",
        "publisher": "era-data",
        "format": "JSON and CSV",
        "primary_key": "compatibility_report_id",
        "foreign_keys": "release_manifest.release_id; consumer repository and commit",
        "required_content": "Expected and observed fields, order, types, hashes, differences, dispositions, result",
        "release_gate": "All 44 accepted differences resolved or carried as reviewed release holds",
    },
    {
        "artifact_id": "AC-13",
        "artifact": "release_manifest",
        "contract_layer": "release provenance",
        "producer": "era-data-pipeline",
        "publisher": "era-data",
        "format": "JSON with DCAT and PROV metadata",
        "primary_key": "release_id",
        "foreign_keys": "All artifact IDs, checksums, source snapshot, producer and consumer commits",
        "required_content": "Immutable version, timestamps, checksums, lineage, compatibility, holds, supersession",
        "release_gate": "Every listed artifact exists and hashes match; migration and rollback records complete",
    },
    {
        "artifact_id": "AC-14",
        "artifact": "catalog_entry",
        "contract_layer": "release discovery",
        "producer": "era-data",
        "publisher": "era-data",
        "format": "JSON with DCAT metadata",
        "primary_key": "dataset and distribution identifiers",
        "foreign_keys": "release_manifest.release_id and distribution checksums",
        "required_content": "Version, status, landing pages, distributions, licence, provenance, compatibility links",
        "release_gate": "Candidate status visible before cutover; latest pointer changes only after all consumer gates",
    },
]


WAVES = [
    {
        "wave_id": "IW-00",
        "name": "Governance acceptance and issue decomposition",
        "repositories": "era-aom;era-program",
        "depends_on": "ADR 0052 and accepted v4, v6, v8 cohorts",
        "deliverables": "Accepted ADR 0054; one owner-scoped issue per delivery wave; pinned baseline",
        "entry_gate": "Recommendation pack validates and human accepts RI-01 through RI-12",
        "exit_gate": "Owners, artifact contracts, dependencies, holds, and rollback responsibility assigned",
        "rollback": "Reject or revise plan; no implementation artifact exists",
    },
    {
        "wave_id": "IW-01",
        "name": "Registry schemas and deterministic producer",
        "repositories": "era-data-pipeline",
        "depends_on": "IW-00",
        "deliverables": "CSVW schemas, opaque-ID ledger, normalized generator, source and row-preservation tests",
        "entry_gate": "Canonical workbook available read only; accepted source dispositions hash-match",
        "exit_gate": "AC-01 through AC-08 and AC-10 through AC-13 build twice identically with valid keys",
        "rollback": "Keep old generator default; remove candidate output only; never recycle allocated IDs",
    },
    {
        "wave_id": "IW-02",
        "name": "Immutable release-candidate publication",
        "repositories": "era-data",
        "depends_on": "IW-01",
        "deliverables": "Versioned candidate registry, product profiles, manifest, catalog candidate, migration draft",
        "entry_gate": "Pinned pipeline candidate passes schemas, hashes, foreign keys, and completeness tests",
        "exit_gate": "Candidate is immutable, separately addressed, downloadable, and not latest",
        "rollback": "Withdraw candidate catalog status while retaining audit record; v2026.1 unchanged",
    },
    {
        "wave_id": "IW-03",
        "name": "Semantic binding integration",
        "repositories": "era-aom;era-data-pipeline;era-data",
        "depends_on": "IW-02",
        "deliverables": "AC-09 binding registry, SHACL checks, final candidate refresh with pinned AOM release",
        "entry_gate": "Stable candidate subject IDs exist; row-level semantic evidence is accepted",
        "exit_gate": "All active bindings validate; unknown mappings remain explicit holds; graph rebuild is clean",
        "rollback": "Pin prior AOM release and candidate; do not delete or reassign published AOM IDs",
    },
    {
        "wave_id": "IW-04",
        "name": "Package compatibility migration",
        "repositories": "eragri",
        "depends_on": "IW-03",
        "deliverables": "Release-pinned package objects, complete dictionary view, AC-12 package report",
        "entry_gate": "Final candidate and migration report are hash pinned",
        "exit_gate": "Package tests reconcile columns, order, types, definitions, release, and checksums",
        "rollback": "Restore prior package default and retain explicit opt-in to candidate",
    },
    {
        "wave_id": "IW-05",
        "name": "Generated documentation alignment",
        "repositories": "era-docs",
        "depends_on": "IW-03;IW-04",
        "deliverables": "Release-pinned generated field, value-set, unit, semantic, and limitation pages",
        "entry_gate": "Registry and package contracts are final candidate artifacts",
        "exit_gate": "Docs drift test passes and every unresolved hold remains visible",
        "rollback": "Restore prior docs target; do not change data or package release",
    },
    {
        "wave_id": "IW-06",
        "name": "Release cutover and programme closure",
        "repositories": "era-data;era-program",
        "depends_on": "IW-04;IW-05",
        "deliverables": "Final immutable release, catalog/latest update, compatibility bundle, closure evidence",
        "entry_gate": "All repository CI green; migration and rollback tested; residual holds accepted",
        "exit_gate": "Observation window passes; issues 27, 21, then 17 close against linked evidence",
        "rollback": "Repoint latest and consumer defaults to prior release; preserve failed release and IDs",
    },
]


CONSTRAINTS = [
    {
        "constraint_id": "GC-01",
        "cohort": "disjoint-round duplicate field keys",
        "case_count": 13,
        "disposition": "approved-for-profile-consolidation",
        "implementation_rule": "Create one logical field identity with distinct round profiles and full source lineage.",
        "release_effect": "Required in IW-01.",
    },
    {
        "constraint_id": "GC-02",
        "cohort": "unresolved field-key cases",
        "case_count": 8,
        "disposition": "hold",
        "implementation_rule": "Represent source rows and hold reason; allocate no merged identity without source review.",
        "release_effect": "May ship only as explicit non-active holds.",
    },
    {
        "constraint_id": "GC-03",
        "cohort": "unmatched lookup pairs",
        "case_count": 41,
        "disposition": "hold",
        "implementation_rule": "Preserve lookup groups; create no field binding from label or fuzzy match.",
        "release_effect": "May ship only as unbound value-set holds.",
    },
    {
        "constraint_id": "GC-04",
        "cohort": "unresolved and conflicting unit rows",
        "case_count": 66,
        "disposition": "hold",
        "implementation_rule": "Preserve raw text and context; create no canonical IRI, quantity kind, or conversion.",
        "release_effect": "All rows remain explicit held unit-mapping records.",
    },
    {
        "constraint_id": "GC-05",
        "cohort": "product-field documentation dispositions",
        "case_count": 138,
        "disposition": "evidence-hold",
        "implementation_rule": "Author reviewed contract or explicit deferral per product field; candidate text is not authority.",
        "release_effect": "Every released field needs reviewed content or visible deferral.",
    },
    {
        "constraint_id": "GC-06",
        "cohort": "consumer contract differences",
        "case_count": 44,
        "disposition": "evidence-hold",
        "implementation_rule": "Carry each difference into compatibility report until reviewed migration or retirement.",
        "release_effect": "No silent addition, removal, rename, reorder, or type change.",
    },
    {
        "constraint_id": "GC-07",
        "cohort": "stable registry identifiers",
        "case_count": 0,
        "disposition": "not-allocated",
        "implementation_rule": "Use central append-only opaque ledger; IDs never encode mutable names and are never recycled.",
        "release_effect": "Allocation begins only after ADR acceptance and IW-01 tests.",
    },
    {
        "constraint_id": "GC-08",
        "cohort": "released v2026.1 artifacts",
        "case_count": 1,
        "disposition": "immutable",
        "implementation_rule": "Write new version path and migration report; never rebuild v2026.1 in place.",
        "release_effect": "Candidate and final release use a new version.",
    },
    {
        "constraint_id": "GC-09",
        "cohort": "shared-core semantic candidates",
        "case_count": 0,
        "disposition": "evidence-required",
        "implementation_rule": "Require equivalent crop and livestock use before core promotion.",
        "release_effect": "Feed-specific resources remain livestock scoped.",
    },
    {
        "constraint_id": "GC-10",
        "cohort": "canonical workbook source",
        "case_count": 1,
        "disposition": "read-only",
        "implementation_rule": "Registry work consumes hash-pinned source; approved spreadsheet tooling is required for source edits.",
        "release_effect": "No workbook correction is part of ADR 0054 planning or candidate generation.",
    },
    {
        "constraint_id": "GC-11",
        "cohort": "release and consumer cutover",
        "case_count": 0,
        "disposition": "not-authorized",
        "implementation_rule": "Candidate publication, consumer migration, latest-pointer change, and issue closure use separate gates.",
        "release_effect": "ADR acceptance alone publishes nothing and migrates no consumer.",
    },
]


DECISIONS = [
    {
        "review_id": "RI-01",
        "title": "Preserve source authority until cutover",
        "recommendation": "Keep canonical workbook as authoring authority while generating a separate normalized registry.",
        "rationale": "ADR 0052 separates current authority from target architecture.",
        "conditions_or_holds": "No source edit or authority cutover is authorized by this plan.",
    },
    {
        "review_id": "RI-02",
        "title": "Implement linked contract artifacts",
        "recommendation": "Implement AC-01 through AC-14 as separately validated and linked artifacts.",
        "rationale": "One nested JSON schema cannot govern source, profiles, values, units, semantics, products, and consumers.",
        "conditions_or_holds": "Names and columns are proposed contracts until ADR 0054 acceptance.",
    },
    {
        "review_id": "RI-03",
        "title": "Use opaque append-only identifiers",
        "recommendation": "Allocate table, field, value-set, member, profile, and binding IDs from central append-only ledgers.",
        "rationale": "Stable identity must survive label, source name, and lifecycle changes.",
        "conditions_or_holds": "No ID is allocated in this review; identifiers are never recycled or derived from mutable labels.",
    },
    {
        "review_id": "RI-04",
        "title": "Preserve every governed source case",
        "recommendation": "Fail generation when source rows, rounds, lookup groups, unit rows, or accepted holds disappear.",
        "rationale": "Current output omits one extraction round and unmatched source cases.",
        "conditions_or_holds": "Held records remain present and inactive rather than silently dropped.",
    },
    {
        "review_id": "RI-05",
        "title": "Publish candidates without mutating releases",
        "recommendation": "Publish registry work under a new immutable candidate version before any latest-pointer change.",
        "rationale": "v2026.1 fingerprints an older canonical source and must remain reproducible.",
        "conditions_or_holds": "Candidate status, supersession intent, migration draft, and rollback target must be explicit.",
    },
    {
        "review_id": "RI-06",
        "title": "Bind AOM through stable registry subjects",
        "recommendation": "Publish reviewed semantic bindings from era-aom against stable registry IDs and governed predicates.",
        "rationale": "String coincidence cannot sustain semantic identity across source and release changes.",
        "conditions_or_holds": "No unreviewed value mapping, inferred unit mapping, or unsupported core promotion.",
    },
    {
        "review_id": "RI-07",
        "title": "Pin package compatibility",
        "recommendation": "Make eragri data and dictionary objects declare compatible era-data release IDs and checksums.",
        "rationale": "Current package data, dictionary, and public schemas differ in count and coverage.",
        "conditions_or_holds": "Prior package contract remains supported until migration release is explicit.",
    },
    {
        "review_id": "RI-08",
        "title": "Generate documentation from released contracts",
        "recommendation": "Generate public data-model guidance from pinned released registry and product artifacts.",
        "rationale": "Hand-maintained claims currently exceed implemented model coverage.",
        "conditions_or_holds": "Generated pages must expose release identity, provenance, deferrals, and unresolved holds.",
    },
    {
        "review_id": "RI-09",
        "title": "Keep shared core evidence-gated",
        "recommendation": "Separate registry implementation from shared-core semantic promotion.",
        "rationale": "Generic labels do not prove equivalent crop and livestock scope.",
        "conditions_or_holds": "Each core promotion needs separate crop-and-livestock evidence and semantic review.",
    },
    {
        "review_id": "RI-10",
        "title": "Use ordered repository waves",
        "recommendation": "Deliver IW-00 through IW-06 in dependency order with one compatibility checkpoint per boundary.",
        "rationale": "Parallel unpinned changes would obscure producer-consumer drift and rollback ownership.",
        "conditions_or_holds": "A downstream wave starts only from a hash-pinned upstream candidate.",
    },
    {
        "review_id": "RI-11",
        "title": "Make rollback release-based",
        "recommendation": "Rollback by restoring prior release pointers and consumer defaults while retaining failed artifacts and IDs.",
        "rationale": "Deleting published identities or rewriting releases destroys auditability.",
        "conditions_or_holds": "Migration tests and rollback target are required before cutover.",
    },
    {
        "review_id": "RI-12",
        "title": "Close issues from end-to-end evidence",
        "recommendation": "Close issue 27 after schema release, issue 21 after dictionary parity, then issue 17 after full managed publication and consumer alignment.",
        "rationale": "Producer completion alone does not satisfy public model, dictionary, governance, and consumer outcomes.",
        "conditions_or_holds": "Residual holds remain linked and cannot disappear through issue closure.",
    },
]


AUTHORITIES = [
    {
        "authority": "AOM ADR 0052",
        "url": "../../docs/decisions/0052-data-model-registry-and-shared-core-contract.md",
        "supports": "Eight contract layers, repository ownership, immutable release rule, and completion gates.",
        "limitation": "Does not define concrete artifacts, PR sequence, stable-ID ledger, or rollback execution.",
    },
    {
        "authority": "ERA ADR 0007",
        "url": "https://github.com/ERAgriculture/era-program/blob/main/project-management/decisions/ADR-0007-canonical-vocab-source.md",
        "supports": "Canonical workbook authority before explicit cutover.",
        "limitation": "Does not make workbook row shape target registry architecture.",
    },
    {
        "authority": "W3C CSV on the Web",
        "url": "https://www.w3.org/TR/tabular-metadata/",
        "supports": "Tabular metadata, datatypes, primary keys, foreign keys, annotations, and validation.",
        "limitation": "Does not decide ERA field identity, source corrections, or semantic mappings.",
    },
    {
        "authority": "Frictionless Table Schema",
        "url": "https://specs.frictionlessdata.io/table-schema/",
        "supports": "Portable JSON table descriptors, constraints, primary keys, and foreign keys.",
        "limitation": "Does not govern RDF semantics, release authority, or human disposition evidence.",
    },
    {
        "authority": "W3C PROV-O",
        "url": "https://www.w3.org/TR/prov-o/",
        "supports": "Entity, activity, agent, derivation, and generation provenance.",
        "limitation": "Does not prescribe ERA release order or compatibility policy.",
    },
    {
        "authority": "W3C DCAT 3",
        "url": "https://www.w3.org/TR/vocab-dcat-3/",
        "supports": "Versioned datasets, distributions, checksums, relationships, and catalog discovery.",
        "limitation": "Does not define field-level registry content or consumer migration semantics.",
    },
]


def write_csv(name: str, rows: list[dict[str, object]]) -> None:
    path = REVIEW / name
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(name: str, value: object) -> None:
    (REVIEW / name).write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def build_evidence(snapshot: dict[str, object]) -> list[dict[str, object]]:
    evidence = []
    for index, source in enumerate(snapshot["sources"], start=1):
        evidence.append(
            {
                "evidence_id": f"EV-{index:02d}",
                "repository": source["repository"],
                "path": source["path"],
                "source_sha256": source["sha256"],
                "supports": source["supports"],
                "claim_boundary": "Read-only pinned evidence; does not authorize source, schema, semantic, package, documentation, release, or migration changes.",
            }
        )
    return evidence


def build_guided_markdown() -> str:
    lines = [
        "# Guided registry implementation recommendations",
        "",
        "Status: **proposed for human review**.",
        "",
        "| ID | Recommendation | Conditions / holds |",
        "|---|---|---|",
    ]
    for row in DECISIONS:
        lines.append(
            f"| `{row['review_id']}` | {row['recommendation']} | {row['conditions_or_holds']} |"
        )
    lines.extend(
        [
            "",
            "## Delivery sequence",
            "",
            "| Wave | Repositories | Exit gate |",
            "|---|---|---|",
        ]
    )
    for row in WAVES:
        lines.append(
            f"| `{row['wave_id']}` {row['name']} | {row['repositories']} | {row['exit_gate']} |"
        )
    lines.extend(
        [
            "",
            "## Human decision fields",
            "",
            "Acceptance must record decision, reviewer, date, and conditions against exact hashes of",
            "`guided_decision_recommendations.json`, `artifact_contracts.csv`,",
            "`implementation_waves.csv`, and `governance_constraints.csv`.",
            "",
            "Acceptance authorizes planning direction only. Each wave still requires its own issue,",
            "implementation PR, validation evidence, and downstream compatibility checkpoint.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    REVIEW.mkdir(parents=True, exist_ok=True)
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert snapshot["status"] == "read-only-cross-repository-evidence"
    assert len(snapshot["repositories"]) == 6
    assert len(snapshot["sources"]) == 16
    assert len(snapshot["tracking_issues"]) == 3

    decisions = [
        {
            **row,
            "recommendation_status": "proposed",
            "human_decision": "",
            "reviewer": "",
            "review_date": "",
            "decision_note": "",
        }
        for row in DECISIONS
    ]
    evidence = build_evidence(snapshot)
    summary = {
        "status": "recommendation-only",
        "repository_count": len(REPOSITORIES),
        "artifact_contract_count": len(ARTIFACTS),
        "implementation_wave_count": len(WAVES),
        "governance_constraint_count": len(CONSTRAINTS),
        "guided_decision_count": len(decisions),
        "evidence_record_count": len(evidence),
        "tracking_issue_count": len(snapshot["tracking_issues"]),
        "approved_profile_consolidation_count": 13,
        "field_hold_count": 8,
        "lookup_hold_count": 41,
        "unit_hold_count": 66,
        "product_field_evidence_hold_count": 138,
        "consumer_difference_hold_count": 44,
        "human_decision_recorded": False,
        "stable_identifiers_allocated": False,
        "source_repository_modified": False,
        "source_workbook_modified": False,
        "registry_generated": False,
        "semantic_bindings_modified": False,
        "package_modified": False,
        "documentation_consumer_modified": False,
        "release_authorized": False,
        "consumer_migration_authorized": False,
        "programme_issue_closure_authorized": False,
    }

    write_csv("repository_contracts.csv", REPOSITORIES)
    write_csv("artifact_contracts.csv", ARTIFACTS)
    write_csv("implementation_waves.csv", WAVES)
    write_csv("governance_constraints.csv", CONSTRAINTS)
    write_csv("authority_comparison.csv", AUTHORITIES)
    write_csv("evidence_register.csv", evidence)
    write_json("guided_decision_recommendations.json", decisions)
    write_json("implementation_plan_summary.json", summary)
    (REVIEW / "GUIDED_IMPLEMENTATION_PLAN.md").write_text(
        build_guided_markdown(), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
