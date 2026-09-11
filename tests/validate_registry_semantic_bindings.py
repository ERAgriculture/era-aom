#!/usr/bin/env python3
"""Validate IW-03 stable registry semantic-binding candidate."""

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from rdflib import Graph, RDF, URIRef


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/registry-bindings"
OUTPUT = ROOT / "dist/registry-bindings/version=2026.2-rc.1"
REVIEW = ROOT / "review/data-model-v11"
AOM = "https://w3id.org/era-aom/schema/"


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


config = json.loads(
    (ROOT / "config/registry-bindings/2026.2-rc.1.json").read_text(encoding="utf-8")
)
active = read_csv(SOURCE / "approved_semantic_bindings.csv")
ledger = read_csv(SOURCE / "semantic_binding_id_ledger.csv")
structural = read_csv(ROOT / "data/livestock-staging/approved_semantic_bindings.csv")
values = read_csv(ROOT / "data/livestock-staging/approved_semantic_value_bindings.csv")
published = read_csv(OUTPUT / "semantic_bindings.csv")
holds = read_csv(OUTPUT / "semantic_binding_holds.csv")
manifest = json.loads((OUTPUT / "manifest.json").read_text(encoding="utf-8"))
summary = json.loads(
    (REVIEW / "registry_semantic_binding_summary.json").read_text(encoding="utf-8")
)

assert active == published
assert len(active) == len(ledger) == 5
assert [row["semantic_binding_id"] for row in active] == [
    f"ERA-SBN-{index:06d}" for index in range(1, 6)
]
assert {row["registry_subject_id"] for row in active} == {
    "ERA-FLD-000041",
    "ERA-FLD-000084",
    "ERA-FLD-000092",
    "ERA-FLD-000093",
    "ERA-FLD-000111",
}
assert all(row["registry_subject_type"] == "field" for row in active)
assert all(row["binding_predicate"] == AOM + "mapsToProperty" for row in active)
assert all(row["lifecycle"] == "active" for row in active)
assert all(row["reviewer_status"] == "approved" for row in active)
assert all(row["domain_scope"] == "livestock-feed" for row in active)
assert not any(
    row["target_iri"].startswith("https://w3id.org/era-aom/core/")
    for row in active
)

assert len(structural) == 13
assert len(values) == 298
assert len(holds) == 307
assert len(structural) + len(values) == 311
assert len({row["semantic_source_key"] for row in active}) == 4
assert Counter(row["reason_code"] for row in holds) == {
    "amount-field-not-proportion": 1,
    "registry-field-not-allocated": 8,
    "registry-subject-held": 2,
    "registry-subject-held-and-target-ambiguous": 1,
    "registry-value-member-not-allocated": 295,
}
assert [row["hold_id"] for row in holds] == [
    f"ERA-SBH-{index:06d}" for index in range(1, 308)
]
assert all(row["lifecycle"] == "held" for row in holds)
assert {
    row["registry_subject_id"] for row in holds if row["registry_subject_id"]
} == {
    "ERA-FLD-000088",
    "ERA-VSM-000535",
    "ERA-VSM-000536",
    "ERA-VSM-000537",
}

structural_partition = {
    row["semantic_source_key"]
    for row in active
    if row["semantic_source_file"].endswith("approved_semantic_bindings.csv")
} | {
    row["semantic_source_key"]
    for row in holds
    if row["source_kind"] == "structural"
}
value_partition = {
    row["semantic_source_key"]
    for row in active
    if row["semantic_source_file"].endswith("approved_semantic_value_bindings.csv")
} | {
    row["semantic_source_key"]
    for row in holds
    if row["source_kind"] == "value"
}
assert structural_partition == {row["legacy_concept_id"] for row in structural}
assert value_partition == {
    row["target_property"] + "|" + row["source_value"] for row in values
}

assert config["status"] == manifest["status"] == "candidate"
assert config["latest"] is manifest["latest"] is False
assert manifest["registry"]["merge_commit"] == (
    "363c81ee709d939bd58a5f0980b3eb5e5d490fd2"
)
assert manifest["counts"]["active_binding_rows"] == 5
assert manifest["counts"]["held_source_decisions"] == 307
assert manifest["rollback"]["latest_pointer_change"] is False

public_candidate_text = "\n".join(
    path.read_text(encoding="utf-8")
    for directory in (SOURCE, OUTPUT)
    for path in sorted(directory.iterdir())
    if path.is_file()
)
for private_field_name in (
    "Animals.Diet",
    "ani_diet",
    "D.Item",
    "D.Source",
    "D.Amount",
):
    assert private_field_name not in public_candidate_text

ttl = Graph().parse(OUTPUT / "semantic_bindings.ttl")
jsonld = Graph().parse(OUTPUT / "semantic_bindings.jsonld")
assert set(ttl) == set(jsonld)
binding_class = URIRef(AOM + "RegistrySemanticBinding")
assert len(set(ttl.subjects(RDF.type, binding_class))) == 5

assert summary["status"] == "implemented-candidate"
assert summary["active_binding_rows"] == 5
assert summary["held_source_decisions"] == 307
assert summary["private_registry_content_copied"] is False
assert summary["clean_store_acceptance"] == "passed"
assert summary["latest_pointer_advanced"] is False
assert summary["downstream_candidate_refresh_complete"] is False

clean_store = json.loads(
    (REVIEW / "clean_store_acceptance.json").read_text(encoding="utf-8")
)
assert clean_store["status"] == "pass"
assert clean_store["empty_store"] is True
assert clean_store["registry_binding_graph"]["bindings"] == 5
assert clean_store["registry_binding_graph"]["triples"] == 153
assert clean_store["livestock_graph"]["concepts"] == 2814
assert clean_store["skosmos"]["representative_cards"] == 55

evidence = read_csv(REVIEW / "evidence_register.csv")
assert len(evidence) == 6
assert all(row["supports"] and row["claim_boundary"] for row in evidence)
local_evidence = {
    "EVID-IW03-001": ROOT / "review/data-model-v10/acceptance_summary.json",
    "EVID-IW03-003": ROOT / "data/livestock-staging/approved_semantic_bindings.csv",
    "EVID-IW03-004": ROOT / "data/livestock-staging/approved_semantic_value_bindings.csv",
    "EVID-IW03-005": OUTPUT / "manifest.json",
    "EVID-IW03-006": REVIEW / "clean_store_acceptance.json",
}
for row in evidence:
    if row["evidence_id"] in local_evidence:
        assert row["sha256"] == sha256(local_evidence[row["evidence_id"]])
assert next(
    row for row in evidence if row["evidence_id"] == "EVID-IW03-002"
)["sha256"] == config["registry"]["publication_manifest_sha256"]

authority = read_csv(REVIEW / "authority_comparison.csv")
assert len(authority) == 6
assert all(row["supports"] and row["limitation"] for row in authority)

method = (
    ROOT / "docs/methods/registry-semantic-binding-governance.md"
).read_text(encoding="utf-8")
review = (REVIEW / "README.md").read_text(encoding="utf-8")
adr = (
    ROOT / "docs/decisions/0054-cross-repository-data-model-registry-implementation-plan.md"
).read_text(encoding="utf-8")
assert "## Authority comparison" in review and "## Evidence" in review
assert "No inference from labels" in method
assert "data-model-v11" in adr

print("Validated IW-03 candidate: 5 active bindings, 307 explicit holds")
