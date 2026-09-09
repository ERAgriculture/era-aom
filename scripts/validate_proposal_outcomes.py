#!/usr/bin/env python3
"""Validate governed proposal outcomes."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
from pathlib import Path
from urllib.parse import urlparse


FIELDS = [
    "outcome_id",
    "issue_number",
    "issue_url",
    "proposal_type",
    "domain",
    "decision",
    "workflow_status",
    "decision_date",
    "reviewer",
    "affected_concept_ids",
    "evidence_refs",
    "rationale",
    "cohort_id",
    "implementation_pr",
    "release_tag",
]
PROPOSAL_TYPES = {"new_concept", "correction", "mapping", "bulk"}
DOMAINS = {"core", "crop", "livestock", "cross-module"}
DECISIONS = {"accepted", "rejected"}
WORKFLOW_STATUSES = {"accepted", "rejected", "implemented", "released"}
OUTCOME_PATTERN = re.compile(r"PROP-\d{6}")
CONCEPT_PATTERN = re.compile(r"AOM_\d{6}")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == FIELDS, "Proposal outcome columns/order differ from contract"
        return list(reader)


def is_github_pull_url(value: str) -> bool:
    parsed = urlparse(value)
    return (
        parsed.scheme == "https"
        and parsed.netloc == "github.com"
        and bool(re.fullmatch(r"/[^/]+/[^/]+/pull/\d+", parsed.path))
    )


def validate_rows(rows: list[dict[str, str]], repository: str) -> None:
    outcome_ids: set[str] = set()
    issue_numbers: set[int] = set()
    for line_number, row in enumerate(rows, 2):
        outcome_id = row["outcome_id"].strip()
        assert OUTCOME_PATTERN.fullmatch(outcome_id), f"line {line_number}: invalid outcome_id"
        assert outcome_id not in outcome_ids, f"line {line_number}: duplicate outcome_id"
        outcome_ids.add(outcome_id)

        assert row["issue_number"].isdigit(), f"line {line_number}: invalid issue_number"
        issue_number = int(row["issue_number"])
        assert issue_number > 0, f"line {line_number}: issue_number must be positive"
        assert issue_number not in issue_numbers, f"line {line_number}: duplicate issue_number"
        issue_numbers.add(issue_number)
        expected_issue_url = f"https://github.com/{repository}/issues/{issue_number}"
        assert row["issue_url"] == expected_issue_url, f"line {line_number}: issue_url mismatch"

        proposal_type = row["proposal_type"]
        domain = row["domain"]
        decision = row["decision"]
        workflow_status = row["workflow_status"]
        assert proposal_type in PROPOSAL_TYPES, f"line {line_number}: invalid proposal_type"
        assert domain in DOMAINS, f"line {line_number}: invalid domain"
        assert decision in DECISIONS, f"line {line_number}: invalid decision"
        assert workflow_status in WORKFLOW_STATUSES, f"line {line_number}: invalid workflow_status"
        if decision == "rejected":
            assert workflow_status == "rejected", f"line {line_number}: rejected decision/status mismatch"
        else:
            assert workflow_status in {"accepted", "implemented", "released"}, (
                f"line {line_number}: accepted decision/status mismatch"
            )

        try:
            dt.date.fromisoformat(row["decision_date"])
        except ValueError as error:
            raise AssertionError(f"line {line_number}: invalid decision_date") from error
        assert row["reviewer"].strip(), f"line {line_number}: reviewer required"
        assert row["evidence_refs"].strip(), f"line {line_number}: evidence_refs required"
        assert row["rationale"].strip(), f"line {line_number}: rationale required"

        concept_ids = [value.strip() for value in row["affected_concept_ids"].split(";") if value.strip()]
        assert len(concept_ids) == len(set(concept_ids)), f"line {line_number}: duplicate affected concept"
        assert all(CONCEPT_PATTERN.fullmatch(value) for value in concept_ids), (
            f"line {line_number}: invalid affected_concept_ids"
        )
        if proposal_type != "new_concept" or workflow_status in {"implemented", "released"}:
            assert concept_ids, f"line {line_number}: affected_concept_ids required"

        if workflow_status in {"implemented", "released"}:
            assert row["cohort_id"].strip(), f"line {line_number}: cohort_id required"
            assert is_github_pull_url(row["implementation_pr"]), (
                f"line {line_number}: implementation_pr must be a GitHub pull URL"
            )
        if workflow_status == "released":
            assert row["release_tag"].strip(), f"line {line_number}: release_tag required"
        else:
            assert not row["release_tag"].strip(), f"line {line_number}: release_tag only allowed when released"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--repository", default="ERAgriculture/era-aom")
    args = parser.parse_args()
    rows = read_rows(args.csv_file)
    validate_rows(rows, args.repository)
    print(f"Validated {len(rows)} governed proposal outcomes from {args.csv_file}.")


if __name__ == "__main__":
    main()
