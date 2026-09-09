#!/usr/bin/env python3
"""Synchronize GitHub labels and proposal project configuration."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LABELS_PATH = ROOT / "config/github-labels.json"
SYSTEM_PATH = ROOT / "config/proposal-review-system.json"


def run_gh(arguments: list[str]) -> str:
    result = subprocess.run(
        ["gh", *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(message)
    return result.stdout


def sync_labels(repository: str, labels: list[dict[str, str]]) -> None:
    for label in labels:
        run_gh([
            "label",
            "create",
            label["name"],
            "--repo",
            repository,
            "--color",
            label["color"],
            "--description",
            label["description"],
            "--force",
        ])
    print(f"Synchronized {len(labels)} labels in {repository}.")


def ensure_project(repository: str, system: dict[str, object]) -> None:
    project = system["project"]
    owner = project["owner"]
    title = project["title"]
    try:
        listing = json.loads(run_gh(["project", "list", "--owner", owner, "--limit", "100", "--format", "json"]))
    except RuntimeError as error:
        raise RuntimeError(
            f"Project access unavailable. Run `gh auth refresh -s project,read:project`, then retry. {error}"
        ) from error
    matches = [item for item in listing.get("projects", []) if item.get("title") == title]
    if matches:
        selected = matches[0]
    else:
        selected = json.loads(run_gh(["project", "create", "--owner", owner, "--title", title, "--format", "json"]))
    project_number = str(selected["number"])
    project_url = selected["url"]
    run_gh([
        "project",
        "edit",
        project_number,
        "--owner",
        owner,
        "--visibility",
        project["visibility"],
        "--description",
        project["description"],
        "--readme",
        project["readme"],
    ])
    fields = json.loads(run_gh(["project", "field-list", project_number, "--owner", owner, "--format", "json"]))
    stage_fields = [field for field in fields.get("fields", []) if field["name"] == project["stage_field"]]
    if not stage_fields:
        run_gh([
            "project",
            "field-create",
            project_number,
            "--owner",
            owner,
            "--name",
            project["stage_field"],
            "--data-type",
            "SINGLE_SELECT",
            "--single-select-options",
            ",".join(project["stages"]),
        ])
    else:
        stage_field = stage_fields[0]
        option_names = [option["name"] for option in stage_field.get("options", [])]
        if stage_field.get("type") != "ProjectV2SingleSelectField" or option_names != project["stages"]:
            raise RuntimeError(
                f"Project field {project['stage_field']} differs from configured single-select stages: {option_names}"
            )
    run_gh(["variable", "set", project["url_variable"], "--repo", repository, "--body", project_url])
    secrets = {line.split("\t", 1)[0] for line in run_gh(["secret", "list", "--repo", repository]).splitlines() if line}
    print(f"Configured project {project_url} and repository variable {project['url_variable']}.")
    if project["token_secret"] not in secrets:
        print(
            f"Missing repository secret {project['token_secret']}. Add a token with project write access "
            "before proposal auto-add can run."
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply-labels", action="store_true")
    parser.add_argument("--apply-project", action="store_true")
    args = parser.parse_args()
    labels = json.loads(LABELS_PATH.read_text(encoding="utf-8"))
    system = json.loads(SYSTEM_PATH.read_text(encoding="utf-8"))
    repository = system["repository"]
    if args.apply_labels:
        sync_labels(repository, labels)
    if args.apply_project:
        try:
            ensure_project(repository, system)
        except RuntimeError as error:
            parser.exit(2, f"error: {error}\n")
    if not args.apply_labels and not args.apply_project:
        print(
            f"Configuration valid: {len(labels)} labels, {len(system['domains'])} routes, "
            f"{len(system['project']['stages'])} project stages."
        )


if __name__ == "__main__":
    main()
