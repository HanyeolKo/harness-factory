---
name: verify-harness
description: Deterministically verify an installed harness schema, references, DAG, permissions, concise-English canonical artifacts, context budgets, cold-start contract, and Claude, Codex, and Gemini adapter parity.
---

# verify-harness

Verify structural integrity. Use `evaluate-harness` to measure whether the harness improves outcomes.

## Procedure

1. Resolve `FACTORY_ROOT` and the target. Read the spec/profile, report settings, state, the memory index only when installed, and only files required by the failing check.
2. Run `python <FACTORY_ROOT>/scripts/validate_runtime_neutral.py <target>`.
3. Check schema, profile-required and profile-forbidden paths, references, DAG, capabilities, permissions, evaluator links, gates, state/journal, installed memory, and Markdown budgets.
4. Confirm `communication.artifact_language` is `en` when configured. Treat absence in an existing 1.0/1.1 spec as the backward-compatible English default.
5. Check each selected provider's managed block, agent permissions, exact watched paths, and byte-identical skill projections.
6. Cold-start from `harness/HARNESS.md` in its declared order. Restore purpose, profile, phase, next action, and task evaluator; adaptive and governed also restore pending events, last harness verdict, and only relevant memory.
7. After an adaptive or governed harness change, run the deterministic trigger checker and the evaluator that motivated the change. Core stops after structural and task evaluation. Ordinary memory content/index changes need deterministic verification only; policy or routing changes are effect-bearing.
8. Report pass/fail, exact commands, raw evidence paths, checks not run, and residual risk using the configured report language and terminology. Keep technical tokens unchanged.

A verification-only request is read-only. If the user also requested repair, update common canonical files first, reproject every selected adapter, and retry at most three times. Verification never claims outcome improvement.
