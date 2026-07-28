# CHECKLIST — Schema 1.1 Delivery

Every applicable item should pass. Make at most three correction rounds. If a failure remains, disclose the item, evidence, and reason in the delivery report.

## 0. Ownership and preservation

- [ ] Canonical harness files, state, append-only ledger, memory, evaluation evidence, and reports remain in the target project.
- [ ] No project-specific state or evidence was copied into the factory repository or plugin package.
- [ ] Existing queue, `next_action`, counters, journal, and evaluation runs were preserved.
- [ ] User content outside managed blocks in `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` was preserved.
- [ ] The target was classified as `create|improve|reconcile`; baseline, file ownership, and preservation manifest were recorded first.
- [ ] The delta uses `unchanged|add|modify-proposed|conflict|approval-required` and is stored under `maintenance/runs/<change-id>/`.
- [ ] No unapproved delete, rename, move, split, merge, semantic replacement, translation, or overwrite of user-owned memory occurred.
- [ ] An atomic request used the smallest build skill rather than reinitializing the full harness.

## 1. Common contract

- [ ] `harness/harness-spec.json` uses `schema_version: 1.1` for a new harness.
- [ ] The spec passes nested required/unsupported-key checks, unique IDs, safe relative paths, references, DAG, and limits.
- [ ] Every domain has a path and coordinator; all agent, skill, evaluator, and gate references resolve.
- [ ] The capability union includes `routing`, `execution`, `verification`, `verdict`, `defect-counting`, and `improvement`.
- [ ] Every agent has `harness/team/agents/<role-id>.md` and every skill has `harness/skills/<skill-id>/SKILL.md`.
- [ ] Execution, task evaluation, harness evaluation, recovery, and improvement loops are distinct.
- [ ] `harness/evaluation/EVALUATION-CONTRACT.md`, both trigger scripts, the targeted suite, state files, recovery files, budget files, ledger files, and the initial journal event exist.
- [ ] Every `skills[].evaluator` follows the kind contract: `entry|evaluation|verification|domain` → task; `harness-evaluation|improvement` → harness experiment.
- [ ] `evaluation/suites/targeted.json` maps exactly `cost-regression|retry-pressure|deterministic-sample` to deterministic metrics.
- [ ] No unresolved `{{...}}` placeholder or construction-session reference remains.
- [ ] Factory source path or repository/ref/commit and initial decisions are recorded in D-001.

### Communication

- [ ] A new harness includes `communication.artifact_language: en`.
- [ ] A new harness includes a valid BCP-47-style `communication.report_language`; the default is `en`.
- [ ] `communication.terminology` is `technical-english|localized`; the default is `technical-english`.
- [ ] `technical-english` uses report-language grammar while retaining stable English technical nouns.
- [ ] `localized` uses conventional local explanatory nouns without duplicating bilingual prose.
- [ ] Existing schema 1.0/1.1 without `communication` remains valid and uses English defaults until additively configured.
- [ ] Canonical skills, roles, memory, loops, and machine-readable prose use concise English with no bilingual duplicate.
- [ ] Existing user-owned content was not auto-translated.
- [ ] User-facing narrative follows report settings, while IDs, paths, commands, evidence, JSON keys, status values, trigger reasons, and verdicts remain exact.
- [ ] `communication.report_language` and `communication.terminology` are excluded from the harness-effect canonical hash.
- [ ] Artifact language and effect-bearing instruction changes remain included in the canonical hash.

### Reading budgets and memory

- [ ] A new harness sets `limits.max_instruction_lines: 120`.
- [ ] Canonical skill files fit that limit or carry `<!-- instruction-budget exception: ... -->` with a valid reason.
- [ ] `memory.index` is `harness/memory/INDEX.md` and `memory.policy` is `preserve-and-reconcile`.
- [ ] A new harness sets `memory.max_document_lines: 80` and `memory.max_summary_chars: 160`.
- [ ] Older specs may omit the new reading fields without invalidation or automatic rewrite.
- [ ] The memory index uses seven English columns, valid statuses, existing active paths, unique IDs and paths, and summaries within budget.
- [ ] Memory files fit the line limit or carry `<!-- reading-budget exception: ... -->` with a valid reason recorded in the index.
- [ ] State and event history are not duplicated in memory; their sources remain `state/state.json` and `ledger/journal.jsonl`.
- [ ] Create, move, supersede, archive, and index changes were atomic; no orphan active entry remains.
- [ ] `HARNESS.md` provides an ordered, bounded read route and progressive disclosure loads only relevant references.

## 2. Seven factory skills

