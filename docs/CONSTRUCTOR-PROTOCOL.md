# CONSTRUCTOR PROTOCOL — Harness Creation and Change Contract

This protocol is shared by all seven factory skills. The constructor analyzes a target project, creates or changes its runtime-neutral canonical harness, and projects native Claude, Codex, and Gemini adapters from that source.

## 0. Ownership and compatibility

- The factory never absorbs a project harness into a package, registry, or central state store.
- The target project owns `harness/`, state, append-only ledger, memory, evaluation runs, reports, reporting policy, and learning evidence.
- Keep an existing harness in place and change it incrementally.
- The factory checkout contains reusable schema, provider contracts, templates, validators, and skills only.
- Feeding project-specific observations back into factory templates is a separate user-approved task.

Classify the target as `create` when no harness exists, `improve` when a valid runtime-neutral spec exists, or `reconcile` for a partial or legacy layout. Before changing an existing harness, capture its validators and evaluators, baseline, file ownership, and preservation manifest. Classify each delta as `unchanged|add|modify-proposed|conflict|approval-required`. Deletion, rename, split, merge, semantic replacement, Learning Gate state change, or reader-destination change requires explicit approval.

Schema 1.1 requires `memory` and event-driven `self_evaluation`. Existing schema 1.0 or 1.1 specs may omit `communication` and the newer reading-cost fields. Existing harnesses may also omit `policies/reporting.json`. Keep those harnesses valid, apply English presentation defaults, and add new fields or the reporting policy only through an explicit preservation-aware delta. Do not auto-translate existing project-owned content or silently change a previously selected report destination.

Every factory skill first runs its bundled `scripts/resolve_factory.py`. Read only a source whose resolver verifies the required contract. Record its path or repository/ref/commit provenance in D-001.

## 1. Select the smallest skill

| Need | Skill |
|---|---|
| No harness, full topology redesign, or full migration | `build-harness` |
| Agent, access, or handoff change | `build-agent` |
| Execution or domain skill change | `build-skill` |
| Task or harness evaluator change | `build-evaluator` |
| Schema, structure, and provider parity verification | `verify-harness` |
| Harness-effect measurement | `evaluate-harness` |
| Correction of an attributed harness defect | `improve-harness` |

Do not use `build-harness` to reinitialize state for an atomic change.

## 2. Discover, then interview

1. Read the factory principles, `interview/QUESTION-BANK.md`, and `CHECKLIST.md`.
2. Inspect target root rules, README and docs, modules, build/test/lint/CI, data contracts, existing agents, skills, hooks, evaluators, state, memory indexes, reports, `policies/reporting.json` when present, and the Learning Gate policy when present.
3. Derive a purpose hypothesis, deterministic task evaluators, domain graph, ownership boundaries, preservation requirements, and a harness-effect baseline.
4. Do not ask for facts already established by files or prior approved D-001 decisions.
5. Ask at most two batches: core Q1–Q4, then at most four relevant conditional questions. Q4 combines cost sensitivity with user-facing report language and terminology. For a new harness, also ask where reader-facing Change Reports and Learning Assist copies should be organized: `file|notion|slack`, defaulting to `file`. If `notion` or `slack` is selected, require a user-supplied page/database/channel/conversation identifier or URL; never guess it.
6. When the user delegates choices, apply the schema 1.1 defaults, `file` reporting destination, and Claude, Codex, and Gemini targets, then disclose them in the delivery report.

## 3. Common design contract

### 3.1 Communication and reading cost

New harnesses include:

```json
{
  "limits": {"max_instruction_lines": 120},
  "communication": {
    "artifact_language": "en",
    "report_language": "en",
    "terminology": "technical-english"
  },
  "memory": {
    "max_document_lines": 80,
    "max_summary_chars": 160
  }
}
```

They also include a separate project-owned reporting policy:

```json
{
  "schema_version": "1.0",
  "reader_destination": "file",
  "reader_target": "harness/reports",
  "canonical_evidence": "file",
  "style": "plain-language-first"
}
```

