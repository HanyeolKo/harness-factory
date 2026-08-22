# Harness Factory Development Harness

Purpose: develop and verify the repository's runtime-neutral contracts, templates, skills, provider adapters, and documentation.

## Cold start

1. Read `harness/harness-spec.json`.
2. Read `harness/team/TEAM-ARCHITECTURE.md`.
3. Read `harness/state/state.json` for the one immediate action.
4. Read `harness/memory/INDEX.md`, then only entries required by that action.
5. Read `harness/state/self-evaluation.json` for pending events and the last harness verdict.
6. Read the current skill and evaluator contract; do not load evaluation or improvement detail when the checker returns `none`.

The target project owns this harness, its state, append-only ledger, memory, reports, learning evidence, and evaluation runs. Canonical meaning changes under `harness/` before any provider projection. Every completed work unit writes a short Change Report. Learning Assist is available on request. The Learning Gate is installed but disabled and only the user may change `enabled`.

Every Korean output must follow `harness/policies/KOREAN-OUTPUT.md`, including the separate honorific-avoidance rule. Main-agent and subagent prompts, results, reports, explanations, and generated Korean artifacts use the same policy.

Task completion uses `factory-contract-tests`; unavailable checks are `blocked`, never `pass`. At task boundaries run the deterministic checker. Improvement requires completed full evidence that attributes a defect to this harness, or an explicit evidence-backed user request.