- [ ] `build-harness` creates or reconciles the complete schema 1.1 baseline without centralizing project state.
- [ ] `build-agent` changes the canonical role, team projection, and every selected provider wrapper atomically.
- [ ] `build-skill` creates a concise English canonical skill and byte-identical selected-provider copies.
- [ ] `build-evaluator` records `scope: task|harness`, evidence runner, verdict owner, and pass conditions.
- [ ] `verify-harness` is deterministic and does not improve the harness automatically.
- [ ] `evaluate-harness` follows only a valid `none|targeted|full` decision or structured user override.
- [ ] `improve-harness` requires completed full attribution or an explicit evidence-backed user request.
- [ ] Each build skill records the correct mandatory event only when an effect-bearing component changed.
- [ ] A report-language or terminology-only change creates no harness-effect event.

## 3. Provider adapters

### Claude

- [ ] `.claude/skills/<skill-id>/SKILL.md` is byte-identical to its canonical skill.
- [ ] `.claude/agents/<namespace>-<role-id>.md` matches spec name, role, access, and meaning.
- [ ] A `read-only` agent has no write or shell capability.
- [ ] `CLAUDE.md` contains exactly one namespaced managed block.

### Codex

- [ ] `.agents/skills/<skill-id>/SKILL.md` is byte-identical to its canonical skill.
- [ ] `.codex/agents/<namespace>-<role-id>.toml` parses and matches spec name, description, and instructions.
- [ ] `.codex/config.toml` limits meet the spec and unrelated settings are preserved.
- [ ] `AGENTS.md` contains exactly one namespaced managed block.

### Gemini

- [ ] `.gemini/skills/<skill-id>/SKILL.md` is byte-identical to its canonical skill.
- [ ] `.gemini/agents/<namespace>-<role-id>.md` parses and preserves role and access meaning.
- [ ] The entry or main orchestrator owns DAG sequencing; wrappers do not call another subagent.
- [ ] `GEMINI.md` contains exactly one namespaced managed block.

### Parity and watched scope

- [ ] Every selected provider exposes equivalent agent, skill, evaluator, gate, and handoff meaning.
- [ ] Adapters are thin wrappers and do not become another canonical source.
- [ ] `watched_paths` contains only exact selected-provider root guidance, spec skill projections, namespaced agent wrappers, and generated config.
- [ ] Unrelated user files and unselected providers do not change watched hashes.
- [ ] No selected provider remains partially projected or semantically stale.

## 4. Task evaluation

- [ ] Every executable unit has a task evaluator.
- [ ] An evidence runner creates raw evidence and a verdict owner compares it with the stored pass condition.
- [ ] Every evaluator command or rubric was run at least once where applicable.
- [ ] No pass exists without raw evidence and a journal event.
- [ ] One failure incident is not counted twice.
- [ ] An unavailable evaluator is `fail|blocked`, never pass.
- [ ] Human approval is a gate and does not replace task evaluation.

## 5. Harness-effect evaluation

- [ ] A separate evaluator has `scope: harness` and `type: experiment`.
- [ ] Baseline, control, and treatment use the same evaluator, metrics, pass rules, and comparable arm conditions.
- [ ] The verdict is exactly `improved|neutral|regressed|inconclusive`.
- [ ] `minimum_samples` gates success-rate and cost comparisons only; it does not suppress retry or deterministic-sample signals.
- [ ] Insufficient full-experiment samples, mismatched arms, or checks not run yield `inconclusive`.
- [ ] A task failure is not automatically attributed to the harness.
- [ ] A task pass is not automatically `improved`.
- [ ] Treatment did not pass through weaker criteria, deleted evidence, or a bypassed gate.
- [ ] Report presentation is not an experiment variable unless the evaluation explicitly studies presentation quality.

## 6. Event-driven trigger

- [ ] `self_evaluation.mode` is `event-driven` and all checker, recorder, state, loop, evaluator, and targeted-suite references resolve.
- [ ] Sample rate, full interval, cooldown, budget ratio, success/cost/retry thresholds, and minimum samples are explicit.
- [ ] Mandatory events include canonical, agent, skill, evaluator, and adapter changes plus cold-start, parity, and repeated-failure incidents.
- [ ] The checker is read-only, deterministic, makes no LLM call, and returns compact JSON with only `none|targeted|full`.
- [ ] The checker never returns `improve` or writes files.
- [ ] Identical valid input produces identical output.
- [ ] Malformed input fails closed as mandatory `full` but routes to verify/recovery rather than effect evaluation or an LLM.
- [ ] `adapter-change|parity-fail` blocks effect evaluation until provider parity passes.
- [ ] Cold-start false-to-true and parity pass-to-fail add one pending event per transition.
- [ ] `targeted` runs only the exact reason mapping in `targeted.json`; it never opens an ad hoc LLM judge.
- [ ] Ordinary memory content and index-row changes leave the canonical hash unchanged and receive deterministic verification.
- [ ] Memory schema, policy, or routing meaning changes create `canonical-contract-change`.
- [ ] Report language and terminology changes leave the effect hash unchanged.
- [ ] Completed-task accounting updates `current_unit`, increments `units_since_full` once, decrements cooldown once, and records raw rolling evidence once.

