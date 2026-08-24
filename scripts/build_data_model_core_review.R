#!/usr/bin/env Rscript

suppressMessages({
  library(data.table)
  library(digest)
  library(jsonlite)
  library(readxl)
})

`%||%` <- function(value, fallback) {
  if (is.null(value) || length(value) == 0L || (length(value) == 1L && is.na(value))) fallback else value
}

args <- commandArgs(trailingOnly = TRUE)
getarg <- function(key, default) {
  matches <- grep(paste0("^--", key, "="), args, value = TRUE)
  if (length(matches)) sub(paste0("^--", key, "="), "", matches[[1]]) else default
}

script_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
script_path <- normalizePath(sub("^--file=", "", script_arg[[1]]), mustWork = TRUE)
root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)

master <- path.expand(getarg(
  "master",
  "~/Library/CloudStorage/OneDrive-CGIAR/ClimateActionNetZero/1_Projects/ERA/ERA/Concept Scheme/era_codes/era_master_sheet.xlsx"
))
era_data <- normalizePath(getarg("era-data", "../era-data-wave1-audit"), mustWork = TRUE)
eragri <- normalizePath(getarg("eragri", "../eragri-wave1-audit"), mustWork = TRUE)
pipeline <- normalizePath(getarg("pipeline", "../era-data-pipeline-wave1-audit"), mustWork = TRUE)
era_docs <- normalizePath(getarg("era-docs", "../era-docs-wave1-audit"), mustWork = TRUE)
output <- normalizePath(
  getarg("out", file.path(root, "review", "data-model-v1")),
  mustWork = FALSE
)
dir.create(output, recursive = TRUE, showWarnings = FALSE)

if (!file.exists(master)) stop("Canonical workbook not found: ", master)

read_sheet <- function(sheet) {
  value <- as.data.table(read_excel(master, sheet = sheet, guess_max = 100000L))
  value[, source_row := .I + 1L]
  value
}

file_sha256 <- function(path) digest(file = path, algo = "sha256")

git_commit <- function(path) {
  output <- system2("git", c("-C", shQuote(path), "rev-parse", "HEAD"), stdout = TRUE)
  trimws(output[[1]])
}

write_table <- function(name, value) {
  path <- file.path(output, name)
  fwrite(value, path, na = "")
  path
}

nonblank <- function(value) !is.na(value) & trimws(as.character(value)) != ""

rounds <- c(
  "majestic_hippo_2020",
  "skinny_cow_2022",
  "industrious_elephant_2023",
  "courageous_camel_2024"
)

active_rounds <- function(row) {
  rounds[vapply(rounds, function(round_name) {
    value <- row[[round_name]]
    length(value) && !is.na(value) && toupper(trimws(as.character(value))) %in% c("TRUE", "Y", "YES", "1")
  }, logical(1))]
}

fields_all <- read_sheet("era_fields_v2")
lookups <- read_sheet("lookup_levels")
units <- read_sheet("unit_harmonization")
field_rows <- fields_all[nonblank(Field)]
valid_fields <- field_rows[nonblank(Table)]
valid_field_keys <- unique(valid_fields[, .(Table, Field)])

model_path <- file.path(era_data, "vocab", "version=2026.1", "era_data_model.schema.json")
agronomy_schema_path <- file.path(era_data, "schemas", "era_compiled.schema.json")
livestock_schema_path <- file.path(era_data, "schemas", "era_compiled_ls.schema.json")
vocab_manifest_path <- file.path(era_data, "vocab", "version=2026.1", "vocab_manifest.json")
model <- fromJSON(model_path, simplifyVector = FALSE)
agronomy_schema <- fromJSON(agronomy_schema_path, simplifyVector = FALSE)
livestock_schema <- fromJSON(livestock_schema_path, simplifyVector = FALSE)
vocab_manifest <- fromJSON(vocab_manifest_path, simplifyVector = FALSE)

model_fields <- rbindlist(lapply(model$tables, function(table) {
  rbindlist(lapply(table$fields, function(field) {
    data.table(
      Table = as.character(table$table),
      Field = as.character(field$field),
      description = as.character(field$description %||% NA_character_),
      type = as.character(field$type %||% NA_character_),
      allowed_value_count = length(field$allowed_values %||% list())
    )
  }), fill = TRUE)
}), fill = TRUE)

load_object <- function(path, object_name) {
  environment <- new.env(parent = emptyenv())
  load(path, envir = environment)
  environment[[object_name]]
}

package_data <- as.data.table(load_object(file.path(eragri, "data", "ERA.Compiled.rda"), "ERA.Compiled"))
package_dictionary <- as.data.table(load_object(file.path(eragri, "data", "ERACompiledFields.rda"), "ERACompiledFields"))

structural_binding_path <- file.path(root, "data", "livestock-staging", "approved_semantic_bindings.csv")
value_binding_path <- file.path(root, "data", "livestock-staging", "approved_semantic_value_bindings.csv")
structural_bindings <- fread(structural_binding_path)
value_bindings <- fread(value_binding_path)

