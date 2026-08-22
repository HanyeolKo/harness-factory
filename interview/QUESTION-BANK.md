# INTERVIEW QUESTION BANK — Phase 1

Use this bank to complete a project-owned schema 1.2 construction receipt in at most two batches. In `create`, Phase 2 cannot start and managed harness artifacts cannot be written until `interview_receipt.status` is `complete` and profile confirmation is recorded.

## Operating rules

1. **Inspect before asking** — Read the current request, root rules, README/docs, build/test/lint/CI, existing harness, state, evaluators, memory, reporting, and Learning Gate policy first.
2. **Do not re-ask request values** — Record a value explicitly supplied in the current request with source `request`.
3. **Prefer structured input** — Use the runtime's structured question/input mechanism with bounded options and a free-text correction; use plain text only when unavailable.
4. **No purpose default** — State a repository-based hypothesis, but obtain purpose from request text or explicit user confirmation.
5. **At most two batches** — Batch one contains unresolved parts of Q1–Q4. Batch two contains at most four relevant conditional questions.
6. **Explicit delegation only** — Silence is not delegation. Apply a default only after explicit delegation and record source `default-delegated`.
7. **Reuse approved decisions** — In `improve|reconcile`, do not repeat an unchanged spec, D-001, or policy decision; record `approved-decision`. Create forbids that source.
8. **Recommend, then confirm profile** — Recommend the lowest sufficient `core|adaptive|governed`, disclose installed and omitted capabilities, and require confirmation. Never change profile automatically.
9. **Record the receipt** — Write required values and sources to `maintenance/runs/<change-id>/delta-plan.json.interview_receipt`; set `harness.construction_receipt` to that file and keep D-001 as a concise pointer/summary.
10. **Protect invariants** — Never permit evidence-free pass, evaluator removal, gate bypass, evidence deletion, provider drift, guessed external targets, or a second canonical profile policy.
11. **Keep project ownership fixed** — Preserve and improve an installed harness in its target project.
12. **Separate presentation** — Canonical prose is concise English. Reader copies and localized narrative never replace exact Git evidence or machine tokens.

## Core batch — four questions

### Q1. Target, purpose, and deliverable

> The repository suggests `<purpose hypothesis>` and a `<code|documentation|data|mixed>` deliverable. Is that purpose correct? Based on it, I recommend `<profile>` because `<reason codes>`; it installs `<included>` and omits `<excluded>`. Confirm or correct each value.

- **No default** — Repository evidence may form a hypothesis but cannot confirm purpose. Reuse a matching approved purpose only in `improve|reconcile`.
- **Maps to** — `harness.id`, `harness.purpose`, `profile`, domain graph, and task evaluator candidates.

### Q2. Task completion

> What proves that one task is complete? (a) existing tests/build/lint, (b) a new deterministic validation script, (c) a stored rubric, or (d) one of a–c plus human approval?

- **Default** — The best discovered deterministic check. If none exists, create a validation-script backlog item and use an explicit temporary rubric.
- **Maps to** — `evaluators[].scope: task`, command, pass condition, runner, owner, and evaluator links for `entry|evaluation|verification|domain` skills.
- **Guard** — Human approval is an `approval_gate`, not an evaluator substitute.

### Q3. Operating mode

> How will the harness run? (a) attended user sessions, (b) long autonomous sessions, or (c) unattended cron/event execution?

- **Default** — (a) attended sessions.
- **Maps to** — Recovery escalation, checkpoint frequency, full interval, cooldown, and approval boundaries.

### Q4. Cost, presentation, runtime, and reporting

> Choose cost sensitivity, report language, `technical-english|localized`, runtime targets, and the `file|notion|slack` reporting destination and target.

- **Delegated defaults** — balanced, `communication.report_language: en`, `communication.terminology: technical-english`, the invoking runtime only, and `file` with `reader_target: harness/reports`.
- **External target** — If `notion` or `slack` is selected, ask for the page/database/channel/conversation identifier or URL. Never infer or guess it.
- **Fixed contract** — `communication.artifact_language: en`; canonical skills, roles, memory, loops, and machine-readable prose remain concise English with no bilingual duplicate. `canonical_evidence: file` remains fixed in `harness/policies/reporting.json`.
- **`technical-english`** — Use the selected report language's grammar, but keep stable technical nouns such as `harness`, `agent`, `skill`, `evaluator`, `baseline`, `control`, and `treatment` in English.
- **`localized`** — Translate explanatory technical nouns when a conventional local term exists. Use localized prose once, without a parallel bilingual copy.
- **Readability** — Reader-facing reports use `plain-language-first`: concrete behavior, reason, execution flow, relevant code, then technical terminology only when useful.
- **Maps to** — Work budget, runtime targets, report presentation, terminology, required schema 1.2 `harness/policies/reporting.json`, and adaptive/governed evaluation settings.
- **Guard** — Report language, terminology, and reader destination do not replace Git evidence. IDs, paths, commands, evidence, JSON keys, status values, reasons, and verdicts remain exact.
- **Cost note** — Adaptive/governed task boundaries run the deterministic checker. `targeted` uses fixed metrics; `full` uses the harness experiment and is ACKed. Core stops after task evaluation and structural verification.

## Profile recommendation

