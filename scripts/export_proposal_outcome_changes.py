#!/usr/bin/env python3
"""Export changed proposal outcomes for GitHub issue synchronization."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import subprocess
from pathlib import Path

from validate_proposal_outcomes import read_rows, validate_rows


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data/governance/proposal_outcomes.csv"
COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")


def rows_by_issue(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["issue_number"]: row for row in rows}


def read_rows_at_commit(commit: str) -> list[dict[str, str]]:
    if not COMMIT_PATTERN.fullmatch(commit) or set(commit) == {"0"}:
        return []
    relative_path = REGISTER.relative_to(ROOT).as_posix()
    result = subprocess.run(
        ["git", "show", f"{commit}:{relative_path}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    reader = csv.DictReader(io.StringIO(result.stdout))
    return list(reader)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--changed-from", default="")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repository", default="ERAgriculture/era-aom")
    args = parser.parse_args()

    current_rows = read_rows(REGISTER)
    validate_rows(current_rows, args.repository)
    previous_rows = read_rows_at_commit(args.changed_from)
    previous_by_issue = rows_by_issue(previous_rows)
    current_by_issue = rows_by_issue(current_rows)
    deleted_issues = sorted(set(previous_by_issue) - set(current_by_issue))
    assert not deleted_issues, f"Proposal outcomes cannot be deleted: {', '.join(deleted_issues)}"

    changed = []
    for line_number, row in enumerate(current_rows, 2):
        if previous_by_issue.get(row["issue_number"]) != row:
            changed.append({"register_line": line_number, **row})
    args.output.write_text(json.dumps(changed, indent=2) + "\n", encoding="utf-8")
    print(f"Exported {len(changed)} changed proposal outcomes to {args.output}.")


if __name__ == "__main__":
    main()
