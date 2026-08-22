---
name: build-skill
description: Add or update one callable runtime-neutral workflow skill in an installed harness, keeping its concise English canonical SKILL.md and all selected provider projections byte-identical.
---

# build-skill

Define skill meaning once in `harness/skills/<skill-id>/SKILL.md`. Provider copies are discovery projections only. If the common spec is absent, use `build-harness`.

## Procedure

1. Resolve `FACTORY_ROOT`; read the runtime contract, target spec/profile, report settings, and only task-relevant memory when installed. If the requested workflow needs a capability outside the current profile, recommend the lowest sufficient profile and route the confirmed topology change to `build-harness reconcile`; do not install that layer here.
2. Record the validator/evaluator baseline, ownership, and preservation manifest. Prefer extending an existing responsibility over a duplicate skill.
3. Define purpose, kind, domains, entry agent, inputs, outputs, and entry conditions.
4. Link `skills[].evaluator`: entry/evaluation/verification/domain to `scope: task`; harness-evaluation/improvement to the `self_evaluation.evaluator` (`scope: harness`, `type: experiment`).
5. Update the spec and orchestration references first.
6. Write a concise English canonical SKILL within `limits.max_instruction_lines`. Put optional or detailed material in references and load it conditionally; do not store bilingual copies.
7. Require provider-path preflight, then copy the canonical file byte-for-byte to every selected provider skill root.
8. In adaptive or governed profiles, keep only each exact projection in `self_evaluation.watched_paths`; never watch a whole provider skill directory.
9. Update managed guidance/team projections, record `skill-change` and any real `adapter-change`, then run `verify-harness`, parity, memory/preservation checks, and the linked task evaluator.

## Atomicity and reporting

Spec, canonical skill, projections, watched paths, guidance, and decision record are one transaction. Preserve user-owned files and memory outside the delta. Report in the configured user-facing language and terminology while keeping machine tokens exact. Runtime-specific meaning, adapter-only edits, and evidence-free passes are invalid.
