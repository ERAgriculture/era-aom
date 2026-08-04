#!/usr/bin/env python3
"""Build conservative final taxon review from aggregate-only evidence."""
import argparse
import collections
import csv
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/livestock-staging/approved_semantic_value_bindings.csv"
FIELDS = [
    "source_name", "accepted_name", "rank", "legacy_ncbi_taxon_id",
    "proposed_ncbi_taxon_id", "decision_action", "status", "reviewer",
    "review_date", "evidence", "rationale",
]
SUGGEST = "https://api.ncbi.nlm.nih.gov/datasets/v2alpha/taxonomy/taxon_suggest/"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
CONTEXTUAL_HOLDS = {
    "creeping bluegrass",
    "zea mays (baby)",
    "brassica oleracea sp.",
    "fabaceae spp",
    "fabaceae spp.",
}


def normalize(value):
    return " ".join(value.strip().split())


def legacy_ids(value):
    found = set()
    for item in value.split(";"):
        parts = item.split("|")
        if len(parts) > 1 and parts[0] == "ncbi-taxonomy" and parts[1].startswith("NCBITaxon_"):
            found.add(parts[1])
    return sorted(found)


def query(name):
    url = SUGGEST + urllib.parse.quote(name, safe="")
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                return json.load(response).get("sci_name_and_ids", [])
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            if attempt == 4:
                return []
            time.sleep(2 ** attempt)
    return []


def exact_hit(name, hits):
    key = name.casefold()
    matches = [
        hit for hit in hits
        if hit.get("matched_term", "").casefold() == key
        or hit.get("sci_name", "").casefold() == key
    ]
    return matches[0] if len(matches) == 1 else None


def fetch_legacy(ids):
    numeric = [value.removeprefix("NCBITaxon_") for value in sorted(ids)]
    if not numeric:
        return {}
    url = EFETCH + "?db=taxonomy&id=" + ",".join(numeric) + "&retmode=xml"
    with urllib.request.urlopen(url, timeout=30) as response:
        taxa = ET.fromstring(response.read()).findall("Taxon")
    assert len(taxa) == len(numeric)
    result = {}
    for requested, taxon in zip(numeric, taxa):
        names = {taxon.findtext("ScientificName")}
        names.update(value.text for value in taxon.findall(".//OtherNames//DispName") if value.text)
        result["NCBITaxon_" + requested] = {
            "tax_id": taxon.findtext("TaxId"),
            "sci_name": taxon.findtext("ScientificName"),
            "rank": taxon.findtext("Rank").upper(),
            "names": {value.casefold() for value in names if value},
        }
    return result


def legacy_hit(name, legacy, records):
    matches = [records[value] for value in legacy if name.casefold() in records[value]["names"]]
    unique = {(hit["tax_id"], hit["sci_name"], hit["rank"]): hit for hit in matches}
    return next(iter(unique.values())) if len(unique) == 1 else None


def candidate(name, legacy, records):
    if name.casefold() in CONTEXTUAL_HOLDS:
        return "", "", "", "hold_contextual", "", "Context or rank syntax prevents safe taxon identity."
    unspecified = re.match(r"^(.+?)\s+spp?\.?$", name, flags=re.IGNORECASE)
    lookup = normalize(unspecified.group(1)) if unspecified else name
    hit = legacy_hit(lookup, legacy, records)
    if not hit:
        hit = exact_hit(lookup, query(lookup))
        time.sleep(0.36)
    if not hit:
        return "", "", "", "hold_unresolved", "", "No unique exact live NCBI name-status match; source review required."
    accepted = hit["sci_name"]
    rank = hit["rank"].lower()
    target = "NCBITaxon_" + hit["tax_id"]
    evidence = "https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=" + hit["tax_id"]
    if unspecified:
        if rank != "genus":
            return "", "", "", "hold_rank_mismatch", evidence, f"Unspecified-species label resolves to {rank}, not genus."
        return accepted, rank, target, "map_unspecified_species_to_genus", evidence, "Source explicitly denotes unspecified species; preserve genus rank."
    if legacy and target not in legacy:
        action = "replace_incorrect"
        rationale = "Live exact name match conflicts with inherited legacy target; replacement requires review."
    elif accepted.casefold() != name.casefold():
        action = "accept_as_synonym"
        rationale = "Preserve source name and use current NCBI accepted name."
    else:
        action = "accept_existing"
        rationale = "Exact live NCBI name match."
    return accepted, rank, target, action, evidence, rationale


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aggregate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    with CONTRACT.open(encoding="utf-8", newline="") as handle:
        governed = {
            normalize(row["source_value"]).casefold()
            for row in csv.DictReader(handle)
            if row["target_property"] == "aom:sourceTaxon"
        }
    names = collections.defaultdict(set)
    with args.aggregate.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            name = normalize(row["source_taxon_label"])
            if name and name.casefold() not in governed:
                names[name].update(legacy_ids(row["candidate_mappings"]))
    records = fetch_legacy({value for values in names.values() for value in values})
    rows = []
    for name in sorted(names, key=str.casefold):
        legacy = sorted(names[name])
        accepted, rank, target, action, evidence, rationale = candidate(name, legacy, records)
        rows.append({
            "source_name": name,
            "accepted_name": accepted,
            "rank": rank,
            "legacy_ncbi_taxon_id": ";".join(legacy),
            "proposed_ncbi_taxon_id": target,
            "decision_action": action,
            "status": "proposed-for-review",
            "reviewer": "",
            "review_date": "",
            "evidence": evidence,
            "rationale": rationale,
        })
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Built final taxon review: {len(rows)} source names; zero automatic approvals")


if __name__ == "__main__":
    main()
