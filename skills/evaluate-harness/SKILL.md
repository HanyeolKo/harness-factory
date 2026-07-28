---
name: evaluate-harness
description: Conditionally measure whether an installed harness improves quality, success rate, cost, time, or stability against a baseline. Use for an explicit benchmark or a valid deterministic targeted/full trigger.
---

# evaluate-harness

In the automatic path, run the deterministic checker first. On `none`, do not load detailed evaluation references or an LLM judge. An explicit user full evaluation uses the structured override contract and never bypasses structural checks.

## Procedure

1. Resolve `FACTORY_ROOT`; read the target spec, self-evaluation state, report settings, and only evaluation-relevant indexed memory.
2. Confirm harness-evaluation and improvement skills link the same `self_evaluation.evaluator`, with `scope: harness` and `type: experiment`.
3. Freeze checker JSON in `harness/evaluation/runs/<run-id>/trigger.json` before evaluation.
   - Route any `input-invalid:*` to `verify-harness` and structural recovery without effect evaluation or an LLM.
   - Preserve automatic `none` as stop.
   - For an explicit full request, preserve raw JSON under `override.original`; use top-level `decision: full`, `mandatory: false`, `override.kind: explicit-user-request`, the original reasons plus `explicit-user-request`, and unchanged deferred reasons, hashes, and acknowledgement snapshot.
4. For `adapter-change|parity-fail`, require selected-provider parity first. Record a new parity transition once and stop on failure.
5. On `targeted`, run only the exact `cost-regression|retry-pressure|deterministic-sample` mappings in the declared suite. Never invent a targeted LLM evaluation.
6. On `full`, freeze commit, fixture, model/version, permissions, tools, budget, evaluator, and pass conditions; then run baseline, control, and treatment. Prefer deterministic metrics and use blind rubrics only for genuinely nondeterministic dimensions.
7. Store raw runs and a machine-readable English report with `improved|neutral|regressed|inconclusive`. Present the user-facing narrative in `communication.report_language` and apply `communication.terminology`; do not translate IDs, paths, commands, evidence, keys, status values, reasons, or verdicts.
8. ACK every completed targeted/full run:

```text
python <target>/harness/triggers/record_self_evaluation.py <target>/harness --decision <targeted|full> --decision-file <target>/harness/evaluation/runs/<run-id>/trigger.json --verdict <improved|neutral|regressed|inconclusive>
```

The recorder validates the frozen decision, reasons, current managed hashes, and failure snapshot. Full ACK consumes only processed events/failures and refreshes hashes, units, and cooldown; targeted ACK updates last decision and cooldown only. Never ACK an incomplete or stale run.

Forward only a full regression or attributed harness defect to `improve-harness`. Evaluation and reporting do not modify harness meaning. Mismatched arms, insufficient samples, or unrun evaluators yield `inconclusive`.
