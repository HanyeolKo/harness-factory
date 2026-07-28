# Principle 1 — Evaluation Is a First-Class Component

## Statement

A task unit without a defined evaluator must not run. Evaluation is specified before execution, not attached afterward as a confidence check.

Task evaluation and harness-effect evaluation are separate. Recovery consumes task failures. Repeated failures may trigger a full harness experiment, but improvement begins only after that experiment attributes the problem to the harness.

## Rules

1. **Define first** — Record the evaluator when a unit enters the queue. Do not defer the completion test until after implementation.
2. **Prefer deterministic evidence** — Use tests, builds, linters, type checks, schema validation, diff checks, or scripts whenever possible. Use an LLM judge only when no deterministic evaluator can represent the requirement.
3. **Require a rubric** — Before using an LLM judge, store explicit criteria and a pass condition for every criterion. An unrecorded impression is not a verdict.
4. **Keep raw evidence** — The runner produces raw evidence. A verdict owner compares it with the pass condition. Record the result and evidence path in `ledger/journal.jsonl`.
5. **Fail closed** — An evaluator that cannot run is never a pass. Record `fail` or `blocked` according to the contract and enter recovery.
6. **Keep approval separate** — Human approval is an `approval_gate`, not a replacement for task evaluation.

## Evaluator classes

| Type | Examples | Use |
|---|---|---|
| Deterministic, existing | Test suite, build, lint, schema validation | Always prefer when available |
| Deterministic, added | Purpose-built validation script, golden-file comparison | Add when the project lacks a suitable check |
| Rubric-based LLM | Document quality, semantic accuracy | Only with a stored rubric and evidence |
| Human approval | Release, deletion, external communication | Gate only; never the sole evaluator |

## Constructor requirements

- During discovery, inspect test runners, CI, linters, build commands, and existing validators before asking the user.
- If no deterministic evaluator exists, put creation of at least one minimal validation script at the top of `state/state.json` and use an explicit temporary rubric until it exists.