source_contracts <- data.table(
  source_id = c(
    "canonical-field-registry",
    "canonical-lookup-registry",
    "canonical-unit-crosswalk",
    "published-extraction-model",
    "published-agronomy-product-schema",
    "published-livestock-product-schema",
    "package-agronomy-data",
    "package-agronomy-dictionary",
    "aom-structural-bindings",
    "aom-value-bindings",
    "pipeline-model-builder",
    "public-data-model-guide"
  ),
  owner_repository = c(
    rep("canonical-workbook", 3),
    rep("ERAgriculture/era-data", 3),
    rep("ERAgriculture/eragri", 2),
    rep("ERAgriculture/era-aom", 2),
    "ERAgriculture/era-data-pipeline",
    "ERAgriculture/era-docs"
  ),
  artifact = c(
    "era_master_sheet.xlsx::era_fields_v2",
    "era_master_sheet.xlsx::lookup_levels",
    "era_master_sheet.xlsx::unit_harmonization",
    "vocab/version=2026.1/era_data_model.schema.json",
    "schemas/era_compiled.schema.json",
    "schemas/era_compiled_ls.schema.json",
    "data/ERA.Compiled.rda",
    "data/ERACompiledFields.rda",
    "data/livestock-staging/approved_semantic_bindings.csv",
    "data/livestock-staging/approved_semantic_value_bindings.csv",
    "R/vocab/build_model_schema.R",
    "chapters/06-data-model-vocab.qmd"
  ),
  source_version = c(
    file_sha256(master),
    file_sha256(master),
    file_sha256(master),
    git_commit(era_data),
    git_commit(era_data),
    git_commit(era_data),
    git_commit(eragri),
    git_commit(eragri),
    file_sha256(structural_binding_path),
    file_sha256(value_binding_path),
    git_commit(pipeline),
    git_commit(era_docs)
  ),
  role = c(
    "extraction-model-authoring-source",
    "field-scoped-enumeration-source",
    "raw-to-canonical-unit-label-crosswalk",
    "published-derived-extraction-model",
    "published-agronomy-product-schema",
    "published-livestock-product-schema",
    "package-consumer-data-snapshot",
    "package-consumer-data-dictionary",
    "reviewed-livestock-semantic-structure",
    "reviewed-livestock-semantic-values",
    "schema-generation-code",
    "human-facing-data-model-documentation"
  ),
  record_count = c(
    nrow(fields_all),
    nrow(lookups),
    nrow(units),
    nrow(model_fields),
    length(agronomy_schema$columns),
    length(livestock_schema$columns),
    ncol(package_data),
    nrow(package_dictionary),
    nrow(structural_bindings),
    nrow(value_bindings),
    NA_integer_,
    NA_integer_
  ),
  key_count = c(
    nrow(valid_field_keys),
    uniqueN(lookups[nonblank(Table) & nonblank(Field)], by = c("Table", "Field")),
    uniqueN(units[nonblank(Out.Unit)]$Out.Unit),
    uniqueN(model_fields, by = c("Table", "Field")),
    uniqueN(vapply(agronomy_schema$columns, `[[`, "", "name")),
    uniqueN(vapply(livestock_schema$columns, `[[`, "", "name")),
    ncol(package_data),
    uniqueN(package_dictionary$Field.Name),
    uniqueN(structural_bindings$legacy_concept_id),
    uniqueN(paste(value_bindings$target_property, value_bindings$source_value, sep = "::")),
    NA_integer_,
    NA_integer_
  ),
  observed_gap = c(
    "Field rows are not uniquely keyed and one populated field lacks a table.",
    "Forty-one table-field pairs do not exactly match current field-registry keys.",
    "Raw labels lack external identifiers; unresolved and conflicting rows remain.",
    "Fourth extraction round is omitted; duplicate logical keys remain duplicated; units are absent.",
    "All 138 column descriptions are blank.",
    "All 138 column descriptions are blank; schema is identical to agronomy despite distinct product.",
    "Unversioned package snapshot has 137 columns and differs from current public schema.",
    "Dictionary documents 106 names and does not exactly match package or public release columns.",
    "All approved structural bindings are livestock/feed scoped.",
    "All approved value bindings are livestock/feed scoped.",
    "Generator lacks uniqueness, complete-round, relationship, unit, and source-drift gates.",
    "Guide overstates unit coverage and does not disclose current contract drift."
  )
)
source_contracts_path <- write_table("source_contracts.csv", source_contracts)

