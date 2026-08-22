# Learning Gate

The Learning Gate is an optional speed regulator for AI-assisted changes. The governed profile installs it inactive until the user explicitly enables it.

Its delivery-blocking semantics stay the same. What changes is the explanation flow: the gate now depends on Learning Assist so the developer reads one plain-language explanation before being quizzed.

## Default behavior

Every governed harness receives the Learning Gate, Learning Assist templates, and the deterministic verifier. Core and adaptive harnesses omit them until the user confirms a governed transition.

The policy still starts with `enabled: false`. When disabled, gate-specific per-change learning artifacts are not required and the gate does not block review, pull request creation, or merge.

## User-owned on/off control

Only an explicit user instruction may change `enabled`. An agent may explain the trade-off or recommend enabling the gate for a risky change, but it must not change the value itself. Reconciliation preserves the existing value.

## Shared explanation flow

All completed work gets a short Change Report. When the gate is enabled and applicable, Learning Assist expands the actual diff into the gate's `diff-explanation.md` using the same readability contract.

```text
implementation
  -> validation
  -> short Change Report
  -> Learning Assist explanation from the actual diff
  -> developer reads it
  -> Learning Gate quiz
  -> pass or hint-based retry
```

The gate must not create a second, denser explanation vocabulary. Explain concrete behavior first, then the reason, runtime flow, relevant code, and only then technical terminology when it helps maintenance.

## Applicability

The default mode remains risk-based. When enabled, the gate applies if either condition is true:

- changed lines meet the configured threshold;
- at least one supplied risk tag appears in the configured risk list.

Matching risk tags still take precedence over low-risk exemptions.

## Change lifecycle

For an applicable change:

1. Write `brief.md` before implementation using concrete problem language.
2. Implement and validate the change.
3. Produce the normal short Change Report.
4. Build `diff-explanation.md` from the actual diff through the Learning Assist explanation contract.
5. Let the developer read that explanation before quiz generation.
6. Generate five questions that test cause/effect, execution flow, failure paths, design responsibility, and meaningful trade-offs rather than vocabulary recall.
7. The developer writes `answers.json`; the implementation agent must not fill it in.
8. On an incorrect answer, do not immediately reveal the final answer:
   - first miss: give a directional hint;
   - second miss: give a concrete scenario or counterexample;
   - final miss: record the failed attempt, then explain the concept directly.
9. If confusing wording or an undefined term caused the miss, rewrite the question or explanation before counting it as a comprehension failure.
10. Commit the source change together with `brief.md`, `diff-explanation.md`, `quiz.json`, and `answers.json`.
11. Record the full source commit SHA, score, required-concept result, attempt count, and content hashes in `verification.json`.
12. Commit only `verification.json`, then run the deterministic verifier before review, pull request creation, or merge.

## Artifact contract

```text
harness/learning/<change-id>/
├── brief.md
├── diff-explanation.md
├── quiz.json
├── answers.json
└── verification.json
```

The default verification thresholds and commit/hash integrity rules remain unchanged.

## Reader-facing document destination

During harness setup, the user chooses where reader-facing Change Reports and Learning Assist copies are organized:

- `file` — default;
- `notion` — user-selected Notion target;
- `slack` — user-selected Slack target.

For Notion or Slack, the target must be supplied by the user. The canonical Learning Gate evidence remains in Git regardless of reader destination, because the verifier binds hashes and commits to project-owned files.

## Pull request and merge integration

The policy still declares review, pull request, and merge gates. The deterministic verifier continues to validate structure, path containment, committed evidence, and integrity. It does not pretend to resolve ambiguous semantic grading.

Learning Assist improves the explanation and feedback path; it does not weaken the gate.

## Factory responsibilities

Harness Factory:

- installs the disabled policy and verifier;
- installs the shared Change Report and Learning Assist contracts;
- asks for reader destination during new-harness setup, defaulting to `file`;
- preserves the user's current `enabled` value and existing learning evidence during improve/reconcile;
- keeps canonical verification evidence in Git even when reader copies are published externally;
- never enables the gate automatically.
