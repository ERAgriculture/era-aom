#!/usr/bin/env python3
"""Validate GitHub proposal intake, review, outcome, and browser contracts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_proposal_outcomes import read_rows, validate_rows  # noqa: E402


labels = json.loads((ROOT / "config/github-labels.json").read_text(encoding="utf-8"))
label_names = [label["name"] for label in labels]
assert len(label_names) == len(set(label_names)) == 13
assert all(len(label["color"]) == 6 for label in labels)
assert {
    "proposal",
    "new-concept",
    "correction",
    "mapping",
    "needs-triage",
    "in-review",
    "accepted",
    "rejected",
    "implemented",
    "released",
    "livestock",
    "crop",
    "core",
} == set(label_names)

system = json.loads((ROOT / "config/proposal-review-system.json").read_text(encoding="utf-8"))
assert system["schema_version"] == 1
assert system["repository"] == "ERAgriculture/era-aom"
assert system["pilot_approver"]["github_login"] == "peetmate"
assert system["permanent_reviewer_status"] == "unappointed"
assert system["status_labels"] == [
    "needs-triage",
    "in-review",
    "accepted",
    "rejected",
    "implemented",
    "released",
]
assert system["stage_by_status"] == {
    "needs-triage": "Completeness / duplicate check",
    "in-review": "Domain review",
    "accepted": "Decision",
    "rejected": "Decision",
    "implemented": "Cohort PR",
    "released": "Release",
}
assert set(system["stage_by_status"].values()) <= set(system["project"]["stages"])
assert set(system["status_labels"]) <= set(label_names)
assert system["project"]["stages"] == [
    "Proposal",
    "Completeness / duplicate check",
    "Domain review",
    "Decision",
    "Cohort PR",
    "Release",
]
assert system["project"]["visibility"] == "PUBLIC"
assert "governance" in system["project"]["readme"].lower()
assert set(system["domains"]) == {
    "aom-core",
    "aom-crop",
    "aom-livestock",
    "cross-module",
    "uncertain",
}
assert system["domains"]["aom-core"]["labels"] == ["core"]
assert system["domains"]["aom-crop"]["labels"] == ["crop"]
assert system["domains"]["aom-livestock"]["labels"] == ["livestock"]
assert system["domains"]["cross-module"]["labels"] == ["crop", "livestock"]
assert all(route["interim_reviewers"] == ["peetmate"] for route in system["domains"].values())

expected_options = ["aom-core", "aom-crop", "aom-livestock", "cross-module", "uncertain"]
form_contracts = {
    "01-new-concept.yml": ("new-concept", "module"),
    "02-correct-concept.yml": ("correction", "domain"),
    "03-mapping.yml": ("mapping", "domain"),
}
for filename, (type_label, domain_field) in form_contracts.items():
    form = yaml.safe_load((ROOT / ".github/ISSUE_TEMPLATE" / filename).read_text(encoding="utf-8"))
    assert set(form["labels"]) == {"proposal", type_label, "needs-triage"}
    assert set(form["labels"]) <= set(label_names)
    fields = {item.get("id"): item for item in form["body"] if item.get("id")}
    assert fields[domain_field]["attributes"]["options"] == expected_options
    assert fields[domain_field]["validations"]["required"] is True

intake_workflow = (ROOT / ".github/workflows/proposal-intake.yml").read_text(encoding="utf-8")
assert "config/proposal-review-system.json" in intake_workflow
assert "actions/add-to-project@244f685bbc3b7adfa8466e08b698b5577571133e" in intake_workflow
assert "vars.PROPOSAL_PROJECT_URL" in intake_workflow
assert "secrets.ADD_TO_PROJECT_PAT" in intake_workflow
assert "aom-proposal-intake" in intake_workflow
assert "scripts/sync_proposal_project_stage.js" in intake_workflow

outcome_workflow = (ROOT / ".github/workflows/sync-proposal-outcomes.yml").read_text(encoding="utf-8")
assert "scripts/validate_proposal_outcomes.py" in outcome_workflow
assert "scripts/export_proposal_outcome_changes.py" in outcome_workflow
assert "aom-proposal-outcome:" in outcome_workflow
assert "['rejected', 'released']" in outcome_workflow
assert "scripts/sync_proposal_project_stage.js" in outcome_workflow

project_sync = (ROOT / "scripts/sync_proposal_project_stage.js").read_text(encoding="utf-8")
assert "updateProjectV2ItemFieldValue" in project_sync
assert "addProjectV2ItemById" in project_sync
assert "ProjectV2SingleSelectField" in project_sync

register_rows = read_rows(ROOT / "data/governance/proposal_outcomes.csv")
validate_rows(register_rows, system["repository"])
assert register_rows == []
sample_rows = [
    {
        "outcome_id": "PROP-000001",
        "issue_number": "120",
        "issue_url": "https://github.com/ERAgriculture/era-aom/issues/120",
        "proposal_type": "correction",
        "domain": "livestock",
        "decision": "accepted",
        "workflow_status": "implemented",
        "decision_date": "2026-09-07",
        "reviewer": "Pete Steward",
        "affected_concept_ids": "AOM_001938",
        "evidence_refs": "https://example.org/evidence",
        "rationale": "Reviewed correction accepted.",
        "cohort_id": "livestock-correction-v1",
        "implementation_pr": "https://github.com/ERAgriculture/era-aom/pull/120",
        "release_tag": "",
    },
    {
        "outcome_id": "PROP-000002",
        "issue_number": "121",
        "issue_url": "https://github.com/ERAgriculture/era-aom/issues/121",
        "proposal_type": "new_concept",
        "domain": "core",
        "decision": "rejected",
        "workflow_status": "rejected",
        "decision_date": "2026-09-07",
        "reviewer": "Pete Steward",
        "affected_concept_ids": "",
        "evidence_refs": "https://example.org/evidence",
        "rationale": "Existing concept already covers requested meaning.",
        "cohort_id": "",
        "implementation_pr": "",
        "release_tag": "",
    },
]
validate_rows(sample_rows, system["repository"])

template = (
    ROOT / "deploy/skosmos/custom-templates/main-content-bottom/10-request-change.twig"
).read_text(encoding="utf-8")
assert "pageType == 'concept'" in template
assert 'id="request-concept-change"' in template
assert "template=02-correct-concept.yml" in template
assert "&amp;concept=" in template
for compose_path in [ROOT / "deploy/local/compose.yaml", ROOT / "deploy/production/compose.yaml"]:
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    mounts = compose["services"]["skosmos"]["volumes"]
    assert any("custom-templates/main-content-bottom" in mount for mount in mounts)

pull_template = ROOT / ".github/PULL_REQUEST_TEMPLATE/proposal-cohort.md"
assert pull_template.is_file()
method = (ROOT / "docs/methods/proposal-review-and-release-governance.md").read_text(encoding="utf-8")
assert "## Non-GitHub intake boundary" in method
assert "ADD_TO_PROJECT_PAT" in method

print("Validated proposal intake, routing, outcome, cohort, and browser contracts.")