duplicate_keys <- valid_fields[, .N, by = .(Table, Field)][N > 1L]
field_key_issues <- rbindlist(list(
  fields_all[!nonblank(Field), .(
    issue_id = sprintf("FIELD-BLANK-%03d", source_row),
    issue_type = "blank-field-row",
    Table = fifelse(is.na(Table), "", Table),
    Field = "",
    source_rows = as.character(source_row),
    active_rounds = "",
    evidence = "Workbook row has no Field value.",
    recommended_disposition = "Classify row as table metadata or remove it from field registry after source review."
  )],
  field_rows[!nonblank(Table), .(
    issue_id = sprintf("FIELD-TABLE-%03d", source_row),
    issue_type = "missing-table-key",
    Table = "",
    Field = as.character(Field),
    source_rows = as.character(source_row),
    active_rounds = paste(active_rounds(.SD), collapse = ";"),
    evidence = "Populated Field has no Table value and is dropped by current schema generator.",
    recommended_disposition = "Assign reviewed table identity or explicitly retire row; never infer table from label alone."
  ), by = source_row],
  rbindlist(lapply(seq_len(nrow(duplicate_keys)), function(index) {
    key <- duplicate_keys[index]
    rows <- valid_fields[Table == key$Table & Field == key$Field]
    round_profiles <- vapply(seq_len(nrow(rows)), function(row_index) {
      paste0(rows$source_row[[row_index]], ":", paste(active_rounds(rows[row_index]), collapse = "+"))
    }, character(1))
    irrigation_collision <- key$Table == "Irrig.Out" && key$Field == "I.Date.Start" &&
      uniqueN(rows$Display_Name[nonblank(rows$Display_Name)]) > 1L
    data.table(
      issue_id = sprintf("FIELD-DUP-%03d", index),
      issue_type = if (irrigation_collision) "duplicate-key-label-conflict" else "duplicate-logical-field-key",
      Table = key$Table,
      Field = key$Field,
      source_rows = paste(rows$source_row, collapse = ";"),
      active_rounds = paste(round_profiles, collapse = " | "),
      evidence = if (irrigation_collision) {
        paste0("Same key carries display names: ", paste(unique(rows$Display_Name), collapse = " | "), ".")
      } else {
        "Same table-field key appears more than once, commonly as round-specific variants."
      },
      recommended_disposition = if (irrigation_collision) {
        "Review probable source-key error; do not auto-rename from display label."
      } else {
        "Create one stable logical field identity plus separate round-specific field profiles."
      }
    )
  }))
), fill = TRUE)
setorder(field_key_issues, issue_id)
if ("source_row" %in% names(field_key_issues)) field_key_issues[, source_row := NULL]
field_key_issues_path <- write_table("field_key_issues.csv", field_key_issues)

field_quality_metrics <- data.table(
  metric = c(
    "workbook_rows",
    "populated_field_rows",
    "valid_table_field_rows",
    "unique_table_field_keys",
    "duplicate_table_field_keys",
    "missing_table_rows",
    "missing_description_rows",
    "missing_datatype_rows",
    "missing_requiredness_rows",
    "declared_extraction_rounds",
    "fields_used_in_courageous_camel_2024",
    "published_model_tables",
    "published_model_field_entries",
    "published_model_unique_field_keys",
    "published_model_allowed_value_fields",
    "published_model_allowed_values",
    "published_model_extraction_rounds"
  ),
  value = c(
    nrow(fields_all),
    nrow(field_rows),
    nrow(valid_fields),
    nrow(valid_field_keys),
    nrow(duplicate_keys),
    nrow(field_rows[!nonblank(Table)]),
    nrow(field_rows[!nonblank(Field_Description)]),
    nrow(field_rows[!nonblank(Data_Type)]),
    nrow(field_rows[!nonblank(Required)]),
    length(rounds),
    nrow(field_rows[vapply(courageous_camel_2024, function(value) {
      !is.na(value) && toupper(trimws(as.character(value))) %in% c("TRUE", "Y", "YES", "1")
    }, logical(1))]),
    length(model$tables),
    nrow(model_fields),
    uniqueN(model_fields, by = c("Table", "Field")),
    nrow(model_fields[allowed_value_count > 0L]),
    sum(model_fields$allowed_value_count),
    length(model$extraction_rounds)
  ),
  interpretation = c(
    "Issue #27 source-row count.",
    "Rows representing fields after blank-field exclusion.",
    "Populated field rows with both table and field identity.",
    "Logical identities available under current composite key.",
    "Keys requiring normalization or source correction.",
    "Populated fields silently omitted by current generator.",
    "Field definitions incomplete.",
    "Datatype defaults currently hide missing governance.",
    "Requiredness metadata incomplete.",
    "Current canonical workbook round columns.",
    "Current generator does not publish this round.",
    "Published v2026.1 extraction-model table count.",
    "Published v2026.1 field entries retain duplicates.",
    "Published v2026.1 logical field-key count.",
    "Exact table-field matching exposes only part of lookup registry.",
    "Allowed values emitted after exact-key matching and 200-value cap.",
    "Published v2026.1 omits courageous_camel_2024."
  )
)
field_quality_metrics_path <- write_table("field_quality_metrics.csv", field_quality_metrics)

