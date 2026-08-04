#!/usr/bin/env python3
"""Build deterministic phase-2 semantic-binding distributions."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/livestock-staging/approved_semantic_bindings.csv"
DIST = ROOT / "dist/livestock-staging"
CONCEPT_BASE = "urn:era-aom:livestock:"
BINDING_BASE = "urn:era-aom:binding:"
PREFIXES = {
    "aom": "urn:era-aom:schema:",
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

assert len(rows) == 13
assert len({row["legacy_concept_id"] for row in rows}) == 13

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
(DIST / "aom-semantic-bindings.ttl").write_text("\n".join(ttl), encoding="utf-8")
print(f"Built {len(rows)} approved phase-2 semantic bindings")
