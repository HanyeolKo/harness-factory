---
name: build-harness
description: Build or migrate a project-owned runtime-neutral agent harness with concise English canonical artifacts, lightweight change reports, Learning Assist, an optional user-controlled Learning Gate, evidence-based evaluation, incremental improvement, and Claude, Codex, and Gemini adapters. Use for first setup or a full topology redesign; use the smaller build skills for one component.
---

# build-harness

Create or reconcile a harness inside the target project. The project owns its spec, state, evidence, reports, learning artifacts, memory, and improvement history; the factory never absorbs them.

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
3. Read `docs/CONSTRUCTOR-PROTOCOL.md`, `references/RUNTIME-CONTRACT.md`, `docs/REPORTING-CONTRACT.md`, `docs/LEARNING-ASSIST.md`, `principles/`, `interview/QUESTION-BANK.md`, and `CHECKLIST.md` progressively.
4. Record source URL, ref, and commit in target D-001; omit local paths and credentials.

## Language, readability, and report destination

- New specs include `communication.artifact_language: en`.
- During setup, let the user choose `communication.report_language` and `communication.terminology` (`technical-english|localized`). Default to `en` and `technical-english`.
- Also ask where reader-facing Change Reports and Learning Assist copies should be organized: `file|notion|slack`. Default to `file`.
- Store that choice in `harness/policies/reporting.json`, not in the runtime-neutral schema.
- For `file`, default `reader_target` to `harness/reports`.
- For `notion` or `slack`, ask the user for the target page/database/channel/conversation identifier or URL. Do not guess it.
- Always keep `canonical_evidence: file` and `style: plain-language-first` in the reporting policy.
- Plain-language-first means concrete behavior -> reason -> execution flow -> relevant code -> technical term only when useful.
- Prefer wording a developer would naturally use when explaining the change to a teammate. Avoid literal translation-like nouns and unnecessary abstraction.
- Keep identifiers, commands, paths, evidence, JSON keys, status values, API names, table names, and conventional technical terms exact.
- Existing harnesses without `policies/reporting.json` remain valid. Add it only as a preservation-aware delta and do not silently change an existing destination.
- Use progressive disclosure: read indexes first, open only task-relevant files, and skip evaluation/improvement references on `none`.

## Workflow

1. **Discover** — inspect root rules, README/docs, modules, build/test/CI, existing agents/skills/hooks, evaluator baselines, file ownership, preservation needs, indexed memory, existing reports, any reporting policy, and any Learning Gate policy. Ask only for unknown purpose, completion criteria, approval boundaries, provider scope, report language/terminology, and reader destination/target.
2. **Plan** — record mode and a `unchanged|add|modify-proposed|conflict|approval-required` delta plan under `harness/maintenance/runs/<change-id>/`. In `improve|reconcile`, write `preservation-before.json` first.
3. **Specify** — create schema 1.1 with a valid DAG. Every skill links an evaluator: entry/evaluation/verification/domain to `scope: task`; harness-evaluation/improvement to the `self_evaluation.evaluator`, which is `scope: harness`, `type: experiment`.
4. **Build common** — in `create`, render the spec, HARNESS, team, canonical skills, loops, recovery, budget, state, append-only ledger, evaluation contract, `memory/INDEX.md`, the reporting policy/templates, and Learning Assist contract. In other modes, touch only delta-owned files.
5. **Install reporting** — every new harness receives `policies/reporting.json`, the short Change Report contract, and `reports/` layout. A completed work unit writes `reports/<change-id>/CHANGE-REPORT.md`. Keep it to one screen or roughly one page and do not restate the full diff. If the reader destination is Notion or Slack, retain the Git file as canonical and publish a reader copy when the integration is available.
6. **Install Learning Assist** — use it on request for deeper explanation or comprehension checks. It starts from the Change Report, reads only relevant actual diff/source, and uses the same plain-language-first style. A voluntary quiz while the Learning Gate is disabled is advisory and never blocks delivery.
7. **Install the Learning Gate** — every new harness receives `policies/learning-gate.json`, `policies/LEARNING-GATE.md`, `learning/_templates/`, and `triggers/verify_learning_gate.py`. Set `enabled: false` by default. Only an explicit user instruction may change `enabled`; agents may recommend a state but must not toggle it. In `improve|reconcile`, preserve the existing value. When enabled and applicable, write the pre-change brief, implement/validate, produce the short Change Report, render `diff-explanation.md` through Learning Assist, let the developer read it, then run the five-question comprehension check and deterministic verification. Wrong answers use progressive hints rather than immediate answer reveal. Matching risk tags override low-risk exemptions.
8. **Budget context** — use `limits.max_instruction_lines`, `memory.max_document_lines`, and `memory.max_summary_chars`; split references before exceeding a budget and retain only routing metadata in indexes.
9. **Install evaluation** — create the full baseline/control/treatment contract and `evaluation/suites/targeted.json`. Map only `cost-regression`, `retry-pressure`, and `deterministic-sample` to fixed deterministic metrics.
10. **Install triggers** — install the read-only checker, completed-run recorder, and Learning Gate verifier. The self-evaluation checker alone runs at task boundaries and returns `none|targeted|full`; the learning verifier runs only when its user-controlled policy is enabled and applicable.
11. **Watch exact artifacts** — hash canonical effect-bearing files separately. List only selected providers' exact root guidance, skill projections, namespaced agent wrappers, and generated config in `self_evaluation.watched_paths`. Per-change reports, learning answers, and verification evidence remain project-owned task evidence rather than harness-effect watched artifacts.
12. **Preflight adapters** — before provider writes, require:

   ```text
   python <FACTORY_ROOT>/scripts/validate_runtime_neutral.py <target> --provider-path-preflight
   ```

   On failure, do not create, write, move, or route around provider paths.
