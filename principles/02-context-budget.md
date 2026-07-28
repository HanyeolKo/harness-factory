# Principle 2 — Context Is a Budget

## Statement

Context is finite and its depletion is easy to miss. A harness therefore treats reading, reasoning, delegation, and session length as declared budgets. Quality loss caused by context exhaustion is a budget-management failure, not an unavoidable accident.

## Rules

1. **Declare a unit budget** — Record a measurable allowance in `budget/CONTEXT-BUDGET.md`. Use tokens, turns, subagents, sessions, or another observable unit appropriate to the runtime.
2. **Track actual use** — At the end of a work unit, append a useful estimate to the ledger. Order-of-magnitude accuracy is sufficient when exact metering is unavailable.
3. **Predefine thresholds** — Decide at harness creation what happens at 80% and 100%: checkpoint, split, offload, change session, or stop.
4. **Store state in files** — Keep queues, research, long intermediate results, and decisions in canonical files. Context contains paths and the smallest working set, not durable state.
5. **Budget reads** — `HARNESS.md` declares cold-start order and limits. Read indexes first and open only references required by the current unit.
6. **Keep internal prose lean** — Canonical runtime instructions are concise English and are not duplicated in multiple languages. User-facing presentation is configured separately.

## Defaults for new harnesses

| Item | Default |
|---|---|
| Work-unit allowance | One quarter of the session context; split units expected to exceed it |
| At 80% | Write a checkpoint, finish only the current unit, start no new unit |
| At 100% | Checkpoint immediately, persist remaining work in `state/state.json`, and stop or replace the session |
| Cold-start reads | Follow `HARNESS.md`; load the spec, current state, memory index, and only current-unit references |
| Canonical skill limit | `limits.max_instruction_lines: 120` |
| Memory document limit | `memory.max_document_lines: 80` |
| Memory summary limit | `memory.max_summary_chars: 160` |

The three reading-cost fields are optional for existing schema 1.0 or 1.1 harnesses. Their absence is backward compatible and must not cause an automatic rewrite of project-owned content. New harnesses include them; migrations add them deliberately and preserve approved exceptions.

## Constructor requirements

- Q4 captures cost sensitivity and adjusts work budgets, sampling, intervals, cooldown, and evaluation budget without suppressing mandatory events.
- Do not force token accounting when the runtime cannot measure it. Turns or completed units may be more honest.
- Split optional detail into indexed references before exceeding a configured budget.
