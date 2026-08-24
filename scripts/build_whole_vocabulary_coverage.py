#!/usr/bin/env python3

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "inventory" / "workbook_sheets.csv"
DISPOSITIONS = ROOT / "inventory" / "sheet_disposition.csv"
OUTPUT = ROOT / "review" / "whole-vocabulary-v1"


RESOURCE_DECISIONS = {
    "bibliography": ("operational-source-management", "era-data-pipeline", "operational-evidence", "excluded-operational", 0, "hold", "Keep source management outside public concept schemes; publish only governed provenance derived from it."),
    "era_fields_v1": ("era-data-schema;aom-core-bindings", "era-data;era-aom", "schema-with-semantic-bindings", "inventory-only-legacy-schema", 0, "1-data-model-and-core", "Retain as migration history; do not create one SKOS concept per field."),
    "era_fields_v2": ("era-data-schema;aom-core-bindings", "era-data;era-aom", "schema-with-semantic-bindings", "inventory-only-current-schema", 0, "1-data-model-and-core", "Formalize fields, datatypes, cardinalities, lookups, and semantic bindings before additional domain migration."),
    "prac": ("aom-crop", "era-aom", "concept-scheme", "pilot-normalized", 196, "2-crop-observation-foundation", "Review pilot identities, hierarchy, definitions, and mappings before release promotion."),
    "prod": ("aom-crop;mappings", "era-aom", "mixed-concept-source", "inventory-only", 0, "3-crop-products-and-components", "Decompose biological source, harvested product, component, management flags, and external mappings before normalization."),
    "lookup_levels": ("era-data-code-lists;aom-core-bindings", "era-data;era-aom", "mixed-code-list-source", "inventory-only", 0, "1-data-model-and-core", "Route values by field; do not publish one undifferentiated ontology hierarchy."),
    "prod_comp": ("aom-crop", "era-aom", "concept-scheme", "inventory-only", 0, "3-crop-products-and-components", "Normalize components with reviewed identity links to products and biological sources."),
    "out": ("aom-crop", "era-aom", "concept-scheme", "pilot-normalized", 116, "2-crop-observation-foundation", "Review pilot outcome hierarchy and bind outcome variables and quantities before promotion."),
    "out_econ": ("aom-crop", "era-aom", "concept-scheme", "inventory-only", 0, "2-crop-observation-foundation", "Integrate economic outcomes with the reviewed outcome scheme rather than publish a disconnected tree."),
    "fert": ("aom-crop;mappings", "era-aom", "mixed-concept-source", "inventory-only", 0, "4-crop-inputs-and-chemicals", "Separate fertilizer material identity, nutrient composition, application role, compound formulation, and ChEBI mapping."),
    "chem": ("aom-crop;mappings", "era-aom", "mixed-concept-source", "inventory-only", 0, "4-crop-inputs-and-chemicals", "Separate commercial product, active ingredient, chemical identity, use context, and ChEBI mapping."),
    "countries": ("era-data-code-lists;mappings", "era-data", "reference-code-list", "inventory-only", 0, "7-reference-context-and-crosswalks", "Publish governed ISO mappings and spatial metadata outside domain concept hierarchies."),
    "trees": ("aom-crop;mappings", "era-aom", "mixed-concept-source", "inventory-only", 0, "5-biological-identity-and-traits", "Separate taxon identity, variety or subspecies, functional traits, management flags, and WFO or GBIF mappings."),
    "journals": ("era-data-provenance", "era-data", "reference-code-list", "inventory-only", 0, "7-reference-context-and-crosswalks", "Treat as source-name normalization, not agricultural ontology concepts."),
    "site_list": ("era-data-location-registry", "era-data", "restricted-review-code-list", "publication-review-required", 0, "7-reference-context-and-crosswalks", "Complete sensitivity review before any publication; never move coordinates into AOM concepts."),
    "residues": ("aom-crop;mappings", "era-aom", "crosswalk", "inventory-only", 0, "3-crop-products-and-components", "Preserve original-to-harmonized mappings and resolve identities with crop product and by-product review."),
    "vars": ("aom-crop;mappings", "era-aom", "mixed-concept-source", "inventory-only", 0, "5-biological-identity-and-traits", "Decompose crop taxon, cultivar or accession, maturity, traits, and practice context before normalization."),
    "vars_animals": ("aom-livestock;mappings", "era-aom", "mixed-concept-source", "reconciled-not-normalized", 0, "6-livestock-non-feed-completion", "Complete animal identity, breed or variety, trait, and practice review; current feed work does not close this sheet."),
    "var_traits": ("mappings", "era-aom", "crosswalk", "inventory-only", 0, "5-biological-identity-and-traits", "Preserve trait normalization as reviewed mappings; do not mint identities from lexical matches alone."),
    "AOM READ.ME": ("maintained-documentation", "era-aom", "documentation-evidence", "excluded-documentation", 0, "0-boundary-governance", "Migrate useful lineage and method notes into maintained documentation, then retain workbook sheet only as provenance."),
    "AOM": ("aom-livestock", "era-aom", "concept-scheme", "release-normalized-partially-reviewed", 2503, "6-livestock-non-feed-completion", "Retain public lineage and complete domain-balanced review beyond feed before formal publication."),
    "ani_diet": ("aom-livestock;mappings", "era-aom", "operational-crosswalk-evidence", "reconciled-not-normalized", 0, "6-livestock-non-feed-completion", "Treat as assignment and decomposition evidence, not an independent public concept scheme."),
    "ani_process": ("aom-livestock;mappings", "era-aom", "operational-crosswalk-evidence", "reconciled-not-normalized", 0, "6-livestock-non-feed-completion", "Treat corrections and process decompositions as governed mappings and evidence."),
    "ssa_feedsdb": ("excluded-restricted", "none", "closed-evidence", "excluded-confirmed", 0, "hold", "Never publish source values; retain only rights-safe reviewed assertions with provenance."),
    "AOM_diets": ("aom-livestock;mappings", "era-aom", "working-subset-crosswalk", "reconciled-not-normalized", 0, "6-livestock-non-feed-completion", "Treat as working subset and crosswalk into AOM identities, not a sibling public scheme."),
    "unit_harmonization": ("era-data-code-lists;mappings;aom-core-bindings", "era-data;era-aom", "crosswalk", "inventory-only", 0, "1-data-model-and-core", "Preserve raw-to-canonical unit mappings and link canonical units to reviewed external unit identifiers."),
    "dois": ("operational-source-management", "era-data-pipeline", "operational-evidence", "excluded-operational", 0, "hold", "Keep source management private; publish governed citation and provenance records only."),
    "aez": ("era-data-code-lists;aom-core-bindings", "era-data;era-aom", "reference-code-list", "inventory-only", 0, "7-reference-context-and-crosswalks", "Publish versioned agroecological-zone code lists and bind observations without treating zones as crop concepts."),
    "dups": ("excluded-scratch", "none", "scratch-evidence", "excluded-scratch", 0, "hold", "Retain only as migration evidence until duplicate dispositions are recorded in governed ledgers."),
    "OLD_diet_process": ("excluded-legacy", "none", "legacy-evidence", "excluded-legacy", 0, "hold", "Retain immutable migration provenance; do not publish as active concepts."),
    "OLD_diet_item": ("excluded-legacy", "none", "legacy-evidence", "excluded-legacy", 0, "hold", "Retain immutable migration provenance; do not publish as active concepts."),
    "OLD_era_fields_v1": ("excluded-legacy", "none", "legacy-evidence", "excluded-legacy", 0, "hold", "Retain immutable migration provenance; do not publish as current schema."),
    "scio - Custom Terms": ("mappings-review", "era-aom", "scratch-mapping-evidence", "excluded-pending-provenance-review", 0, "hold", "Review provenance and identity before moving any term or mapping into governed sources."),
}


