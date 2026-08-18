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
- Reader-facing Change Reports and Learning Assist explanations use the `plain-language-first` style declared in `policies/reporting.json`.
- Plain-language-first means: concrete behavior -> reason -> execution flow -> relevant code -> technical term only when useful.
- Prefer wording a developer would naturally use when explaining the change to a teammate. Avoid literal translation-like nouns and unnecessary architecture abstraction.
- Keep identifiers, commands, paths, API names, table names, evidence tokens, status values, and conventional technical terms exact.
- During new-harness setup, ask where reader-facing reports should be organized. Allowed destinations are `file|notion|slack`; default is `file`.
- Store that choice in `harness/policies/reporting.json`.
- For `file`, default `reader_target` to `harness/reports`. For `notion` or `slack`, require a user-supplied target identifier or URL. Never guess an external target.
- `canonical_evidence` remains `file`: Git files are always the verification source even when a reader copy is published externally.
- Existing 1.0/1.1 harnesses without `policies/reporting.json` remain valid. Add it only as a preservation-aware delta.
- Presentation-only language, terminology, reader destination, and external publication do not by themselves establish harness-effect improvement.
- `limits.max_instruction_lines`, `memory.max_document_lines`, and `memory.max_summary_chars` bound reading cost when present. Read an index first, then only relevant documents.

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
- Wrong-answer remediation is progressive: first miss directional hint, second miss concrete scenario/counterexample, final miss record failure then explain the concept.
- If confusing wording or an undefined term caused a miss, rewrite before counting it as a comprehension failure.

## Optional Learning Gate

Every newly generated harness installs the Learning Gate but sets `policies/learning-gate.json.enabled` to `false`.

- `control.owner` is `user`.
- `control.agents_may_change_enabled` is `false`.
- `control.activation_requires_explicit_user_instruction` is `true`.
- Only an explicit user instruction may change `enabled`.
- `improve|reconcile` preserves the existing enabled value and existing learning evidence.
- Disabled means no gate-specific per-change learning requirements and no review, PR, or merge blocking.
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

Generated paths are:

```text
harness/
├── policies/
│   ├── reporting.json
│   ├── learning-gate.json
│   └── LEARNING-GATE.md
├── reports/
│   └── <change-id>/CHANGE-REPORT.md
├── learning/
│   ├── _templates/
│   └── <change-id>/
└── triggers/
    └── verify_learning_gate.py
```

## Existing harnesses

Classify no harness as `create`, a valid runtime-neutral spec as `improve`, and a partial/legacy harness as `reconcile`. Before `improve|reconcile`, freeze original validator/evaluator results, ownership, and `preservation-before.json`; apply only a classified `unchanged|add|modify-proposed|conflict|approval-required` delta.

Preserve existing IDs, state, append-only ledger, evaluation runs, evaluators, gates, root rules, user-owned or unknown files, durable memory, learning evidence, reports, the user's Learning Gate enabled value, and any existing reporting policy. Deletion, rename, semantic replacement, split, merge, gate-state change, or reader-destination change needs explicit approval. Upsert only namespaced managed blocks and generated adapters.

## Memory

Schema 1.1 memory uses `harness/memory/INDEX.md` with `preserve-and-reconcile`. Current state and events remain in state/ledger rather than memory. Summaries and documents obey configured budgets. Ordinary memory changes receive deterministic verification; policy/routing changes remain effect-bearing canonical changes.

## Provider adapters

| Provider | Root guidance | Skill projection | Agent projection |
|---|---|---|---|
| Claude | `CLAUDE.md` managed block | `.claude/skills/<skill-id>/SKILL.md` | `.claude/agents/<namespace>-<role-id>.md` |
| Codex | `AGENTS.md` managed block | `.agents/skills/<skill-id>/SKILL.md` | `.codex/agents/<namespace>-<role-id>.toml` |
| Gemini | `GEMINI.md` managed block | `.gemini/skills/<skill-id>/SKILL.md` | `.gemini/agents/<namespace>-<role-id>.md` |

Skills are byte-identical to canonical files. Root guidance points to the reporting/Learning Assist flow and Learning Gate policy without changing runtime-neutral meaning. Provider adapters must not toggle gate state, invent an external report target, or create provider-specific grading semantics.

Before any provider write, require provider-path preflight. Reject absolute paths, lexical traversal, and symlink escape.

## Watched artifacts and self-evaluation

The checker hashes effect-bearing canonical files separately. `self_evaluation.watched_paths` lists only selected providers' exact root guidance, skill projections, namespaced wrappers, and generated provider config. Per-change reports, learning answers, and verification records are task evidence rather than provider parity artifacts.

At a task boundary, run only the read-only deterministic checker. `input-invalid:*` routes to structural verification, `adapter-change|parity-fail` restores parity first, targeted evaluation uses fixed deterministic mappings, and full evaluation uses the linked experiment under identical baseline/control/treatment conditions. Freeze checker JSON before evaluation and ACK completed targeted/full runs with the recorder contract.

Learning Gate verification is separate from harness-effect evaluation. It verifies developer-understanding evidence for the current change; it does not establish that the harness improved.

## Improvement

Open a candidate only after a full regression, attributed harness defect, or explicit evidence-backed user request. Freeze baseline/preservation evidence, change one hypothesis and at most two components, update common spec/canonical files and selected adapters atomically, and rerun the frozen suite. Accept `improved` or explicitly approved `neutral`; revert `regressed|inconclusive` while retaining evidence.

## Compatibility

The validator reads schema 1.0 and 1.1. Existing 1.1 specs may omit communication and new reading-cost fields. New harnesses include memory, event-driven self-evaluation, a separate reporting policy, lightweight Change Reports, selectable reader destination, Learning Assist, the disabled-by-default user-controlled Learning Gate, concise-English canonical artifacts, and explicit instruction/memory budgets.
