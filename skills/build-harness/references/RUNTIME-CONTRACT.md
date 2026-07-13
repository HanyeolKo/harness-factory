# Runtime-neutral contract

The canonical state lives under `harness/`. Claude and Codex files are generated adapters, not independent sources of truth.

## Canonical layers

1. `harness/harness-spec.json` defines roles, skills, orchestration, evaluation, approval gates, improvement, limits, and selected runtimes.
2. `harness/team/agents/<role-id>.md` contains runtime-neutral role instructions.
3. Every `skills[].instructions` points to the canonical `harness/skills/<skill-id>/SKILL.md` body.
4. `harness/loops/`, `state/`, and `ledger/` hold the execution, evidence, recovery, and improvement protocol.
5. Runtime adapters expose the same IDs and handoffs in native discovery formats.

## Required semantics

- Role and skill IDs are lower-kebab-case and unique.
- Roles use abstract model tiers: `fast`, `balanced`, or `deep`. Vendor model names belong only in adapter files.
- The normal orchestration graph is acyclic. Retry and improvement feedback are expressed in the improvement contract.
- Every executable work unit names an evaluator and a pass condition.
- Every approval gate has a stable ID, trigger, owner, and required action; an empty list explicitly means no gates.
- Evidence collection and verdict ownership are separate capabilities, even when a small project assigns both to one role.
- Improvement changes the canonical spec first, regenerates every selected adapter, then reruns the original evaluator and parity validation.

## Claude adapter

- Root guidance: managed block in `CLAUDE.md`
- Project skills: `.claude/skills/<skill-id>/SKILL.md`
- Subagents: `.claude/agents/<namespace>-<role-id>.md`
- Invocation: `/<skill-id>`

Claude agent frontmatter maps common access explicitly. A `read-only` role uses only `Read, Grep, Glob`, disallows `Write, Edit, NotebookEdit, Bash`, and uses `permissionMode: plan`. A `workspace-write` role still uses a minimal allowlist and never uses `bypassPermissions`.

## Codex adapter

- Root guidance: managed block in `AGENTS.md`
- Project skills: `.agents/skills/<skill-id>/SKILL.md`
- Custom agents: `.codex/agents/<namespace>-<role-id>.toml`
- Global subagent limits: `.codex/config.toml`
- Invocation: `$<skill-id>`

Each Codex agent TOML declares its own `name`, `description`, and `developer_instructions`. Merge root managed blocks and the global `[agents]` limits without deleting unrelated user configuration. If an existing definition conflicts, stop and report the exact field instead of silently replacing it.

## Parity

For every selected runtime, the adapter must expose the same role IDs, skill IDs, orchestration edges, evaluator ownership, improvement triggers, and approval gates. Each Claude/Codex `SKILL.md` is a byte-identical copy of the common file named by that skill's `instructions`, including arbitrary domain skills. Runtime-specific model names, agent permission syntax, and file locations may differ.
