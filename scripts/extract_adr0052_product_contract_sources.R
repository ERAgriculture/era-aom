#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 3) {
  stop(
    "Usage: Rscript scripts/extract_adr0052_product_contract_sources.R <era-data> <eragri> <output-json>"
  )
}

era_data <- normalizePath(args[[1]], mustWork = TRUE)
eragri <- normalizePath(args[[2]], mustWork = TRUE)
output <- args[[3]]

repo_commit <- function(path) {
  result <- system2("git", c("-C", shQuote(path), "rev-parse", "HEAD"), stdout = TRUE)
  if (length(result) != 1) stop("Could not resolve commit for ", path)
  result[[1]]
}

repo_clean <- function(path) {
  length(system2("git", c("-C", shQuote(path), "status", "--porcelain"), stdout = TRUE)) == 0
}

file_sha256 <- function(path) {
  digest::digest(file = path, algo = "sha256", serialize = FALSE)
}

load_single_object <- function(path) {
  environment <- new.env(parent = emptyenv())
  loaded <- load(path, envir = environment)
  if (length(loaded) != 1) stop("Expected one object in ", path)
  environment[[loaded[[1]]]]
}

schema_source <- function(repo, relative_path, commit) {
  path <- file.path(repo, relative_path)
  schema <- jsonlite::fromJSON(path, simplifyVector = FALSE)
  columns <- lapply(seq_along(schema$columns), function(index) {
    column <- schema$columns[[index]]
    list(
      position = index,
      name = column$name,
      physical_type = column$type,
      description = column$description
    )
  })
  list(
    repository = "ERAgriculture/era-data",
    commit = commit,
    path = relative_path,
    sha256 = file_sha256(path),
    product = schema$product,
    column_count = length(columns),
    columns = columns
  )
}

if (!repo_clean(era_data)) stop("era-data worktree is not clean")
if (!repo_clean(eragri)) stop("eragri worktree is not clean")

era_data_commit <- repo_commit(era_data)
eragri_commit <- repo_commit(eragri)
package_data_path <- file.path(eragri, "data/ERA.Compiled.rda")
package_dictionary_path <- file.path(eragri, "data/ERACompiledFields.rda")
package_data <- load_single_object(package_data_path)
package_dictionary <- load_single_object(package_dictionary_path)

snapshot <- list(
  snapshot_date = "2026-09-01",
  status = "read-only-source-evidence",
  source_repositories = list(
    list(repository = "ERAgriculture/era-data", commit = era_data_commit, clean = TRUE),
    list(repository = "ERAgriculture/eragri", commit = eragri_commit, clean = TRUE)
  ),
  sources = list(
    agronomy_schema = schema_source(
      era_data,
      "schemas/era_compiled.schema.json",
      era_data_commit
    ),
    livestock_schema = schema_source(
      era_data,
      "schemas/era_compiled_ls.schema.json",
      era_data_commit
    ),
    package_data = list(
      repository = "ERAgriculture/eragri",
      commit = eragri_commit,
      path = "data/ERA.Compiled.rda",
      sha256 = file_sha256(package_data_path),
      object = "ERA.Compiled",
      row_count = nrow(package_data),
      column_count = ncol(package_data),
      columns = lapply(seq_along(names(package_data)), function(index) {
        list(position = index, name = names(package_data)[[index]])
      })
    ),
    package_dictionary = list(
      repository = "ERAgriculture/eragri",
      commit = eragri_commit,
      path = "data/ERACompiledFields.rda",
      sha256 = file_sha256(package_dictionary_path),
      object = "ERACompiledFields",
      row_count = nrow(package_dictionary),
      column_count = ncol(package_dictionary),
      columns = names(package_dictionary),
      rows = lapply(seq_len(nrow(package_dictionary)), function(index) {
        list(
          row = index,
          field_name = as.character(package_dictionary$Field.Name[[index]]),
          data_type = as.character(package_dictionary$Data.Type[[index]]),
          description = as.character(package_dictionary$Description[[index]]),
          example = as.character(package_dictionary$Example[[index]])
        )
      })
    )
  )
)

dir.create(dirname(output), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(snapshot, output, pretty = TRUE, auto_unbox = TRUE, null = "null")
cat("Wrote ADR 0052 product-contract source snapshot to", output, "\n")
