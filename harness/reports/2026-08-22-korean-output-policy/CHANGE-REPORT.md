# Change Report: Korean Output Policy

## What changed

The harness now applies the `fluent-korean` coding output rules to every Korean output from main agents, subagents, reports, explanations, documentation, and generated artifacts. A separate project override avoids honorific Korean and selects neutral written endings by default.

## Why and flow

The policy prevents omitted sentence elements, missing particles and endings, compressed technical noun strings, unclear metaphor, and ambiguous em-dash relationships. Main runtime guidance and every canonical agent role now route Korean output through one shared policy. Subagent prompts are checked before dispatch, and results are checked again before delivery.

## Key files

- `harness/policies/KOREAN-OUTPUT.md`: source provenance, full operational rules, and separate honorific override
- `harness/HARNESS.md`: common routing requirement
- `harness/team/agents/*.md`: subagent output requirement
- `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`: selected runtime guidance

## Validation

Provider path preflight and the full runtime-neutral validator passed. The linked task evaluator passed 32 tests with one Windows symlink fixture skipped because the process lacks symlink privilege. A deterministic policy check confirmed one policy, three provider roots, six role references, and unchanged reporting and Learning Gate policies.

## Need to know

The policy paraphrases the upstream MIT-licensed output style as an English canonical harness contract and records the exact upstream blob. User-facing Korean output uses the configured `ko` report language while machine tokens remain exact. The Learning Gate remains disabled and user-owned.
