#!/usr/bin/env python3
"""Build recommendation-only ADR 0052 product-contract review."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/data-model-v7"
SNAPSHOT = REVIEW / "source_snapshot.json"
DIFFS = ROOT / "review/data-model-v1/consumer_contract_diffs.csv"
DIFFS_SHA256 = "09638c0baf86e4231c2f8778c298df9bdf9bb45b075d210fd858fa2a36cc014f"
COMPARISON = ROOT / "review/data-model-v1/consumer_contract_comparison.csv"
COMPARISON_SHA256 = "78059447ba5c4cdea497b6012f66fd5187ed3f22b02fe9e7bc43f82779c8203f"
EXPECTED_SOURCE_HASHES = {
    "agronomy_schema": "a06d2b18da35d5a56004e1abf918df42be1b9d0f0cffe8b4aec53a878794507f",
    "livestock_schema": "6979df8efd8c673e41a75cf0ab847d28cda1ab81b4b19eba3cd7a0d78e525507",
    "package_data": "00318de7341cad728e991ab0bf536fe68aeaeff4f732b7fde0b06e5f68e92091",
    "package_dictionary": "85ff22c5c595888899b0c3c5cbfaab3fe1b377dfedcb52fdb0dd44d322aaffd9",
}
EXPLICIT_ALIASES = {
    "Analysis.Function": "Analysis.Function ",
    "ISO.3166.1.alpha.3": "ISO.3166-1.alpha-3",
}
NO_DOCUMENTATION_CANDIDATE = {
    "Mean.Error.Type",
    "MeanC.Error",
    "MeanT.Error",
    "Mulch.Code",
    "Partial.Outcome.Code",
    "Rep.Animals",
    "Tree.Feed",
}
PUBLISHED_ONLY_FIELDS = {"C14", "T14"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(name: str, value: object) -> None:
    (REVIEW / name).write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def json_sha256(value: object) -> str:
    payload = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def dictionary_candidate(
    field_name: str, dictionary_rows: dict[str, dict[str, object]]
) -> tuple[str, dict[str, object] | None]:
    if field_name in dictionary_rows:
        return "exact-name", dictionary_rows[field_name]
    if field_name in EXPLICIT_ALIASES:
        return "explicit-alias", dictionary_rows[EXPLICIT_ALIASES[field_name]]
    if re.fullmatch(r"C(?:[1-9]|1[0-4])", field_name):
        return "pattern-alias", dictionary_rows["C1:Cn"]
    if re.fullmatch(r"T(?:[1-9]|1[0-4])", field_name):
        return "pattern-alias", dictionary_rows["T1:Tn"]
    return "none", None


def field_disposition(field_name: str, candidate_kind: str) -> str:
    if field_name in PUBLISHED_ONLY_FIELDS:
        return "hold-published-only-release-lineage"
    if candidate_kind == "exact-name":
        return "hold-review-exact-dictionary-candidate"
    if candidate_kind == "explicit-alias":
        return "hold-review-explicit-alias-candidate"
    if candidate_kind == "pattern-alias":
        return "hold-review-pattern-expansion-candidate"
    return "hold-author-missing-product-documentation"


def difference_disposition(row: dict[str, str]) -> str:
    comparison = row["comparison"]
    side = row["side"]
    identifier = row["identifier"]
    if comparison == "published-agronomy-schema-vs-eragri-data":
        if side == "package-only":
            return "hold-package-only-release-provenance"
        return "hold-published-only-release-provenance"
    if side == "data-only":
        if identifier in EXPLICIT_ALIASES:
            return "hold-review-explicit-alias-candidate"
        if re.fullmatch(r"[CT](?:[1-9]|1[0-3])", identifier):
            return "hold-review-pattern-expansion-candidate"
        return "hold-undocumented-package-field"
    if identifier in EXPLICIT_ALIASES.values():
        return "hold-explicit-alias-definition-review"
    if identifier in {"C1:Cn", "T1:Tn"}:
        return "hold-pattern-alias-definition-review"
    return "hold-dictionary-only-retirement-review"


def load_sources() -> tuple[dict[str, object], list[dict[str, str]]]:
    assert sha256(DIFFS) == DIFFS_SHA256
    assert sha256(COMPARISON) == COMPARISON_SHA256
    snapshot = read_json(SNAPSHOT)
    assert isinstance(snapshot, dict)
    sources = snapshot["sources"]
    for source_name, expected_hash in EXPECTED_SOURCE_HASHES.items():
        assert sources[source_name]["sha256"] == expected_hash
    with DIFFS.open(encoding="utf-8", newline="") as handle:
        differences = list(csv.DictReader(handle))
    return snapshot, differences


def build_field_recommendations(snapshot: dict[str, object]) -> list[dict[str, object]]:
    sources = snapshot["sources"]
    agronomy_columns = sources["agronomy_schema"]["columns"]
    livestock_columns = sources["livestock_schema"]["columns"]
    package_columns = sources["package_data"]["columns"]
    dictionary_rows = {
        row["field_name"]: row for row in sources["package_dictionary"]["rows"]
    }
    livestock_by_name = {row["name"]: row for row in livestock_columns}
    package_by_name = {row["name"]: row for row in package_columns}
    recommendations = []
    for agronomy in agronomy_columns:
        field_name = agronomy["name"]
        livestock = livestock_by_name[field_name]
        candidate_kind, candidate = dictionary_candidate(field_name, dictionary_rows)
        disposition = field_disposition(field_name, candidate_kind)
        recommendations.append(
            {
                "field_id": f"PF-{int(agronomy['position']):03d}",
                "field_name": field_name,
                "agronomy_position": int(agronomy["position"]),
                "livestock_position": int(livestock["position"]),
                "same_schema_position": agronomy["position"] == livestock["position"],
                "agronomy_physical_type": agronomy["physical_type"],
                "livestock_physical_type": livestock["physical_type"],
                "physical_type_match": agronomy["physical_type"]
                == livestock["physical_type"],
                "agronomy_schema_description": agronomy["description"],
                "livestock_schema_description": livestock["description"],
                "package_data_present": field_name in package_by_name,
                "package_data_position": (
                    int(package_by_name[field_name]["position"])
                    if field_name in package_by_name
                    else None
                ),
                "dictionary_candidate_kind": candidate_kind,
                "dictionary_candidate_row": int(candidate["row"]) if candidate else None,
                "dictionary_candidate_name": candidate["field_name"] if candidate else "",
                "dictionary_candidate_data_type": candidate["data_type"] if candidate else "",
                "dictionary_candidate_description": candidate["description"] if candidate else "",
                "dictionary_candidate_example": candidate["example"] if candidate else "",
                "recommended_disposition": disposition,
                "required_review": (
                    "Establish release lineage and compatibility before reviewing the pattern dictionary candidate."
                    if field_name in PUBLISHED_ONLY_FIELDS
                    else "Review meaning, logical type, derivation, units or basis, values, applicability, and lifecycle; candidate text is not authority."
                ),
                "recommendation_status": "proposed",
                "approved_description": "",
                "approved_logical_type": "",
                "approved_derivation": "",
                "approved_unit_or_basis": "",
                "approved_controlled_values": "",
                "human_decision": "",
                "reviewer": "",
                "review_date": "",
                "decision_note": "",
            }
        )
    return recommendations


def build_difference_recommendations(
    differences: list[dict[str, str]],
) -> list[dict[str, object]]:
    recommendations = []
    for index, row in enumerate(differences, start=1):
        recommendations.append(
            {
                "difference_id": f"CD-{index:03d}",
                "comparison": row["comparison"],
                "side": row["side"],
                "identifier": row["identifier"],
                "prior_recommendation": row["recommended_disposition"],
                "recommended_disposition": difference_disposition(row),
                "required_evidence": "Pinned producer release, package snapshot, dictionary identity, intended field meaning, and compatibility or retirement decision.",
                "recommendation_status": "proposed",
                "human_decision": "",
                "reviewer": "",
                "review_date": "",
                "decision_note": "",
            }
        )
    return recommendations


GUIDED_DECISIONS = [
    {
        "review_id": "PC-01",
        "title": "Separate extraction and product contracts",
        "recommendation": "Govern extraction schemas separately from released analytical product schemas.",
        "rationale": "Different derivations, release histories, and consumer obligations make one contract ambiguous.",
        "conditions_or_holds": "No extraction or product schema changes until producer ownership and compatibility profiles are approved.",
    },
    {
        "review_id": "PC-02",
        "title": "Share logical set, preserve product order",
        "recommendation": "Use one reviewed 138-field logical set with separate agronomy and livestock ordered product profiles.",
        "rationale": "Current products share names and physical types but differ at 33 field positions.",
        "conditions_or_holds": "Do not call current schema files identical or reorder either product without migration evidence.",
    },
    {
        "review_id": "PC-03",
        "title": "Complete field documentation",
        "recommendation": "Require reviewed documentation or explicit deferral for every public product field.",
        "rationale": "Both published 138-column schemas have blank descriptions.",
        "conditions_or_holds": "Each field remains held until description, logical type, derivation, unit or basis, values, applicability, and lifecycle are reviewed.",
    },
    {
        "review_id": "PC-04",
        "title": "Treat dictionary text as candidate evidence",
        "recommendation": "Review exact-name package dictionary rows as candidates, not authoritative mappings.",
        "rationale": "Package dictionary documents 106 names but differs from public schemas and package data.",
        "conditions_or_holds": "No description or datatype may be copied into product contracts without field-level review.",
    },
    {
        "review_id": "PC-05",
        "title": "Review explicit alias candidates",
        "recommendation": "Review trailing-space and punctuation variants through explicit governed aliases.",
        "rationale": "Analysis.Function and ISO.3166.1.alpha.3 each have one plausible dictionary variant.",
        "conditions_or_holds": "No automatic trim, punctuation normalization, rename, or identity assertion.",
    },
    {
        "review_id": "PC-06",
        "title": "Expand pattern fields explicitly",
        "recommendation": "Replace C1:Cn and T1:Tn patterns with explicit governed field aliases only after scope review.",
        "rationale": "Pattern dictionary rows cannot identify each released field or its derivation by themselves.",
        "conditions_or_holds": "C1-C14 and T1-T14 remain separately reviewable; no generated aliases are approved here.",
    },
    {
        "review_id": "PC-07",
        "title": "Pin package compatibility",
        "recommendation": "Publish release provenance and compatibility profile for each package data snapshot and dictionary.",
        "rationale": "Current package data has 137 columns and does not match current public schema exactly.",
        "conditions_or_holds": "No package snapshot may be treated as current release without a pinned producer release and checksum.",
    },
    {
        "review_id": "PC-08",
        "title": "Hold C14 and T14 lineage",
        "recommendation": "Retain C14 and T14 as published-only holds pending release and derivation lineage.",
        "rationale": "Both fields occur in published schemas but not package data.",
        "conditions_or_holds": "No removal, package addition, or pattern mapping is approved.",
    },
    {
        "review_id": "PC-09",
        "title": "Hold B.Code provenance",
        "recommendation": "Retain B.Code as package-only hold pending provenance and compatibility or retirement decision.",
        "rationale": "B.Code occurs in package data but not published schemas or exact dictionary names.",
        "conditions_or_holds": "No schema addition or package removal is approved.",
    },
    {
        "review_id": "PC-10",
        "title": "Review Irrig.Meth.T retirement",
        "recommendation": "Review Irrig.Meth.T as dictionary-only legacy or retirement case.",
        "rationale": "It occurs in dictionary but not package data or published schemas.",
        "conditions_or_holds": "No alias target or retirement is inferred from absence.",
    },
    {
        "review_id": "PC-11",
        "title": "Use complete product field contract",
        "recommendation": "Record physical and logical type, nullability, derivation, unit or basis, controlled values, applicability, lifecycle, and evidence per field.",
        "rationale": "Names, physical types, and descriptions alone cannot support validation or interpretation.",
        "conditions_or_holds": "Unknown properties remain explicit reviewed deferrals rather than guessed values.",
    },
    {
        "review_id": "PC-12",
        "title": "Close through consumer parity",
        "recommendation": "Require schema, data, package, dictionary, and documentation compatibility report before closure.",
        "rationale": "Forty-four current producer-consumer differences cross repository boundaries.",
        "conditions_or_holds": "No release, migration, source edit, package edit, documentation edit, or issue closure is approved here.",
    },
]


AUTHORITIES = [
    {
        "authority": "W3C CSV on the Web",
        "url": "https://www.w3.org/TR/tabular-metadata/",
        "supports": "Column metadata, datatypes, titles, descriptions, constraints, keys, foreign keys, and table annotations.",
        "limitation": "Does not supply ERA field meaning, derivation, units, source identity, or release compatibility decisions.",
    },
    {
        "authority": "Frictionless Table Schema v1",
        "url": "https://specs.frictionlessdata.io/table-schema/",
        "supports": "Ordered field descriptors with names, types, formats, examples, descriptions, constraints, primary keys, and foreign keys.",
        "limitation": "Portable descriptor structure does not make current package dictionary rows authoritative or equivalent to published products.",
    },
    {
        "authority": "JSON Schema 2020-12 validation vocabulary",
        "url": "https://json-schema.org/draft/2020-12/json-schema-validation",
        "supports": "Validation plus title, description, examples, read/write status, and deprecation annotations.",
        "limitation": "Annotation keywords do not define ERA derivation lineage, release provenance, or field identity across repositories.",
    },
    {
        "authority": "W3C PROV-O",
        "url": "https://www.w3.org/TR/prov-o/",
        "supports": "Entities, activities, agents, derivation, generation, and attribution for product-field and release lineage.",
        "limitation": "Does not prescribe ERA physical schemas, logical field types, or consumer compatibility policy.",
    },
    {
        "authority": "W3C DCAT 3",
        "url": "https://www.w3.org/TR/vocab-dcat-3/",
        "supports": "Dataset, distribution, version, conformance, checksum, and provenance-oriented catalog metadata.",
        "limitation": "Does not resolve field-level meaning or package-to-release differences.",
    },
    {
        "authority": "ERA ADR 0052",
        "url": "../../docs/decisions/0052-data-model-registry-and-shared-core-contract.md",
        "supports": "ERA ownership, product-contract boundary, field completeness, compatibility, release, and closure gates.",
        "limitation": "Architecture decision still requires human row-level product-field and consumer-difference review.",
    },
]


def build_evidence(
    snapshot: dict[str, object],
    field_rows: list[dict[str, object]],
    difference_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    snapshot_sha256 = sha256(SNAPSHOT)
    field_rows_sha256 = json_sha256(field_rows)
    difference_rows_sha256 = json_sha256(difference_rows)
    authorities_sha256 = json_sha256(AUTHORITIES)
    return [
        {
            "evidence_id": "PC-E01",
            "claim": "Agronomy and livestock schemas each contain 138 fields with identical name sets and physical types.",
            "source": "source_snapshot.json",
            "source_sha256": snapshot_sha256,
            "supports": "Shared logical-field-set recommendation.",
            "claim_boundary": "Does not prove product meaning, field order, derivation, values, or release equivalence.",
        },
        {
            "evidence_id": "PC-E02",
            "claim": "Thirty-three field positions differ between published agronomy and livestock schemas.",
            "source": "product_field_recommendations.json",
            "source_sha256": field_rows_sha256,
            "supports": "Separate ordered product profiles.",
            "claim_boundary": "Position difference alone does not prove either order is wrong.",
        },
        {
            "evidence_id": "PC-E03",
            "claim": "All 276 published schema description cells are blank.",
            "source": "source_snapshot.json",
            "source_sha256": snapshot_sha256,
            "supports": "Complete documentation or explicit deferral gate.",
            "claim_boundary": "Blank schema descriptions do not prove no external documentation exists.",
        },
        {
            "evidence_id": "PC-E04",
            "claim": "Package data contains 137 fields; package dictionary contains 106 rows.",
            "source": "source_snapshot.json",
            "source_sha256": snapshot_sha256,
            "supports": "Release-pinned package compatibility and candidate-only dictionary use.",
            "claim_boundary": "Unversioned package objects do not identify intended public release compatibility.",
        },
        {
            "evidence_id": "PC-E05",
            "claim": "Product-field review yields 101 exact-name, two explicit-alias, 26 pattern, seven missing-documentation, and two published-only holds.",
            "source": "product_field_recommendations.json",
            "source_sha256": field_rows_sha256,
            "supports": "Complete 138-field guided review cohort.",
            "claim_boundary": "Candidate classification is lexical and release evidence, not approved semantic identity.",
        },
        {
            "evidence_id": "PC-E06",
            "claim": "Forty-four producer-consumer differences remain across public schema, package data, and package dictionary.",
            "source": "../data-model-v1/consumer_contract_diffs.csv",
            "source_sha256": DIFFS_SHA256,
            "supports": "Complete compatibility disposition cohort.",
            "claim_boundary": "Differences do not authorize automatic rename, addition, removal, or retirement.",
        },
        {
            "evidence_id": "PC-E07",
            "claim": "All 44 differences have one proposed evidence-hold disposition.",
            "source": "consumer_difference_recommendations.json",
            "source_sha256": difference_rows_sha256,
            "supports": "Human review can accept or amend complete difference cohort.",
            "claim_boundary": "No consumer migration or source change is approved.",
        },
        {
            "evidence_id": "PC-E08",
            "claim": "CSVW and Frictionless both support ordered, documented tabular field contracts.",
            "source": "authority_comparison.json",
            "source_sha256": authorities_sha256,
            "supports": "Portable product contract structure and field-order preservation.",
            "claim_boundary": "Neither standard supplies ERA-specific field content.",
        },
        {
            "evidence_id": "PC-E09",
            "claim": "PROV-O and DCAT 3 support derivation, release, distribution, version, conformance, and provenance metadata.",
            "source": "authority_comparison.json",
            "source_sha256": authorities_sha256,
            "supports": "Release lineage and compatibility profile design.",
            "claim_boundary": "Neither authority resolves current ERA field differences.",
        },
        {
            "evidence_id": "PC-E10",
            "claim": "JSON Schema annotations improve documentation but remain separate from validation semantics.",
            "source": "authority_comparison.json",
            "source_sha256": authorities_sha256,
            "supports": "Descriptions and lifecycle annotations in JSON product schemas.",
            "claim_boundary": "Annotations alone do not establish field identity or release provenance.",
        },
    ]


def write_markdown(
    field_rows: list[dict[str, object]], difference_rows: list[dict[str, object]]
) -> None:
    field_counts = Counter(row["recommended_disposition"] for row in field_rows)
    difference_counts = Counter(row["recommended_disposition"] for row in difference_rows)
    readme = """# ADR 0052 product-contract review

