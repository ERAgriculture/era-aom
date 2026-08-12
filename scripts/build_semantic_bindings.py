#!/usr/bin/env python3
"""Build deterministic phase-2 semantic-binding distributions."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/livestock-staging/approved_semantic_bindings.csv"
VALUE_SOURCE = ROOT / "data/livestock-staging/approved_semantic_value_bindings.csv"
FACET_SOURCE = ROOT / "data/livestock-staging/approved_ingredient_facet_concepts.csv"
FACET_MAPPING_SOURCE = ROOT / "data/livestock-staging/approved_ingredient_component_value_mappings.csv"
FACET_DECOMPOSITION_SOURCE = ROOT / "data/livestock-staging/approved_ingredient_component_decompositions.csv"
FACET_HOLD_SOURCE = ROOT / "data/livestock-staging/approved_ingredient_component_value_holds.csv"
MATERIAL_FACET_SOURCE = ROOT / "data/livestock-staging/approved_feed_material_facets.csv"
GENERATED_MATERIAL_FACET_SOURCE = ROOT / "data/livestock-staging/approved_generated_feed_material_facets.csv"
HARD_TAIL_MATERIAL_FACET_SOURCE = ROOT / "data/livestock-staging/approved_hard_tail_feed_material_facets.csv"
STRUCTURAL_MATERIAL_FACET_SOURCE = ROOT / "data/livestock-staging/approved_structural_feed_material_facets.csv"
EXTERNAL_MATERIAL_FACET_SOURCE = ROOT / "data/livestock-staging/approved_feed_material_external_facets.csv"
PROCESS_STATE_RELATION_SOURCE = ROOT / "data/livestock-staging/approved_process_state_relations.csv"
FORMULATION_CLASSIFICATION_SOURCE = ROOT / "data/livestock-staging/approved_feed_formulation_classifications.csv"
TAXONOMY_CLASSIFICATION_SOURCE = ROOT / "data/livestock-staging/approved_feed_taxonomy_classifications.csv"
CONCEPT_TYPE_SOURCE = ROOT / "data/livestock-staging/approved_concept_semantic_types.csv"
FEED_ROLE_SOURCE = ROOT / "data/livestock-staging/approved_feed_role_assertions.csv"
COMPONENT_RETENTION_SOURCE = ROOT / "data/livestock-staging/approved_component_retention_relations.csv"
EXTERNAL_RESOURCE_LABEL_SOURCE = ROOT / "review/livestock-v9/feedipedia_definition_evidence.csv"
EXTERNAL_RESOURCE_LABEL_OVERRIDE_SOURCE = ROOT / "data/livestock-staging/approved_external_resource_labels.csv"
DIST = ROOT / "dist/livestock-staging"
CONCEPT_BASE = "urn:era-aom:livestock:"
BINDING_BASE = "urn:era-aom:binding:"
VALUE_BINDING_BASE = "urn:era-aom:value-binding:"
PREFIXES = {
    "aom": "urn:era-aom:schema:",
    "owl": "http://www.w3.org/2002/07/owl#",
    "qudt": "http://qudt.org/schema/qudt/",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "sosa": "http://www.w3.org/ns/sosa/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}


def expand(value):
    if not value or value == "iri" or value.startswith("http"):
        return value
    prefix, local = value.split(":", 1)
    return PREFIXES[prefix] + local


with SOURCE.open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))
with VALUE_SOURCE.open(encoding="utf-8", newline="") as handle:
    value_rows = list(csv.DictReader(handle))
with FACET_SOURCE.open(encoding="utf-8", newline="") as handle:
    facet_rows = list(csv.DictReader(handle))
with FACET_MAPPING_SOURCE.open(encoding="utf-8", newline="") as handle:
    facet_mappings = list(csv.DictReader(handle))
with FACET_DECOMPOSITION_SOURCE.open(encoding="utf-8", newline="") as handle:
    facet_decompositions = list(csv.DictReader(handle))
with FACET_HOLD_SOURCE.open(encoding="utf-8", newline="") as handle:
    facet_holds = list(csv.DictReader(handle))
with MATERIAL_FACET_SOURCE.open(encoding="utf-8", newline="") as handle:
    material_facets = list(csv.DictReader(handle))
with GENERATED_MATERIAL_FACET_SOURCE.open(encoding="utf-8", newline="") as handle:
    generated_material_facets = list(csv.DictReader(handle))
with HARD_TAIL_MATERIAL_FACET_SOURCE.open(encoding="utf-8", newline="") as handle:
    hard_tail_material_facets = list(csv.DictReader(handle))
with STRUCTURAL_MATERIAL_FACET_SOURCE.open(encoding="utf-8", newline="") as handle:
    structural_material_facets = list(csv.DictReader(handle))
with EXTERNAL_MATERIAL_FACET_SOURCE.open(encoding="utf-8", newline="") as handle:
    external_material_facets = list(csv.DictReader(handle))
with PROCESS_STATE_RELATION_SOURCE.open(encoding="utf-8", newline="") as handle:
    process_state_relations = list(csv.DictReader(handle))
with FORMULATION_CLASSIFICATION_SOURCE.open(encoding="utf-8", newline="") as handle:
    formulation_classifications = list(csv.DictReader(handle))
with TAXONOMY_CLASSIFICATION_SOURCE.open(encoding="utf-8", newline="") as handle:
    taxonomy_classifications = list(csv.DictReader(handle))
with CONCEPT_TYPE_SOURCE.open(encoding="utf-8", newline="") as handle:
    concept_semantic_types = list(csv.DictReader(handle))
with FEED_ROLE_SOURCE.open(encoding="utf-8", newline="") as handle:
    feed_role_assertions = list(csv.DictReader(handle))
with COMPONENT_RETENTION_SOURCE.open(encoding="utf-8", newline="") as handle:
    component_retention_relations = list(csv.DictReader(handle))
with EXTERNAL_RESOURCE_LABEL_SOURCE.open(encoding="utf-8", newline="") as handle:
    external_resource_label_evidence = list(csv.DictReader(handle))
with EXTERNAL_RESOURCE_LABEL_OVERRIDE_SOURCE.open(encoding="utf-8", newline="") as handle:
    external_resource_label_overrides = list(csv.DictReader(handle))
material_facets += (
    generated_material_facets + hard_tail_material_facets
    + structural_material_facets
)

assert len(rows) == 13
assert len({row["legacy_concept_id"] for row in rows}) == 13
assert len(value_rows) == 298
assert {row["binding_action"] for row in value_rows} == {
    "map_to_existing", "map_to_external", "hold_ambiguous", "hold_non_taxon"
}
assert len(facet_rows) == 124 and len(facet_mappings) == 46 and len(facet_decompositions) == 64
assert len(facet_holds) == 9
assert len({
    (row["feed_material_id"], row["target_property"], row["target_concept_id"])
    for row in material_facets
}) == len(material_facets)
assert len(external_material_facets) == 3
assert len(process_state_relations) == 2
assert len(formulation_classifications) == 29
assert len(taxonomy_classifications) == 220
classification_by_id = {row["concept_id"]: row for row in formulation_classifications}
classification_by_id.update({row["concept_id"]: row for row in taxonomy_classifications})
assert {
    row["semantic_class"] for row in classification_by_id.values()
    if row["semantic_class"]
} == {"aom:Feed", "aom:FeedMaterial", "aom:FeedFormulation", "aom:FeedAdditive"}
assert all(row["status"] in {"approved", "hold", "reviewed"} for row in classification_by_id.values())
semantic_class_by_id = {
    row["concept_id"]: row["semantic_class"]
    for row in classification_by_id.values() if row["semantic_class"]
}
concept_type_by_id = {
    row["concept_id"]: row["semantic_class"]
    for row in concept_semantic_types
}
assert len(concept_type_by_id) == len(concept_semantic_types)
assert list(semantic_class_by_id.values()).count("aom:FeedFormulation") == 39


def feed_class(concept_id):
    if concept_id in classification_by_id and not classification_by_id[concept_id]["semantic_class"]:
        if concept_id in concept_type_by_id:
            return concept_type_by_id[concept_id]
        raise ValueError(f"Unclassified feed-branch hold has semantic facets: {concept_id}")
    return semantic_class_by_id.get(concept_id, "aom:FeedMaterial")
facet_by_id = {row["concept_id"]: row for row in facet_rows}
facet_value_rows = []
for row in facet_mappings:
    facet = facet_by_id[row["target_concept_id"]]
    facet_value_rows.append({
        "identifier": "ingredient-component:" + row["source_value"].lower().replace(" ", "-"),
        "target_property": facet["target_property"], "source_value": row["source_value"],
        "binding_action": "map_to_existing", "target_concept_id": row["target_concept_id"],
        "target_uri": "", "target_label": row["target_label"],
        "value_class": facet["value_class"], "status": row["status"],
    })
for row in facet_decompositions:
    facet = facet_by_id[row["target_concept_id"]]
    facet_value_rows.append({
        "identifier": "ingredient-component:" + row["source_value"].lower().replace(" ", "-") + ":" + row["assertion_order"],
        "target_property": facet["target_property"], "source_value": row["source_value"],
        "binding_action": "decompose_to_existing", "target_concept_id": row["target_concept_id"],
        "target_uri": "", "target_label": row["target_label"],
        "value_class": facet["value_class"], "status": row["status"],
    })
for row in facet_holds:
    facet_value_rows.append({
        "identifier": "ingredient-component:" + row["source_value"].lower().replace(" ", "-") + ":hold",
        "target_property": row["target_property"], "source_value": row["source_value"],
        "binding_action": row["binding_action"], "target_concept_id": "",
        "target_uri": "", "target_label": "", "value_class": row["value_class"],
        "status": row["status"],
    })
for row in value_rows:
    row["identifier"] = "ingredient-source:" + row["source_value"].lower().replace(" ", "-")
all_value_rows = value_rows + facet_value_rows

graph = []
for concept_id, semantic_class in sorted(semantic_class_by_id.items()):
    graph.append({
        "@id": CONCEPT_BASE + concept_id,
        "@type": ["skos:Concept", semantic_class],
    })
for row in concept_semantic_types:
    graph.append({
        "@id": CONCEPT_BASE + row["concept_id"],
        "@type": ["skos:Concept", row["semantic_class"]],
    })
for row in facet_rows:
    graph.append({
        "@id": CONCEPT_BASE + row["concept_id"],
        "@type": ["skos:Concept", row["value_class"]],
    })
for row in rows:
    concept_uri = CONCEPT_BASE + row["legacy_concept_id"]
    binding = {
        "@id": BINDING_BASE + row["legacy_concept_id"],
        "@type": "aom:SemanticBinding",
        "aom:legacyConcept": {"@id": concept_uri},
        "aom:bindingKind": row["binding_kind"],
        "aom:targetClass": {"@id": expand(row["target_class"])},
        "aom:targetProperty": {"@id": expand(row["target_property"])},
        "aom:unitRequirement": row["unit_requirement"],
        "aom:compatibilityPolicy": row["compatibility_policy"],
        "aom:bindingStatus": row["status"],
    }
    value_class = expand(row["value_class"])
    if value_class and value_class != "iri":
        binding["aom:valueClass"] = {"@id": value_class}
    if row["quantity_kind_uri"]:
        binding["aom:quantityKind"] = {"@id": row["quantity_kind_uri"]}
    graph.append(binding)
    if row["binding_kind"] == "observable_property":
        graph.append({"@id": concept_uri, "@type": ["skos:Concept", "sosa:ObservableProperty"]})

for row in all_value_rows:
    binding = {
        "@id": VALUE_BINDING_BASE + row["identifier"],
        "@type": "aom:SemanticValueBinding",
        "aom:valueTargetProperty": {"@id": expand(row["target_property"])},
        "aom:sourceValue": row["source_value"],
        "aom:bindingAction": row["binding_action"],
        "aom:targetValueClass": {"@id": expand(row["value_class"])},
        "aom:valueBindingStatus": row["status"],
    }
    target = row["target_uri"] or (CONCEPT_BASE + row["target_concept_id"] if row["target_concept_id"] else "")
    if target:
        binding["aom:valueTargetConcept"] = {"@id": target}
        if row["target_concept_id"]:
            graph.append({"@id": target, "@type": ["skos:Concept", row["value_class"]]})
    graph.append(binding)

external_resource_labels = {}
for row in external_resource_label_evidence:
    if row["http_status"] != "200" or not row["page_heading"]:
        continue
    for uri in {row["feedipedia_url"], row["final_url"]} - {""}:
        existing_label = external_resource_labels.setdefault(uri, row["page_heading"])
        if existing_label != row["page_heading"]:
            raise ValueError(f"Conflicting external resource labels for {uri}")
for row in external_resource_label_overrides:
    external_resource_labels[row["target_uri"]] = row["target_label"]
for uri, label in sorted(external_resource_labels.items()):
    graph.append({
        "@id": uri,
        "skos:prefLabel": {"@value": label, "@language": "en"},
        "rdfs:label": {"@value": label, "@language": "en"},
    })

for row in material_facets:
    material = CONCEPT_BASE + row["feed_material_id"]
    facet = facet_by_id[row["target_concept_id"]]
    graph.append({
        "@id": CONCEPT_BASE + row["target_concept_id"],
        "@type": ["skos:Concept", facet["value_class"]],
    })
    graph.append({
        "@id": material,
        "@type": ["skos:Concept", feed_class(row["feed_material_id"])],
        row["target_property"]: {"@id": CONCEPT_BASE + row["target_concept_id"]},
    })
for row in external_material_facets:
    material = CONCEPT_BASE + row["feed_material_id"]
    graph.append({
        "@id": row["target_uri"],
        "@type": row["target_type"],
        "skos:prefLabel": {"@value": row["target_label"], "@language": "en"},
        "rdfs:label": {"@value": row["target_label"], "@language": "en"},
    })
    graph.append({
        "@id": material,
        "@type": ["skos:Concept", feed_class(row["feed_material_id"])],
        row["target_property"]: {"@id": row["target_uri"]},
    })
for row in process_state_relations:
    process = CONCEPT_BASE + row["process_concept_id"]
    result = CONCEPT_BASE + row["result_concept_id"]
    graph.append({"@id": process, "@type": ["skos:Concept", "aom:ProcessingMethod"]})
    graph.append({"@id": result, "@type": ["skos:Concept", row["result_class"]]})
    graph.append({
        "@id": process,
        row["relation_property"]: {"@id": result},
    })
for row in feed_role_assertions:
    role = CONCEPT_BASE + row["role_concept_id"]
    graph.append({"@id": role, "@type": ["skos:Concept", row["role_class"]]})
    graph.append({
        "@id": CONCEPT_BASE + row["subject_id"],
        "@type": "skos:Concept",
        row["relation_property"]: {"@id": role},
    })
for row in component_retention_relations:
    state = CONCEPT_BASE + row["state_concept_id"]
    retained = CONCEPT_BASE + row["retained_concept_id"]
    graph.append({"@id": state, "@type": ["skos:Concept", "aom:ComponentRetentionState"]})
    graph.append({"@id": retained, "@type": ["skos:Concept", row["retained_class"]]})
    graph.append({
        "@id": state,
        row["relation_property"]: {"@id": retained},
    })

document = {"@context": PREFIXES, "@graph": graph}
DIST.mkdir(parents=True, exist_ok=True)
(DIST / "aom-semantic-bindings.jsonld").write_text(
    json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

ttl = [*(f"@prefix {key}: <{value}> ." for key, value in PREFIXES.items()), ""]
for concept_id, semantic_class in sorted(semantic_class_by_id.items()):
    ttl.append(
        f"<{CONCEPT_BASE + concept_id}> a skos:Concept, {semantic_class} .\n"
    )
for row in concept_semantic_types:
    ttl.append(
        f"<{CONCEPT_BASE + row['concept_id']}> a skos:Concept, {row['semantic_class']} .\n"
    )
for row in facet_rows:
    ttl.append(
        f"<{CONCEPT_BASE + row['concept_id']}> a skos:Concept, {row['value_class']} .\n"
    )
for row in rows:
    concept_uri = CONCEPT_BASE + row["legacy_concept_id"]
    terms = [
        "a aom:SemanticBinding",
        f"aom:legacyConcept <{concept_uri}>",
        f'aom:bindingKind {json.dumps(row["binding_kind"])}',
        f'aom:targetClass <{expand(row["target_class"])}>',
        f'aom:targetProperty <{expand(row["target_property"])}>',
        f'aom:unitRequirement {json.dumps(row["unit_requirement"])}',
        f'aom:compatibilityPolicy {json.dumps(row["compatibility_policy"])}',
        f'aom:bindingStatus {json.dumps(row["status"])}',
    ]
    value_class = expand(row["value_class"])
    if value_class and value_class != "iri":
        terms.append(f"aom:valueClass <{value_class}>")
    if row["quantity_kind_uri"]:
        terms.append(f'aom:quantityKind <{row["quantity_kind_uri"]}>')
    ttl.append(f"<{BINDING_BASE + row['legacy_concept_id']}> " + " ;\n  ".join(terms) + " .\n")
    if row["binding_kind"] == "observable_property":
        ttl.append(f"<{concept_uri}> a skos:Concept, sosa:ObservableProperty .\n")
for row in all_value_rows:
    terms = [
        "a aom:SemanticValueBinding",
        f'aom:valueTargetProperty <{expand(row["target_property"])}>',
        f'aom:sourceValue {json.dumps(row["source_value"])}',
        f'aom:bindingAction {json.dumps(row["binding_action"])}',
        f'aom:targetValueClass <{expand(row["value_class"])}>',
        f'aom:valueBindingStatus {json.dumps(row["status"])}',
    ]
    target = row["target_uri"] or (CONCEPT_BASE + row["target_concept_id"] if row["target_concept_id"] else "")
    if target:
        terms.append(f"aom:valueTargetConcept <{target}>")
        if row["target_concept_id"]:
            ttl.append(f"<{target}> a skos:Concept, {row['value_class']} .\n")
    identifier = VALUE_BINDING_BASE + row["identifier"]
    ttl.append(f"<{identifier}> " + " ;\n  ".join(terms) + " .\n")
for uri, label in sorted(external_resource_labels.items()):
    label_text = json.dumps(label, ensure_ascii=False)
    ttl.append(
        f"<{uri}> skos:prefLabel {label_text}@en ;\n"
        f"  rdfs:label {label_text}@en .\n"
    )
for row in material_facets:
    material = CONCEPT_BASE + row["feed_material_id"]
    target = CONCEPT_BASE + row["target_concept_id"]
    facet = facet_by_id[row["target_concept_id"]]
    ttl.append(f"<{target}> a skos:Concept, {facet['value_class']} .\n")
    ttl.append(
        f"<{material}> a skos:Concept, {feed_class(row['feed_material_id'])} ;\n"
        f"  {row['target_property']} <{target}> .\n"
    )
for row in external_material_facets:
    material = CONCEPT_BASE + row["feed_material_id"]
    label = json.dumps(row["target_label"], ensure_ascii=False)
    ttl.append(
        f'<{row["target_uri"]}> a {row["target_type"]} ;\n'
        f"  skos:prefLabel {label}@en ;\n"
        f"  rdfs:label {label}@en .\n"
    )
    ttl.append(
        f"<{material}> a skos:Concept, {feed_class(row['feed_material_id'])} ;\n"
        f'  {row["target_property"]} <{row["target_uri"]}> .\n'
    )
for row in process_state_relations:
    process = CONCEPT_BASE + row["process_concept_id"]
    result = CONCEPT_BASE + row["result_concept_id"]
    ttl.append(f"<{process}> a skos:Concept, aom:ProcessingMethod .\n")
    ttl.append(f"<{result}> a skos:Concept, {row['result_class']} .\n")
    ttl.append(f"<{process}> {row['relation_property']} <{result}> .\n")
for row in feed_role_assertions:
    subject = CONCEPT_BASE + row["subject_id"]
    role = CONCEPT_BASE + row["role_concept_id"]
    ttl.append(f"<{role}> a skos:Concept, {row['role_class']} .\n")
    ttl.append(f"<{subject}> a skos:Concept ;\n  {row['relation_property']} <{role}> .\n")
for row in component_retention_relations:
    state = CONCEPT_BASE + row["state_concept_id"]
    retained = CONCEPT_BASE + row["retained_concept_id"]
    ttl.append(f"<{state}> a skos:Concept, aom:ComponentRetentionState .\n")
    ttl.append(f"<{retained}> a skos:Concept, {row['retained_class']} .\n")
    ttl.append(f"<{state}> {row['relation_property']} <{retained}> .\n")
(DIST / "aom-semantic-bindings.ttl").write_text("\n".join(ttl), encoding="utf-8")
print(
    f"Built {len(rows)} structural and {len(all_value_rows)} value semantic bindings; "
    f"{len(material_facets)} material facets and {len(external_resource_labels)} external labels"
)