- `communication.artifact_language` is fixed to `en`. Canonical skills, roles, memory, loops, and machine-readable prose use concise English without bilingual duplication.
- Wrap an exact non-English project name or machine token in backticks; keep surrounding canonical prose English.
- `communication.report_language` accepts the supported BCP-47-style tag selected during setup. `communication.terminology` is `technical-english|localized`.
- `technical-english` uses report-language grammar but keeps stable technical nouns such as `harness`, `agent`, `skill`, `evaluator`, `baseline`, `control`, and `treatment` in English.
- `localized` translates explanatory technical nouns when a conventional local term exists. Use one natural prose style, not parallel bilingual output.
- Report settings affect user-facing narrative only. Never translate IDs, paths, commands, evidence, JSON keys, status values, trigger reasons, or verdicts.
- `policies/reporting.json` controls only where reader-facing copies are organized and the readability style. `file` is the default; `notion|slack` require an explicit user target. `canonical_evidence` remains `file` even for external reader copies.
- `plain-language-first` means concrete behavior -> reason -> execution flow -> relevant code -> technical term only when useful. Prefer wording a developer would naturally use with a teammate and avoid literal translation-like nouns or unnecessary abstraction.
- Every completed work unit leaves a short `reports/<change-id>/CHANGE-REPORT.md`. It is supporting documentation, not a delivery gate, and should stay to one screen or roughly one page instead of restating the full diff.
- Learning Assist starts from the Change Report and reads only relevant actual diff/source. On ordinary work it runs only when the user asks for deeper explanation or a comprehension check.
- When the Learning Gate is enabled and applicable, the Gate depends on Learning Assist: produce the Change Report, expand the actual diff with the same explanation contract, let the developer read it, then quiz. The Gate must not create a second denser vocabulary.
- A Learning Assist quiz while the Gate is disabled is advisory and non-blocking. Wrong-answer remediation is progressive: first directional hint, second concrete scenario/counterexample, final failed attempt recorded before direct concept explanation. If confusing wording or an undefined term caused the miss, rewrite before counting it as a comprehension failure.
- Exclude `communication.report_language` and `communication.terminology` from the harness-effect canonical hash. Reader-destination changes are presentation/routing changes unless they modify effect-bearing instructions.
- Use index-first progressive disclosure. Split references before a configured limit, or record the correct English exception marker and reason.

### 3.2 Domains and agents

- Derive roles from project boundaries; do not copy a fixed team.
- The capability union includes `routing`, `execution`, `verification`, `verdict`, `defect-counting`, and `improvement`.
- Each agent declares lane, capabilities, domains, access, and an abstract `fast|balanced|deep` tier.
- Vendor model names live only in provider adapters.
- Normal handoff is a DAG. Represent retry and improvement feedback as loops, not reverse DAG edges.

### 3.3 Evaluator links

Every schema 1.1 `skills[].evaluator` is valid:

- `entry|evaluation|verification|domain` → `scope: task`; verification uses the structural validator.
- `harness-evaluation|improvement` → `self_evaluation.evaluator` with `scope: harness` and `type: experiment`.

Keep executor, task evidence runner, and task verdict owner distinct in the contract, even if one small-project agent fills multiple roles. A task failure does not by itself prove a harness defect.

### 3.4 Approval gates

Record every human approval boundary in `approval_gates` with `id`, `trigger`, `owner`, and `required_action`. Do not rely on provider-only free text for a gate.

## 4. `build-harness` transaction

1. Resolve `create|improve|reconcile`; freeze baseline, ownership, preservation manifest, existing reporting policy, Learning Gate state, and classified delta plan.
2. Build or migrate the schema 1.1 spec with evaluator links, communication settings, memory, reading budgets, and event-driven self-evaluation.
3. Validate JSON keys, IDs, relative paths, references, limits, and DAGs.
4. Render concise English team, agent, skill, loop, recovery, budget, state, ledger, and `memory/INDEX.md` canonical artifacts.
5. Render `policies/reporting.json`, the Change Report template, Learning Assist templates/contract, the disabled-by-default Learning Gate policy/templates, task evaluators, and the `scope: harness`, `type: experiment` evaluator.
6. Map `cost-regression|retry-pressure|deterministic-sample` to fixed deterministic metrics in `evaluation/suites/targeted.json`.
7. Render the checker, recorder, Learning Gate verifier, and self-evaluation state.
8. Hash the effect-bearing canonical contract separately. Exclude ordinary memory content, index rows, per-change reports/learning answers, and presentation-only communication fields. Put only exact selected-provider managed artifacts in `watched_paths`.
9. Project every selected provider adapter, including root guidance for the reporting/Learning Assist/Gate flow.
10. Run the validator, instruction and memory budgets, provider parity, linked task evaluators, cold-start, Learning Assist/reporting contract checks, Learning Gate contract checks, and `CHECKLIST.md`.
11. Run and ACK a baseline full evaluation, or explicitly leave the initial mandatory event pending.