### Structured explicit-full override

- [ ] The complete raw checker output is preserved in `override.original`.
- [ ] Top-level effective values are `decision: full`, `mandatory: false`, and `override.kind: explicit-user-request`.
- [ ] Original reasons remain first, followed by the override marker; deferred reasons, hashes, and `acknowledgement` remain unchanged.
- [ ] Only budget and cooldown may be bypassed; invalid input and parity checks remain blocking.

### Trigger fixtures

- [ ] No signal → `none`.
- [ ] Deterministic sample or bounded metric regression → `targeted`.
- [ ] Full interval reached → `full`.
- [ ] Canonical hash change or mandatory event → mandatory `full`.
- [ ] Repeated failure threshold → mandatory `full`.
- [ ] Non-mandatory signal over budget → `none` plus deferred reason.
- [ ] Non-mandatory signal during cooldown → `none` plus deferred reason.
- [ ] Budget or cooldown never hides a mandatory event.
- [ ] Presentation-only changes produce no full signal.

### Recorder and ACK fixtures

- [ ] Checker JSON is frozen in the run's `trigger.json` before evaluation.
- [ ] The recorder is called after every completed `targeted|full` run.
- [ ] Malformed decision file, decision mismatch, or stale managed hash rejects ACK.
- [ ] Full ACK consumes only the pending-event and failure snapshots frozen at evaluation start.
- [ ] Incidents created during evaluation remain pending.
- [ ] Full ACK updates canonical/provider hashes, units, cooldown, and verdict.
- [ ] Targeted ACK updates its last decision, verdict, and cooldown but consumes no mandatory event.
- [ ] The same mandatory signal does not immediately repeat after full ACK.
- [ ] A later cold-start or parity transition is detected again.
- [ ] An incomplete or stale run changes no state.

## 7. Improvement gate

- [ ] A completed full evaluation attributes a regression or defect to the harness, or the user made an explicit evidence-backed request.
- [ ] The candidate contains one hypothesis, at most two component changes, an expected metric effect, and rollback conditions.
- [ ] Files outside the delta and user-owned memory remain untouched.
- [ ] The spec and canonical files changed before adapters.
- [ ] Every selected provider was reprojected.
- [ ] `verify-harness`, budgets, parity, cold-start, the original task evaluator, and the same full experiment were rerun.
- [ ] Only `improved` or explicitly pre-approved `neutral` was accepted.
- [ ] `regressed|inconclusive` was safely rolled back with evidence retained.
- [ ] Gate bypass, evidence deletion, evaluator weakening, hidden failure, and unrelated state reset were not treated as improvement.

## 8. Cold-start

A context-free session can answer from files:

- [ ] Harness purpose and current phase.
- [ ] The single immediate next action.
- [ ] The linked task evaluator and pass condition.
- [ ] Domain execution order and handoff.
- [ ] Pending self-evaluation events and last harness verdict.
- [ ] Which indexed memory entries to read for the current action.
- [ ] When improvement is permitted.
- [ ] Which report language and terminology to use for user-facing output.

The test fails if it needs conversation memory, exceeds declared read budgets, or finds a blank `next_action`. A `coldstart_fail` false-to-true transition adds `coldstart-fail` once.

## 9. Repository and target checks

Factory repository:

```powershell
python scripts\test_runtime_neutral_contract.py
python scripts\test_self_evaluation_trigger.py
python scripts\skill_smoke_build_harness.py
```

Target project:

```powershell
python scripts\validate_runtime_neutral.py <target-project>
python <target-project>\harness\triggers\check_self_evaluation.py <target-project>\harness
```

- [ ] Actual command results and evidence paths were recorded.
- [ ] A command not run was not reported as pass.

## 10. Delivery report

- [ ] The report uses `communication.report_language` and `communication.terminology` while keeping technical tokens exact.
- [ ] It summarizes mode, baseline, preservation manifest, delta classification, conflicts, files changed, and retained state/ledger.
- [ ] It explains canonical English artifacts, reading budgets, memory index, and progressive disclosure.
- [ ] It summarizes domain, agent, skill, evaluator topology, providers, and model-tier mapping.
- [ ] It distinguishes task evaluation from harness-effect evaluation and gives exact invocation commands.
- [ ] It lists sampling, cooldown, budget, thresholds, mandatory events, and ACK behavior.
- [ ] It records verification rounds, each correction, raw evidence, and checks not run.
- [ ] Residual failures are either explicitly `none` or listed with reasons.
- [ ] It gives first-run, recovery, and rollback instructions.
