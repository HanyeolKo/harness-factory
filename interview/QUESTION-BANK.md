# INTERVIEW QUESTION BANK — Phase 1

Use this bank to configure a project-owned harness quickly. Inspect first; ask only for decisions that cannot be established safely from the repository or an approved prior decision.

## Operating rules

1. **At most two batches** — Batch one contains core Q1–Q4. Batch two contains at most four relevant conditional questions.
2. **Inspect before asking** — Read root rules, README and docs, build/test/lint/CI, existing harness files, state, evaluators, and memory index.
3. **Reuse approved decisions** — Do not repeat an unchanged purpose or boundary already recorded in the spec or D-001.
4. **Apply disclosed defaults** — If the user delegates a choice, use the defaults below and list them in the delivery report.
5. **Prefer bounded choices** — Offer concise options plus a short free-text correction.
6. **Record decisions** — Write answers and applied defaults to `ledger/DECISIONS.md` D-001.
7. **Keep project ownership fixed** — Do not ask whether to move an installed harness into the factory. Preserve and improve it inside the target project.
8. **Protect invariants** — User direction may change design choices, but never permits evidence-free pass, evaluator removal, gate bypass, evidence deletion, or provider semantic drift.
9. **Separate artifacts from presentation** — Internal canonical prose is concise English. Report language and terminology affect user-facing narrative only; technical tokens are never translated.

## Core batch — four questions

### Q1. Target, purpose, and deliverable

> The repository suggests that this harness should manage `<scope>` for `<purpose hypothesis>`. Is that correct, and is the main deliverable code, documentation, data, or a mix?

- **Default** — Current repository. Reuse a matching approved purpose; require input only for a new, conflicting, or unresolved purpose.
- **Maps to** — `harness.id`, `harness.purpose`, domain graph, task evaluator candidates.

### Q2. Task completion

> What proves that one task is complete? (a) existing tests/build/lint, (b) a new deterministic validation script, (c) a stored rubric, or (d) one of a–c plus human approval?

- **Default** — The best discovered deterministic check. If none exists, create a validation-script backlog item and use an explicit temporary rubric.
- **Maps to** — `evaluators[].scope: task`, command, pass condition, runner, owner, and evaluator links for `entry|evaluation|verification|domain` skills.
- **Guard** — Human approval is an `approval_gate`, not an evaluator substitute.

### Q3. Operating mode

> How will the harness run? (a) attended user sessions, (b) long autonomous sessions, or (c) unattended cron/event execution?

- **Default** — (a) attended sessions.
- **Maps to** — Recovery escalation, checkpoint frequency, full interval, cooldown, and approval boundaries.

### Q4. Cost and report presentation

> Choose cost sensitivity: (a) tight, (b) balanced, or (c) loose. Also choose the user-facing report language tag and terminology style: `technical-english` or `localized`.

- **Defaults** — (b), `communication.report_language: en`, and `communication.terminology: technical-english`.
- **Fixed contract** — `communication.artifact_language: en`; canonical skills, roles, memory, loops, and machine-readable prose remain concise English with no bilingual duplicate.
- **`technical-english`** — Use the selected report language's grammar, but keep stable technical nouns such as `harness`, `agent`, `skill`, `evaluator`, `baseline`, `control`, and `treatment` in English.
- **`localized`** — Translate explanatory technical nouns when a conventional local term exists. Use localized prose once, without a parallel bilingual copy.
- **Maps to** — Work budget, `targeted_sample_rate`, `cooldown_units`, `budget_ratio`, `full_interval_units`, report presentation, and terminology.
- **Guard** — Report language and terminology are excluded from the effect hash. IDs, paths, commands, evidence, JSON keys, status values, reasons, and verdicts remain exact.
- **Cost note** — Each task boundary runs the deterministic checker. `targeted` uses fixed metrics; `full` uses the harness experiment and is ACKed. Invalid input and unresolved parity never enter effect evaluation.

