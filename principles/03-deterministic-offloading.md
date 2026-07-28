# Principle 3 — Deterministic Offloading

## Statement

LLM reasoning is costly and nondeterministic; scripts and files are cheap and repeatable. Offload every mechanical operation that is likely to recur. Use an LLM for judgment, then persist the decision so later runs can reuse it without reconstructing context.

## Rules

1. **The second repetition is a script candidate** — When an operation recurs, decide whether to automate it. A third manual repetition requires an explicit reason.
2. **Files own durable state** — Queue state, progress, source evidence, research, and intermediate artifacts live in files. In-context memory is only a cache; canonical files win on disagreement.
3. **Evaluate offloaded work** — A script must expose deterministic output and exit behavior. Do not ask an LLM to repeat checks already performed by the script.
4. **Declare the boundary** — Every loop states which steps are deterministic and which require judgment. An ambiguous boundary leaks cost into the LLM path.
5. **Require safe replay** — Offloaded operations used by recovery are idempotent or explicitly guarded against duplicate effects.

## Decision table

| Signal | Action |
|---|---|
| The same command sequence recurs | Put it in `scripts/` or beside the harness component that owns it |
| A long list or table stays in context | Persist it and retain only its path and short routing metadata |
| A prior procedure must be rediscovered | Record it as a candidate; adopt it only after effect evaluation when it changes the harness |
| The LLM performs conversion, aggregation, counting, or hashing | Replace that step with deterministic code; LLM arithmetic is not an evaluator |

## Constructor requirements

- Inventory existing scripts, Makefiles, task runners, and CI commands in `ENVIRONMENT.md` so a cold session does not reinvent them.
- Offloading is a discipline, not a target. Do not automate a one-off operation when the automation costs more than the saved work.
