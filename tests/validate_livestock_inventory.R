#!/usr/bin/env Rscript

path <- if (length(commandArgs(trailingOnly = TRUE))) {
  commandArgs(trailingOnly = TRUE)[[1]]
} else {
  "inventory/livestock_reconciliation.json"
}

if (!requireNamespace("jsonlite", quietly = TRUE)) {
  stop("Missing R package: jsonlite", call. = FALSE)
}

report <- jsonlite::read_json(path, simplifyVector = TRUE)
expect <- function(value, message) {
  if (!isTRUE(value)) stop(message, call. = FALSE)
}

expect(report$public_release$doi == "10.7910/DVN/75E7HV", "Unexpected DOI")
expect(report$public_release$version == "2.0", "Unexpected release version")
expect(
  report$public_release$md5 == "9dd9b11879805f22c18ec7e0173f80ba",
  "Public file checksum changed"
)
expect(report$public_release$rows == 2503L, "Public row count changed")
expect(report$public_release$meaningful_columns == 38L, "Column count changed")
expect(report$alignment$aom_id_mismatches == 0L, "AOM IDs drifted")
expect(report$alignment$hierarchy_level_mismatches == 0L, "Hierarchy drifted")
expect(
  report$identity_integrity$duplicate_aom_ids == "AOM_006275",
  "Duplicate-ID case changed"
)
expect(
  report$privacy$workbook_path_published == FALSE,
  "Private workbook path exposed"
)
expect(
  report$privacy$workbook_fingerprint_published == FALSE,
  "Private workbook fingerprint exposed"
)
expect(
  report$privacy$ssa_feedsdb_values_published == FALSE,
  "Restricted SSA Feeds values exposed"
)

cat("Livestock inventory validation passed\n")
