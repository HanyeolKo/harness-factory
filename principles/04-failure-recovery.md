# Principle 4 — Recovery Is Designed In

## Statement

Failure and interruption are normal in long-running agent work. Recovery is part of the harness structure, not an improvised response after an incident.

## Rules

1. **Checkpoint first** — Before destructive or hard-to-reverse steps, and at 80% of a context budget, update `state/state.json` and create a recoverable checkpoint when appropriate.
2. **Classify before acting** — Every failure receives a stable class and one of two responses: `R` permits bounded automated recovery; `S` stops automation, checkpoints, and waits for user input or approval. Unknown failures are `S`. Exhausted `R` attempts become `S`.
3. **Bound every retry** — Record retry limits, backoff, and the next action after exhaustion in `recovery/RECOVERY-PLAYBOOK.md`.
4. **Resume from files** — A recovered session restores state from `state/state.json`, `ledger/journal.jsonl`, and `recovery/CHECKPOINT.md`, never from assumed conversation memory.
5. **Treat recurrence as evidence** — Count every occurrence of the same failure key, including recovered attempts. Three occurrences by default create a mandatory full harness-evaluation signal. Improvement is allowed only after the full experiment attributes the cause to the harness.

## Standard classes

| Class | Meaning | Grade | Default response |
|---|---|---|---|
| `transient` | Network errors, timeouts, temporary resource pressure | `R` | Backoff retry, default 3 attempts at 2s, 4s, and 8s |
| `structural` | A real defect in code, configuration, or environment | `R` | Do not repeat unchanged work; diagnose, modify, and rerun the evaluator, then escalate at the fix-attempt limit |
| `scope` | Incorrect task definition, insufficient authority, or missing information | `S` | Checkpoint and request user direction |
| `budget` | Context or cost allowance exceeded | `R` | Checkpoint and split or replace the session; total-budget exhaustion is `S` |
| `gate` | A human approval boundary was reached | `S` | Wait for approval; this is a designed stop, not a task failure |

## Failure keys

- Record each failure as `<class>:<subtype>`, for example `structural:unsafe-any`.
- Reuse an existing stable key before creating a new one. Fragmented keys hide recurrence.
- Never lower counters or erase evidence because a later retry succeeded.

## Constructor requirements

- Adjust retry limits and `R` to `S` escalation using the user's operating mode and failure tolerance. Unattended operation should escalate more conservatively.
- List release, deletion, external communication, migration execution, and other irreversible steps as approval gates. Gates are never retry targets.
