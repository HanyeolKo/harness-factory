# Principle 6 — Evidence-Based Incremental Improvement

## Statement

The factory creates and changes project-owned harnesses. It does not centralize project state. Routine self-checking runs only a deterministic checker; harness-effect evaluation and improvement load only when valid evidence requires them.

## Rules

1. **Separate task and harness verdicts** — Task evaluators judge deliverables. A harness experiment judges whether the harness changed outcomes.
2. **Link every skill** — In schema 1.1 and schema 1.2, `entry|evaluation|verification|domain` skills link to a `scope: task` evaluator. Adaptive and governed `harness-evaluation|improvement` skills link to `self_evaluation.evaluator` with `scope: harness` and `type: experiment`.
3. **Keep the checker read-only** — It returns only `none|targeted|full`; it never calls an LLM, writes state, or returns `improve`.
4. **Reject damaged inputs** — Route `input-invalid:*` to `verify-harness`, structural recovery, and recheck. Do not open effect evaluation or an LLM judge.
5. **Verify adapters first** — `adapter-change|parity-fail` requires provider parity to pass before effect evaluation.
6. **Fix targeted scope** — Only `cost-regression|retry-pressure|deterministic-sample` may select the deterministic metrics mapped in `evaluation/suites/targeted.json`. No ad hoc targeted LLM judge is allowed.
7. **Watch exact managed artifacts** — Hash the canonical contract separately and watch only selected providers' root guidance, spec skill projections, namespaced agent wrappers, and generated config. Exclude unrelated user files.
8. **Record incident transitions** — Add pending events once when cold-start changes false to true or parity changes pass to fail.
9. **Acknowledge completed evaluation** — Run the recorder after every completed `targeted|full` evaluation so one incident is not evaluated repeatedly.
10. **Use comparable experiments** — `full` compares baseline, control, and treatment with the same evaluator, conditions, metrics, and pass rules.
11. **Improve only after attribution** — Change one hypothesis and at most two components after a completed full report attributes a regression or defect to the harness, or after an explicit evidence-backed user request.
12. **Keep acceptance fixed** — Accept `improved` or explicitly pre-approved `neutral`. Never weaken an evaluator, bypass a gate, delete evidence, or hide a failure.

## Routing

```text
checker
├─ input-invalid:* ─────→ verify + structural recovery → recheck
├─ adapter/parity ──────→ parity verify → recheck/pass
├─ none ────────────────→ stop
├─ targeted ────────────→ fixed deterministic suite → recorder ACK
└─ full ────────────────→ harness experiment → recorder ACK
                                      └─ attributed regression → improve
```

Mandatory full signals include canonical, agent, skill, evaluator, and adapter changes; cold-start and parity incidents; and repeated failure keys. `minimum_samples` gates success-rate and cost comparisons only. `targeted_sample_rate` creates an independent deterministic sample. Budget and cooldown defer every non-mandatory cost, retry, sample, and interval signal but never a mandatory signal.

An explicit user-requested full evaluation uses the structured override contract, preserves the original checker output, and does not bypass `input-invalid:*` or provider parity.

## Effect-hash boundary

- Canonical instructions and `communication.artifact_language` are effect-bearing.
- `communication.report_language` and `communication.terminology` affect presentation only and are excluded from the harness-effect canonical hash.
- Reports may localize narrative, but IDs, paths, commands, evidence, JSON keys, status values, trigger reasons, and verdicts are never translated.
- Ordinary memory content and index-row changes use deterministic verification. Memory policy or routing changes are canonical effect changes.

## ACK transition

Freeze checker JSON at `harness/evaluation/runs/<run-id>/trigger.json` before evaluation, then run:

```text
python harness/triggers/record_self_evaluation.py harness --decision <targeted|full> --decision-file harness/evaluation/runs/<run-id>/trigger.json --verdict <improved|neutral|regressed|inconclusive>
```

The recorder validates the frozen decision and reasons, current managed hashes, and the frozen failure acknowledgement. A full ACK consumes only the pending events and failures captured at evaluation start, then updates managed hashes, units, cooldown, and verdict. A targeted ACK updates its decision, verdict, and cooldown but does not consume mandatory events. New incidents that arise during evaluation remain pending. Never ACK an incomplete or stale run.

## Standard improvement transaction

1. Confirm a completed full report and harness attribution, or an explicit evidence-backed request.
2. Freeze baseline, preservation evidence, the intended metric, and rollback conditions.
3. Select one hypothesis and at most two component changes.
4. Update the spec and canonical components first; reproject every selected provider's exact managed artifacts.
5. Run structural verification, provider parity, cold-start, and the original task evaluator.
6. Repeat the same full harness experiment and ACK it.
7. Accept or roll back, then append the decision and evidence to the ledger.