13. **Project adapters** — preserve user text outside managed blocks and render Claude (`CLAUDE.md`, `.claude/skills`, `.claude/agents`), Codex (`AGENTS.md`, `.agents/skills`, `.codex/agents`, `.codex/config.toml`), and Gemini (`GEMINI.md`, `.gemini/skills`, `.gemini/agents`) as selected. Root guidance exposes the reporting/Learning Assist flow and Learning Gate path without runtime-specific semantics.
14. **Expose workflows** — create `<id>`, `<id>-eval`, `<id>-verify`, `<id>-evaluate`, and `<id>-improve`; keep legacy `-retro` only as an alias.
15. **Validate** — run the validator, memory/index checks, linked evaluators, provider parity, cold-start test, and `python <FACTORY_ROOT>/scripts/test_learning_gate_contract.py`. Compare `preservation-after.json` with the baseline. Record new `coldstart-fail` or `parity-fail` transitions once.
16. **Repair** — repair common canonical files first and reproject every selected adapter, for at most three rounds. Disclose residual failures.

## Preservation

Preserve existing IDs, state, append-only ledger, evaluation runs, gates, evaluator semantics, user rules, unknown-ownership files, durable memory, reports, learning evidence, the user's Learning Gate `enabled` value, and any existing reporting policy. Deletion, rename, semantic replacement, split, merge, Learning Gate state change, or reader-destination change requires an exact field/path proposal and explicit approval. Upsert only namespaced managed blocks and generated adapters. Never move an installed harness into the factory package.

Memory uses `harness/memory/INDEX.md` with `preserve-and-reconcile`. Create, move, supersede, archive, and index updates are one transaction. Keep current state in `state.json` and events in `journal.jsonl`, not memory. Ordinary memory changes get deterministic verification; policy or routing changes are canonical effect changes.

## Evaluation and ACK

- Route `input-invalid:*` to verification and structural recovery without effect evaluation or an LLM.
- Require provider parity before evaluating `adapter-change|parity-fail`.
- On `none`, load no evaluation or improvement workflow.
- On `targeted`, run only the fixed reason mapping. On `full`, run the linked experiment.
- Freeze checker JSON in `evaluation/runs/<run-id>/trigger.json`. A user-requested full run must preserve the raw decision under `override.original` and use the structured override contract.
- ACK every completed targeted/full run with `record_self_evaluation.py`.

Open improvement only after a full regression or attributed harness defect. Change one hypothesis and at most two components, then rerun the frozen suite.

Learning Assist and Learning Gate are separate from harness-effect evaluation. Learning Assist explains. Learning Gate verifies developer-understanding evidence for the current change when enabled/applicable. Neither claims that the harness itself improved.

## Delivery

Report mode, delta, preservation, created/changed files, retained state, topology, providers, memory routing, reader destination, Learning Assist availability, Learning Gate status/ownership, trigger/ACK policy, checks, and residual risk using the configured report language and terminology. Keep technical tokens exact. Do not commit automatically.

## Invariants

Canonical spec and common files lead; adapters derive from them. No raw evidence means no pass. Do not bypass gates, weaken evaluators, drift one provider, centralize project state, overwrite project-owned configuration/memory, guess an external report target, or change the Learning Gate enabled state without explicit user instruction. A disabled Learning Gate must not create gate-specific blocking work. Reader copies in Notion or Slack never replace canonical Git evidence.
