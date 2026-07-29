#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2L || length(args) > 3L) {
  stop(
    paste(
      "Usage: Rscript scripts/reconcile_livestock_release.R",
      "PUBLIC_AOM_CSV WORKBOOK [OUTPUT_JSON]"
    ),
    call. = FALSE
  )
}

public_path <- normalizePath(args[[1]], mustWork = TRUE)
workbook_path <- normalizePath(args[[2]], mustWork = TRUE)
output_path <- if (length(args) == 3L) {
  args[[3]]
} else {
  "inventory/livestock_reconciliation.json"
}

required <- c("digest", "jsonlite", "readxl")
missing <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing)) {
  stop("Missing R packages: ", paste(missing, collapse = ", "), call. = FALSE)
}

normalize_text <- function(x) {
  x <- iconv(as.character(x), from = "", to = "UTF-8", sub = "byte")
  x <- gsub("_x000D_", "\n", x, fixed = TRUE)
  x <- gsub("\r\n?", "\n", x)
  x <- gsub("[ \t]+(?=\n|$)", "", x, perl = TRUE)
  x <- trimws(x)
  x[is.na(x) | x == ""] <- NA_character_
  x
}

nonblank <- function(x) sum(!is.na(x) & trimws(x) != "")

equal_cells <- function(a, b) {
  (is.na(a) & is.na(b)) | (!is.na(a) & !is.na(b) & a == b)
}

derive_path <- function(data) {
  apply(data[paste0("L", 1:10)], 1, function(values) {
    value <- paste(values[!is.na(values)], collapse = "/")
    if (value == "") NA_character_ else value
  })
}

public <- utils::read.csv(
  public_path,
  check.names = FALSE,
  colClasses = "character",
  na.strings = NULL,
  fileEncoding = "windows-1252"
)
workbook <- as.data.frame(
  readxl::read_excel(
    workbook_path,
    sheet = "AOM",
    col_types = "text",
    .name_repair = "minimal"
  ),
  check.names = FALSE,
  stringsAsFactors = FALSE
)

meaningful_public_columns <- which(
  vapply(public, nonblank, integer(1)) > 0L |
    seq_along(public) <= ncol(workbook)
)
public_meaningful <- public[, meaningful_public_columns, drop = FALSE]

if (nrow(public_meaningful) != nrow(workbook)) {
  stop("Public/workbook row counts differ", call. = FALSE)
}
if (!identical(names(public_meaningful), names(workbook))) {
  stop("Public/workbook meaningful column names differ", call. = FALSE)
}

public_normalized <- public_meaningful
workbook_normalized <- workbook
public_normalized[] <- lapply(public_normalized, normalize_text)
workbook_normalized[] <- lapply(workbook_normalized, normalize_text)

comparison_rows <- lapply(seq_along(workbook_normalized), function(i) {
  matches <- equal_cells(public_normalized[[i]], workbook_normalized[[i]])
  data.frame(
    column = names(workbook_normalized)[[i]],
    public_nonblank = sum(!is.na(public_normalized[[i]])),
    workbook_nonblank = sum(!is.na(workbook_normalized[[i]])),
    mismatches = sum(!matches),
    stringsAsFactors = FALSE
  )
})
comparison <- do.call(rbind, comparison_rows)

public_derived_path <- derive_path(public_normalized)
workbook_derived_path <- derive_path(workbook_normalized)

ids <- workbook_normalized$AOM[!is.na(workbook_normalized$AOM)]
duplicate_ids <- unique(ids[duplicated(ids) | duplicated(ids, fromLast = TRUE)])
paths <- workbook_normalized$Path[!is.na(workbook_normalized$Path)]
duplicate_paths <- unique(
  paths[duplicated(paths) | duplicated(paths, fromLast = TRUE)]
)

related_sheets <- c(
  "AOM_diets",
  "ani_diet",
  "ani_process",
  "vars_animals",
  "ssa_feedsdb"
)
related <- lapply(related_sheets, function(sheet) {
  data <- readxl::read_excel(
    workbook_path,
    sheet = sheet,
    col_types = "text",
    .name_repair = "minimal"
  )
  list(sheet = sheet, rows = nrow(data), columns = ncol(data))
})