lookup_pairs <- lookups[nonblank(Table) & nonblank(Field), .(
  source_rows = paste(source_row, collapse = ";"),
  value_rows = .N,
  distinct_current_values = uniqueN(Values_New[nonblank(Values_New)]),
  described_values = sum(nonblank(Description)),
  old_values = sum(nonblank(Values_Old))
), by = .(Table, Field)]
lookup_field_candidates <- valid_field_keys[, .(
  candidate_registry_keys = paste(sort(paste(Table, Field, sep = ".")), collapse = ";")
), by = Field]
lookup_binding_audit <- merge(lookup_pairs, valid_field_keys[, .(Table, Field, exact_match = "yes")], by = c("Table", "Field"), all.x = TRUE)
lookup_binding_audit <- merge(lookup_binding_audit, lookup_field_candidates, by = "Field", all.x = TRUE)
lookup_binding_audit[is.na(exact_match), exact_match := "no"]
lookup_binding_audit[is.na(candidate_registry_keys), candidate_registry_keys := ""]
lookup_binding_audit[, generator_disposition := fifelse(
  exact_match == "yes",
  "eligible-for-inline-allowed-values",
  "omitted-by-exact-key-join"
)]
lookup_binding_audit[, recommended_disposition := fifelse(
  exact_match == "yes",
  "Mint stable value-set identity and bind field by key; keep values in separate governed table.",
  "Review stale table-field key against candidate registry keys; do not fuzzy-join automatically."
)]
setcolorder(lookup_binding_audit, c(
  "Table", "Field", "source_rows", "value_rows", "distinct_current_values",
  "described_values", "old_values", "exact_match", "candidate_registry_keys",
  "generator_disposition", "recommended_disposition"
))
setorder(lookup_binding_audit, Table, Field)
lookup_binding_audit_path <- write_table("lookup_binding_audit.csv", lookup_binding_audit)

unit_profiles <- units[nonblank(Out.Unit), .(
  raw_occurrences = .N,
  distinct_nonblank_corrections = uniqueN(Out.Unit.Correct[nonblank(Out.Unit.Correct)])
), by = Out.Unit]
unit_mapping_audit <- merge(units, unit_profiles, by = "Out.Unit", all.x = TRUE, sort = FALSE)
unit_mapping_audit[, mapping_status := fcase(
  !nonblank(Out.Unit.Correct), "unresolved",
  distinct_nonblank_corrections > 1L, "conflicting-canonical-label",
  trimws(as.character(Out.Unit)) == trimws(as.character(Out.Unit.Correct)), "identity-label",
  default = "normalized-label"
)]
unit_mapping_audit[, `:=`(
  canonical_unit_uri = "",
  external_mapping_status = "not-reviewed",
  recommended_disposition = fcase(
    mapping_status == "unresolved", "Preserve raw label and hold canonical mapping until unit meaning is reviewed.",
    mapping_status == "conflicting-canonical-label", "Resolve contextual or temporal distinction; never choose one correction silently.",
    mapping_status == "identity-label", "Retain label mapping and review canonical identifier plus quantity kind.",
    default = "Validate normalization or conversion semantics and review canonical identifier plus quantity kind."
  )
)]
setnames(unit_mapping_audit, c("Out.Unit", "Out.Unit.Correct"), c("raw_unit", "canonical_label"))
normalize_audit_text <- function(value) gsub("[\r\n]+", "\\\\n", as.character(value))
unit_mapping_audit[, raw_unit := normalize_audit_text(raw_unit)]
unit_mapping_audit[, canonical_label := normalize_audit_text(canonical_label)]
setcolorder(unit_mapping_audit, c(
  "source_row", "raw_unit", "canonical_label", "raw_occurrences",
  "distinct_nonblank_corrections", "mapping_status", "canonical_unit_uri",
  "external_mapping_status", "recommended_disposition"
))
setorder(unit_mapping_audit, source_row)
unit_mapping_audit_path <- write_table("unit_mapping_audit.csv", unit_mapping_audit)

schema_columns <- function(schema) vapply(schema$columns, `[[`, "", "name")
schema_descriptions <- function(schema) vapply(schema$columns, function(column) as.character(column$description %||% ""), "")
agronomy_columns <- schema_columns(agronomy_schema)
livestock_columns <- schema_columns(livestock_schema)

