---
name: build-agent
description: Add or update one project-specific runtime-neutral harness agent, then synchronize the common role and all selected-provider wrappers atomically. Use for roles, permissions, capabilities, or handoffs in an existing harness.
---

# build-agent

Change one agent role in an installed harness. If `harness/harness-spec.json` is absent, use `build-harness`.

## Procedure

1. Resolve `FACTORY_ROOT`, then read the runtime contract, target spec/profile, report settings, and only relevant indexed memory when installed. If the requested role needs a capability outside the current profile, recommend the lowest sufficient profile and route the confirmed topology change to `build-harness reconcile`; do not install that layer here.
2. Inventory the domain, agents, handoffs, evaluators, gates, ownership, and preservation baseline. Prefer extending a matching role over duplication.
3. Define a lower-kebab-case ID, lane, capabilities, domains, access, `fast|balanced|deep` tier, input/output, and handoff.
4. Add or reuse approval gates for broader write access, destructive work, or external effects.
5. Update spec agents/domains/orchestration first. Keep normal handoffs acyclic; retry and improvement belong in loops.
6. Write the concise English canonical role and team projection within instruction budgets.
7. Require provider-path preflight before writes. Render thin wrappers for every selected runtime without copying role meaning.
8. Record the reason, exact delta, and `agent-change`; add `adapter-change` only when a provider artifact changed.
9. Run `verify-harness`, provider parity, memory/preservation checks, and affected task evaluators. Record a new parity transition once.

## Atomicity and reporting

Treat spec, common role, team projection, all selected wrappers, watched paths, and decision record as one change. Preserve user files and memory outside the delta. Report in `communication.report_language` with the configured terminology; keep IDs, paths, commands, evidence, and verdicts unchanged. Do not call the change complete while projections differ.