## Conditional batch — ask at most four

### Q5. Large-work unit

> Which boundary is natural: file, module, feature, service, or data batch, and approximately how many units exist?

- **Default** — Propose from discovery and ask only for correction.
- **Maps to** — Execution loop, state queue, and evaluation sampling unit.

### Q6. Destructive or external approval

> Which release, deletion, external communication, migration, security, or cost steps require human approval?

- **Default** — Gate every destructive, irreversible, or externally visible step.
- **Maps to** — `approval_gates`.

### Q7. Autonomous stop conditions

> When must automation stop and ask: unclear scope, retry exhaustion, budget exhaustion, gate reached, or another condition?

- **Default** — Stop and escalate for all four listed conditions.
- **Maps to** — Recovery and waiting state.

### Q8. Rubric quality

> Which two or three criteria define a good nondeterministic deliverable, such as accuracy, evidence, length, or performance?

- **Default** — Propose a deliverable-specific rubric and request confirmation.
- **Maps to** — Task evaluator rubric.

### Q9. Existing root rules

> Existing `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md` files were found. May the harness keep its canonical files under `harness/` and upsert only namespaced managed blocks?

- **Default** — Yes; preserve all user content outside managed blocks.
- **Maps to** — Harness root, provider managed blocks, and exact `watched_paths`.

### Q10. Journal detail

> Should the journal record (a) verdicts, failures, and decisions only, (b) unit start/end plus those records, or (c) maximum detail?

- **Default** — (b).
- **Maps to** — Journal events and report detail.

### Q11. Complex topology and providers

> Does the project need domain coordinators or specialized workers, and which of Claude, Codex, and Gemini should receive adapters?

- **Default** — Derive dynamic roles that cover `routing`, `execution`, `verification`, `verdict`, `defect-counting`, and `improvement`; generate all three providers.
- **Maps to** — Domains, agents, skills, orchestration, evaluators, runtime targets, and provider adapters.
- **Guard** — Even when one agent fills several roles, separate deliverable, evidence, and verdict stages.

### Q12. Existing baseline

> Can recent task records produce success rate, average cost, and retry count? Which metric must a harness change preserve or improve?

- **Default** — Compute available metrics from deterministic task records. Without a comparable baseline, restrict the harness verdict to `inconclusive`.
- **Maps to** — Harness experiment, baseline, thresholds, minimum samples, and harness-evaluation/improvement evaluator links.

### Q13. Reconciliation conflict

> Existing `<file or rule>` conflicts with proposed `<field or path>`. Should its meaning remain in place with an additive extension, or coexist at a separate path?

- **Default** — Apply additive `improve|reconcile` deltas when no conflict exists. A deletion, rename, move, split, merge, or semantic replacement has no default and requires explicit approval.
- **Maps to** — Mode, ownership, preservation manifest, and `unchanged|add|modify-proposed|conflict|approval-required` delta plan.
- **Guard** — Never offer centralization in the factory or automatic overwrite of user-owned memory.

## Defaults

