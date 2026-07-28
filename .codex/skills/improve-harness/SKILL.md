---
name: improve-harness
description: Incrementally improve an installed project harness from completed full-evaluation evidence, then verify and re-evaluate the candidate and retain only a proven improvement or explicitly approved neutral result.
---

# improve-harness

Keep all improvement state and evidence in the target project. The factory does not centralize installed harnesses.

## Entry gate

Require either an ACKed full report that attributes a regression or defect to the harness, or an explicit user request backed by effect evidence. `input-invalid:*`, unresolved parity, a single weak signal, sampling, or an interval alone is not an LLM improvement trigger; verify and recover first.

## Procedure

1. Read the full decision/report, smallest relevant journal window, prior candidate effects, baseline, report settings, ownership, and indexed memory. Write `preservation-before.json`.
2. Confirm the improvement skill links a `scope: harness`, `type: experiment` evaluator. Separate product defects from harness causes; return product defects to task recovery.
3. Record one hypothesis and at most two changes with target metric, exact files, and rollback condition in `delta-plan.json`, classified as `unchanged|add|modify-proposed|conflict|approval-required`.
4. Use the matching atomic build skill. Update spec and concise English canonical artifacts first, then reproject only selected providers' exact managed artifacts. Keep communication presentation settings separate from effect-bearing instructions. Update durable memory and its index atomically.
5. Require provider parity before effect evaluation. Record a new parity failure once and recover structurally.
6. Run `verify-harness`, memory/instruction budgets, cold-start, preservation comparison, the structural evaluator, and the original task evaluator. Write `preservation-after.json`.
7. Freeze checker JSON and rerun the same full experiment under the same conditions. Store the report and ACK the completed run:

```text
python <target>/harness/triggers/record_self_evaluation.py <target>/harness --decision full --decision-file <target>/harness/evaluation/runs/<run-id>/trigger.json --verdict <improved|neutral|regressed|inconclusive>
```

8. Accept `improved` or pre-approved `neutral`. Revert `regressed|inconclusive` candidates and retain rejected evidence.
9. Append decisions and journal events. Present the result in the configured report language and terminology while keeping all machine tokens exact.

Unapproved deletion or overwrite of user configuration/memory, evaluator weakening, gate bypass, hidden failures, bulk hypotheses, and one-provider semantic drift are not improvements.
