#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1L || length(args) > 2L) {
  stop(
    "Usage: Rscript scripts/generate_pilot.R WORKBOOK [OUTPUT_DIR]",
    call. = FALSE
  )
}

workbook <- normalizePath(args[[1]], mustWork = TRUE)
output_dir <- if (length(args) == 2L) args[[2]] else "data/pilot"
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

if (!requireNamespace("readxl", quietly = TRUE)) {
  stop("Missing R package: readxl", call. = FALSE)
}

clean <- function(x) {
  x <- as.character(x)
  x <- gsub("\r\n?", "\n", x)
  x <- gsub("[ \t]+(?=\n|$)", "", x, perl = TRUE)
  x[is.na(x) | trimws(x) == ""] <- NA_character_
  x
}

read_sheet <- function(sheet) {
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
  data[] <- lapply(data, clean)
  as.data.frame(data, check.names = FALSE, stringsAsFactors = FALSE)
}

key <- function(...) {
  values <- list(...)
  do.call(paste, c(lapply(values, function(x) ifelse(is.na(x), "<NA>", x)), sep = "\u241f"))
}

truth <- function(x) {
  !is.na(x) & tolower(trimws(x)) %in% c("true", "yes", "y", "1")
}

normalize_decimal_code <- function(x) {
  ifelse(
    is.na(x),
    NA_character_,
    format(as.numeric(x), scientific = FALSE, trim = TRUE, digits = 15)
  )
}

new_rows <- function() list()
concept_rows <- new_rows()
label_rows <- new_rows()
definition_rows <- new_rows()
note_rows <- new_rows()
relation_rows <- new_rows()
property_rows <- new_rows()
source_rows <- new_rows()
registry_path <- file.path(output_dir, "id_registry.csv")
registry <- if (file.exists(registry_path)) {
  utils::read.csv(
    registry_path,
    check.names = FALSE,
    colClasses = "character",
    na.strings = "",
    stringsAsFactors = FALSE
  )
} else {
  data.frame(
    scheme_id = character(),
    concept_type = character(),
    parent_id = character(),
    source_label = character(),
    source_notation = character(),
    concept_id = character(),
    stringsAsFactors = FALSE
  )
}

append_row <- function(rows, value) {
  rows[[length(rows) + 1L]] <- value
  rows
}

add_concept <- function(
  concept_id,
  scheme_id,
  concept_type,
  notation,
  status,
  source_sheet,
  source_row
) {
  concept_rows <<- append_row(
    concept_rows,
    data.frame(
      concept_id = concept_id,
      scheme_id = scheme_id,
      concept_type = concept_type,
      notation = ifelse(is.na(notation), "", notation),
      status = status,
      source_sheet = source_sheet,
      source_row = source_row,
      stringsAsFactors = FALSE
    )
  )
}

add_label <- function(concept_id, label_type, label, source_column) {
  if (is.na(label)) return(invisible(NULL))
  label_rows <<- append_row(
    label_rows,
    data.frame(
      concept_id = concept_id,
      language = "en",
      label_type = label_type,
      label = label,
      source_column = source_column,
      stringsAsFactors = FALSE
    )
  )
}

add_definition <- function(concept_id, definition, source_column = "Definition") {
  if (is.na(definition)) return(invisible(NULL))
  definition_rows <<- append_row(
    definition_rows,
    data.frame(
      concept_id = concept_id,
      language = "en",
      definition = definition,
      source_column = source_column,
      stringsAsFactors = FALSE
    )
  )
}

add_note <- function(concept_id, note, source_column = "Notes") {
  if (is.na(note)) return(invisible(NULL))
  note_rows <<- append_row(
    note_rows,
    data.frame(
      concept_id = concept_id,
      language = "en",
      note_type = "scope_note",
      note = note,
      source_column = source_column,
      stringsAsFactors = FALSE
    )
  )
}

add_relation <- function(subject_id, object_id) {
  relation_rows <<- append_row(
    relation_rows,
    data.frame(
      subject_id = subject_id,
      relation_type = "broader",
      object_id = object_id,
      stringsAsFactors = FALSE
    )
  )
}

add_property <- function(concept_id, property, value, value_type, source_column) {
  if (is.na(value)) return(invisible(NULL))
  property_rows <<- append_row(
    property_rows,
    data.frame(
      concept_id = concept_id,
      property = property,
      value = value,
      value_type = value_type,
      source_column = source_column,
      stringsAsFactors = FALSE
    )
  )
}

