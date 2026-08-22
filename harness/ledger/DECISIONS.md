# Decisions

## D-001 — Initial Harness Factory development harness

- Date: 2026-08-22
- Mode: `create`
- Purpose: develop and verify Harness Factory runtime-neutral contracts, templates, skills, adapters, and documentation.
- Factory source: `https://github.com/HanyeolKo/harness-factory.git`, ref `main`, commit `337e3b9c8b60a6f862f5b3740f08f8e6e7e1b629`.
- Runtime targets: Claude, Codex, Gemini.
- Operation: attended sessions; balanced cost sensitivity.
- Task evaluator: `factory-contract-tests` using `python scripts/test_runtime_neutral_contract.py` with additional affected repository checks.
- Reports: `report_language: ko`, `terminology: technical-english`, `reader_destination: file`, `reader_target: harness/reports`.
- Canonical artifacts: concise English; IDs, commands, paths, evidence, reasons, and verdicts remain exact.
- Learning Assist: available on request. Learning Gate: installed with `enabled: false`; only the user may change it.
- Approval gates: publishing/release/external writes and destructive or compatibility-changing repository operations.
- Initial full harness evaluation: pending `canonical-contract-change`; no comparable historical baseline is available, so any initial effect verdict remains `inconclusive` until samples exist.

## D-002 — Fluent Korean output policy

- Date: 2026-08-22
- Mode: `improve`
- Source: `https://github.com/snflkd/fluent-korean`, ref `main`, output-style blob `bce347c1db5566b1fbabebb2540efa1b8ba8b256`.
- Scope: every Korean output from main agents, subagents, reports, explanations, documentation, and generated artifacts.
- Canonical policy: `harness/policies/KOREAN-OUTPUT.md` records the complete operational rules in concise English.
- Separate user override: avoid honorific Korean and use neutral written endings unless an explicit tone or artifact convention overrides it.
- Preserved: `communication.report_language: ko`, reporting destination, Learning Gate `enabled: false`, state history, ledger history, and existing provider text outside managed blocks.

## D-003 — Read-only evidence runner request and validation contract

- Date: 2026-08-22
- Mode: `improve`
- Source evidence: `harness/evaluation/runs/2026-08-22-generated-harness-review/report.json`; initial full verdict `inconclusive`, with high-confidence harness-attributed evidence-chain defects.
- Hypothesis: a read-only `evidence-runner` that owns exact execution requests and evidence validation, with the main orchestrator as command executor and persistence owner, increases evidence-complete handoffs without broader agent permissions.
- Components: `evidence-runner` agent contract and the shared evidence handoff contract.
- Access decision: preserve `evidence-runner` as `read-only`. Reject the workspace-write alternative because selected provider sandboxes cannot enforce evidence-path-only writes.
- Provider delta: synchronize description-only wrappers for Claude, Codex, and Gemini; do not add shell or write tools.
- Evidence binding: persist `execution-request.json` before execution; bind request, approval status, raw paths, exit state, and deterministic hashes in a twelve-field manifest.
- Acceptance: retain only if the frozen full comparison is `improved` with structural, parity, cold-start, permission, agent-count, and handoff-count non-regression.
- Residual risk: evidence-root restrictions remain main-orchestrator contract enforcement rather than a dedicated path sandbox.