consumer_contract_comparison <- data.table(
  contract = c(
    "canonical-era-fields-v2",
    "published-era-data-model-2026.1",
    "published-era-compiled-schema-2026.1",
    "published-era-compiled-ls-schema-2026.1",
    "eragri-era-compiled-snapshot",
    "eragri-era-compiled-dictionary"
  ),
  role = c(
    "extraction-model-source",
    "derived-extraction-model",
    "agronomy-product-schema",
    "livestock-product-schema",
    "package-data-snapshot",
    "package-data-dictionary"
  ),
  object_count = c(uniqueN(valid_fields$Table), length(model$tables), 1L, 1L, 1L, 1L),
  field_entries = c(nrow(valid_fields), nrow(model_fields), length(agronomy_columns), length(livestock_columns), ncol(package_data), nrow(package_dictionary)),
  unique_field_keys = c(nrow(valid_field_keys), uniqueN(model_fields, by = c("Table", "Field")), uniqueN(agronomy_columns), uniqueN(livestock_columns), ncol(package_data), uniqueN(package_dictionary$Field.Name)),
  populated_descriptions = c(
    sum(nonblank(valid_fields$Field_Description)),
    sum(nonblank(model_fields$description)),
    sum(nonblank(schema_descriptions(agronomy_schema))),
    sum(nonblank(schema_descriptions(livestock_schema))),
    NA_integer_,
    sum(nonblank(package_dictionary$Description))
  ),
  declared_rounds = c(length(rounds), length(model$extraction_rounds), NA_integer_, NA_integer_, NA_integer_, NA_integer_),
  observed_boundary = c(
    "Authoring registry for extraction tables, not compiled-product dictionary.",
    "Derived registry omits one round and retains duplicate field entries.",
    "Current public product contract has 138 columns with no descriptions.",
    "Current public livestock contract has same names and types as agronomy with no descriptions.",
    "Package snapshot has 137 columns and no embedded release provenance.",
    "Package dictionary documents 106 names and includes aliases/pattern fields not present literally."
  ),
  required_action = c(
    "Normalize logical fields, round profiles, relationships, lifecycle, and units.",
    "Regenerate from normalized source and fail on omitted rounds or duplicate keys.",
    "Create complete versioned product-field dictionary and link controlled values.",
    "Create livestock product profile and document genuine shared versus product-specific fields.",
    "Pin package data to release and publish compatibility mapping.",
    "Generate package dictionary from approved product schema plus curated descriptions."
  )
)
consumer_contract_comparison_path <- write_table("consumer_contract_comparison.csv", consumer_contract_comparison)

consumer_diffs <- rbindlist(list(
  data.table(
    comparison = "published-agronomy-schema-vs-eragri-data",
    side = "published-only",
    identifier = setdiff(agronomy_columns, names(package_data))
  ),
  data.table(
    comparison = "published-agronomy-schema-vs-eragri-data",
    side = "package-only",
    identifier = setdiff(names(package_data), agronomy_columns)
  ),
  data.table(
    comparison = "eragri-data-vs-eragri-dictionary",
    side = "data-only",
    identifier = setdiff(names(package_data), package_dictionary$Field.Name)
  ),
  data.table(
    comparison = "eragri-data-vs-eragri-dictionary",
    side = "dictionary-only",
    identifier = setdiff(package_dictionary$Field.Name, names(package_data))
  )
), fill = TRUE)
consumer_diffs[, recommended_disposition := fifelse(
  comparison == "published-agronomy-schema-vs-eragri-data",
  "Resolve through explicit release compatibility profile; do not assume package snapshot is current release.",
  "Replace literal or pattern drift with generated dictionary entries and explicit aliases."
)]
setorder(consumer_diffs, comparison, side, identifier)
consumer_diffs_path <- write_table("consumer_contract_diffs.csv", consumer_diffs)

semantic_binding_scope <- copy(structural_bindings)
semantic_binding_scope[, domain_scope := fifelse(
  grepl("Ingredient|FeedMaterial", target_class) | grepl("ingredient|sourceTaxon", target_property),
  "livestock-feed",
  "livestock-grazing-observation"
)]
semantic_binding_scope[, shared_core_disposition := fifelse(
  binding_kind == "observable_property",
  "Retain domain property in livestock; evaluate generic observation scaffold for core after crop comparison.",
  "Retain binding in livestock until equivalent crop data-model use is demonstrated."
)]
semantic_binding_scope_path <- write_table("semantic_binding_scope.csv", semantic_binding_scope)

shared_core_boundary <- data.table(
  boundary_id = c(
    "CORE-01", "CORE-02", "CORE-03", "CORE-04",
    "CORE-05", "CORE-06", "CORE-07", "CORE-08"
  ),
  semantic_family = c(
    "release-and-evidence-governance",
    "semantic-binding-governance",
    "observation-event",
    "quantity-value-and-unit",
    "process-application",
    "biological-source-and-context",
    "feed-domain-model",
    "crop-and-livestock-code-values"
  ),
  current_evidence = c(
    "AOM schema defines Module, MappingAssertion, ChangeProposal, Release, Evidence, and Reviewer.",
    "AOM schema defines SemanticBinding and SemanticValueBinding, but approved rows are livestock scoped.",
    "AOM schema defines QuantitativeObservation and uses SOSA observation predicates for livestock grazing.",
    "AOM schema uses QUDT QuantityValue, quantity kinds, and unit requirements in approved livestock bindings.",
    "AOM schema defines ProcessingMethod and ProcessApplication through feed-focused reviews.",
    "Source taxon and feature context recur conceptually across domains, but only livestock value contracts are approved.",
    "Feed, formulation, additive, ingredient, feed role, form, composition, and feed process classes are domain specific.",
    "Workbook lookups mix domain concepts, interface enumerations, units, and operational values."
  ),
  target_module = c(
    "aom-core-candidate",
    "aom-core-candidate",
    "aom-core-candidate",
    "aom-core-candidate",
    "hold-for-cross-domain-review",
    "hold-for-cross-domain-review",
    "aom-livestock",
    "route-by-field"
  ),
  approval_condition = c(
    "Confirm repository-wide use and preserve PROV/DCAT-aligned provenance.",
    "Define stable dataset-field and value-set binding keys usable outside livestock.",
    "Compare crop outcome records and livestock observations; use current SOSA Property model.",
    "Approve raw-unit preservation, quantity-kind, unit-IRI, and conversion-basis contract.",
    "Compare crop management processes before extracting generic process classes.",
    "Complete crop product, species, site, and context review before shared promotion.",
    "Keep current identifiers and semantics within livestock module.",
    "Classify each value set as concept scheme, code list, enumeration, unit map, or operational control."
  ),
  prohibited_shortcut = c(
    "Do not treat repository location as proof of cross-domain scope.",
    "Do not promote livestock bindings merely because class names are generic.",
    "Do not type all outcome labels as one undifferentiated observable-property hierarchy.",
    "Do not infer canonical units, dimensions, denominators, or conversions from labels alone.",
    "Do not move feed processes to core before crop comparison.",
    "Do not equate same labels across crop and livestock without scope evidence.",
    "Do not move feed-specific classes into shared core.",
    "Do not publish all lookup rows as one SKOS scheme."
  )
)
shared_core_boundary_path <- write_table("shared_core_boundary.csv", shared_core_boundary)