WAVES = [
    ("0-boundary-governance", 0, "Classify every workbook resource and approve module boundaries", "Whole-resource coverage matrix; ADR 0051; no semantic implementation", "era-program #17; ADR 0007; ADR 0008"),
    ("1-data-model-and-core", 1, "Formalize tabular schema, controlled-value bindings, units, and shared observation semantics", "Machine-readable field schema; versioned code-list contracts; reviewed AOM bindings", "era-program #27; era_fields_v2; lookup_levels; unit_harmonization"),
    ("2-crop-observation-foundation", 2, "Promote reviewed crop practice and outcome foundations", "Governed prac, out, and out_econ schemes with stable IDs and mappings", "Wave 1 contracts; pilot collision and source review"),
    ("3-crop-products-and-components", 3, "Model crop products, components, and residue mappings", "Reviewed prod, prod_comp, and residues contracts", "Waves 1-2; biological-source and product-role predicates"),
    ("4-crop-inputs-and-chemicals", 4, "Separate material, formulation, chemical identity, composition, and use", "Reviewed fert and chem contracts with external mapping evidence", "Waves 1-3; chemical identity governance"),
    ("5-biological-identity-and-traits", 5, "Normalize crop and animal biological identity, varieties, accessions, and traits", "Reviewed trees, vars, vars_animals, and var_traits contracts", "Identifier reuse audit; WFO, NCBI, GBIF, and trait mapping review"),
    ("6-livestock-non-feed-completion", 6, "Close livestock coverage outside the recent feed-heavy review", "Domain-balanced AOM audit plus governed supporting crosswalks", "ADR 0049 visual acceptance; public lineage preservation"),
    ("7-reference-context-and-crosswalks", 7, "Publish reference code lists, context registries, and remaining mappings", "Versioned countries, journals, AEZ, site, unit, and mapping distributions", "Privacy review; Waves 1-6 identifiers"),
]


