# Proposal outcome register

`proposal_outcomes.csv` is the governed machine-readable register for final
proposal decisions. Each row records one GitHub proposal issue, human reviewer,
evidence, rationale, affected concept IDs, cohort implementation, and release.

Accepted rows progress through `accepted`, `implemented`, and `released`.
Rejected rows use `rejected`. Update existing rows; never create multiple final
outcomes for one issue. Merged changes trigger issue-label, register-link, and
closure automation.

Validate before review:

```sh
python scripts/validate_proposal_outcomes.py data/governance/proposal_outcomes.csv
```

Full process: [proposal review and release governance](../../docs/methods/proposal-review-and-release-governance.md).