recommendations <- data.table(
  recommendation_id = sprintf("DM-%02d", 1:12),
  priority = c("blocker", "blocker", "blocker", "high", "high", "high", "high", "high", "medium", "medium", "medium", "medium"),
  owner_repository = c(
    "era-data-pipeline", "canonical-workbook;era-data-pipeline", "canonical-workbook;era-data-pipeline",
    "canonical-workbook;era-data-pipeline;era-aom", "era-data-pipeline;era-data", "era-data;era-docs",
    "eragri;era-data", "era-aom", "era-aom;era-data-pipeline", "era-data",
    "era-data-pipeline;era-data", "era-program"
  ),
  action = c(
    "Define normalized tables, fields, field profiles, value sets, unit mappings, and semantic bindings as separate governed resources.",
    "Assign stable field keys and require one logical table-field identity; represent extraction-round differences in field profiles.",
    "Resolve 21 field-key issues, including probable Irrig.Out date-key conflict, before schema regeneration.",
    "Replace lookup_levels label join with explicit field_key to value_set_id relationship and review 41 unmatched pairs.",
    "Separate extraction-model schema from compiled-product schemas and derive each through explicit transformations.",
    "Document every 138-column public product schema field and publish product-specific controlled-value links.",
    "Pin eragri data and dictionaries to an ERA release and generate compatibility reports for column additions, removals, and aliases.",
    "Promote only demonstrated governance, observation, quantity, and provenance scaffolds to shared core after crop-livestock comparison.",
    "Generalize semantic binding contract to stable dataset, table, field, value-set, and release identifiers without moving domain concepts to core.",
    "Publish tabular contracts as CSVW and/or Frictionless Table Schema descriptors validated against governed registry sources.",
    "Retain raw unit text; add reviewed canonical unit URI, quantity kind, conversion rule, basis, and provenance; resolve 64 blanks and ZMK/ha conflict.",
    "Close issues #27 and #21 only after source, generated schema, released Parquet, package, catalog, and documentation parity gates pass."
  ),
  acceptance_evidence = c(
    "Machine-readable normalized registry with unique keys and foreign-key validation.",
    "No duplicate logical field keys; four extraction rounds represented without duplicate field definitions.",
    "Every issue row has reviewed source disposition and regenerated output.",
    "All 83 value-set pairs resolve through explicit keys or reviewed retirement; no fuzzy join.",
    "Separate extraction and product manifests with declared derivation lineage.",
    "Both product schemas contain 138 reviewed descriptions or explicit documented deferrals.",
    "Package objects expose release ID and zero unexplained schema drift.",
    "Approved shared-core register with crop and livestock evidence per promoted family.",
    "Bindings validate against stable keys and preserve domain-module target ownership.",
    "Descriptors validate tables, datatypes, keys, requiredness, and foreign keys.",
    "Every unit row has governed status; canonical mappings carry identifier, quantity kind, and transformation evidence where applicable.",
    "Cross-repository compatibility matrix and green contract tests."
  ),
  semantic_change_authorized = "no"
)
recommendations_path <- write_table("recommendation_register.csv", recommendations)