Recommendation-only checkpoint for published agronomy and livestock schemas,
the `eragri` package data snapshot, and package dictionary. It preserves all
138 product fields and all 44 known consumer differences for human review.

## Boundaries

- Source repositories were read only at pinned clean commits.
- Package dictionary rows are candidate evidence, never automatic mappings.
- No field description, logical type, derivation, unit, basis, values, alias,
  source correction, schema change, package change, release, or migration is
  approved.
- Unknown cases remain explicit holds.
- No spreadsheet artifact was authored; approved spreadsheet runtime remained
  unavailable, and the existing source CSV was read only and hash pinned.

## Files

- `METHOD.md` — source, classification, and decision method.
- `GUIDED_PRODUCT_CONTRACT_RECOMMENDATIONS.md` — human review sequence.
- `source_snapshot.json` — hash-pinned schema and package evidence.
- `product_field_recommendations.json` — complete 138-field cohort.
- `consumer_difference_recommendations.json` — complete 44-difference cohort.
- `guided_decision_recommendations.json` — twelve proposed policy decisions.
- `authority_comparison.json` — authority support and limitations.
- `evidence_register.json` — claim-level evidence boundaries.
- `disposition_summary.json` — machine-readable counts and non-actions.

## Human checkpoint

All recommendations have `human decision pending`. Review `PC-01` through
`PC-12`, then accept or amend exact 138-field and 44-difference artifacts.
"""
    method = f"""# ADR 0052 product-contract review method