add_source <- function(sheet, row, concept_id) {
  source_rows <<- append_row(
    source_rows,
    data.frame(
      source_sheet = sheet,
      source_row = row,
      concept_id = concept_id,
      stringsAsFactors = FALSE
    )
  )
}

allocate_node_ids <- function(
  scheme_id,
  scheme,
  concept_type,
  parent_ids,
  source_labels,
  source_notations
) {
  parent_values <- ifelse(is.na(parent_ids), "", parent_ids)
  notation_values <- ifelse(is.na(source_notations), "", source_notations)
  node_keys <- key(parent_values, source_labels, notation_values)
  unique_keys <- unique(node_keys)
  result <- setNames(character(length(unique_keys)), unique_keys)

  relevant <- registry[
    registry$scheme_id == scheme_id &
      registry$concept_type == concept_type,
  ]
  existing_numbers <- suppressWarnings(
    as.integer(sub(".*:", "", relevant$concept_id))
  )
  next_number <- if (length(existing_numbers) && any(!is.na(existing_numbers))) {
    max(existing_numbers, na.rm = TRUE) + 1L
  } else {
    1L
  }

  for (node_key in unique_keys) {
    row <- which(node_keys == node_key)[[1]]
    matches <- ifelse(is.na(relevant$parent_id), "", relevant$parent_id) ==
      parent_values[[row]] &
      relevant$source_label == source_labels[[row]] &
      ifelse(is.na(relevant$source_notation), "", relevant$source_notation) ==
        notation_values[[row]]
    if (any(matches)) {
      concept_id <- relevant$concept_id[which(matches)[[1]]]
    } else {
      concept_id <- sprintf(
        "era:%s:%s:%03d",
        scheme,
        concept_type,
        next_number
      )
      next_number <- next_number + 1L
      registry <<- rbind(
        registry,
        data.frame(
          scheme_id = scheme_id,
          concept_type = concept_type,
          parent_id = parent_values[[row]],
          source_label = source_labels[[row]],
          source_notation = notation_values[[row]],
          concept_id = concept_id,
          stringsAsFactors = FALSE
        )
      )
      relevant <- registry[
        registry$scheme_id == scheme_id &
          registry$concept_type == concept_type,
      ]
    }
    result[[node_key]] <- concept_id
  }
  unname(result[node_keys])
}

add_hierarchy <- function(
  data,
  sheet,
  scheme,
  levels,
  leaf_label,
  leaf_code,
  leaf_alt = NULL
) {
  scheme_id <- paste0("era:scheme:", scheme)
  parent_ids <- rep(NA_character_, nrow(data))
  parent_keys <- rep("", nrow(data))

  for (level_index in seq_along(levels)) {
    level <- levels[[level_index]]
    level_key <- key(parent_keys, data[[level$label]], data[[level$code]])
    unique_keys <- unique(level_key)
    allocated_ids <- allocate_node_ids(
      scheme_id,
      scheme,
      level$type,
      parent_ids,
      data[[level$label]],
      data[[level$code]]
    )
    level_ids <- setNames(allocated_ids[match(unique_keys, level_key)], unique_keys)

    for (node_key in unique_keys) {
      rows <- which(level_key == node_key)
      first <- rows[[1]]
      node_id <- level_ids[[node_key]]
      add_concept(
        node_id,
        scheme_id,
        level$type,
        data[[level$code]][[first]],
        "active",
        sheet,
        first + 1L
      )
      add_label(node_id, "pref", data[[level$label]][[first]], level$label)
      if (!is.na(parent_ids[[first]])) add_relation(node_id, parent_ids[[first]])
    }

    parent_ids <- unname(level_ids[level_key])
    parent_keys <- level_key
  }

  leaf_ids <- paste0("era:", scheme, ":", data[[leaf_code]])
  if (anyDuplicated(leaf_ids)) {
    stop("Duplicate leaf identifiers in ", sheet, call. = FALSE)
  }

  for (i in seq_len(nrow(data))) {
    leaf_id <- leaf_ids[[i]]
    deprecated_raw <- data[["Depreciated"]][[i]]
    status <- if (is.na(deprecated_raw)) {
      "unknown"
    } else if (truth(deprecated_raw)) {
      "deprecated"
    } else {
      "active"
    }
    add_concept(
      leaf_id,
      scheme_id,
      paste0("leaf_", scheme),
      data[[leaf_code]][[i]],
      status,
      sheet,
      i + 1L
    )
    add_label(leaf_id, "pref", data[[leaf_label]][[i]], leaf_label)
    if (!is.null(leaf_alt)) {
      alt_value <- data[[leaf_alt]][[i]]
      if (!is.na(alt_value) && alt_value != data[[leaf_label]][[i]]) {
        add_label(leaf_id, "alt", alt_value, leaf_alt)
      }
    }
    add_definition(leaf_id, data[["Definition"]][[i]])
    add_note(leaf_id, data[["Notes"]][[i]])
    add_relation(leaf_id, parent_ids[[i]])
    add_source(sheet, i + 1L, leaf_id)
  }

  leaf_ids
}

