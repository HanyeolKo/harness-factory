# Change Report — 2026-08-22-evidence-runner-contract

## At a glance

The read-only evidence runner now defines exact evaluator requests and validates persisted evidence. The main orchestrator executes the request and writes only evaluation evidence.

## Why this changed

The generated harness assigned command execution and raw-evidence retention to a read-only role. Claude and Gemini read-only wrappers cannot execute shell commands, and no persistence owner was declared. Structural validation passed even though the declared evaluation handoff could not complete.

## What is different now

The canonical role, evaluation loop, team architecture, and spec handoff agree on three owners: evidence runner for request and validation, main orchestrator for execution and persistence, and contract evaluator for verdict. Provider wrappers changed only their description and remain read-only.

## Important flow

`work unit -> execution-request.json -> main orchestrator command -> raw streams and manifest -> evidence-runner validation -> contract-evaluator verdict`

The manifest binds twelve required fields, including request hash, approval-gate status, raw paths, exit state, artifact hash, and next role. Its pre-validation next role is `evidence-runner`; the read-only validator returns a separate result whose next role is `contract-evaluator`. A command that does not start uses `exit_code: null` and the exact `null\n` hash encoding.

## Key files

- `harness/team/agents/evidence-runner.md`
- `harness/evaluation/EVIDENCE-CONTRACT.md`
- `harness/loops/EVAL-LOOP.md`
- `harness/harness-spec.json`
- selected provider evidence-runner wrappers

## Validation performed

Provider-path preflight, runtime-neutral validation, repository contract tests, self-evaluation trigger tests, Learning Gate contract tests, smoke tests, and `git diff --check` passed. A completed probe and an approval-blocked probe both validated request order, root confinement, twelve fields, and deterministic hashes. Independent contract review passed after two rejected probe revisions were retained as evidence.

## What to know next

The full comparison retains this candidate as an improvement in the scoped evidence-contract metric. Native Claude and Gemini end-to-end execution remains unrun. The configured Korean reader copy is stored with evaluation evidence because the current validator applies English canonical checks to `harness/reports` despite `report_language: ko`.
