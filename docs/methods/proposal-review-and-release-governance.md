# Proposal review and release governance

## Purpose

Provide one traceable route from external request through triage, human semantic
decision, cohort implementation, and versioned release. GitHub issue is intake
and discussion record. Governed repository register is decision record. Neither
form submission nor automation authorizes semantic change.

Tracking: [era-aom issue 117](https://github.com/ERAgriculture/era-aom/issues/117).
Identity and mapping evidence remain governed by ADR 0028, ADR 0030, ADR 0033,
and repository `AGENTS.md`.

## Intake contract

Use one structured issue form:

- new concept;
- correction to existing concept;
- external mapping.

Every proposal supplies domain or module, evidence, intended change, and
contributor affiliation. Forms apply `proposal`, proposal-type, and
`needs-triage` labels. `proposal-intake.yml` reads issue-form headings, adds
domain labels, assigns configured reviewer, posts next-gate guidance, adds issue
to GitHub Project, and synchronizes its `Review stage` field when project
variable and token exist.

AI may help prepare proposal. Human reviewer owns decision. Form content cannot
mint IDs, assert identity, change hierarchy, or edit release data.

## Reviewer roster

Machine-readable routing lives in `config/proposal-review-system.json`.

- Permanent core reviewer: unappointed.
- Permanent crop reviewer: unappointed.
- Permanent livestock reviewer: unappointed.
- Interim reviewer and pilot approver: Pete Steward (`peetmate`).
- Cross-module proposal requires crop and livestock review; current interim
  route assigns Pete Steward until permanent reviewers are appointed.

Roster change requires reviewed pull request. Workflow uses permanent reviewer
list when non-empty; otherwise uses interim list. Assignment means routing, not
approval.

## Workflow states

| Label | Required meaning | Project stage |
|---|---|---|
| `needs-triage` | Completeness, duplicate, identity-collision, and scope checks pending | Completeness / duplicate check |
| `in-review` | Evidence and semantic review active | Domain review |
| `accepted` | Human decision recorded; implementation not yet complete | Decision |
| `rejected` | Human rejection and rationale recorded; issue closes | Decision |
| `implemented` | Accepted proposal included in merged cohort PR | Cohort PR |
| `released` | Cohort included in versioned release; issue closes | Release |

Only one status label may apply. Automation keeps Project `Review stage` field
aligned with full path:
Proposal, Completeness / duplicate check, Domain review, Decision, Cohort PR,
Release. Project tracks work; outcome register governs decision.

## Triage and decision

1. Confirm required fields and usable evidence.
2. Search preferred, alternative, hidden, and deprecated labels plus external
   mappings before any ID allocation.
3. Identify duplicates, affected descendants, modules, consumers, and release
   boundary.
4. Route cross-module claims to every affected reviewer.
5. Record explicit accept or reject decision, reviewer, date, evidence, and
   rationale in `data/governance/proposal_outcomes.csv` through reviewed PR.
6. Keep uncertainty as review state or separate hold; never manufacture final
   outcome to clear queue.

`scripts/validate_proposal_outcomes.py` enforces register schema, one final row
per issue, identifier syntax, decision/status compatibility, human attribution,
implementation PR requirements, and release-tag requirements.

## Cohort implementation and release

Accepted proposals batch by semantic dependency and affected module. Cohort PR
uses `.github/PULL_REQUEST_TEMPLATE/proposal-cohort.md`, references every issue,
and updates each register row to `implemented` with cohort ID and merged PR URL.
Semantic cohorts still require repository collision, deterministic rebuild,
validator, empty-store, Skosmos, and checksum gates.

Release PR updates row to `released` and records immutable release tag.
`sync-proposal-outcomes.yml` validates changed rows, applies matching status
label, synchronizes project stage, links issue to exact register commit/line,
and closes only rejected or released issues. Accepted or implemented issues
remain open.

## GitHub configuration

Label and project setup is reproducible:

```sh
python scripts/configure_github_review_system.py --apply-labels
gh auth refresh -s project,read:project
python scripts/configure_github_review_system.py --apply-project
gh secret set ADD_TO_PROJECT_PAT --repo ERAgriculture/era-aom
```

Secret token needs project write access plus repository issue access. Project
setup writes `PROPOSAL_PROJECT_URL` repository variable. Missing variable skips
project addition; configured variable with missing or invalid token fails job
rather than silently passing.

## Non-GitHub intake boundary

Future web form is adapter, not second governance system. It must:

1. collect same required fields and consent;
2. submit through GitHub API using scoped installation credential;
3. create issue matching canonical form headings and labels;
4. preserve contributor attribution without exposing private contact data;
5. return issue URL to contributor;
6. enter identical routing, review, outcome-register, cohort, and release path.

Web adapter must not write ontology source, outcome register, project status,
or releases directly. Authentication, abuse controls, privacy notice, and rate
limits require separate design and security review before deployment.