AUTHORITY_ROWS = [
    ("canonical-workbook", "ERA ADR 0007 and structural workbook inventory", "Current source records, identifiers, labels, fields, controlled values, and migration evidence until approved cutover", "Workbook sheet layout does not decide target module or imply every row is an ontology concept", "https://github.com/ERAgriculture/era-program/blob/main/project-management/decisions/ADR-0007-canonical-vocab-source.md;inventory/workbook_sheets.csv;inventory/workbook_columns.csv"),
    ("module-architecture", "ERA ADR 0008 and AOM MODULES", "AOM umbrella boundary and sibling aom-core, aom-crop, aom-livestock, and mappings products", "Architecture does not approve row-level identity or hierarchy", "https://github.com/ERAgriculture/era-program/blob/main/project-management/decisions/ADR-0008-normalized-vocabulary-architecture.md;MODULES.md"),
    ("livestock-lineage", "AOM Livestock v2 public release and reconciliation", "Published livestock identifiers, hierarchy lineage, authorship, DOI, and public provenance", "Does not cover crop vocabulary and does not make working diet sheets independent schemes", "https://doi.org/10.7910/DVN/75E7HV;inventory/AOM_LIVESTOCK_RECONCILIATION.md"),
    ("skos", "W3C SKOS Recommendation", "Concept schemes, concept labels, notations, semantic relations, collections, and mappings", "Not a tabular field schema, dataset catalog, or validation language", "https://www.w3.org/TR/skos-reference/"),
    ("csvw", "W3C Model for Tabular Data and Metadata on the Web", "Tables, columns, rows, cells, datatypes, and tabular metadata", "Does not supply agricultural concept identity or hierarchy", "https://www.w3.org/TR/tabular-data-model/"),
    ("shacl", "W3C SHACL Recommendation", "Constraints and validation reports for RDF data graphs", "Validation shapes do not establish vocabulary authority or concept identity", "https://www.w3.org/TR/shacl/"),
    ("dcat", "W3C DCAT 3 Recommendation", "Catalog, dataset, distribution, checksum, and version metadata", "Catalog metadata does not replace source schemas or controlled vocabularies", "https://www.w3.org/TR/vocab-dcat-3/"),
]


