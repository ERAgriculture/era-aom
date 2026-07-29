#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1L) {
  stop("Usage: Rscript tests/check_roundtrip.R WORKBOOK", call. = FALSE)
}

workbook <- normalizePath(args[[1]], mustWork = TRUE)
data_dir <- "data/pilot"
temp_dir <- tempfile("era-vocab-roundtrip-")
dir.create(temp_dir)

clean <- function(data) {
  data[] <- lapply(data, function(x) {
    x <- as.character(x)
    x <- gsub("\r\n?", "\n", x)
    x <- gsub("[ \t]+(?=\n|$)", "", x, perl = TRUE)
    x[is.na(x) | trimws(x) == ""] <- NA_character_
    x
  })
  as.data.frame(data, check.names = FALSE, stringsAsFactors = FALSE)
}

normalize_decimal_code <- function(x) {
  ifelse(
    is.na(x),
    NA_character_,
    format(as.numeric(x), scientific = FALSE, trim = TRUE, digits = 15)
  )
}

for (sheet in c("prac", "out")) {
  output <- file.path(temp_dir, paste0(sheet, ".csv"))
  status <- system2(
    "Rscript",
    c("scripts/reconstruct_legacy.R", data_dir, sheet, output)
  )
  if (status != 0L) stop("Reconstruction failed for ", sheet, call. = FALSE)

  expected <- clean(
    readxl::read_excel(
      workbook,
      sheet = sheet,
      col_types = "text",
      .name_repair = "minimal"
    )
  )
  if (sheet == "out") expected$Code <- normalize_decimal_code(expected$Code)
  actual <- clean(
    utils::read.csv(
      output,
      check.names = FALSE,
      colClasses = "character",
      na.strings = "",
      stringsAsFactors = FALSE
    )
  )

  if (!identical(names(actual), names(expected))) {
    stop("Column mismatch for ", sheet, call. = FALSE)
  }
  if (!identical(actual, expected)) {
    mismatches <- sum(
      (is.na(actual) != is.na(expected)) |
        (!is.na(actual) & !is.na(expected) & actual != expected)
    )
    stop(sheet, " round-trip mismatches: ", mismatches, call. = FALSE)
  }
  cat(sheet, "round-trip passed:", nrow(actual), "rows\n")
}