## Inputs

- Agronomy schema SHA-256: `{EXPECTED_SOURCE_HASHES['agronomy_schema']}`
- Livestock schema SHA-256: `{EXPECTED_SOURCE_HASHES['livestock_schema']}`
- Package data SHA-256: `{EXPECTED_SOURCE_HASHES['package_data']}`
- Package dictionary SHA-256: `{EXPECTED_SOURCE_HASHES['package_dictionary']}`
- Consumer differences SHA-256: `{DIFFS_SHA256}`
- Consumer comparison SHA-256: `{COMPARISON_SHA256}`

Source snapshot was extracted from clean, pinned `era-data` and `eragri`
commits with:

```sh
Rscript scripts/extract_adr0052_product_contract_sources.R \\
  /path/to/era-data /path/to/eragri review/data-model-v7/source_snapshot.json
```

CI uses committed snapshot, not mutable sibling repositories.

## Method

1. Preserve both ordered 138-field schema lists and physical types exactly.
2. Compare field-name sets, physical types, positions, and blank descriptions.
3. Compare package data and dictionary using exact names only.
4. Record two explicit lexical alias candidates without asserting identity.
5. Record `C1:Cn` and `T1:Tn` as pattern candidates without expansion approval.
6. Override `C14` and `T14` as published-only release-lineage holds.
7. Preserve every v1 consumer difference and classify one evidence hold.
8. Leave all approved content and human-decision fields blank.
9. Validate counts, source hashes, membership, boundaries, and deterministic rebuild.

