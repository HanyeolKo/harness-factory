---
name: build-evaluator
description: Add or update an evidence-based task or harness-effect evaluator with a runner, verdict owner, raw evidence, and explicit pass condition. Use for tests, builds, lint, validation scripts, rubrics, or before-and-after harness experiments.
---

# build-evaluator

Keep task completion separate from harness effect. Human approval is a gate, not an evaluator.

## Types

- `scope: task`: judges one unit or entry/evaluation/verification/domain skill. Structural verification uses the validator.
- `scope: harness`: adaptive or governed only; compares baseline/control/treatment, uses `type: experiment`, and is linked by self-evaluation plus harness-evaluation/improvement skills.

## Procedure

1. Resolve `FACTORY_ROOT`; read evaluation principles, the target spec/profile, existing commands, report settings, and relevant indexed memory when installed. A harness-effect evaluator requested for core requires a proposed and user-confirmed adaptive transition through `build-harness reconcile`.
2. Freeze the baseline and preservation manifest. Never weaken an existing pass condition to make a candidate pass.
3. Define target, raw evidence, runner, verdict owner, command, and pass condition. Prefer deterministic evidence; use a written rubric only when deterministic checks cannot exist.
4. Link task evaluators to affected queue units and skills. Link one harness experiment ID consistently through `self_evaluation` and harness workflows.
5. If targeted routing changes, edit only the fixed deterministic mappings for `cost-regression`, `retry-pressure`, and `deterministic-sample`.
6. Execute the command and confirm both evidence shape and pass/fail behavior. Unavailable execution is `fail(structural:evaluator-unavailable)`.
7. Update spec and canonical evaluation files first. Require provider-path preflight before projecting selected adapters and exact watched paths.
8. Record `evaluator-change` and any real `adapter-change`; run `verify-harness`, parity, memory/preservation checks, and block effect evaluation until parity passes.

Report narrative in the configured language and terminology, but never translate commands, paths, evidence, keys, IDs, status values, or verdicts. Executor self-judgment, mismatched experiment arms, hidden evaluation cost, gate substitution, and evidence-free pass are invalid.
