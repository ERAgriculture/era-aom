#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
data_dir <- if (length(args) >= 1L) args[[1]] else "data/pilot"
output_dir <- if (length(args) >= 2L) args[[2]] else "dist/pilot"
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

if (!requireNamespace("jsonlite", quietly = TRUE)) {
  stop("Missing R package: jsonlite", call. = FALSE)
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
labels <- read_table("labels")
definitions <- read_table("definitions")
notes <- read_table("notes")
relations <- read_table("relations")
schemes <- read_table("schemes")

iri <- function(id) sub("^era:", "urn:era:", id)

json_values <- function(values, language = NULL) {
  values <- values[!is.na(values)]
  lapply(values, function(value) {
    result <- list("@value" = value)
    if (!is.null(language)) result[["@language"]] <- language
    result
  })
}

turtle_escape <- function(value) {
  value <- gsub("\\\\", "\\\\\\\\", value)
  value <- gsub("\"", "\\\\\"", value)
  value <- gsub("\r\n?", "\\\\n", value)
  gsub("\n", "\\\\n", value)
}

turtle_literal <- function(value, language = NULL) {
  result <- paste0("\"", turtle_escape(value), "\"")
  if (!is.null(language)) result <- paste0(result, "@", language)
  result
}

for (scheme_row in seq_len(nrow(schemes))) {
  scheme <- schemes[scheme_row, ]
  scheme_concepts <- concepts[concepts$scheme_id == scheme$scheme_id, ]
  concept_ids <- scheme_concepts$concept_id
  scheme_labels <- labels[labels$concept_id %in% concept_ids, ]
  scheme_definitions <- definitions[definitions$concept_id %in% concept_ids, ]
  scheme_notes <- notes[notes$concept_id %in% concept_ids, ]
  scheme_relations <- relations[relations$subject_id %in% concept_ids, ]

  graph <- list(
    list(
      "@id" = iri(scheme$scheme_id),
      "@type" = "skos:ConceptScheme",
      "skos:prefLabel" = json_values(scheme$preferred_label_en, "en"),
      "era:status" = scheme$status
    )
  )

  for (i in seq_len(nrow(scheme_concepts))) {
    concept <- scheme_concepts[i, ]
    concept_labels <- scheme_labels[scheme_labels$concept_id == concept$concept_id, ]
    concept_definitions <- scheme_definitions[
      scheme_definitions$concept_id == concept$concept_id,
    ]
    concept_notes <- scheme_notes[scheme_notes$concept_id == concept$concept_id, ]
    broader <- scheme_relations$object_id[
      scheme_relations$subject_id == concept$concept_id &
        scheme_relations$relation_type == "broader"
    ]

    node <- list(
      "@id" = iri(concept$concept_id),
      "@type" = "skos:Concept",
      "skos:inScheme" = list("@id" = iri(concept$scheme_id)),
      "skos:prefLabel" = json_values(
        concept_labels$label[concept_labels$label_type == "pref"],
        "en"
      ),
      "skos:notation" = if (is.na(concept$notation)) {
        NULL
      } else {
        concept$notation
      },
      "era:conceptType" = concept$concept_type,
      "era:status" = concept$status
    )
    alt <- concept_labels$label[concept_labels$label_type == "alt"]
    if (length(alt)) node[["skos:altLabel"]] <- json_values(alt, "en")
    if (nrow(concept_definitions)) {
      node[["skos:definition"]] <- json_values(
        concept_definitions$definition,
        "en"
      )
    }
    if (nrow(concept_notes)) {
      node[["skos:scopeNote"]] <- json_values(concept_notes$note, "en")
    }
    if (length(broader)) {
      node[["skos:broader"]] <- lapply(broader, function(id) list("@id" = iri(id)))
    }
    if (concept$status == "deprecated") node[["owl:deprecated"]] <- TRUE
    graph[[length(graph) + 1L]] <- node
  }

  document <- list(
    "@context" = list(
      skos = "http://www.w3.org/2004/02/skos/core#",
      owl = "http://www.w3.org/2002/07/owl#",
      era = "urn:era:property:"
    ),
    "@graph" = graph
  )

  basename <- scheme$notation
  jsonlite::write_json(
    document,
    file.path(output_dir, paste0(basename, ".jsonld")),
    auto_unbox = TRUE,
    pretty = TRUE,
    null = "null"
  )

  turtle <- c(
    "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
    "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
    "@prefix era: <urn:era:property:> .",
    "",
    paste0(
      "<", iri(scheme$scheme_id), "> a skos:ConceptScheme ;",
      "\n  skos:prefLabel ",
      turtle_literal(scheme$preferred_label_en, "en"),
      " ;\n  era:status ",
      turtle_literal(scheme$status),
      " .\n"
    )
  )

  for (i in seq_len(nrow(scheme_concepts))) {
    concept <- scheme_concepts[i, ]
    concept_labels <- scheme_labels[scheme_labels$concept_id == concept$concept_id, ]
    predicates <- c(
      "a skos:Concept",
      paste0("skos:inScheme <", iri(concept$scheme_id), ">"),
      paste0(
        "skos:prefLabel ",
        turtle_literal(
          concept_labels$label[concept_labels$label_type == "pref"][[1]],
          "en"
        )
      ),
      paste0("era:conceptType ", turtle_literal(concept$concept_type)),
      paste0("era:status ", turtle_literal(concept$status))
    )
    if (!is.na(concept$notation)) {
      predicates <- c(
        predicates,
        paste0("skos:notation ", turtle_literal(concept$notation))
      )
    }
    alt <- concept_labels$label[concept_labels$label_type == "alt"]
    if (length(alt)) {
      predicates <- c(
        predicates,
        vapply(
          alt,
          function(value) paste0("skos:altLabel ", turtle_literal(value, "en")),
          character(1)
        )
      )
    }
    defs <- scheme_definitions$definition[
      scheme_definitions$concept_id == concept$concept_id
    ]
    if (length(defs)) {
      predicates <- c(
        predicates,
        vapply(
          defs,
          function(value) paste0("skos:definition ", turtle_literal(value, "en")),
          character(1)
        )
      )
    }
    concept_notes <- scheme_notes$note[
      scheme_notes$concept_id == concept$concept_id
    ]
    if (length(concept_notes)) {
      predicates <- c(
        predicates,
        vapply(
          concept_notes,
          function(value) paste0("skos:scopeNote ", turtle_literal(value, "en")),
          character(1)
        )
      )
    }
    broader <- scheme_relations$object_id[
      scheme_relations$subject_id == concept$concept_id
    ]
    if (length(broader)) {
      predicates <- c(
        predicates,
        vapply(
          broader,
          function(id) paste0("skos:broader <", iri(id), ">"),
          character(1)
        )
      )
    }
    if (concept$status == "deprecated") {
      predicates <- c(predicates, "owl:deprecated true")
    }
    turtle <- c(
      turtle,
      paste0(
        "<", iri(concept$concept_id), "> ",
        paste(predicates, collapse = " ;\n  "),
        " .\n"
      )
    )
  }

  turtle <- sub("\n$", "", turtle)
  writeLines(turtle, file.path(output_dir, paste0(basename, ".ttl")), useBytes = TRUE)
}

cat("Built pilot JSON-LD and Turtle in", output_dir, "\n")