Initial self-evaluation state uses empty managed hashes and a `canonical-contract-change` pending event. Never watch an entire provider root or unrelated user agent/skill directory.

## 5. Atomic build transaction

`build-agent`, `build-skill`, and `build-evaluator` use one transaction:

1. Read the spec, state, ledger, selected providers, `policies/reporting.json` when present, report settings, Learning Gate state, and only relevant indexed memory.
2. Freeze baseline, ownership, and the preservation manifest.
3. Run `verify-harness` before mutation.
4. Analyze conflicting IDs and affected handoffs or evaluator links.
5. Update the spec and concise English canonical component first. Update durable memory and its index atomically.
6. Reproject the exact affected artifacts for every selected provider.
7. Add only exact generated projection, wrapper, root guidance, and config paths to `watched_paths`.
8. Add the appropriate mandatory event once.
9. Run `verify-harness`, parity, budgets, memory, preservation, and affected task evaluators. Repair structural or new parity failures before effect evaluation.
10. Rerun the checker and route only a valid decision.

Event mapping is agent → `agent-change`, skill → `skill-change`, evaluator → `evaluator-change`, common effect contract → `canonical-contract-change`, and provider artifact → `adapter-change`. A report-language, terminology, or reader-destination-only change is presentation/routing-only unless it changes effect-bearing instructions. Never reinitialize queues, append-only ledgers, evaluation runs, existing Learning Gate evidence, or an existing reporting target.

## 6. Provider projection

Read IDs and paths from `providers/<id>/contract.json`.

### Claude

- Preserve content outside the managed block in `CLAUDE.md`.
- Copy each canonical skill byte-identically to `.claude/skills/<skill-id>/SKILL.md`.
- Generate `.claude/agents/<namespace>-<role-id>.md`.
- Root guidance points to `policies/reporting.json`, Learning Assist, and the Learning Gate without changing their common semantics.
- A `read-only` agent receives no write or shell capability.

### Codex

- Preserve content outside the managed block in `AGENTS.md`.
- Copy each canonical skill byte-identically to `.agents/skills/<skill-id>/SKILL.md`.
- Generate `.codex/agents/<namespace>-<role-id>.toml`.
- Structurally merge only related agent limits into `.codex/config.toml`; preserve unrelated settings.
- Root guidance points to `policies/reporting.json`, Learning Assist, and the Learning Gate without changing their common semantics.

### Gemini

- Preserve content outside the managed block in `GEMINI.md`.
- Copy each canonical skill byte-identically to `.gemini/skills/<skill-id>/SKILL.md`.
- Generate `.gemini/agents/<namespace>-<role-id>.md`.
- Root guidance points to `policies/reporting.json`, Learning Assist, and the Learning Gate without changing their common semantics.
- The entry or main orchestrator owns DAG sequencing. A wrapper references the common role contract and does not call another subagent.

Adapters are thin wrappers. They do not duplicate role meaning as another source of truth.

## 7. Event-driven self-evaluation

Schema 1.1 records checker, recorder, state, harness evaluator, targeted suite, sampling, interval, cooldown, budget, thresholds, mandatory events, and exact `watched_paths`. At each task boundary, route in this order:

1. `input-invalid:*` → block effect evaluation and LLM use; run `verify-harness`, structural recovery, and recheck.
2. `adapter-change|parity-fail` → require provider parity to pass, then recheck. Record cold-start false-to-true and parity pass-to-fail transitions once.
3. Automatic `none` → stop. An explicit user-requested full run preserves the complete raw checker JSON in `override.original`, sets top-level `decision: full`, `mandatory: false`, and `override.kind: explicit-user-request`, appends its marker after original reasons, and retains the same deferred reasons, hashes, and `acknowledgement`. This structured override may bypass budget and cooldown only; it never bypasses invalid input or parity.
4. `targeted` → run only the fixed metric mapped to `cost-regression|retry-pressure|deterministic-sample`. No arbitrary targeted LLM judge.
5. `full` → run the harness experiment.

