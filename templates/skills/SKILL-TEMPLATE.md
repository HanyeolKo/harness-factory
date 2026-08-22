# Generated skill surface

Use `templates/adapters/shared/SKILL-TEMPLATE.md` and a schema 1.2 spec for new harnesses. This file is only a call-surface reference. Adaptive and governed skills select only durable memory needed for the current unit through `memory.index` and update the memory and index atomically; core has no durable-memory contract.

| Skill | Responsibility | Load when |
|---|---|---|
| `<id>` | Execute work and hand off to the task evaluator | User requests work |
| `<id>-eval` | Judge one task as pass or fail; internal compatibility surface | After the task |
| `<id>-verify` | Check schema, adapter parity, and cold start | After configuration changes |
| `<id>-evaluate` | Compare baseline, control, and treatment | Adaptive or governed explicit request/trigger |
| `<id>-improve` | Make evidence-backed incremental improvements | Adaptive or governed attributed defect |

The canonical skill is `harness/skills/<skill-id>/SKILL.md`. Claude `.claude/skills`, Codex `.agents/skills`, and Gemini `.gemini/skills` projections must be byte-identical. Keep an existing `<id>-retro` only as a compatibility alias for `<id>-improve`.