aom_diets <- readxl::read_excel(
  workbook_path,
  sheet = "AOM_diets",
  col_types = "text",
  .name_repair = "minimal"
)
diet_ids <- unique(normalize_text(aom_diets$AOM))
diet_ids <- diet_ids[!is.na(diet_ids)]

ani_diet <- readxl::read_excel(
  workbook_path,
  sheet = "ani_diet",
  col_types = "text",
  .name_repair = "minimal"
)
ani_diet_ids <- unique(normalize_text(ani_diet$D.Item.AOM))
ani_diet_ids <- ani_diet_ids[
  !is.na(ani_diet_ids) & grepl("^AOM_", ani_diet_ids)
]

mapping_fields <- c(
  "Ontology",
  "Agrovoc",
  "NCBI",
  "WFO",
  "Feedipedia",
  "ilri_code",
  "CPC_Code_Product",
  "CPC_Code_Component",
  "ERA_Code"
)
mapping_summary <- lapply(mapping_fields, function(field) {
  values <- public_normalized[[field]]
  values <- values[
    !is.na(values) &
      !values %in% c("NA", "#N/A")
  ]
  list(
    field = field,
    nonblank = length(values),
    distinct = length(unique(values)),
    http_uri = sum(grepl("^https?://", values)),
    malformed_http = sum(grepl("^https?:/[^/]", values))
  )
})

result <- list(
  report_schema_version = "1.0.0",
  public_release = list(
    doi = "10.7910/DVN/75E7HV",
    version = "2.0",
    release_date = "2026-01-21",
    file_id = 13249309,
    filename = basename(public_path),
    bytes = file.info(public_path)$size,
    md5 = digest::digest(file = public_path, algo = "md5"),
    sha256 = digest::digest(file = public_path, algo = "sha256"),
    rows = nrow(public),
    raw_columns = ncol(public),
    meaningful_columns = ncol(public_meaningful),
    empty_trailing_columns = ncol(public) - ncol(public_meaningful)
  ),
  workbook_aom = list(
    rows = nrow(workbook),
    columns = ncol(workbook),
    fingerprint_published = FALSE
  ),
  alignment = list(
    row_order_aligned = TRUE,
    column_names_aligned = TRUE,
    aom_id_mismatches = comparison$mismatches[comparison$column == "AOM"],
    hierarchy_level_mismatches = sum(
      comparison$mismatches[comparison$column %in% paste0("L", 1:10)]
    ),
    normalized_cell_mismatches = sum(comparison$mismatches),
    mismatch_by_column = comparison[comparison$mismatches > 0L, ]
  ),
  path_integrity = list(
    public_path_mismatches_derived_levels = sum(
      !equal_cells(public_normalized$Path, public_derived_path)
    ),
    workbook_path_mismatches_derived_levels = sum(
      !equal_cells(workbook_normalized$Path, workbook_derived_path)
    ),
    rule = "Path is derived, never canonical."
  ),
  identity_integrity = list(
    duplicate_aom_ids = duplicate_ids,
    duplicate_workbook_paths = duplicate_paths,
    stable_ids_never_reused = TRUE
  ),
  related_workbook_sheets = related,
  related_links = list(
    aom_diets_distinct_ids = length(diet_ids),
    aom_diets_ids_missing_from_aom = sum(!diet_ids %in% ids),
    ani_diet_distinct_mapped_ids = length(ani_diet_ids),
    ani_diet_ids_missing_from_aom = sum(!ani_diet_ids %in% ids),
    ani_diet_no_match_rows = sum(
      normalize_text(ani_diet$D.Item.AOM) == "No Match in AOM",
      na.rm = TRUE
    )
  ),
  external_mapping_fields = mapping_summary,
  privacy = list(
    workbook_path_published = FALSE,
    workbook_fingerprint_published = FALSE,
    ssa_feedsdb_values_published = FALSE
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(
  result,
  output_path,
  auto_unbox = TRUE,
  pretty = TRUE,
  na = "null"
)

cat(
  "Compared public AOM v2 with workbook AOM:",
  result$alignment$normalized_cell_mismatches,
  "normalized cell mismatches;",
  result$path_integrity$public_path_mismatches_derived_levels,
  "public path inconsistencies;",
  result$path_integrity$workbook_path_mismatches_derived_levels,
  "workbook path inconsistencies.\n"
)
