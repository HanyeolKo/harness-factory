# Runtime-neutral contract

The target project's `harness/` directory owns canonical meaning and operational state. Harness Factory is a construction tool; Claude, Codex, and Gemini files are discovery and delegation adapters.

## Canonical layers

1. Schema 1.1 `harness/harness-spec.json` defines providers, communication, limits, domains, roles, skills, DAG, evaluators, gates, memory, loops, and self-evaluation.
2. `team/agents/<role-id>.md` and `skills/<skill-id>/SKILL.md` hold provider-neutral meaning.
3. `loops/` separates execution, task evaluation, harness-effect evaluation, and improvement.
4. `policies/learning-gate.json`, `policies/LEARNING-GATE.md`, `learning/`, and `triggers/verify_learning_gate.py` define the optional project-owned learning speed regulator.
5. `state/`, append-only `ledger/`, `evaluation/`, `learning/`, and `memory/` remain in the target project and are never sent to the factory.
6. `providers/<id>/contract.json` declares native projection paths and capabilities.

## Language and context

- New canonical artifacts use concise English: `communication.artifact_language: en`.
- `communication.report_language` is a language tag chosen during setup; default `en`.
- `communication.terminology` is `technical-english|localized`; default `technical-english`.
- `technical-english` uses `report_language` grammar but keeps stable technical nouns such as `harness`, `agent`, `skill`, `evaluator`, `baseline`, `control`, and `treatment` in English.
- `localized` translates explanatory technical nouns when a conventional local term exists. Both modes preserve machine tokens and stored verdicts such as `pass|fail` exactly, and neither mode duplicates bilingual prose.
- These presentation fields affect only user-facing narrative. IDs, commands, paths, evidence, JSON keys, reason/status/verdict values, and stored machine reports stay exact.
- Do not duplicate bilingual prose in canonical files. Normalize user prose into concise English for canonical artifacts.
- Wrap an exact non-English project name or machine token in backticks and keep its surrounding canonical prose English.
- Existing 1.0/1.1 specs without `communication` remain valid and use the English defaults until additively configured.
- Presentation-only report language and terminology are excluded from the harness-effect canonical hash. Artifact language and instructions remain effect-bearing.
- `limits.max_instruction_lines`, `memory.max_document_lines`, and `memory.max_summary_chars` bound reading cost when present. Read an index first, then only relevant documents. On `none`, do not load evaluation or improvement references.

## Common semantics

- IDs are lower-kebab-case. Agent models use abstract `fast|balanced|deep` tiers.
- Normal handoffs form a DAG; retries and improvement feedback live in loop contracts.
- Every schema 1.1 skill links an evaluator:
  - entry/evaluation/verification/domain → `scope: task`
  - harness-evaluation/improvement → `self_evaluation.evaluator`, `scope: harness`, `type: experiment`
- Human approval is a stable-ID gate, not an evaluator.
- Change the common spec and canonical file before every selected adapter.

## Optional learning gate

Every newly generated harness installs the learning gate but sets `policies/learning-gate.json.enabled` to `false`.

- `control.owner` is `user`.
- `control.agents_may_change_enabled` is `false`.
- `control.activation_requires_explicit_user_instruction` is `true`.
- An agent may explain or recommend the gate, but only an explicit user instruction may change `enabled`.
- `improve|reconcile` preserves the existing enabled value and existing learning evidence.
- Disabled means no per-change learning artifacts, no quiz work, and no review, PR, or merge blocking.
- Enabled applies only under the configured scope. The default scope is risk-based, with a changed-line threshold, risk tags, and low-risk exemptions.
- Applicable changes require a pre-change brief, an explanation based on the actual diff, five medium-difficulty questions with at least three free-text items, developer-authored answers, and deterministic verification.
- Verification binds SHA-256 hashes of `quiz.json` and `answers.json` to a committed source snapshot. That source commit contains the code and the first four learning artifacts; only the committed `verification.json` may change between it and a clean `HEAD`. Matching risk tags override low-risk exemptions. Stale, uncommitted, path-escaped, or missing evidence is a failure.
- The implementation agent must not author the developer's answers or act as the sole semantic judge of an ambiguous answer.
- Learning verification is task-understanding evidence and a delivery gate. It is separate from harness-effect evaluation and does not establish that the harness improved.

Generated paths are:

