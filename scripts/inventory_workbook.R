#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1L || length(args) > 2L) {
  stop(
    "Usage: Rscript scripts/inventory_workbook.R WORKBOOK [OUTPUT_DIR]",
    call. = FALSE
  )
}

workbook <- normalizePath(args[[1]], mustWork = TRUE)
output_dir <- if (length(args) == 2L) args[[2]] else "inventory/generated"
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

required <- c("digest", "jsonlite", "readxl")
missing <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing)) {
  stop("Missing R packages: ", paste(missing, collapse = ", "), call. = FALSE)
}

blank <- function(x) is.na(x) | trimws(as.character(x)) == ""

infer_scalar_type <- function(x) {
  values <- trimws(as.character(x[!blank(x)]))
  if (!length(values)) return("empty")

  tests <- c(
    logical = all(tolower(values) %in% c("true", "false", "yes", "no", "0", "1")),
    integer = all(grepl("^[+-]?[0-9]+$", values)),
    numeric = all(grepl("^[+-]?(?:[0-9]+\\.?[0-9]*|\\.[0-9]+)$", values)),
    date = all(grepl("^\\d{4}-\\d{2}-\\d{2}(?:[ T].*)?$", values))
  )
  matches <- names(tests)[tests]
  if (length(matches)) matches[[1]] else "text"
}

sheet_names <- readxl::excel_sheets(workbook)
disposition_path <- file.path("inventory", "sheet_disposition.csv")
if (!file.exists(disposition_path)) {
  stop("Missing disposition file: ", disposition_path, call. = FALSE)
}
disposition <- utils::read.csv(
  disposition_path,
  check.names = FALSE,
  stringsAsFactors = FALSE
)
if (!setequal(sheet_names, disposition$sheet)) {
  stop(
    "Disposition sheet names must exactly match workbook sheet names.",
    call. = FALSE
  )
}

sheet_rows <- vector("list", length(sheet_names))
column_rows <- list()

for (i in seq_along(sheet_names)) {
  sheet <- sheet_names[[i]]
  data <- suppressWarnings(
    suppressMessages(
      readxl::read_excel(
        workbook,
        sheet = sheet,
        col_types = "text",
        .name_repair = "minimal"
      )
    )
  )
  headers <- names(data)
  nonblank_rows <- if (nrow(data)) {
    sum(rowSums(vapply(data, function(x) !blank(x), logical(nrow(data)))) > 0)
  } else {
    0L
  }
  duplicate_headers <- duplicated(headers) | duplicated(headers, fromLast = TRUE)

  sheet_disposition <- disposition[match(sheet, disposition$sheet), ]
  sheet_rows[[i]] <- data.frame(
    sheet_order = i,
    sheet = sheet,
    resource_type = sheet_disposition$resource_type,
    publication = sheet_disposition$publication,
    decision_status = sheet_disposition$decision_status,
    rows_read = nrow(data),
    nonblank_rows = nonblank_rows,
    columns = ncol(data),
    blank_cells = sum(vapply(data, function(x) sum(blank(x)), integer(1))),
    duplicate_header_positions = sum(duplicate_headers),
    stringsAsFactors = FALSE
  )

  if (ncol(data) && sheet_disposition$publication != "exclude") {
    column_rows[[length(column_rows) + 1L]] <- do.call(
      rbind,
      lapply(seq_along(data), function(j) {
        values <- data[[j]]
        present <- !blank(values)
        present_values <- as.character(values[present])
        data.frame(
          sheet = sheet,
          column_position = j,
          column = headers[[j]],
          inferred_scalar_type = infer_scalar_type(values),
          nonblank_values = sum(present),
          blank_values = sum(!present),
          distinct_nonblank_values = length(unique(present_values)),
          candidate_key = sum(present) > 0L &&
            !anyDuplicated(present_values) &&
            sum(present) == nrow(data),
          duplicate_header = duplicate_headers[[j]],
          stringsAsFactors = FALSE
        )
      })
    )
  }
}

sheets <- do.call(rbind, sheet_rows)
columns <- if (length(column_rows)) {
  do.call(rbind, column_rows)
} else {
  data.frame()
}

info <- file.info(workbook)
manifest <- list(
  inventory_schema_version = "1.0.0",
  generated_at_utc = format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"),
  source = list(
    filename = basename(workbook),
    bytes = unname(info$size),
    modified_at_utc = format(info$mtime, "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"),
    sha256 = digest::digest(file = workbook, algo = "sha256")
  ),
  workbook = list(
    sheet_count = length(sheet_names),
    sheet_names = sheet_names
  ),
  privacy = list(
    cell_values_exported = FALSE,
    note = "Structural metadata only; publication disposition reviewed separately."
  )
)

utils::write.csv(
  sheets,
  file.path(output_dir, "workbook_sheets.csv"),
  row.names = FALSE,
  na = ""
)
utils::write.csv(
  columns,
  file.path(output_dir, "workbook_columns.csv"),
  row.names = FALSE,
  na = ""
)
jsonlite::write_json(
  manifest,
  file.path(output_dir, "workbook_manifest.json"),
  auto_unbox = TRUE,
  pretty = TRUE
)

cat(
  "Inventoried", length(sheet_names), "sheets from", basename(workbook), "\n",
  "SHA-256:", manifest$source$sha256, "\n",
  "Cell values exported: no\n"
)
