# Generated skill surface

Use `templates/adapters/shared/SKILL-TEMPLATE.md` and a schema 1.1 spec for new harnesses. This file is only a call-surface reference. A generated skill selects only durable memory needed for the current unit through `memory.index` and updates the memory and index atomically.

| Skill | Responsibility | Load when |
|---|---|---|
| `<id>` | Execute work and hand off to the task evaluator | User requests work |
| `<id>-eval` | Judge one task as pass or fail; internal compatibility surface | After the task |
| `<id>-verify` | Check schema, adapter parity, and cold start | After configuration changes |
| `<id>-evaluate` | Compare baseline, control, and treatment | Explicit request or targeted/full trigger |
| `<id>-improve` | Make evidence-backed incremental improvements | Full regression or attributed harness defect |

The canonical skill is `harness/skills/<skill-id>/SKILL.md`. Claude `.claude/skills`, Codex `.agents/skills`, and Gemini `.gemini/skills` projections must be byte-identical. Keep an existing `<id>-retro` only as a compatibility alias for `<id>-improve`.
