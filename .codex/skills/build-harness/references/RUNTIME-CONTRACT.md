# Runtime-neutral contract

The target project's `harness/` directory owns canonical meaning and operational state. Harness Factory is a construction tool; Claude, Codex, and Gemini files are discovery and delegation adapters.

## Canonical layers

1. Schema 1.1 `harness/harness-spec.json` defines providers, communication, limits, domains, roles, skills, DAG, evaluators, gates, memory, loops, and self-evaluation.
2. `team/agents/<role-id>.md` and `skills/<skill-id>/SKILL.md` hold provider-neutral meaning.
3. `loops/` separates execution, task evaluation, harness-effect evaluation, and improvement.
4. `policies/reporting.json`, `reports/`, the Learning Assist contract, `policies/learning-gate.json`, `policies/LEARNING-GATE.md`, `learning/`, and `triggers/verify_learning_gate.py` define change comprehension and the optional project-owned learning gate.
5. `state/`, append-only `ledger/`, `evaluation/`, `learning/`, reports, and `memory/` remain in the target project and are never sent to the factory.
6. `providers/<id>/contract.json` declares native projection paths and capabilities.

## Language, readability, and reporting

- New canonical artifacts use concise English: `communication.artifact_language: en`.
- `communication.report_language` is a language tag chosen during setup; default `en`.
- `communication.terminology` is `technical-english|localized`; default `technical-english`.
- `technical-english` uses `report_language` grammar while retaining stable technical nouns such as `harness`, `agent`, `skill`, `evaluator`, `baseline`, `control`, and `treatment`.
- `localized` translates explanatory technical nouns when a conventional local term exists. Both modes preserve machine tokens and stored verdicts such as `pass|fail` exactly, and neither mode duplicates bilingual prose.
- These presentation fields affect only user-facing narrative. IDs, commands, paths, evidence, JSON keys, reason/status/verdict values, and stored machine reports stay exact.
- Do not duplicate bilingual prose in canonical files. Normalize user prose into concise English for canonical artifacts.
- Wrap an exact non-English project name or machine token in backticks and keep its surrounding canonical prose English.
- Existing 1.0/1.1 specs without `communication` remain valid and use the English defaults until additively configured.
- Presentation-only report language and terminology are excluded from the harness-effect canonical hash. Artifact language and instructions remain effect-bearing.
- Reader-facing Change Reports and Learning Assist explanations use the `plain-language-first` style declared in `policies/reporting.json`.
- Plain-language-first means: concrete behavior -> reason -> execution flow -> relevant code -> technical term only when useful.
- Prefer wording a developer would naturally use when explaining the change to a teammate. Avoid literal translation-like nouns and unnecessary architecture abstraction.
- Keep identifiers, commands, paths, API names, table names, evidence tokens, status values, and conventional technical terms exact.
- In `localized` mode, use natural report-language prose, preserve machine tokens rather than surrounding jargon, and introduce optional exact terminology once after the behavior is clear.
- During new-harness setup, ask where reader-facing reports should be organized. Allowed destinations are `file|notion|slack`; default is `file`.
- Store that choice in `harness/policies/reporting.json`.
- For `file`, default `reader_target` to `harness/reports`. For `notion` or `slack`, require a user-supplied target identifier or URL. Never guess an external target.
- `canonical_evidence` remains `file`: Git files are always the verification source even when a reader copy is published externally.
- Existing 1.0/1.1 harnesses without `policies/reporting.json` remain valid. Add it only as a preservation-aware delta.
- Presentation-only language, terminology, reader destination, and external publication do not by themselves establish harness-effect improvement.
- `limits.max_instruction_lines`, `memory.max_document_lines`, and `memory.max_summary_chars` bound reading cost when present. Read an index first, then only relevant documents.

## Common semantics

- IDs are lower-kebab-case. Agent models use abstract `fast|balanced|deep` tiers.
- Normal handoffs form a DAG; retries and improvement feedback live in loop contracts.
- Every schema 1.1 skill links an evaluator:
  - entry/evaluation/verification/domain -> `scope: task`
  - harness-evaluation/improvement -> `self_evaluation.evaluator`, `scope: harness`, `type: experiment`
- Human approval is a stable-ID gate, not an evaluator.
- Change the common spec and canonical file before every selected adapter.

## Change Report

Every completed work unit produces a short canonical report at:

```text
harness/reports/<change-id>/CHANGE-REPORT.md
```

The Change Report is supporting documentation and does not block delivery. Keep it to one screen or roughly one page and include only what changed, why, important impact/flow, key files, actual validation, and anything the developer should know next.

