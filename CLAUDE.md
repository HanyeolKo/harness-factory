

<!-- harness-factory:start harness-factory-dev -->
## harness-factory-dev harness

- Canonical contract: `harness/harness-spec.json`
- Entry: `/harness-factory-dev`
- Task evaluation: `/harness-factory-dev-eval` (internal/compatibility)
- Structural verification: `/harness-factory-dev-verify`
- Harness effect evaluation: `/harness-factory-dev-evaluate`
- Evidence-gated improvement: `/harness-factory-dev-improve`
- Trigger: `python harness/triggers/check_self_evaluation.py harness`
- ACK: `python harness/triggers/record_self_evaluation.py harness --decision <targeted|full> --decision-file harness/evaluation/runs/<run-id>/trigger.json --verdict <improved|neutral|regressed|inconclusive>`
- Targeted suite: `harness/evaluation/suites/targeted.json`
- Reporting policy: `harness/policies/reporting.json` (`file` default; optional `notion|slack`; Git remains canonical evidence)
- Learning Assist: start from the short Change Report and expand only the relevant actual diff/source using plain-language-first wording
- Learning gate policy: `harness/policies/learning-gate.json` (installed disabled; only the user may change `enabled`)
- Learning gate verifier: `python harness/triggers/verify_learning_gate.py harness --change-id <change-id> --changed-lines <count> --risk-tag <tag>`
- Reports: follow `communication.report_language` and `communication.terminology`; if absent, use `en` and `technical-english`
- Korean output policy: read `harness/policies/KOREAN-OUTPUT.md` and apply it to every Korean prompt, response, report, explanation, subagent handoff, and generated artifact
- Honorific override: avoid honorific Korean by default and use a neutral written style; keep this rule separate from the fluent-Korean clarity rules
- `technical-english`: report-language grammar with stable technical nouns kept in English; `localized`: conventional local explanatory nouns
- In both modes, keep machine tokens exact and do not duplicate bilingual prose
- Skills: `.claude/skills/harness-factory-dev*/SKILL.md`
- Agents: `.claude/agents/harness-factory-dev-*.md`

Every completed work unit leaves a short Change Report. If the user asks for deeper understanding, use Learning Assist without blocking delivery. At review, pull request, and merge boundaries, read the learning gate policy. When disabled, do not create gate-specific blocking work. When enabled and applicable, use the Learning Assist explanation first, let the developer read it, then require the five-question quiz, developer-authored answers, and committed source-snapshot/hash verification. Wrong answers receive progressive hints before the final concept explanation. A matching risk tag overrides a low-risk exemption. Agents may recommend enabling or disabling the gate but must not change `enabled` without an explicit user instruction.

Every schema 1.1 skill has an evaluator link. At task boundaries run only the deterministic checker. Route `input-invalid:*` to structural verification/recovery without effect evaluation or LLM. For `adapter-change|parity-fail`, require provider parity verification before effect evaluation and append a new `parity-fail` pending event on a pass-to-fail transition. Targeted evaluation may run only the deterministic reason mapping in `targeted.json`.

Before evaluation, freeze the checker JSON at `harness/evaluation/runs/<run-id>/trigger.json`. After every completed targeted/full evaluation, run the recorder with that decision file. A full ACK updates managed canonical/provider hashes and clears only the processed pending-event snapshot, preventing the same mandatory signal from reopening evaluation; newly arrived events remain pending. Load improvement after full evidence attributes a regression to the harness or an explicit evidence-backed user request; the request path must establish baseline/full evidence before applying a candidate. Update the canonical contract before regenerating every selected provider adapter.
<!-- harness-factory:end harness-factory-dev -->