authority_comparison <- data.table(
  authority_id = c("AUTH-01", "AUTH-02", "AUTH-03", "AUTH-04", "AUTH-05", "AUTH-06", "AUTH-07", "AUTH-08"),
  authority = c(
    "ERA ADR 0007",
    "AOM ADR 0051",
    "W3C CSVW",
    "Frictionless Table Schema",
    "W3C SHACL",
    "W3C SOSA/SSN 2023",
    "QUDT",
    "W3C PROV-O and DCAT 3"
  ),
  supports = c(
    "Canonical workbook authority until governed cutover.",
    "Resource routing and Wave 1 data-model/shared-core sequence.",
    "Column metadata, datatypes, keys, foreign keys, annotations, and tabular validation.",
    "Portable JSON field descriptors, constraints, primary keys, and foreign keys.",
    "Validation of RDF semantic bindings and shared-core graphs.",
    "Observation, feature, procedure, result, and identifiable property relations.",
    "Quantity values, quantity kinds, units, dimensions, and conversion semantics.",
    "Provenance plus dataset, distribution, version, and checksum metadata."
  ),
  does_not_support = c(
    "Workbook layout does not define target architecture or approve semantic identity.",
    "Architecture does not resolve field rows, lookup keys, units, or consumer drift.",
    "Does not decide agricultural concept identity or external ontology mappings.",
    "Does not provide domain semantics or replace RDF graph validation.",
    "Does not define raw tabular release schema or choose canonical units.",
    "Does not define ERA outcome taxonomy or measured quantity kinds by itself.",
    "Does not prove a raw label denotes a unit or authorize conversion without context.",
    "Does not define field-level agricultural meaning or table constraints."
  ),
  evidence = c(
    "https://github.com/ERAgriculture/era-program/blob/main/project-management/decisions/ADR-0007-canonical-vocab-source.md",
    "docs/decisions/0051-whole-vocabulary-resource-boundaries-and-migration-sequence.md",
    "https://www.w3.org/TR/tabular-data-model/;https://www.w3.org/TR/tabular-metadata/",
    "https://specs.frictionlessdata.io/table-schema/",
    "https://www.w3.org/TR/shacl/",
    "https://www.w3.org/TR/vocab-ssn-2023/",
    "https://www.qudt.org/catalog/qudt-catalog.html",
    "https://www.w3.org/TR/prov-o/;https://www.w3.org/TR/vocab-dcat-3/"
  )
)
authority_comparison_path <- write_table("authority_comparison.csv", authority_comparison)

evidence_register <- data.table(
  claim_id = sprintf("EVID-%02d", 1:14),
  claim = c(
    "Current canonical field sheet has 754 workbook rows but only 733 unique valid table-field keys.",
    "Seventeen logical field keys are duplicated and one populated field lacks table identity.",
    "Current schema generator omits courageous_camel_2024 despite 324 field rows carrying that round.",
    "Published extraction model retains 750 field entries over 733 unique keys and includes no unit field.",
    "Only 42 of 83 lookup table-field pairs exactly match current field-registry keys.",
    "Unit crosswalk has 64 blank corrections and one raw label with two distinct nonblank corrections.",
    "Published agronomy and livestock product schemas each contain 138 columns and zero descriptions.",
    "eragri package data has 137 columns while package dictionary has 106 field names.",
    "Current approved semantic bindings cover 13 livestock/feed or grazing concepts and no crop source fields.",
    "Current approved semantic value contract contains 298 livestock/feed-scoped rows.",
    "Published vocab v2026.1 records an older workbook fingerprint than current canonical workbook.",
    "CSVW and Frictionless Table Schema can represent field datatypes, constraints, and key relationships.",
    "QUDT can identify units and quantity kinds but label matching alone cannot authorize a mapping or conversion.",
    "Shared-core promotion requires crop-livestock evidence; current generic scaffolds remain candidates, not completed core migration."
  ),
  disposition = c(
    "confirmed", "confirmed", "confirmed", "confirmed", "confirmed", "confirmed", "confirmed",
    "confirmed", "confirmed", "confirmed", "confirmed", "authority-supported", "authority-supported", "governance-decision"
  ),
  evidence = c(
    "source_contracts.csv;field_quality_metrics.csv",
    "field_key_issues.csv",
    "field_quality_metrics.csv;R/vocab/build_model_schema.R",
    "consumer_contract_comparison.csv;vocab/version=2026.1/era_data_model.schema.json",
    "lookup_binding_audit.csv",
    "unit_mapping_audit.csv",
    "consumer_contract_comparison.csv;schemas/era_compiled.schema.json;schemas/era_compiled_ls.schema.json",
    "consumer_contract_comparison.csv;consumer_contract_diffs.csv",
    "semantic_binding_scope.csv",
    "source_contracts.csv;approved_semantic_value_bindings.csv",
    "source_contracts.csv;vocab/version=2026.1/vocab_manifest.json",
    "https://www.w3.org/TR/tabular-metadata/;https://specs.frictionlessdata.io/table-schema/",
    "https://www.qudt.org/catalog/qudt-catalog.html;unit_mapping_audit.csv",
    "docs/decisions/0051-whole-vocabulary-resource-boundaries-and-migration-sequence.md;shared_core_boundary.csv"
  ),
  limitation = c(
    "Counts describe current workbook structure, not approved target fields.",
    "Duplicate rows may encode round variants; audit does not auto-merge them.",
    "Round flags do not prove fields are populated in released data.",
    "Published model derives from v2026.1 source and is not rebuilt from current workbook in this review.",
    "Unmatched pairs may be stale names, source omissions, or intentional external tables; no candidate is auto-approved.",
    "Audit evaluates labels only and does not infer dimensions or conversion factors.",
    "Schema files describe released product columns but do not prove data values satisfy intended semantics.",
    "Package snapshot may intentionally represent an older release; missing provenance prevents automatic reconciliation.",
    "Generic target classes do not establish shared-core scope.",
    "Reviewed value bindings cover only observed livestock contract values.",
    "Different fingerprint signals lineage drift, not that immutable v2026.1 should be overwritten.",
    "Neither standard decides agricultural semantics or ontology identity.",
    "QUDT coverage varies by unit type; currencies and contextual ratios may require other authorities or ERA mappings.",
    "No semantic entity is promoted or moved by this recommendation-only review."
  )
)
evidence_register_path <- write_table("evidence_register.csv", evidence_register)