The checker is read-only and returns only `none|targeted|full`. A trigger is not an improvement command. The existing completed-task state transaction updates `current_unit`, increments `units_since_full` once, applies `cooldown_remaining_units = max(0, n-1)` once, and records recent and rolling raw evidence without another LLM call.

## 8. `evaluate-harness` contract

- Compare baseline, control, and treatment with the same evaluator, pass conditions, and arm conditions.
- Insufficient samples, mismatched arms, or an evaluator not run yields `inconclusive`.
- Freeze checker JSON at `<target>/harness/evaluation/runs/<run-id>/trigger.json` before evaluation.
- After every completed `targeted|full` run, call:

```powershell
python <target>\harness\triggers\record_self_evaluation.py <target>\harness --decision <targeted|full> --decision-file <target>\harness\evaluation\runs\<run-id>\trigger.json --verdict <improved|neutral|regressed|inconclusive>
```

The recorder verifies frozen decision and reasons, current managed hashes, and the acknowledgement failure snapshot. A full ACK consumes only the pending and failure snapshots captured at start, then updates canonical/provider hashes, units, cooldown, and verdict. A targeted ACK updates its last decision, verdict, and cooldown but consumes no mandatory event. Preserve incidents that occur during evaluation. Never replace frozen reasons with a later rolling-metric decision or ACK an incomplete or stale run.

Pass only an attributed regression or harness defect to `improve-harness`.

## 9. `improve-harness` contract

Entry requires a completed full report with harness attribution or an explicit evidence-backed user request. Resolve structural damage and parity first.

1. Confirm attribution and target metric.
2. Freeze baseline, preservation manifest, delta plan, and rollback conditions in `maintenance/runs/<change-id>/`.
3. Choose one hypothesis and at most two component changes.
4. Update the common spec and canonical documents first.
5. Reproject every selected provider.
6. Run `verify-harness`, budgets, cold-start, parity, and the original task evaluator.
7. Freeze a new checker decision and run the same full harness experiment.
8. ACK the completed full run.
9. Accept `improved` or explicitly pre-approved `neutral` only.
10. Safely roll back `regressed|inconclusive` and retain all evidence.

Evaluator weakening, approval-gate bypass, evidence deletion, hidden failures, unrelated state reset, one-provider semantic drift, Learning Gate state changes without explicit user instruction, and guessed external report targets are forbidden.

## 10. Validation and delivery

Run:

```powershell
python <FACTORY_ROOT>\scripts\validate_runtime_neutral.py <target>
python <target>\harness\triggers\check_self_evaluation.py <target>\harness
# After a completed targeted/full run, use the recorder command in section 8.
```

Run the structural, provider, evaluator, trigger-fixture, preservation, budget, cold-start, reporting/Learning Assist, and Learning Gate checklists. Make at most three correction rounds, and disclose every remaining failure.

The delivery report follows `communication.report_language` and `communication.terminology` while keeping technical tokens exact. Include mode, delta, preservation, files changed, retained state and ledger, defaults, topology, providers, reader destination, Learning Assist availability, Learning Gate status/ownership, task and harness evaluation commands, trigger/ACK settings, budgets, verification rounds, checks not run, and residual failures.

## 11. Invariants

1. No task unit runs without a task evaluator.
2. No raw evidence and ledger record means no pass.
3. No approval gate is crossed without approval.
4. `state.next_action` is never blank; the journal is append-only.
5. Failures, fallbacks, and checks not run remain visible.
6. Canonical meaning changes before adapter projection.
7. Selected providers preserve equivalent agent, skill, evaluator, gate, handoff, reporting, and Learning Assist meaning.
8. A trigger never modifies the harness by itself.
9. The factory never centrally owns project state.
10. User configuration, durable memory, reporting policy, learning evidence, and unknown-origin files are not deleted, overwritten, translated, renamed, or retargeted without approval.
11. Internal canonical prose is concise English; user-facing presentation remains separate and plain-language-first.
12. Presentation-only communication and reader-destination changes do not affect the harness-effect hash unless they change effect-bearing instructions.
13. A disabled Learning Gate creates no gate-specific blocking work; an enabled applicable Gate uses Learning Assist before the quiz and never fails the user solely for unnecessary vocabulary recall.
14. Notion or Slack reader copies never replace canonical Git evidence, and their target is never guessed.
