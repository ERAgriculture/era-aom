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
DIST = ROOT / "dist/livestock-staging"
CONCEPT_BASE = "urn:era-aom:livestock:"
BINDING_BASE = "urn:era-aom:binding:"
VALUE_BINDING_BASE = "urn:era-aom:value-binding:"
PREFIXES = {
    "aom": "urn:era-aom:schema:",
    "owl": "http://www.w3.org/2002/07/owl#",
    "qudt": "http://qudt.org/schema/qudt/",
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
material_facets += generated_material_facets

assert len(rows) == 13
assert len({row["legacy_concept_id"] for row in rows}) == 13
assert len(value_rows) == 298
assert {row["binding_action"] for row in value_rows} == {
    "map_to_existing", "map_to_external", "hold_ambiguous", "hold_non_taxon"
}
assert len(facet_rows) == 99 and len(facet_mappings) == 45 and len(facet_decompositions) == 65
assert len(facet_holds) == 10
assert len(material_facets) == 1625
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

for row in material_facets:
    material = CONCEPT_BASE + row["feed_material_id"]
    facet = facet_by_id[row["target_concept_id"]]
    graph.append({
        "@id": CONCEPT_BASE + row["target_concept_id"],
        "@type": ["skos:Concept", facet["value_class"]],
    })
    graph.append({
        "@id": material,
        "@type": ["skos:Concept", "aom:FeedMaterial"],
        row["target_property"]: {"@id": CONCEPT_BASE + row["target_concept_id"]},
    })

document = {"@context": PREFIXES, "@graph": graph}
DIST.mkdir(parents=True, exist_ok=True)
(DIST / "aom-semantic-bindings.jsonld").write_text(
    json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

ttl = [*(f"@prefix {key}: <{value}> ." for key, value in PREFIXES.items()), ""]
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
for row in material_facets:
    material = CONCEPT_BASE + row["feed_material_id"]
    target = CONCEPT_BASE + row["target_concept_id"]
    facet = facet_by_id[row["target_concept_id"]]
    ttl.append(f"<{target}> a skos:Concept, {facet['value_class']} .\n")
    ttl.append(
        f"<{material}> a skos:Concept, aom:FeedMaterial ;\n"
        f"  {row['target_property']} <{target}> .\n"
    )
(DIST / "aom-semantic-bindings.ttl").write_text("\n".join(ttl), encoding="utf-8")
print(f"Built {len(rows)} structural and {len(all_value_rows)} value semantic bindings")