## Decision rule

No lexical match, position, datatype label, pattern, or absence proves identity,
meaning, derivation, compatibility, or retirement. Human review must resolve
each proposed policy and row. Unsupported cases remain holds.
"""
    guided_lines = [
        "# Guided product-contract recommendations",
        "",
        "Status: **human decision pending**.",
        "",
        "| ID | Recommendation | Conditions / holds |",
        "|---|---|---|",
    ]
    for decision in GUIDED_DECISIONS:
        guided_lines.append(
            f"| `{decision['review_id']}` | {decision['recommendation']} | {decision['conditions_or_holds']} |"
        )
    guided_lines.extend(
        [
            "",
            "## Product-field cohort",
            "",
            f"- Total fields: {len(field_rows)}",
            f"- Dispositions: `{json.dumps(dict(sorted(field_counts.items())), sort_keys=True)}`",
            "- Review artifact: `product_field_recommendations.json`",
            "",
            "## Consumer-difference cohort",
            "",
            f"- Total differences: {len(difference_rows)}",
            f"- Dispositions: `{json.dumps(dict(sorted(difference_counts.items())), sort_keys=True)}`",
            "- Review artifact: `consumer_difference_recommendations.json`",
            "",
        ]
    )
    (REVIEW / "README.md").write_text(readme, encoding="utf-8")
    (REVIEW / "METHOD.md").write_text(method, encoding="utf-8")
    (REVIEW / "GUIDED_PRODUCT_CONTRACT_RECOMMENDATIONS.md").write_text(
        "\n".join(guided_lines), encoding="utf-8"
    )


def main() -> None:
    REVIEW.mkdir(parents=True, exist_ok=True)
    snapshot, differences = load_sources()
    field_rows = build_field_recommendations(snapshot)
    difference_rows = build_difference_recommendations(differences)
    guided = [
        {
            **decision,
            "recommendation_status": "proposed",
            "human_decision": "",
            "reviewer": "",
            "review_date": "",
            "decision_note": "",
        }
        for decision in GUIDED_DECISIONS
    ]
    field_counts = Counter(row["recommended_disposition"] for row in field_rows)
    difference_counts = Counter(
        row["recommended_disposition"] for row in difference_rows
    )
    schema_order_difference_count = sum(
        not row["same_schema_position"] for row in field_rows
    )
    shared_package_fields = [row for row in field_rows if row["package_data_present"]]
    package_order_difference_count = sum(
        first["field_name"] != second["name"]
        for first, second in zip(
            shared_package_fields,
            [
                row
                for row in snapshot["sources"]["package_data"]["columns"]
                if row["name"] in {field["field_name"] for field in shared_package_fields}
            ],
        )
    )
    summary = {
        "status": "recommendation-only",
        "review_date": "2026-09-01",
        "source_snapshot_sha256": sha256(SNAPSHOT),
        "consumer_differences_sha256": DIFFS_SHA256,
        "consumer_comparison_sha256": COMPARISON_SHA256,
        "source_hashes": EXPECTED_SOURCE_HASHES,
        "product_field_count": len(field_rows),
        "shared_schema_name_count": 138,
        "shared_schema_type_match_count": 138,
        "schema_order_difference_count": schema_order_difference_count,
        "blank_published_description_count": 276,
        "package_data_field_count": int(snapshot["sources"]["package_data"]["column_count"]),
        "package_dictionary_row_count": int(snapshot["sources"]["package_dictionary"]["row_count"]),
        "schema_package_shared_field_count": len(shared_package_fields),
        "schema_package_shared_order_difference_count": package_order_difference_count,
        "product_field_disposition_counts": dict(sorted(field_counts.items())),
        "consumer_difference_count": len(difference_rows),
        "consumer_difference_disposition_counts": dict(sorted(difference_counts.items())),
        "guided_decision_count": len(guided),
        "human_decision_recorded": False,
        "approved_field_documentation_created": False,
        "field_identity_mappings_created": False,
        "source_repository_modified": False,
        "source_workbook_modified": False,
        "schema_modified": False,
        "package_modified": False,
        "documentation_consumer_modified": False,
        "release_authorized": False,
        "consumer_migration_authorized": False,
        "spreadsheet_artifact_authored": False,
    }
    write_json("product_field_recommendations.json", field_rows)
    write_json("consumer_difference_recommendations.json", difference_rows)
    write_json("guided_decision_recommendations.json", guided)
    write_json("authority_comparison.json", AUTHORITIES)
    write_json("evidence_register.json", build_evidence(snapshot, field_rows, difference_rows))
    write_json("disposition_summary.json", summary)
    write_markdown(field_rows, difference_rows)
    print(
        f"Built ADR 0052 product-contract review: {len(field_rows)} fields, "
        f"{len(difference_rows)} differences, {len(guided)} decisions"
    )


if __name__ == "__main__":
    main()
