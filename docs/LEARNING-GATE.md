# Learning Gate

The learning gate is an optional speed regulator for AI-assisted changes. It is installed with a generated harness but remains inactive until the user explicitly enables it.

## Default behavior

Every new harness receives:

```text
harness/
├── policies/
│   ├── learning-gate.json
│   └── LEARNING-GATE.md
├── learning/
│   └── _templates/
└── triggers/
    └── verify_learning_gate.py
```

The generated policy starts with:

```json
{
  "enabled": false,
  "control": {
    "owner": "user",
    "agents_may_change_enabled": false,
    "activation_requires_explicit_user_instruction": true
  }
}
```

When `enabled` is `false`, the gate returns `skip`, creates no per-change learning artifacts, and does not block review, pull request creation, or merge.

## User-owned on/off control

Only an explicit user instruction may change `enabled`. An agent may explain the trade-off or recommend enabling the gate for a risky change, but it must not change the value itself. Reconciliation preserves the existing value.

To enable the gate, the user changes:

```json
"enabled": true
```

To disable it again:

```json
"enabled": false
```

Changing thresholds, risk tags, or exemptions does not transfer ownership of the on/off decision to an agent.

## Applicability

The default mode is risk-based. When enabled, the gate applies if either condition is true:

- changed lines meet the configured threshold;
- at least one supplied risk tag appears in the configured risk list.

The default risk tags cover architecture, transaction boundaries, authentication, authorization, data models, external integrations, and unfamiliar technology. Typo, formatting, generated-file, and dependency-lockfile changes are exempt by default.

A CI workflow or local command should supply changed-line and risk metadata. `--apply` forces the gate to run; it does not bypass validation.

## Change lifecycle

For an applicable change:

1. Write `brief.md` before implementation.
2. Implement and validate the change.
3. Write `diff-explanation.md` from the actual diff.
4. Generate five medium-difficulty questions focused on design intent, failure modes, trade-offs, interaction, and code impact.
5. The developer writes `answers.json`. The implementation agent must not fill it in.
6. Record score, required-concept score, attempt count, current commit SHA, and content hashes in `verification.json`.
7. Run the deterministic verifier before review, pull request creation, or merge.

```text
python harness/triggers/verify_learning_gate.py harness \
  --change-id CHG-2026-0081 \
  --changed-lines 120 \
  --risk-tag transaction-boundary-change
```

A successful result is bound to the exact `quiz.json`, `answers.json`, and commit SHA. Changing code or answers after verification makes the evidence stale.

## Artifact contract

```text
harness/learning/<change-id>/
├── brief.md
├── diff-explanation.md
├── quiz.json
├── answers.json
└── verification.json
```

The default quiz contract requires:

- exactly five questions;
- at least three free-text questions;
- a score of at least 80;
- a required-concepts score of 100;
- at most three attempts;
- complete answers for every question;
- matching quiz, answer, and commit hashes.

The quiz should test whether the developer can explain why the code exists and how it fails, not whether they can repeat syntax.

## Pull request and merge integration

The policy declares review, pull request, and merge gates. Enforcement depends on the project's workflow. A GitHub Actions job can invoke the verifier and be configured as a required check. Local wrappers can call the same command before `git push` or PR creation.

The verifier is deterministic. It validates structure and integrity but does not pretend to resolve ambiguous semantic grading. Ambiguous free-text answers should be routed to human review or an evaluator distinct from the implementation agent.

## Factory responsibilities

Harness Factory:

- installs the disabled policy and templates;
- preserves the user's current `enabled` value during improve or reconcile operations;
- projects the policy path into runtime guidance;
- provides deterministic verification and contract tests;
- never enables the gate automatically.

The target project owns all learning artifacts and verification history. The factory does not collect them.