If the reporting policy selects `notion` or `slack`, publish a reader copy to the configured target when that integration is available. Report publication failure clearly. Do not invalidate valid Git evidence merely because an external copy failed unless the user explicitly made publication a delivery requirement.

## Learning Assist

Learning Assist is the shared comprehension layer. It starts from the Change Report and reads only the relevant actual diff/source.

- On ordinary work, invoke it only when the user asks for deeper explanation or a comprehension check.
- When the Learning Gate is enabled and applicable, invoke Learning Assist automatically before the gate quiz.
- The gate's `diff-explanation.md` uses this same explanation contract; do not create a second denser vocabulary.
- A voluntary comprehension quiz while the gate is disabled is advisory and never blocks delivery.
- Questions test mental models, not vocabulary recall.
- Before publishing, check for one main idea per sentence, no more than three new concepts, and no unexplained mixed-language nouns outside machine tokens.
- Wrong-answer remediation is progressive: first miss directional hint, second miss concrete scenario/counterexample, final miss record failure then explain the concept.
- If confusing wording or an undefined term caused a miss, rewrite before counting it as a comprehension failure.

## Optional Learning Gate

Every newly generated harness installs the Learning Gate but sets `policies/learning-gate.json.enabled` to `false`.

- `control.owner` is `user`.
- `control.agents_may_change_enabled` is `false`.
- `control.activation_requires_explicit_user_instruction` is `true`.
- Only an explicit user instruction may change `enabled`.
- `improve|reconcile` preserves the existing enabled value and existing learning evidence.
- Disabled means no per-change learning artifacts, no quiz work, and no review, PR, or merge blocking.
- Enabled applies only under the configured scope. The default scope remains risk-based with a changed-line threshold, risk tags, and low-risk exemptions.

For an applicable change, the flow is:

```text
pre-change brief
-> implementation
-> task validation
-> short Change Report
-> Learning Assist explanation from actual diff
-> developer reads explanation
-> five-question Learning Gate quiz
-> pass or hint-based retry
-> deterministic verification
```

The source commit still contains the code plus `brief.md`, `diff-explanation.md`, `quiz.json`, and developer-authored `answers.json`. `verification.json` records the full source commit SHA, score, required-concept result, attempt count, and hashes. Only committed `verification.json` may follow that source snapshot before a clean verified `HEAD`.

Matching risk tags override low-risk exemptions. Stale, uncommitted, path-escaped, or missing evidence is a failure. The implementation agent must not author the developer's answers or act as the sole semantic judge of an ambiguous answer.

Learning verification is task-understanding evidence and a delivery gate. It is separate from harness-effect evaluation and does not establish that the harness improved.

Generated paths are:

```text
harness/
├── policies/
│   ├── reporting.json
│   ├── learning-gate.json
│   └── LEARNING-GATE.md
├── reports/
│   └── <change-id>/CHANGE-REPORT.md
├── learning-assist/
│   ├── _templates/
│   │   ├── explanation.md.tmpl
│   │   ├── quiz.json.tmpl
│   │   └── comprehension.json.tmpl
│   └── <change-id>/        # created only for user-requested durable Assist output
├── learning/
│   ├── _templates/
│   └── <change-id>/
└── triggers/
    └── verify_learning_gate.py
```

## Existing harnesses

Classify no harness as `create`, a valid runtime-neutral spec as `improve`, and a partial/legacy harness as `reconcile`. Before `improve|reconcile`, freeze original validator/evaluator results, ownership, and `preservation-before.json`; apply only a classified `unchanged|add|modify-proposed|conflict|approval-required` delta.

Preserve existing IDs, state, append-only ledger, evaluation runs, evaluators, gates, root rules, user-owned or unknown files, durable memory, learning evidence, reports, the user's Learning Gate enabled value, and any existing reporting policy. Deletion, rename, semantic replacement, split, merge, gate-state change, or reader-destination change needs explicit approval. Upsert only namespaced managed blocks and generated adapters. Completion requires the new contract, original evaluators, and preservation comparison to pass.

## Memory

Schema 1.1 memory uses `harness/memory/INDEX.md` with `preserve-and-reconcile`. New indexes use:

```text
ID | Path | Summary | Read when | Source | Last verified | Status
```

Statuses are `active|superseded|archived|empty`. Active paths must exist inside the target. IDs and paths are unique; memory must not duplicate task state or event history. Summaries and documents obey configured budgets.

Create, move, rename, supersede, archive, and index updates are one transaction. Ordinary memory content and index rows are excluded from the full-trigger hash and get deterministic verification. Memory policy and routing in the spec or `HARNESS.md` are effect-bearing canonical changes.

## Provider adapters

