# Evaluation Evidence Contract

The read-only evidence runner owns the request and validation contract. The main orchestrator executes declared evaluator commands and retains raw evidence without modifying source.

## Allowed roots

- Task evidence: `harness/evaluation/task-evidence/<unit-id>/`
- Harness-effect evidence: `harness/evaluation/runs/<run-id>/`

No executor write may target source, configuration, state, ledger, memory, reports, learning artifacts, or a path outside these roots. The executor uses the main orchestrator's existing authority; no read-only agent receives broader tools.

## Execution request

The evidence runner returns `execution_request` with:

- `unit_id`
- `evaluator`
- `command`
- `evidence_root`
- `expected_artifacts`
- `approval_gate_status`
- `return_role`

The main orchestrator rejects escaped roots, unresolved approval gates, and commands that differ from the linked evaluator or declared affected checks.

## Required manifest

Each completed or blocked execution writes `manifest.json` beside its raw files with:

- `unit_id`
- `evaluator`
- `command`
- `request_hash`
- `approval_gate_status`
- `stdout_path`
- `stderr_path`
- `exit_code`
- `artifact_hash`
- `checks_not_run`
- `status`
- `next_role`

Use `completed|blocked` for `status`. Use `none|approved:<gate-id>|blocked:<gate-id>` for `approval_gate_status`. Use `null` for `exit_code` only when the command did not start.

The orchestrator writes `next_role: evidence-runner` because validation has not happened yet. The read-only validator does not rewrite the manifest.

Persist `execution-request.json` before command execution. Compute `request_hash` as SHA-256 over the UTF-8 bytes of its `execution_request` object serialized as JSON with keys sorted, no insignificant whitespace, and non-ASCII characters preserved. Compute `artifact_hash` as SHA-256 over `stdout bytes + b"\0stderr\0" + stderr bytes + b"\0exit-code\0" + exit encoding`. Use the ASCII decimal exit code plus `b"\n"` for a started command, or `b"null\n"` when the command did not start.

## Producer, validator, and consumer

The main orchestrator is the producer. It persists the request before execution, executes the exact request, and captures the command, gate status, raw streams, exit code, unavailable checks, request hash, and artifact hash inside the requested evidence root. It does not issue a verdict.

`evidence-runner` is the read-only validator. It checks that the manifest belongs to the current work unit and evaluator, `command` and `approval_gate_status` match the persisted request, paths remain inside the requested root, raw files exist, and manifest `next_role` is `evidence-runner`. It requires deterministic `request_hash` and `artifact_hash` verification. When native read-only tools cannot recompute a hash, it requests the main orchestrator to run the declared formula and return the result. Its validation result contains `manifest_path`, `validation_status`, `checks_not_run`, and `next_role`; valid completed or blocked evidence uses `next_role: contract-evaluator`.

`contract-evaluator` is the consumer and verdict owner. Missing, stale, escaped, or mismatched evidence is `blocked`, never `pass`.

## Handoff

The evidence runner first hands `execution_request` to the main orchestrator. The orchestrator returns the manifest path to the same evidence runner. The validator's result, not the persisted manifest, sets `next_role` to `contract-evaluator`. Failed or unavailable execution still goes to `contract-evaluator` with `validation_status: valid`, manifest `status: blocked`, and exact `checks_not_run`. Invalid evidence returns `validation_status: invalid` and does not authorize a verdict. The evaluator may hand a fail or blocked verdict to `defect-analyst` under the declared DAG.
