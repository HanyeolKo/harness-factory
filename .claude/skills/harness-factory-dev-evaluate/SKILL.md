---
name: "harness-factory-dev-evaluate"
description: "Execute the harness-evaluation workflow for Harness Factory development."
---

# harness-factory-dev-evaluate

Read `harness/harness-spec.json` first. Find `harness-factory-dev-evaluate` in `skills` and confirm its kind, entry agent, domains, instructions, and evaluator.

- kind: `harness-evaluation`
- entry agent: `contract-evaluator`
- domains: factory-development
- evaluator: `harness-effect`

Run only from a valid targeted or full decision. Freeze trigger JSON and compare baseline, control, and treatment under identical conditions.

Follow the common spec and `harness/team/agents/<role-id>.md` for delegation. Select only memory needed for the current unit through `memory.index`. Never bypass an evaluator, approval gate, or raw evidence. Stop on parity failure if a runtime adapter differs from this canonical skill. Keep canonical output concise and English. Wrap exact non-English names or tokens in backticks. Format only user-facing narrative with the configured report language and terminology. If `communication` is absent, use `en` reports with `technical-english`. That mode keeps stable technical nouns in English; `localized` translates explanatory nouns when a conventional local term exists. Both modes preserve every machine token exactly and avoid bilingual duplication.