```text
harness/
├── policies/
│   ├── learning-gate.json
│   └── LEARNING-GATE.md
├── learning/
│   ├── _templates/
│   └── <change-id>/
└── triggers/
    └── verify_learning_gate.py
```

## Existing harnesses

Classify no harness as `create`, a valid runtime-neutral spec as `improve`, and a partial/legacy harness as `reconcile`. Before `improve|reconcile`, freeze original validator/evaluator results, ownership, and `preservation-before.json`; apply only a classified `unchanged|add|modify-proposed|conflict|approval-required` delta.

Preserve existing IDs, state, append-only ledger, evaluation runs, evaluators, gates, root rules, user-owned or unknown files, durable memory, learning evidence, and the user's learning-gate enabled value. Deletion, rename, semantic replacement, split, merge, or a learning-gate state change needs explicit approval. Upsert only namespaced managed blocks and generated adapters. Completion requires the new contract, original evaluators, and preservation comparison to pass.

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

Each root guidance block points to `policies/learning-gate.json`, states its current user-owned control rule, and invokes the verifier only when enabled and applicable. Provider adapters must not add a runtime-specific learning-gate meaning or toggle state.

Before any provider write, require provider-path preflight. Reject absolute paths, lexical traversal, and symlink escape. On failure, do not create, write, move, or bypass the provider path.

## Watched artifacts

The checker hashes effect-bearing `harness/` canonical files separately. `self_evaluation.watched_paths` lists only selected providers' exact:

- root guidance file;
- projection for every spec skill;
- namespaced wrapper for every spec role;
- generated provider config.

Never watch a provider directory, unrelated user skill/agent, unselected provider, or the factory repository. Per-change learning answers and verification records are task evidence, not provider parity artifacts.

## Event-driven self-evaluation

1. At a task boundary, run only the read-only deterministic checker. It returns compact JSON `none|targeted|full`, never writes state, calls an LLM, or returns `improve`.
2. `input-invalid:*` is not effect evidence. Run `verify-harness`, recover structure, and recheck without an LLM evaluator.
3. `adapter-change|parity-fail` requires provider parity before effect evaluation. Record cold-start false→true and parity pass→fail transitions once.
4. `targeted` runs only the declared deterministic suite mapping:
   - `cost-regression` → fixed cost metric;
   - `retry-pressure` → fixed retry metric;
   - `deterministic-sample` → fixed sample fixture/metric.
5. `full` runs the linked experiment under identical baseline/control/treatment conditions.
6. `minimum_samples` applies to success/cost comparisons only. Sampling is independent. Budget and cooldown defer every non-mandatory signal; canonical/agent/skill/evaluator/adapter changes, cold-start/parity incidents, and repeated failures are mandatory.

## Recorder and ACK

Freeze checker JSON before evaluation, then ACK each completed targeted/full run:

```text
python harness/triggers/record_self_evaluation.py harness --decision <targeted|full> --decision-file harness/evaluation/runs/<run-id>/trigger.json --verdict <improved|neutral|regressed|inconclusive>
```

An explicit full request preserves raw checker JSON under `override.original` and uses the structured override shared by evaluator and recorder. Direct decision mutation or unstructured budget/cooldown bypass is invalid.

The recorder verifies frozen decision/reasons, current managed hashes, and the acknowledgement failure snapshot. Full ACK consumes only the processed pending/reason and frozen failure snapshots, then refreshes canonical/provider hashes, units, cooldown, and verdict. Targeted ACK updates last decision/verdict and cooldown without consuming mandatory events. Preserve incidents created during evaluation. Never ACK incomplete, stale, or mismatched runs.

## Improvement

Open a candidate only after a full regression or attributed harness defect, or an explicit evidence-backed user request. Freeze baseline and preservation evidence; change one hypothesis and at most two components; update common spec/canonical files, selected adapters, memory index, and decision record atomically. Run structural/task verification, parity, cold-start, and the same full suite. Accept `improved` or explicitly approved `neutral`; revert `regressed|inconclusive` while retaining evidence.

## Compatibility

The validator reads schema 1.0 and 1.1. Version 1.0 does not require memory, self-evaluation files, skill evaluator links, communication, or a learning gate. Existing 1.1 specs may omit communication and new reading-cost fields. New harnesses include memory, event-driven self-evaluation, the disabled-by-default user-controlled learning gate, concise-English artifacts, selectable report presentation, and explicit instruction/memory budgets.