status_counts <- as.list(table(unit_mapping_audit$mapping_status))
lookup_status_counts <- as.list(table(lookup_binding_audit$exact_match))
summary <- list(
  review = "data-model-v1",
  review_date = "2026-08-24",
  status = "recommendation-only",
  source_workbook_sha256 = file_sha256(master),
  source_workbook_md5 = digest(file = master, algo = "md5"),
  published_vocab_workbook_md5 = vocab_manifest$source$workbook_md5,
  field_registry = list(
    workbook_rows = nrow(fields_all),
    populated_field_rows = nrow(field_rows),
    valid_field_rows = nrow(valid_fields),
    unique_field_keys = nrow(valid_field_keys),
    duplicate_field_keys = nrow(duplicate_keys),
    issue_rows = nrow(field_key_issues),
    missing_descriptions = nrow(field_rows[!nonblank(Field_Description)]),
    missing_datatypes = nrow(field_rows[!nonblank(Data_Type)]),
    courageous_camel_fields = nrow(field_rows[vapply(courageous_camel_2024, function(value) {
      !is.na(value) && toupper(trimws(as.character(value))) %in% c("TRUE", "Y", "YES", "1")
    }, logical(1))])
  ),
  published_model = list(
    tables = length(model$tables),
    field_entries = nrow(model_fields),
    unique_field_keys = uniqueN(model_fields, by = c("Table", "Field")),
    extraction_rounds = unlist(model$extraction_rounds),
    fields_with_allowed_values = nrow(model_fields[allowed_value_count > 0L]),
    allowed_values = sum(model_fields$allowed_value_count)
  ),
  lookup_registry = list(
    rows = nrow(lookups),
    table_field_pairs = nrow(lookup_binding_audit),
    exact_matches = as.integer(lookup_status_counts$yes %||% 0L),
    unmatched_pairs = as.integer(lookup_status_counts$no %||% 0L)
  ),
  unit_registry = c(list(rows = nrow(unit_mapping_audit)), lapply(status_counts, as.integer)),
  consumers = list(
    agronomy_schema_columns = length(agronomy_columns),
    livestock_schema_columns = length(livestock_columns),
    product_schema_descriptions = sum(nonblank(schema_descriptions(agronomy_schema))) + sum(nonblank(schema_descriptions(livestock_schema))),
    eragri_data_columns = ncol(package_data),
    eragri_dictionary_fields = nrow(package_dictionary),
    recorded_differences = nrow(consumer_diffs)
  ),
  semantic_bindings = list(
    structural = nrow(structural_bindings),
    values = nrow(value_bindings),
    crop_source_bindings = 0L
  ),
  recommendations = nrow(recommendations),
  semantic_changes = 0L,
  allocated_identifiers = 0L,
  outputs = list(
    source_contracts_sha256 = file_sha256(source_contracts_path),
    field_key_issues_sha256 = file_sha256(field_key_issues_path),
    field_quality_metrics_sha256 = file_sha256(field_quality_metrics_path),
    lookup_binding_audit_sha256 = file_sha256(lookup_binding_audit_path),
    unit_mapping_audit_sha256 = file_sha256(unit_mapping_audit_path),
    consumer_contract_comparison_sha256 = file_sha256(consumer_contract_comparison_path),
    consumer_contract_diffs_sha256 = file_sha256(consumer_diffs_path),
    semantic_binding_scope_sha256 = file_sha256(semantic_binding_scope_path),
    shared_core_boundary_sha256 = file_sha256(shared_core_boundary_path),
    recommendation_register_sha256 = file_sha256(recommendations_path),
    authority_comparison_sha256 = file_sha256(authority_comparison_path),
    evidence_register_sha256 = file_sha256(evidence_register_path)
  )
)
write_json(summary, file.path(output, "review_summary.json"), auto_unbox = TRUE, pretty = TRUE)

cat(sprintf(
  "Data-model review: %d unique field keys, %d lookup pairs, %d unit rows, %d recommendations -> %s\n",
  nrow(valid_field_keys), nrow(lookup_binding_audit), nrow(unit_mapping_audit), nrow(recommendations), output
))
