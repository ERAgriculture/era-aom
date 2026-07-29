#!/usr/bin/env Rscript

data_dir <- if (length(commandArgs(trailingOnly = TRUE))) {
  commandArgs(trailingOnly = TRUE)[[1]]
} else {
  "data/pilot"
}

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
id_registry <- read_table("id_registry")
labels <- read_table("labels")
definitions <- read_table("definitions")
notes <- read_table("notes")
relations <- read_table("relations")
properties <- read_table("properties")
source_records <- read_table("source_records")
schemes <- read_table("schemes")

fail <- function(message) stop(message, call. = FALSE)
expect <- function(value, message) if (!isTRUE(value)) fail(message)

expect(nrow(schemes) == 2L, "Expected two pilot schemes")
expect(!anyDuplicated(id_registry$concept_id), "Duplicate registered concept_id")
expect(
  !anyDuplicated(
    id_registry[c(
      "scheme_id",
      "concept_type",
      "parent_id",
      "source_label",
      "source_notation"
    )]
  ),
  "Duplicate ID registry key"
)
expect(!anyDuplicated(schemes$scheme_id), "Duplicate scheme_id")
expect(!anyDuplicated(concepts$concept_id), "Duplicate concept_id")
expect(all(concepts$scheme_id %in% schemes$scheme_id), "Unknown concept scheme")
expect(
  all(concepts$status %in% c("active", "deprecated", "unknown")),
  "Invalid concept status"
)
expect(
  all(relations$subject_id %in% concepts$concept_id),
  "Unknown relation subject"
)
expect(
  all(relations$object_id %in% concepts$concept_id),
  "Unknown relation object"
)
expect(
  all(c(labels$concept_id, definitions$concept_id, notes$concept_id) %in%
    concepts$concept_id),
  "Unknown annotation concept"
)
expect(
  all(properties$concept_id %in% concepts$concept_id),
  "Unknown property concept"
)
expect(
  !anyDuplicated(source_records[c("source_sheet", "source_row")]),
  "Duplicate source record"
)
expect(
  !anyDuplicated(source_records$concept_id),
  "Leaf linked to multiple source records"
)

pref <- labels[labels$label_type == "pref", ]
pref_counts <- table(pref$concept_id)
expect(
  all(concepts$concept_id %in% names(pref_counts)),
  "Concept missing preferred label"
)
expect(all(pref_counts == 1L), "Concept has multiple preferred labels")
expect(all(labels$language == "en"), "Unexpected pilot language")
expect(
  all(labels$label_type %in% c("pref", "alt", "hidden")),
  "Invalid label type"
)
expect(
  !anyDuplicated(labels[c("concept_id", "language", "label")]),
  "SKOS label literal reused across label types"
)

leaf_prac <- concepts[concepts$concept_type == "leaf_practice", ]
leaf_out <- concepts[concepts$concept_type == "leaf_outcome", ]
expect(nrow(leaf_prac) == 196L, "Practice leaf count changed")
expect(nrow(leaf_out) == 116L, "Outcome leaf count changed")
expect(
  all(leaf_prac$concept_id == paste0("era:practice:", leaf_prac$notation)),
  "Practice leaf ID rule broken"
)
expect(
  all(leaf_out$concept_id == paste0("era:outcome:", leaf_out$notation)),
  "Outcome leaf ID rule broken"
)

parents <- setNames(relations$object_id, relations$subject_id)
for (start in concepts$concept_id) {
  seen <- character()
  current <- start
  while (current %in% names(parents) &&
    !is.na(parents[[current]]) &&
    nzchar(parents[[current]])) {
    current <- parents[[current]]
    if (current %in% seen) fail(paste("Hierarchy cycle from", start))
    seen <- c(seen, current)
  }
}

cat(
  "Pilot validation passed:",
  nrow(concepts), "concepts,",
  nrow(labels), "labels,",
  nrow(relations), "relations\n"
)
