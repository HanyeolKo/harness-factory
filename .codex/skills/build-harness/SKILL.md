---
name: build-harness
description: Build or migrate a project-owned runtime-neutral agent harness with concise English canonical artifacts, evidence-based evaluation, an optional user-controlled learning gate, incremental improvement, and Claude, Codex, and Gemini adapters. Use for first setup or a full topology redesign; use the smaller build skills for one component.
---

# build-harness

Create or reconcile a harness inside the target project. The project owns its spec, state, evidence, learning artifacts, memory, and improvement history; the factory never absorbs them.

## Use

Classify the target as create|improve|reconcile:

- No `harness/`: `create`.
- Valid runtime-neutral spec: `improve`.
- Partial or legacy harness: `reconcile`.
- Use `build-agent`, `build-skill`, or `build-evaluator` for one component.
- Use `verify-harness` for structure, `evaluate-harness` for measured effect, and `improve-harness` for an attributed defect.

## Resolve the factory

1. Run `scripts/resolve_factory.py`; pass `--factory-root <path>` when known or `--offline` when required.
2. Treat stdout as `FACTORY_ROOT`. Do not bypass a failed contract check with ad hoc templates.
3. Read `docs/CONSTRUCTOR-PROTOCOL.md`, `references/RUNTIME-CONTRACT.md`, `principles/`, `interview/QUESTION-BANK.md`, and `CHECKLIST.md` progressively.
4. Record source URL, ref, and commit in target D-001; omit local paths and credentials.

## Language and reading-cost contract

- New specs include `communication.artifact_language: en`.
- During setup, let the user choose `communication.report_language` and `communication.terminology` (`technical-english|localized`). Default to `en` and `technical-english`.
- `technical-english` uses report-language grammar while retaining stable English technical nouns such as `harness`, `agent`, `skill`, `evaluator`, `baseline`, `control`, and `treatment`.
- `localized` translates explanatory technical nouns when a conventional local term exists. Both modes preserve machine tokens and avoid parallel bilingual prose.
- Write canonical skills, roles, memory, loops, and machine-readable prose in concise English. Normalize user prose into English without changing identifiers, commands, paths, evidence, JSON keys, status values, or verdicts.
- Wrap an exact non-English project name or machine token in backticks and keep its surrounding canonical prose English.
- Apply the report choice only to user-facing narrative. Never store parallel translations in canonical artifacts.
- Use progressive disclosure: read indexes first, open only task-relevant files, and skip evaluation/improvement references on `none`.
- New harnesses set instruction and memory budgets. Existing 1.0/1.1 specs without `communication` remain valid and default to English reports until additively configured; do not auto-translate existing project-owned content.
- Report-only language or terminology changes do not constitute harness-effect changes. Artifact-language or instruction changes do.

## Workflow

1. **Discover** — inspect root rules, README/docs, modules, build/test/CI, existing agents/skills/hooks, evaluator baselines, file ownership, preservation needs, indexed memory, and any existing learning-gate policy. Ask only for unknown purpose, completion criteria, approval boundaries, provider scope, and report language/terminology.
2. **Plan** — record mode and a `unchanged|add|modify-proposed|conflict|approval-required` delta plan under `harness/maintenance/runs/<change-id>/`. In `improve|reconcile`, write `preservation-before.json` first.
3. **Specify** — create schema 1.1 with a valid DAG. Every skill links an evaluator: entry/evaluation/verification/domain to `scope: task`; harness-evaluation/improvement to the `self_evaluation.evaluator`, which is `scope: harness`, `type: experiment`.
4. **Build common** — in `create`, render the spec, HARNESS, team, canonical skills, loops, recovery, budget, state, append-only ledger, evaluation contract, and `memory/INDEX.md`. In other modes, touch only delta-owned files.
5. **Install the learning gate** — every new harness receives `policies/learning-gate.json`, `policies/LEARNING-GATE.md`, `learning/_templates/`, and `triggers/verify_learning_gate.py`. Set `enabled: false` by default. Only an explicit user instruction may change `enabled`; agents may recommend a state but must not toggle it. In `improve|reconcile`, preserve the existing value. When disabled, create no per-change learning artifacts and block no review, PR, or merge step. When enabled and applicable, require a pre-change brief, actual-diff explanation, five-question understanding quiz, developer-authored answers, and verification bound to a committed source snapshot before the configured gates. Matching risk tags override low-risk exemptions.
6. **Budget context** — use `limits.max_instruction_lines`, `memory.max_document_lines`, and `memory.max_summary_chars`; split references before exceeding a budget and retain only routing metadata in indexes.
7. **Install evaluation** — create the full baseline/control/treatment contract and `evaluation/suites/targeted.json`. Map only `cost-regression`, `retry-pressure`, and `deterministic-sample` to fixed deterministic metrics.
8. **Install triggers** — install the read-only checker, completed-run recorder, and learning-gate verifier. The self-evaluation checker alone runs at task boundaries and returns `none|targeted|full`; the learning verifier runs only when its user-controlled policy is enabled and applicable.
9. **Watch exact artifacts** — hash canonical effect-bearing files separately. List only selected providers' exact root guidance, skill projections, namespaced agent wrappers, and generated config in `self_evaluation.watched_paths`. Learning answers and per-change verification evidence remain project-owned task evidence rather than harness-effect watched artifacts.
10. **Preflight adapters** — before provider writes, require:

   ```text
   python <FACTORY_ROOT>/scripts/validate_runtime_neutral.py <target> --provider-path-preflight
   ```

   On failure, do not create, write, move, or route around provider paths.