| Profile | Recommendation signals | Active layer |
|---|---|---|
| `core` | bounded task execution | routing, execution, task evaluation, structural verification, verdict, defect counting, short reporting |
| `adaptive` | durable memory, recurring workflow, long-running/unattended work, harness-effect measurement, or evidence-gated improvement | core plus memory, self-evaluation, harness experiment, improvement |
| `governed` | enabled/applicable Learning Gate, audit/education evidence, or blocking review/release control | adaptive plus installed Learning Assist and user-controlled Learning Gate support |

Reporting is common to all schema 1.2 profiles and does not raise profile by itself. Lower profiles may provide a one-off explanation without installing Learning Assist. Ordinary destructive/external approval gates and multiple runtime targets also do not imply governed.

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

- **Delegated default** — Derive the smallest profile-valid role set and generate the invoking runtime only. Do not infer governed or all providers from provider count.
- **Maps to** — Domains, agents, skills, orchestration, evaluators, runtime targets, and provider adapters.
- **Guard** — Even when one agent fills several roles, separate deliverable, evidence, and verdict stages.

### Q12. Existing baseline

> Can recent task records produce success rate, average cost, and retry count? Which metric must a harness change preserve or improve?

- **Default** — Compute available metrics from deterministic task records. Without a comparable baseline, restrict the harness verdict to `inconclusive`.
- **Maps to** — Harness experiment, baseline, thresholds, minimum samples, and harness-evaluation/improvement evaluator links.

### Q13. Reconciliation conflict

> Existing `<file or rule>` conflicts with proposed `<field or path>`. Should its meaning remain in place with an additive extension, or coexist at a separate path?

- **Default** — Apply additive `improve|reconcile` deltas when no conflict exists. A deletion, rename, move, split, merge, semantic replacement, Learning Gate state change, or reporting target change has no default and requires explicit approval.
- **Maps to** — Mode, ownership, preservation manifest, and `unchanged|add|modify-proposed|conflict|approval-required` delta plan.
- **Guard** — Never offer centralization in the factory or automatic overwrite of user-owned memory, learning evidence, or reporting policy.

## Defaults

| Field | Default |
|---|---|
| `TARGET` | Current repository |
| `HARNESS_OWNERSHIP` | Target project owns canonical files, state, ledger, memory, reports, learning evidence, and policies |
| `EXISTING_HARNESS_MODE` | None → `create`; valid spec → `improve`; partial/legacy → `reconcile` |
| `CHANGE_POLICY` | Baseline + ownership + preservation manifest + classified delta plan |
| `SCHEMA_VERSION` | New harness: `1.2`; compatible existing harness: preserve `1.0|1.1` until an approved migration |
| `PROFILE` | Recommend the lowest sufficient `core|adaptive|governed`; no automatic selection or change |
| `ARTIFACT_LANGUAGE` | `communication.artifact_language: en` |
| `REPORT_LANGUAGE` | `communication.report_language: en` |
| `REPORT_TERMINOLOGY` | `communication.terminology: technical-english` |
| `REPORT_DESTINATION` | Required for schema 1.2. Delegated file target: `harness/reports` |
| `REPORT_STYLE` | `plain-language-first` |
| `CANONICAL_REPORT_EVIDENCE` | `file`; Notion/Slack are reader copies only |
| `COMMUNICATION_COMPATIBILITY` | Existing 1.0/1.1 may omit `communication`; use English defaults until additively configured |
| `REPORTING_COMPATIBILITY` | Existing harnesses may omit `policies/reporting.json`; add it only through a preservation-aware delta |
| `TARGET_MARKDOWN_LINES` | `limits.target_markdown_lines: 50` for new harnesses |
| `MAX_MARKDOWN_LINES` | `limits.max_markdown_lines: 100` hard maximum after rendering |
| `MAX_INSTRUCTION_LINES` | `limits.max_instruction_lines: 100` for new harnesses |
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
| `INITIAL_SELF_EVALUATION` | Adaptive/governed create stores verified canonical/provider hashes with `pending_events: []`; installation alone opens no mandatory full |
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
| `PRESENTATION_TRIGGER` | Report language/terminology/reader destination only → no harness-effect change unless effect-bearing instructions change |
| `TEAM_ARCHITECTURE` | Capability backbone with roles derived from project boundaries |
| `RUNTIME_TARGETS` | Invoking runtime only after explicit default delegation; otherwise ask |
| `WATCHED_PATHS` | Canonical hash plus exact selected-provider managed artifacts only |

Numeric defaults are starting points. When reliable historical evidence exists, adjust them and record the reason in D-001. A report-presentation preference never changes experiment thresholds.

## Receipt and transition guards

- Required decisions are `purpose`, `deliverable_type`, `task_evaluator`, `operation_mode`, `cost_sensitivity`, `report_language`, `terminology`, `runtime_targets`, `approval_gates`, and `reporting`. An ordinary decision is `{value, source}` with source `request|user-answer|repository-confirmed|default-delegated|approved-decision`.
- Profile records `current`, `recommended`, `selected`, `reason_codes`, `confirmation_source`, and `override_reason`; create uses `current: null`. Selected must match `harness-spec.json.profile`; a mismatch with recommended needs a non-empty reason.
- Never infer a downgrade from inactivity. Record exact removed layers and paths, retained/archive evidence paths, and explicit approval. `default-delegated` cannot approve removal.
- Governed to adaptive requires retired governance need, disabled Gate, and no active gate evidence. Adaptive to core also requires no pending events, non-template memory, completed evaluation/ACK, or improvement history. Direct governed to core requires both removal sets.

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
