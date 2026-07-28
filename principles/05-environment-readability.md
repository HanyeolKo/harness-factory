# Principle 5 — Environment Readability

## Statement

A future session starts without the current conversation. The harness must let that session restore state and choose one next action from files within five minutes. This property is verified by a cold-start test.

## Rules

1. **Use one entry point** — Reading starts at `HARNESS.md`, which gives an ordered, bounded route through the spec, state, indexes, and current-unit references.
2. **Keep current state in one place** — `state/state.json` is the source of truth for phase, queue, current unit, and `next_action`.
3. **Make non-use explicit** — When a standard axis or file is intentionally unused, record `unused` and a reason. Silence forces a cold session to guess whether something is missing.
4. **Treat names as contracts** — Keep declared filenames and paths stable. A change updates `ledger/DECISIONS.md` and the `HARNESS.md` file map in the same transaction.
5. **Make commands executable** — Commands in `ENVIRONMENT.md` are copy-ready. Write `npm test`, not “run the tests.”
6. **Avoid conversation references** — Canonical artifacts must stand alone and use concise English. Remove phrases that depend on prior chat context.

## Cold-start test

Run this before delivery, after an accepted harness improvement, and at every new session start.

1. Assume an empty context and begin only with `HARNESS.md`.
2. Follow its declared read order and budgets.
3. Answer from file evidence:
   - What is the harness purpose and current phase?
   - What single action should run next?
   - Which task evaluator decides whether that action is complete?
4. Confirm the pending self-evaluation events, last harness verdict, and only the memory entries required by the action.

If any answer is unavailable, the test fails. Record the false-to-true `coldstart_fail` transition in `harness/state/self-evaluation.json` and add `coldstart-fail` once to `pending_events`. The deterministic trigger routes evaluation; it never authorizes automatic improvement by itself.

## Constructor requirements

- Perform the test from the generated files rather than from construction-session memory.
- A blank `state.next_action`, missing evaluator link, unbounded read route, or required prior conversation is a failure.
