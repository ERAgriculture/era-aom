#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2L || length(args) > 3L) {
  stop(
    "Usage: Rscript scripts/reconstruct_legacy.R DATA_DIR SHEET [OUTPUT]",
    call. = FALSE
  )
}

data_dir <- args[[1]]
sheet <- args[[2]]
output <- if (length(args) == 3L) args[[3]] else paste0(sheet, ".csv")
if (!sheet %in% c("prac", "out")) stop("SHEET must be prac or out", call. = FALSE)

read_table <- function(name) {
  utils::read.csv(
    file.path(data_dir, paste0(name, ".csv")),
    check.names = FALSE,
    colClasses = "character",
    na.strings = "",
    stringsAsFactors = FALSE
  )
}

concepts <- read_table("concepts")
labels <- read_table("labels")
definitions <- read_table("definitions")
notes <- read_table("notes")
relations <- read_table("relations")
properties <- read_table("properties")
source_records <- read_table("source_records")

pref <- labels[labels$label_type == "pref", c("concept_id", "label")]
names(pref)[2] <- "pref_label"

lookup_label <- function(ids, type = "pref", source_column = NULL) {
  candidates <- labels[labels$label_type == type, ]
  if (!is.null(source_column)) {
    candidates <- candidates[candidates$source_column == source_column, ]
  }
  candidates$label[match(ids, candidates$concept_id)]
}

lookup_definition <- function(ids) {
  definitions$definition[match(ids, definitions$concept_id)]
}

lookup_note <- function(ids) {
  notes$note[match(ids, notes$concept_id)]
}

lookup_property <- function(ids, property) {
  candidates <- properties[properties$property == property, ]
  candidates$value[match(ids, candidates$concept_id)]
}

parent <- function(ids) {
  candidates <- relations[relations$relation_type == "broader", ]
  candidates$object_id[match(ids, candidates$subject_id)]
}

leaf_type <- if (sheet == "prac") "leaf_practice" else "leaf_outcome"
leaf <- concepts[concepts$concept_type == leaf_type, ]
leaf <- merge(
  leaf,
  source_records[source_records$source_sheet == sheet, ],
  by = "concept_id",
  suffixes = c("", "_record"),
  sort = FALSE
)
leaf <- leaf[order(as.integer(leaf$source_row_record)), ]
leaf_ids <- leaf$concept_id

if (sheet == "prac") {
  practice_ids <- parent(leaf_ids)
  theme_ids <- parent(practice_ids)
  result <- data.frame(
    Code = leaf$notation,
    Theme = lookup_label(theme_ids),
    Theme.Code = concepts$notation[match(theme_ids, concepts$concept_id)],
    Practice = lookup_label(practice_ids),
    Practice.Code = concepts$notation[match(practice_ids, concepts$concept_id)],
    Subpractice = lookup_label(leaf_ids),
    Subpractice.Code = lookup_property(leaf_ids, "legacy_subpractice_code"),
    Subpractice.S = lookup_property(leaf_ids, "legacy_short_label"),
    Subpractice.Suffix = lookup_property(leaf_ids, "short_suffix"),
    Definition = lookup_definition(leaf_ids),
    Notes = lookup_note(leaf_ids),
    Linked.Tab = lookup_property(leaf_ids, "linked_table"),
    Linked.Col = lookup_property(leaf_ids, "linked_column"),
    Depreciated = lookup_property(leaf_ids, "legacy_deprecated"),
    check.names = FALSE,
    stringsAsFactors = FALSE
  )
} else {
  indicator_ids <- parent(leaf_ids)
  subpillar_ids <- parent(indicator_ids)
  pillar_ids <- parent(subpillar_ids)
  result <- data.frame(
    Code = leaf$notation,
    Pillar = lookup_label(pillar_ids),
    Pillar.Code = concepts$notation[match(pillar_ids, concepts$concept_id)],
    Subpillar = lookup_label(subpillar_ids),
    Subpillar.Code = concepts$notation[match(subpillar_ids, concepts$concept_id)],
    Indicator = lookup_label(indicator_ids),
    Indicator.Code = concepts$notation[match(indicator_ids, concepts$concept_id)],
    Subindicator = lookup_label(leaf_ids),
    Subindicator.Short = lookup_property(leaf_ids, "legacy_short_label"),
    Subindicator.Code = lookup_property(leaf_ids, "legacy_subindicator_code"),
    Definition = lookup_definition(leaf_ids),
    Notes = lookup_note(leaf_ids),
    `Example units` = lookup_property(leaf_ids, "example_units"),
    Original.Outcome = lookup_property(leaf_ids, "original_outcome"),
    `Negative Values` = lookup_property(leaf_ids, "negative_values"),
    Sign = lookup_property(leaf_ids, "direction_sign"),
    TC.Ratio = lookup_property(leaf_ids, "treatment_control_ratio"),
    Not.Perc = lookup_property(leaf_ids, "not_percentage"),
    Depreciated = lookup_property(leaf_ids, "legacy_deprecated"),
    Previous.Names = lookup_label(leaf_ids, "alt", "Previous.Names"),
    check.names = FALSE,
    stringsAsFactors = FALSE
  )
}

utils::write.csv(
  result,
  output,
  row.names = FALSE,
  na = "",
  quote = TRUE,
  fileEncoding = "UTF-8"
)
cat("Reconstructed", nrow(result), sheet, "rows in", output, "\n")