| Field | Default |
|---|---|
| `TARGET` | Current repository |
| `HARNESS_OWNERSHIP` | Target project owns canonical files, state, ledger, memory, and evidence |
| `EXISTING_HARNESS_MODE` | None → `create`; valid spec → `improve`; partial/legacy → `reconcile` |
| `CHANGE_POLICY` | Baseline + ownership + preservation manifest + classified delta plan |
| `SCHEMA_VERSION` | `1.1` |
| `ARTIFACT_LANGUAGE` | `communication.artifact_language: en` |
| `REPORT_LANGUAGE` | `communication.report_language: en` |
| `REPORT_TERMINOLOGY` | `communication.terminology: technical-english` |
| `COMMUNICATION_COMPATIBILITY` | Existing 1.0/1.1 may omit `communication`; use English defaults until additively configured |
| `MAX_INSTRUCTION_LINES` | `limits.max_instruction_lines: 120` for new harnesses |
| `MEMORY_INDEX` | `harness/memory/INDEX.md`; read selected entries only; do not duplicate state or events |
| `MEMORY_POLICY` | `preserve-and-reconcile` |
| `MEMORY_MAX_DOCUMENT_LINES` | `memory.max_document_lines: 80` for new harnesses |
| `MEMORY_MAX_SUMMARY_CHARS` | `memory.max_summary_chars: 160` for new harnesses |
| `READING_BUDGET_COMPATIBILITY` | Older specs may omit new fields; preserve content and add limits only through an explicit delta |
| `TASK_EVALUATOR` | Best discovered deterministic check; otherwise add a validation script |
| `HARNESS_EVALUATOR` | `scope: harness`, `type: experiment`; linked by harness-evaluation/improvement skills |
| `PASS_CONDITION` | Command exit 0 or every rubric criterion passes |
| `OPERATION_MODE` | Attended session |
| `WORK_BUDGET` | Warn at 80%; checkpoint and stop or replace at 100% |
| `WORK_UNIT` | Discovery-based proposal |
| `PARALLELISM` | Safe independent boundaries only; declare limits in the spec |
| `DETERMINISTIC_BOUNDARY` | Scripts validate, aggregate, and trigger; LLMs handle semantic judgment only |
| `GATES` | Every destructive or externally visible step |
| `JOURNAL_LEVEL` | Unit start/end + evidence + verdict + decision |
| `HARNESS_ROOT` | `<target>/harness/` |
| `SELF_EVALUATION_MODE` | `event-driven`; invalid input → verify/recovery; adapter/parity → verify first |
| `TARGETED_SAMPLE_RATE` | `0.05`, adjusted from project evidence |
| `TARGETED_SUITE` | Fixed cost/retry/sample deterministic metrics at `self_evaluation.targeted_suite` |
| `EVALUATION_ACK` | Freeze checker JSON in run `trigger.json`; record every completed `targeted|full` |
| `FULL_INTERVAL_UNITS` | `10` |
| `COOLDOWN_UNITS` | `2` completed units after the last evaluation |
| `EVALUATION_BUDGET_RATIO` | At most `0.10` of the total work budget |
| `SUCCESS_RATE_DROP_POINTS` | `5` percentage points |
| `COST_INCREASE_RATIO` | `0.20` |
| `FAIL_THRESHOLD` | Three occurrences of one failure key |
| `RETRY_THRESHOLD` | Three retries per unit |
| `MINIMUM_SAMPLES` | Five units |
| `MANDATORY_EVENTS` | Canonical/agent/skill/evaluator/adapter changes and cold-start/parity failures |
| `MEMORY_TRIGGER` | Content/index row → deterministic verify; policy/routing → canonical full |
| `PRESENTATION_TRIGGER` | Report language/terminology only → no harness-effect change |
| `TEAM_ARCHITECTURE` | Capability backbone with roles derived from project boundaries |
| `RUNTIME_TARGETS` | Claude + Codex + Gemini unless the user narrows them |
| `WATCHED_PATHS` | Canonical hash plus exact selected-provider managed artifacts only |

Numeric defaults are starting points. When reliable historical evidence exists, adjust them and record the reason in D-001. A report-presentation preference never changes experiment thresholds.

## Fields derived without asking

| Field | Source |
|---|---|
| Build/run/lint/test commands | Repository and CI; record absence and create backlog when missing |
| Project tree, existing scripts, forbidden actions | Repository, CI, and root rules |
| Existing harness state | Target state and ledger; preserve in place |
| Provider-native paths | `providers/<id>/contract.json` |
| Skill evaluator links | Skill kind and evaluator scope/type |
| Exact watched artifacts | Spec and selected provider projections |
| Created date | Construction time |
| Interview summary and verify round | Recorded decisions and actual verification evidence |
