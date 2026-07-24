# Required generated skill presets

Render each preset through `SKILL.md.tmpl`. Create the canonical `harness/skills/<skill-id>/SKILL.md` once and copy it byte-for-byte to every selected provider skill root. Provider adapters never rewrite skill meaning.

In schema 1.1 every skill object has `evaluator`. Link entry/evaluation/verification/domain skills to a `scope: task` evaluator. Link harness-evaluation/improvement skills to the `self_evaluation.evaluator`, which is `scope: harness`, `type: experiment`.

## Entry — `<id>`

```markdown
---
name: {{SKILL_ID_JSON}}
description: {{SKILL_DESCRIPTION_JSON}}
---

# {{SKILL_NAME}}

1. Read `{{HARNESS_ROOT}}/HARNESS.md`, `harness-spec.json`, and `state/state.json`.
2. Resolve the requested unit and `orchestration.entry_skill`; delegate only along the spec DAG.
3. Use the selected provider native agent projection. Gemini main orchestration owns handoff sequencing.
4. Run this skill's linked scope=task evaluator and preserve raw evidence.
5. Update task state and append the journal.
6. If cold-start changes false→true, append `coldstart-fail` to self-evaluation pending events once. If parity changes pass→fail, append `parity-fail` once.
7. At the task boundary run only `python {{HARNESS_ROOT}}/triggers/check_self_evaluation.py {{HARNESS_ROOT}}`.
8. Route `input-invalid:*` to `{{SKILL_NAME}}-verify` and structural recovery without effect evaluation/LLM. Require parity verification before evaluating `adapter-change|parity-fail`.
9. On `none`, stop. On `targeted|full`, invoke `{{SKILL_NAME}}-evaluate` with the decision JSON.

Never infer improvement from a checker result. Missing evaluator, parity failure, or approval gate blocks a pass.
```

## Task evaluation — `<id>-eval`

```markdown
---
name: {{SKILL_ID_JSON}}
description: {{SKILL_DESCRIPTION_JSON}}
---

# {{SKILL_NAME}}-eval

1. Resolve this skill's `evaluator` link and require `scope: task`.
2. The runner executes the frozen command and preserves command, cwd, exit code, and raw output.
3. The owner compares evidence with the frozen pass condition.
4. Record `pass|fail`; count one stable failure key per incident and update rolling metrics.
5. Do not start harness evaluation or improvement. The task-boundary checker owns scheduling.
```

## Structural verification — `<id>-verify`

```markdown
---
name: {{SKILL_ID_JSON}}
description: {{SKILL_DESCRIPTION_JSON}}
---

# {{SKILL_NAME}}-verify

Run the linked scope=task structural validator. Validate schema, references, DAG, permissions, root managed blocks, canonical skill byte parity, watched provider paths, self-evaluation state, and cold-start readability. If parity changes pass→fail, append `parity-fail` to pending events without duplicates. Verification does not modify the harness or claim outcome improvement.
```

## Harness effect evaluation — `<id>-evaluate`

```markdown
---
name: {{SKILL_ID_JSON}}
description: {{SKILL_DESCRIPTION_JSON}}
---

# {{SKILL_NAME}}-evaluate

1. Run or preserve the deterministic checker decision.
2. For `input-invalid:*`, stop and route to verification/structural recovery; do not open effect evaluation or an LLM judge.
3. For `adapter-change|parity-fail`, require provider parity verification to pass first.
4. On `none`, stop. On `targeted`, execute only the reason mapping in `evaluation/suites/targeted.json`; never invent an LLM targeted suite.
5. On `full`, use the linked scope=harness,type=experiment evaluator and freeze baseline/control/treatment conditions.
6. Store immutable runs and report `improved|neutral|regressed|inconclusive`.
7. After every completed targeted/full run invoke:
   `python {{HARNESS_ROOT}}/triggers/record_self_evaluation.py {{HARNESS_ROOT}} --decision <targeted|full> --decision-file {{HARNESS_ROOT}}/evaluation/runs/<run-id>/trigger.json --verdict <verdict>`
8. Forward only a full regression or attributed harness defect to `{{SKILL_NAME}}-improve`.

The recorder validates the frozen trigger file and requires its managed hashes to remain current. Full ACK clears only processed pending events and refreshes watched hashes/units/cooldown; targeted updates last decision/cooldown. Never ACK an incomplete run.
```

## Improvement — `<id>-improve`

```markdown
---
name: {{SKILL_ID_JSON}}
description: {{SKILL_DESCRIPTION_JSON}}
---

# {{SKILL_NAME}}-improve

1. Require a completed full effect report that attributes a regression to the harness, or an explicit evidence-backed user request.
2. Route malformed state and unresolved parity to structural verification/recovery first; do not treat them as an LLM improvement trigger.
3. Stage one hypothesis and at most two component changes, common spec first.
4. Regenerate every selected provider adapter and run the linked task structural evaluator plus the original task evaluator.
5. Rerun the frozen scope=harness,type=experiment evaluator, store the report, then call the recorder for the completed full run.
6. Accept improved or explicitly approved neutral; revert regressed/inconclusive.
7. Record decisions, runs, and rejected proposals inside this project only.
```

Existing `<id>-retro` may remain only as a compatibility alias to `<id>-improve`; it must not contain an independent periodic policy.