EVIDENCE_ROWS = [
    ("COV-001", "AOM is an umbrella product, not livestock shorthand", "supported", "https://github.com/ERAgriculture/era-program/blob/main/project-management/decisions/ADR-0008-normalized-vocabulary-architecture.md;MODULES.md", "Architecture claim only; shared concepts still require review."),
    ("COV-002", "Canonical workbook contains 33 sheets with distinct resource roles", "supported", "inventory/workbook_sheets.csv; inventory/sheet_disposition.csv", "Inventory records structure, not approval of every proposed disposition."),
    ("COV-003", "Only prac, out, and AOM currently have normalized source-row coverage", "supported", "data/pilot/source_records.csv; data/livestock-staging/legacy_records.csv", "Generated concepts and overlays can make output counts differ from source-row counts."),
    ("COV-004", "Recent semantic review is substantially deeper for livestock feed than for crop or shared core", "supported", "review/livestock-v2 through review/livestock-v40; data/pilot", "Livestock staging also contains non-feed concepts; feed review must not be described as complete livestock review."),
    ("COV-005", "Field registries, code lists, crosswalks, and operational tables must not be flattened into one SKOS hierarchy", "supported", "W3C SKOS; W3C CSVW; W3C SHACL; W3C DCAT 3", "Exact serialization and ownership still require implementation decisions."),
    ("COV-006", "AOM_diets, ani_diet, and ani_process are supporting subsets or crosswalk evidence rather than independent public concept schemes", "supported", "inventory/AOM_LIVESTOCK_RECONCILIATION.md; workbook column inventory", "Individual values may still justify governed concepts or mappings after review."),
    ("COV-007", "vars_animals remains outside normalized source tables", "supported", "inventory/AOM_LIVESTOCK_RECONCILIATION.md; data/livestock-staging", "Reconciliation does not equal semantic normalization."),
    ("COV-008", "ssa_feedsdb must remain excluded from public distributions", "supported", "inventory/sheet_disposition.csv; tests/validate_livestock_inventory.py", "Rights-safe derived assertions still require source and rights review."),
    ("COV-009", "Whole-vocabulary migration should begin with data-model and module boundaries before mass concept normalization", "recommended", "https://github.com/ERAgriculture/era-program/blob/main/project-management/decisions/ADR-0007-canonical-vocab-source.md;https://github.com/ERAgriculture/era-program/blob/main/project-management/decisions/ADR-0008-normalized-vocabulary-architecture.md;W3C standards boundary", "Human approval required through ADR 0051."),
]


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    inventory_rows = read_csv(INVENTORY)
    disposition_rows = {row["sheet"]: row for row in read_csv(DISPOSITIONS)}
    inventory_sheets = {row["sheet"] for row in inventory_rows}
    decision_sheets = set(RESOURCE_DECISIONS)
    if inventory_sheets != decision_sheets:
        missing = sorted(inventory_sheets - decision_sheets)
        unexpected = sorted(decision_sheets - inventory_sheets)
        raise ValueError(f"Coverage decisions mismatch: missing={missing}, unexpected={unexpected}")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    coverage_rows = []
    for inventory_row in inventory_rows:
        sheet = inventory_row["sheet"]
        disposition = disposition_rows[sheet]
        target_product, owner_repository, treatment, state, normalized_rows, wave, next_action = RESOURCE_DECISIONS[sheet]
        coverage_rows.append({
            "sheet_order": inventory_row["sheet_order"],
            "sheet": sheet,
            "inventory_resource_type": inventory_row["resource_type"],
            "publication_disposition": inventory_row["publication"],
            "disposition_status": disposition["decision_status"],
            "nonblank_rows": inventory_row["nonblank_rows"],
            "columns": inventory_row["columns"],
            "target_product": target_product,
            "owner_repository": owner_repository,
            "recommended_treatment": treatment,
            "current_coverage_state": state,
            "normalized_source_rows": normalized_rows,
            "migration_wave": wave,
            "next_action": next_action,
        })

    coverage_path = OUTPUT / "resource_coverage.csv"
    write_csv(coverage_path, list(coverage_rows[0]), coverage_rows)

    wave_rows = [
        {
            "wave": wave,
            "order": order,
            "objective": objective,
            "exit_artifact": exit_artifact,
            "dependencies": dependencies,
        }
        for wave, order, objective, exit_artifact, dependencies in WAVES
    ]
    waves_path = OUTPUT / "migration_waves.csv"
    write_csv(waves_path, list(wave_rows[0]), wave_rows)

    authority_rows = [
        {
            "authority_id": authority_id,
            "authority": authority,
            "supports": supports,
            "does_not_support": does_not_support,
            "evidence": evidence,
        }
        for authority_id, authority, supports, does_not_support, evidence in AUTHORITY_ROWS
    ]
    authority_path = OUTPUT / "authority_comparison.csv"
    write_csv(authority_path, list(authority_rows[0]), authority_rows)

    evidence_rows = [
        {
            "claim_id": claim_id,
            "claim": claim,
            "disposition": disposition,
            "evidence": evidence,
            "limitation": limitation,
        }
        for claim_id, claim, disposition, evidence, limitation in EVIDENCE_ROWS
    ]
    evidence_path = OUTPUT / "evidence_register.csv"
    write_csv(evidence_path, list(evidence_rows[0]), evidence_rows)

    publication_counts = Counter(row["publication_disposition"] for row in coverage_rows)
    resource_type_counts = Counter(row["inventory_resource_type"] for row in coverage_rows)
    state_counts = Counter(row["current_coverage_state"] for row in coverage_rows)
    concept_scheme_rows = [row for row in coverage_rows if row["inventory_resource_type"] == "concept_scheme"]
    normalized_sheets = [row["sheet"] for row in coverage_rows if int(row["normalized_source_rows"]) > 0]
    module_coverage = {}
    for module in ("aom-core", "aom-crop", "aom-livestock", "mappings"):
        targeted = [row for row in coverage_rows if module in row["target_product"]]
        normalized = [row["sheet"] for row in targeted if int(row["normalized_source_rows"]) > 0]
        module_coverage[module] = {
            "targeted_sheets": [row["sheet"] for row in targeted],
            "targeted_sheet_count": len(targeted),
            "normalized_source_sheets": normalized,
            "normalized_source_sheet_count": len(normalized),
        }
    summary = {
        "review": "whole-vocabulary-v1",
        "review_date": "2026-08-24",
        "status": "recommendation-only",
        "source_inventory": "inventory/workbook_sheets.csv",
        "workbook_sheets": len(coverage_rows),
        "workbook_nonblank_rows": sum(int(row["nonblank_rows"]) for row in coverage_rows),
        "publication_counts": dict(sorted(publication_counts.items())),
        "resource_type_counts": dict(sorted(resource_type_counts.items())),
        "current_coverage_state_counts": dict(sorted(state_counts.items())),
        "public_or_review_sheets": sum(row["publication_disposition"] in {"public", "review"} for row in coverage_rows),
        "public_or_review_rows": sum(int(row["nonblank_rows"]) for row in coverage_rows if row["publication_disposition"] in {"public", "review"}),
        "concept_scheme_sheets": len(concept_scheme_rows),
        "concept_scheme_rows": sum(int(row["nonblank_rows"]) for row in concept_scheme_rows),
        "normalized_source_sheets": normalized_sheets,
        "normalized_source_sheet_count": len(normalized_sheets),
        "normalized_source_rows": sum(int(row["normalized_source_rows"]) for row in coverage_rows),
        "module_coverage": module_coverage,
        "migration_wave_count": len(WAVES),
        "semantic_changes": 0,
        "allocated_identifiers": 0,
        "outputs": {
            "resource_coverage_sha256": file_sha256(coverage_path),
            "migration_waves_sha256": file_sha256(waves_path),
            "authority_comparison_sha256": file_sha256(authority_path),
            "evidence_register_sha256": file_sha256(evidence_path),
        },
    }
    (OUTPUT / "coverage_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"Reviewed {summary['workbook_sheets']} workbook sheets; "
        f"normalized source coverage exists for {summary['normalized_source_sheet_count']} sheets."
    )


if __name__ == "__main__":
    main()