11. **Project adapters** — preserve user text outside managed blocks and render Claude (`CLAUDE.md`, `.claude/skills`, `.claude/agents`), Codex (`AGENTS.md`, `.agents/skills`, `.codex/agents`, `.codex/config.toml`), and Gemini (`GEMINI.md`, `.gemini/skills`, `.gemini/agents`) as selected. Each root guidance block points to the learning policy and states that agents cannot change its enabled state.
12. **Expose workflows** — create `<id>`, `<id>-eval`, `<id>-verify`, `<id>-evaluate`, and `<id>-improve`; keep legacy `-retro` only as an alias.
13. **Validate** — run the validator, memory/index checks, linked evaluators, provider parity, cold-start test, and `python <FACTORY_ROOT>/scripts/test_learning_gate_contract.py`. Compare `preservation-after.json` with the baseline. Record new `coldstart-fail` or `parity-fail` transitions once.
14. **Repair** — repair common canonical files first and reproject every selected adapter, for at most three rounds. Disclose residual failures.

## Preservation

Preserve existing IDs, state, append-only ledger, evaluation runs, gates, evaluator semantics, user rules, unknown-ownership files, durable memory, learning evidence, and the user's learning-gate `enabled` value. Deletion, rename, semantic replacement, split, merge, or learning-gate state change requires an exact field/path proposal and explicit approval. Upsert only namespaced managed blocks and generated adapters. Never move an installed harness into the factory package.

Memory uses `harness/memory/INDEX.md` with `preserve-and-reconcile`. Create, move, supersede, archive, and index updates are one transaction. Keep current state in `state.json` and events in `journal.jsonl`, not memory. Ordinary memory changes get deterministic verification; policy or routing changes are canonical effect changes.

## Evaluation and ACK

- Route `input-invalid:*` to verification and structural recovery without effect evaluation or an LLM.
- Require provider parity before evaluating `adapter-change|parity-fail`.
- On `none`, load no evaluation or improvement workflow.
- On `targeted`, run only the fixed reason mapping. On `full`, run the linked experiment.
- Freeze checker JSON in `evaluation/runs/<run-id>/trigger.json`. A user-requested full run must preserve the raw decision under `override.original` and use the structured override contract.
- ACK every completed targeted/full run:

```text
python <target>/harness/triggers/record_self_evaluation.py <target>/harness --decision <targeted|full> --decision-file <target>/harness/evaluation/runs/<run-id>/trigger.json --verdict <improved|neutral|regressed|inconclusive>
```

Open improvement only after a full regression or attributed harness defect. Change one hypothesis and at most two components, then rerun the frozen suite.

The learning gate is separate from harness-effect evaluation. Disabled means `skip`. Enabled learning verification establishes developer-understanding evidence for the current change; it does not claim that the harness itself improved.

## Delivery

Report mode, delta, preservation, created/changed files, retained state, topology, providers, memory routing, learning-gate status and ownership, trigger/ACK policy, checks, and residual risk using the configured report language and terminology. Keep technical tokens exact. Do not commit automatically.

## Invariants

Canonical spec and common files lead; adapters derive from them. No raw evidence means no pass. Do not bypass gates, weaken evaluators, drift one provider, centralize project state, overwrite project-owned configuration or memory without approval, or change the learning gate's enabled state without an explicit user instruction. A disabled learning gate must not create learning work or block delivery.