prac <- read_sheet("prac")
prac_ids <- add_hierarchy(
  prac,
  "prac",
  "practice",
  list(
    list(type = "theme", label = "Theme", code = "Theme.Code"),
    list(type = "practice", label = "Practice", code = "Practice.Code")
  ),
  leaf_label = "Subpractice",
  leaf_code = "Code",
  leaf_alt = "Subpractice.S"
)

prac_properties <- list(
  legacy_subpractice_code = c("Subpractice.Code", "string"),
  legacy_short_label = c("Subpractice.S", "string"),
  short_suffix = c("Subpractice.Suffix", "string"),
  linked_table = c("Linked.Tab", "string"),
  linked_column = c("Linked.Col", "string"),
  legacy_deprecated = c("Depreciated", "boolean")
)
for (i in seq_len(nrow(prac))) {
  for (property in names(prac_properties)) {
    spec <- prac_properties[[property]]
    add_property(prac_ids[[i]], property, prac[[spec[[1]]]][[i]], spec[[2]], spec[[1]])
  }
}

out <- read_sheet("out")
out$Code <- normalize_decimal_code(out$Code)
out_ids <- add_hierarchy(
  out,
  "out",
  "outcome",
  list(
    list(type = "pillar", label = "Pillar", code = "Pillar.Code"),
    list(type = "subpillar", label = "Subpillar", code = "Subpillar.Code"),
    list(type = "indicator", label = "Indicator", code = "Indicator.Code")
  ),
  leaf_label = "Subindicator",
  leaf_code = "Code",
  leaf_alt = "Subindicator.Short"
)

out_properties <- list(
  legacy_subindicator_code = c("Subindicator.Code", "string"),
  legacy_short_label = c("Subindicator.Short", "string"),
  example_units = c("Example units", "string"),
  original_outcome = c("Original.Outcome", "string"),
  negative_values = c("Negative Values", "boolean"),
  direction_sign = c("Sign", "string"),
  treatment_control_ratio = c("TC.Ratio", "boolean"),
  not_percentage = c("Not.Perc", "string"),
  legacy_deprecated = c("Depreciated", "boolean")
)
for (i in seq_len(nrow(out))) {
  for (property in names(out_properties)) {
    spec <- out_properties[[property]]
    add_property(out_ids[[i]], property, out[[spec[[1]]]][[i]], spec[[2]], spec[[1]])
  }
  add_label(out_ids[[i]], "alt", out[["Previous.Names"]][[i]], "Previous.Names")
}

bind <- function(rows) {
  if (!length(rows)) data.frame() else do.call(rbind, rows)
}

tables <- list(
  id_registry = registry,
  concepts = bind(concept_rows),
  labels = unique(bind(label_rows)),
  definitions = unique(bind(definition_rows)),
  notes = unique(bind(note_rows)),
  relations = unique(bind(relation_rows)),
  properties = unique(bind(property_rows)),
  source_records = bind(source_rows)
)

tables$schemes <- data.frame(
  scheme_id = c("era:scheme:practice", "era:scheme:outcome"),
  notation = c("prac", "out"),
  preferred_label_en = c("AOM crop agricultural practices", "AOM crop outcomes"),
  status = c("pilot", "pilot"),
  stringsAsFactors = FALSE
)

column_order <- c(
  "id_registry",
  "schemes",
  "concepts",
  "labels",
  "definitions",
  "notes",
  "relations",
  "properties",
  "source_records"
)
for (table in column_order) {
  utils::write.csv(
    tables[[table]],
    file.path(output_dir, paste0(table, ".csv")),
    row.names = FALSE,
    na = "",
    quote = TRUE,
    fileEncoding = "UTF-8"
  )
}

cat(
  "Generated", nrow(tables$concepts), "concepts,",
  nrow(tables$labels), "labels, and",
  nrow(tables$relations), "relations in", output_dir, "\n"
)
