# Change Report — 2026-08-22-initial-harness

## What changed

The Harness Factory repository now owns a schema 1.1 development harness. It includes the canonical contract, six agent roles, six workflow skills, task and harness-effect evaluators, state, ledger, memory, recovery, reporting, Learning Assist, and Learning Gate contracts. Claude, Codex, and Gemini adapters project the same meaning.

## Why and flow

Future work follows `factory-router -> factory-builder -> evidence-runner -> contract-evaluator`. Failed or blocked tasks go to `defect-analyst` for stable failure classification. `harness-improver` acts only after full evidence attributes a defect to the harness. The deterministic boundary checker selects `none|targeted|full` without a routine LLM call.

## Key files

- `harness/harness-spec.json`: runtime-neutral source of truth and exact provider watched paths
- `harness/HARNESS.md`: cold-start order and operating rules
- `harness/policies/reporting.json`: `ko + technical-english` and file reader destination
- `harness/policies/learning-gate.json`: installed with `enabled: false` and user-owned control
- `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`: namespaced managed blocks; prior `GEMINI.md` text is preserved

## Validation

Provider path preflight and the full validator passed. The runtime-neutral suite passed 32 tests, self-evaluation passed 29 tests, Learning Assist and Learning Gate contracts passed, and the build-harness smoke suite passed 32 tests. One Windows symlink fixture in each relevant suite was skipped because the process lacks symlink privilege; resolved-path escape checks passed.

## Need to know

The initial `canonical-contract-change` remains pending for full harness-effect evaluation. No comparable baseline or five completed work-unit samples exist, so this build did not invent an effect verdict or ACK the event. Learning Assist is available on request, and only the user may change the Learning Gate `enabled` value. Factory validator 0.2.1 checks canonical Change Reports as English artifacts even when `report_language` is `ko`; Korean delivery remains user-facing while this Git report stays English for validator compatibility.