| Provider | Root guidance | Skill projection | Agent projection |
|---|---|---|---|
| Claude | `CLAUDE.md` managed block | `.claude/skills/<skill-id>/SKILL.md` | `.claude/agents/<namespace>-<role-id>.md` |
| Codex | `AGENTS.md` managed block | `.agents/skills/<skill-id>/SKILL.md` | `.codex/agents/<namespace>-<role-id>.toml` |
| Gemini | `GEMINI.md` managed block | `.gemini/skills/<skill-id>/SKILL.md` | `.gemini/agents/<namespace>-<role-id>.md` |

Skills are byte-identical to canonical files. Agent wrappers contain only minimal native metadata and the common role path. The Gemini main orchestrator owns DAG sequencing; Gemini subagents do not recursively delegate.

Each root guidance block points to `policies/reporting.json` when present and `policies/learning-gate.json`, states the current user-owned gate control rule, and invokes the verifier only when the gate is enabled and applicable. Provider adapters must not add runtime-specific Learning Gate meaning, invent an external report target, toggle gate state, or create provider-specific grading semantics.

Before any provider write, require provider-path preflight. Reject absolute paths, lexical traversal, and symlink escape. On failure, do not create, write, move, or bypass the provider path.

## Watched artifacts and self-evaluation

The checker hashes effect-bearing `harness/` canonical files separately. `self_evaluation.watched_paths` lists only selected providers' exact:

- root guidance file;
- projection for every spec skill;
- namespaced wrapper for every spec role;
- generated provider config.

Never watch a provider directory, unrelated user skill/agent, unselected provider, or the factory repository. Per-change reports, learning answers, and verification records are task evidence rather than provider parity artifacts.

## Event-driven self-evaluation

1. At a task boundary, run only the read-only deterministic checker. It returns compact JSON `none|targeted|full`, never writes state, calls an LLM, or returns `improve`.
2. `input-invalid:*` is not effect evidence. Run `verify-harness`, recover structure, and recheck without an LLM evaluator.
3. `adapter-change|parity-fail` requires provider parity before effect evaluation. Record cold-start false->true and parity pass->fail transitions once.
4. `targeted` runs only the declared deterministic suite mapping:
   - `cost-regression` -> fixed cost metric;
   - `retry-pressure` -> fixed retry metric;
   - `deterministic-sample` -> fixed sample fixture/metric.
5. `full` runs the linked experiment under identical baseline/control/treatment conditions.
6. `minimum_samples` applies to success/cost comparisons only. Sampling is independent. Budget and cooldown defer every non-mandatory signal; canonical/agent/skill/evaluator/adapter changes, cold-start/parity incidents, and repeated failures are mandatory.

## Recorder and ACK

Freeze checker JSON before evaluation, then ACK each completed targeted/full run:

```text
python harness/triggers/record_self_evaluation.py harness --decision <targeted|full> --decision-file harness/evaluation/runs/<run-id>/trigger.json --verdict <improved|neutral|regressed|inconclusive>
```

An explicit full request preserves raw checker JSON under `override.original` and uses the structured override shared by evaluator and recorder. Direct decision mutation or unstructured budget/cooldown bypass is invalid.

The recorder verifies frozen decision/reasons, current managed hashes, and the acknowledgement failure snapshot. Full ACK consumes only the processed pending/reason and frozen failure snapshots, then refreshes canonical/provider hashes, units, cooldown, and verdict. Targeted ACK updates last decision/verdict and cooldown without consuming mandatory events. Preserve incidents created during evaluation. Never ACK incomplete, stale, or mismatched runs.

Learning Gate verification is separate from harness-effect evaluation. It verifies developer-understanding evidence for the current change; it does not establish that the harness improved.

## Improvement

Open a candidate only after a full regression or attributed harness defect, or an explicit evidence-backed user request. Freeze baseline and preservation evidence; change one hypothesis and at most two components; update common spec/canonical files, selected adapters, memory index, and decision record atomically. Run structural/task verification, parity, cold-start, and the same full suite. Accept `improved` or explicitly approved `neutral`; revert `regressed|inconclusive` while retaining evidence.

## Compatibility

The validator reads schema 1.0 and 1.1. Version 1.0 does not require memory, self-evaluation files, skill evaluator links, communication, a reporting policy, or a Learning Gate. Existing 1.1 specs may omit communication, a reporting policy, and new reading-cost fields. New harnesses include memory, event-driven self-evaluation, a separate reporting policy, lightweight Change Reports, selectable reader destination, Learning Assist, the disabled-by-default user-controlled Learning Gate, concise-English canonical artifacts, and explicit instruction/memory budgets.
