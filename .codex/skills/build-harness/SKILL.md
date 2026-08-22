---
name: build-harness
description: Build or migrate a project-owned runtime-neutral harness from a confirmed create interview and the lowest sufficient core, adaptive, or governed profile. Use for first setup or a full topology redesign; use smaller build skills for one component.
---

<!-- document-budget exception: required-sequential-instruction | Construction decisions and the ordered transaction form one callable workflow. -->
# build-harness

Create or reconcile a harness inside the target project. The project owns every installed artifact and evidence record; the factory never absorbs them.

## Select and resolve

- No `harness/` is `create`; a valid runtime-neutral spec is `improve`; a partial or legacy harness is `reconcile`.
- Use `build-agent`, `build-skill`, or `build-evaluator` for one component, `verify-harness` for structure, `evaluate-harness` for measured effect, and `improve-harness` for an attributed defect.

## Resolve the factory

1. Run `scripts/resolve_factory.py`; pass `--factory-root <path>` when known or `--offline` when required.
2. Treat stdout as `FACTORY_ROOT`. Do not bypass a failed contract check with ad hoc templates.
3. Read `docs/CONSTRUCTOR-PROTOCOL.md`, this skill's `references/RUNTIME-CONTRACT.md`, `interview/QUESTION-BANK.md`, `principles/07-document-discipline.md`, and `CHECKLIST.md`; always load reporting references, then load learning and evaluation references only when the confirmed profile requires them.
4. Record source URL, ref, and commit in target D-001; omit local paths and credentials.

## Create interview hard stop

1. Inspect the request and repository before asking. Never ask again for a value explicitly supplied in the current request.
2. Prefer the runtime's structured input mechanism with bounded options and a free-text correction; use plain text only when structured input is unavailable.
3. Purpose has no default. Obtain it from the request or an explicit user confirmation of a stated hypothesis.
4. Silence is not delegation. Apply a default only after explicit delegation and record its source as `default-delegated`.
5. Resolve purpose, deliverable type, task evaluator, operation mode, cost sensitivity, `artifact_language`, `report_language`, `terminology`, runtime targets, approval gates, and reporting destination/target. Canonical artifacts use English; an external target must come from the user.
6. Recommend the lowest sufficient profile, state what it installs and omits, and require confirmation. `core` installs task execution/evaluation/verification and short reporting; `adaptive` adds durable memory, harness-effect evaluation, and evidence-gated improvement; `governed` adds installed Learning Assist, the Learning Gate, and audit/education controls. Reporting destination alone does not raise the profile.
7. Record all values and sources in `harness/maintenance/runs/<change-id>/delta-plan.json.interview_receipt`. In `create`, do not enter Phase 2 or write managed harness artifacts until the receipt is `complete` and profile confirmation is recorded.
8. A profile may be recommended but never changed automatically. The canonical current value is `harness-spec.json.profile`; `harness.construction_receipt` points to its delta-plan history. Do not install a second profile policy source.

## Workflow

1. **Discover** repository facts, existing policies/evidence, ownership, and preservation needs; ask only unresolved decisions through the interview contract.
2. **Plan** the classified delta. For `improve|reconcile`, freeze validator/evaluator results and `preservation-before.json` before proposing changes.
3. **Specify** schema 1.2 with the confirmed profile, a valid DAG, task evaluator links, selected runtime targets, and 50-line target/100-line Markdown maximum.
4. **Build common** profile-owned files only. Every profile installs reporting and a short Change Report. Core omits active memory, self-evaluation, harness-evaluation, improvement, and installed learning files; adaptive adds memory and effect/improvement files; governed adds installed Learning Assist and Learning Gate support.
5. **Preflight** before provider writes: `python <FACTORY_ROOT>/scripts/validate_runtime_neutral.py <target> --provider-path-preflight --construction-mode <mode> --delta-plan <path>`.
6. **Project adapters** only for confirmed runtime targets. Preserve text outside namespaced managed blocks; common spec and files lead every projection.
7. **Validate** with the same construction flags, profile topology, document budgets, references, evaluator links, provider parity, cold start, preservation, and applicable reporting/learning tests.
8. **Initialize adaptive/governed state** after create verification with the verified canonical/provider hashes and `pending_events: []`; installation alone opens no mandatory full. Preserve existing schema 1.1 state during improve/reconcile.
9. **Repair** common canonical files first and reproject every selected adapter for at most three rounds; disclose residual failures.

## Preservation

Preserve existing IDs, state, append-only ledger, evaluation runs, gates, evaluator semantics, user rules, unknown files, memory, reports, learning evidence, reporting policy, Learning Gate state, and `memory.policy: preserve-and-reconcile`. Never move project state into the factory.

- Recommend `core -> adaptive` for durable memory, recurring workflows, long-running/unattended work, harness-effect measurement, or evidence-gated improvement. Recommend `adaptive -> governed` only for an enabled/applicable Learning Gate, audit/education evidence, or blocking review/release control.
- Do not infer a downgrade from a quiet period. `governed -> adaptive` requires retired governance need, disabled Gate, no active gate evidence, and an exact preservation plan. `adaptive -> core` additionally requires no pending events, non-template memory, completed evaluation/ACK, or improvement history. Direct `governed -> core` requires both layer-removal sets and retained/archive evidence paths.
- Any downgrade, deletion, rename, move, split, merge, semantic replacement, gate-state change, or destination change requires exact paths and explicit approval recorded in `approval_required`; default delegation cannot approve removal.
- Adaptive/governed route `input-invalid:*` to structural recovery, require parity before effect evaluation, run only fixed targeted reasons, freeze full evidence, and ACK completed targeted/full runs. Improvement requires attributed full evidence and one bounded hypothesis.

## Delivery

Report mode, receipt sources, confirmed profile and reasons, installed and omitted capabilities, preservation, changed files, providers, governed layers, checks, and residual failures using configured report language and terminology. Keep machine tokens exact. Do not commit automatically.

## Invariants

Canonical spec and common files lead; adapters derive. No raw evidence means no pass. Never bypass gates, weaken evaluators, drift one provider, overwrite project-owned files, guess an external target, or change profile or Learning Gate state without explicit user direction. Disabled gates create no blocking work; reader copies never replace Git evidence.
