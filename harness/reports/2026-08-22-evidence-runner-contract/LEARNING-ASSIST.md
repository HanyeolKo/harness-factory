# Learning Assist: pre-change evidence runner contract

> Status: The candidate has not been applied to canonical source or provider adapters.

## Concrete problem

The evidence runner must execute evaluator commands and retain raw output. The canonical spec declares this role read-only. The Claude adapter denies Bash, and the Gemini adapter omits run_shell_command, so those providers cannot execute the command. Codex can execute commands in a read-only sandbox, but the contract does not name an owner that may persist evidence files.

Structural validation can therefore pass while the evaluation handoff remains impossible. The factory-contract-tests pass condition requires retained raw output, so a missing command result or evidence file must produce blocked rather than pass.

## Current flow

factory-builder -> evidence-runner -> contract-evaluator

1. factory-builder marks implementation ready.
2. evidence-runner executes the evaluator command.
3. evidence-runner retains stdout, stderr, and exit code.
4. contract-evaluator compares retained evidence with the pass condition.

Provider capabilities do not currently support steps 2 and 3, and the handoff has no required manifest fields or bounded write path.

## Single hypothesis

Giving the evidence runner command execution plus evidence-path-only persistence across all selected providers will increase evidence-complete handoffs without regressing structure, parity, or cold start.

The candidate changes two components:

1. evidence-runner agent contract and access projections;
2. shared evidence manifest and storage-path contract.

The harness-effect runner, telemetry writer, failure-state schema, and small-task fast path remain separate hypotheses.

## Intended flow

work unit -> evaluator command -> raw stdout/stderr -> manifest -> contract verdict

The evidence runner must not modify source. The main orchestrator may persist evidence only under harness/evaluation/task-evidence/<unit-id>/ and harness/evaluation/runs/<run-id>/. The manifest requires unit_id, evaluator, command, request_hash, approval_gate_status, stdout_path, stderr_path, exit_code, artifact_hash, checks_not_run, status, and next_role. The contract evaluator may issue a verdict only when the request binding, manifest, and raw files validate.

## Pass conditions

- Claude, Codex, and Gemini keep the evidence runner read-only while the main orchestrator executes and persists the exact request.
- Provider access meaning matches the canonical spec.
- validate_runtime_neutral.py and the existing contract suite pass.
- Agent count, handoff count, and delegation depth do not increase.
- The role contract permits no source-path writes.
- Structural checks and cold-start restoration do not regress.

## Residual risk

The current access schema supports only read-only or workspace-write. It cannot express command execution plus path-scoped evidence writes.

## Safety revision before provider changes

The first projection proposal would have changed evidence-runner to workspace-write. Safety review rejected that proposal because provider sandboxes could not enforce evidence-path-only writes. No provider wrapper was changed.

The retained candidate keeps evidence-runner read-only. It returns an exact execution request, the existing main orchestrator runs that command and persists only evidence files, and the same evidence runner validates the returned manifest before the contract evaluator issues a verdict. This leaves the number of workspace-write agents unchanged.

The residual risk moves to orchestration discipline: the main orchestrator must enforce the declared evidence root and must not combine source edits with the evidence execution step.

## Korean reader copy

The configured Korean reader copy is retained at harness/evaluation/runs/2026-08-22-generated-harness-review/LEARNING-ASSIST.ko.md because the current validator applies artifact_language English checks to harness/reports despite report_language ko.
