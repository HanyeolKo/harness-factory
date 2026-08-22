---
name: "harness-factory-dev-improve"
description: "Execute the improvement workflow for Harness Factory development."
---

# harness-factory-dev-improve

Read `harness/harness-spec.json` first. Find `harness-factory-dev-improve` in `skills` and confirm its kind, entry agent, domains, instructions, and evaluator.

- kind: `improvement`
- entry agent: `harness-improver`
- domains: factory-development
- evaluator: `harness-effect`

Require attributed full evidence, change one hypothesis and at most two components, reproject all providers, rerun the frozen suite, and retain rollback evidence.

Follow the common spec and `harness/team/agents/<role-id>.md` for delegation. Select only memory needed for the current unit through `memory.index`. Never bypass an evaluator, approval gate, or raw evidence. Stop on parity failure if a runtime adapter differs from this canonical skill. Keep canonical output concise and English. Wrap exact non-English names or tokens in backticks. Format only user-facing narrative with the configured report language and terminology. If `communication` is absent, use `en` reports with `technical-english`. That mode keeps stable technical nouns in English; `localized` translates explanatory nouns when a conventional local term exists. Both modes preserve every machine token exactly and avoid bilingual duplication.
