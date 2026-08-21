# Harness Factory

[English](README.md) | [한국어](README.ko.md)

Harness Factory gives each project its own agent harness. It derives project-specific agents, skills, evaluators, and native adapters instead of copying a fixed team. The resulting state, evidence, and improvement history stay in the target repository.

One canonical `harness/` directory supports Claude Code, Codex, and Gemini CLI. Cheap deterministic checks run at task boundaries; heavier evaluation only runs when evidence calls for it.

## Quick start

You need Git, Python 3.11 or later, write access to the target project, and at least one supported runtime.

### Claude Code

Run these commands inside Claude Code:

```text
/plugin marketplace add HanyeolKo/harness-factory
/plugin install harness-factory@harness-factory-marketplace
/reload-plugins
```

Start a new session, then build a harness:

```text
/harness-factory:build-harness "D:\workspace\step_fps"
```

The same installation is available from a terminal:

```powershell
claude plugin marketplace add HanyeolKo/harness-factory
claude plugin install harness-factory@harness-factory-marketplace
```

### Codex

Register the marketplace:

```powershell
codex plugin marketplace add HanyeolKo/harness-factory --ref main
codex plugin marketplace list
```

Install `harness-factory` from `/plugins` in Codex CLI or from the Plugins screen in the desktop app. Start a new task, then run:

```text
$harness-factory:build-harness "D:\workspace\step_fps"
```

### Gemini CLI

Install the extension:

```powershell
gemini extensions install https://github.com/HanyeolKo/harness-factory --ref main
```

Restart Gemini CLI and confirm that it is available:

```text
/extensions list
```

Then ask Gemini to use the skill:

```text
Use the build-harness skill to create a Claude, Codex, and Gemini harness in D:\workspace\step_fps.
```

Unless you request a smaller set, `build-harness` creates adapters for all three runtimes. It inspects the project first and only asks about goals, approval gates, completion criteria, reporting preferences, or reader destination settings that cannot be inferred safely.

## Language and reading-cost contract

Harness internals use concise English by default. Skills, agent instructions, memory entries, loop contracts, and other runtime-facing documents should state each rule once and use progressive disclosure: read the index first, then load only the references required for the current task. Generated harnesses do not duplicate internal content in multiple languages.

New harnesses record language choices in `harness/harness-spec.json`:

- `communication.artifact_language` is fixed to `en`.
- `communication.report_language` accepts a BCP-47-style language tag and defaults to `en`.
- `communication.terminology` is either `technical-english` or `localized`.

`report_language` chooses the grammar of user-facing reports. With `technical-english`, stable terms such as `harness`, `agent`, `skill`, `evaluator`, `baseline`, `control`, and `treatment` remain English. With `localized`, explanatory technical nouns use conventional terms from the report language where possible. For example, `ko + technical-english` uses Korean sentence grammar while keeping `baseline`, `treatment`, and the verdict `pass` exactly; `ko + localized` may localize the two explanatory nouns while keeping `pass` exact.

Neither mode translates identifiers, commands, paths, evidence, JSON keys, reason or status values, or stored verdicts such as `pass` and `fail`. Reports use one natural prose style rather than repeating the same content bilingually. In an English canonical artifact, wrap an exact non-English project name or machine token in backticks and keep the surrounding prose English. Changing only presentation settings does not trigger a full harness-effect evaluation. The `communication` object is optional for existing schema 1.0 and 1.1 harnesses for compatibility; when it is absent, all three fields use the English defaults above. Newly generated harnesses always include it.

## Change reports and Learning Assist

Every completed work unit leaves a short `harness/reports/<change-id>/CHANGE-REPORT.md`. The default report is intentionally smaller than a design document: what changed, why, the important flow, key files, checks actually run, and anything the developer should know next.

New harness setup asks where reader-facing change and learning documents should be organized. The choice is stored in `harness/policies/reporting.json`:

- `file` is the default and uses the project-owned report files directly.
- `notion` publishes a reader copy to a user-selected Notion page or database.
- `slack` publishes a reader copy to a user-selected Slack channel or conversation.

Notion and Slack targets must come from the user; agents do not guess them. Git remains the canonical evidence source even when a reader copy is published externally.

Learning Assist is non-blocking when used on its own. Ask for a deeper explanation or comprehension check and it expands only the relevant actual diff/source. Explanations use a plain-language-first order: concrete behavior, reason, execution flow, relevant code, then a technical term only when that term helps future maintenance. Quiz questions test the implementation mental model rather than vocabulary recall. A wrong answer gets a directional hint, then a concrete scenario or counterexample, and only after the final failed attempt is recorded does the concept get explained directly.

When localized reporting is selected, explanatory prose uses natural wording in the report language. Identifiers, paths, commands, and configuration keys remain exact, but ordinary explanations do not keep surrounding English process jargon by default. If an exact technical term helps source reading, explain the behavior first and introduce the term once in backticks or parentheses.

## Optional learning gate

Every new harness still installs a Learning Gate as a project-owned policy, and it still starts with `enabled: false`.

- Only an explicit user instruction may change `enabled`; agents may recommend a state but cannot toggle it.
- Disabled means no gate-specific learning work, review block, pull request block, or merge block.
- Enabled changes use the configured risk-based scope, with matching risk tags taking precedence over low-risk exemptions.
- When enabled and applicable, the gate depends on Learning Assist: implementation and task validation produce the short Change Report, Learning Assist explains the actual diff in the same readable style, the developer reads that explanation, and only then does the five-question Gate quiz run.
- Incorrect answers use progressive hints instead of immediately revealing the answer. If confusing wording or an undefined term caused the miss, the explanation/question is rewritten before counting that miss as a comprehension failure.
- Passing evidence remains bound to the project-owned committed source snapshot, quiz/answer hashes, and `verification.json`; external reader copies never replace this Git evidence.
- Existing harnesses preserve the user's current on/off value during improve or reconcile operations.

The policies live at `harness/policies/reporting.json` and `harness/policies/learning-gate.json`. See [Learning Assist](docs/LEARNING-ASSIST.md), [Reporting Contract](docs/REPORTING-CONTRACT.md), and [Learning Gate](docs/LEARNING-GATE.md).

## Seven focused skills

Use the narrowest skill that matches the change:

| Skill | Purpose |
|---|---|
| `build-harness` | Create a new harness, reconcile an existing one, or perform a full topology migration |
| `build-agent` | Add or modify one project role |
| `build-skill` | Add or modify one project-owned execution skill |
| `build-evaluator` | Add or modify a task evaluator or harness-effect evaluator |
| `verify-harness` | Deterministically verify schema, references, DAGs, permissions, and adapter parity |
| `evaluate-harness` | Compare baseline, control, and treatment evidence |
| `improve-harness` | Change one or two proven harness defects and re-evaluate the result |

Atomic build skills update the common specification first, project it into the selected runtime adapters, and verify parity. You do not need to rebuild the entire harness to change one agent, skill, or evaluator.

## Project ownership and incremental change

Harness Factory is not a central control plane or package registry for installed harnesses. Each target project owns its canonical specification, state, append-only ledger, evaluation evidence, learning evidence, reports, and memory.

`build-harness` classifies a target as `create`, `improve`, or `reconcile`. For an existing harness, it records the baseline, file ownership, and preservation manifest before applying a narrow delta. Existing IDs, state, ledgers, evaluators, approval gates, user rules, learning-gate state, learning evidence, reporting policy, and files of unknown ownership are not deleted, renamed, or semantically replaced without approval.

The source of truth is `harness/harness-spec.json` together with the common files and project-owned policies it references. Edit canonical files first; generated runtime adapters may be replaced on the next projection.

## Evaluation without constant LLM calls

Task completion and harness-effect evaluation are separate. Every task uses its linked task evaluator, while a read-only deterministic checker decides whether the harness itself needs more evaluation:

```text
task boundary
  → deterministic checker
  → input-invalid:*: verify and repair structure; do not open effect evaluation
  → adapter-change|parity-fail: restore provider parity first
  → none: stop
  → targeted: run only the fixed deterministic metrics for the reason
  → full: compare baseline, control, and treatment
  → completed targeted/full: acknowledge the frozen decision
  → attributed harness defect: consider improve-harness
```

Cooldowns, sample thresholds, and an evaluation budget defer non-mandatory work. General memory edits are checked deterministically and do not trigger a full experiment by themselves. This keeps routine boundaries inexpensive while preserving stronger evaluation for contract changes, regressions, cold-start failures, and adapter drift.

Learning Gate verification is separate from this harness-effect loop. It verifies developer-understanding evidence for an applicable change; it does not claim that the harness improved. Learning Assist by itself is explanatory and non-blocking.

## Generated layout

```text
<target>/
├── harness/                              # Runtime-neutral source of truth
│   ├── harness-spec.json                 # Schema 1.1
│   ├── HARNESS.md
│   ├── team/agents/<role-id>.md
│   ├── skills/<skill-id>/SKILL.md
│   ├── policies/
│   │   ├── reporting.json                # file|notion|slack reader destination
│   │   ├── learning-gate.json            # Installed with enabled=false
│   │   └── LEARNING-GATE.md
│   ├── reports/
│   │   └── <change-id>/CHANGE-REPORT.md
│   ├── learning-assist/
│   │   ├── _templates/
│   │   └── <change-id>/                  # Optional, user-requested session artifacts
│   ├── learning/
│   │   ├── _templates/
│   │   └── <change-id>/                  # Gate evidence when enabled and applicable
│   ├── loops/
│   │   └── HARNESS-EVAL-LOOP.md
│   ├── evaluation/
│   │   ├── EVALUATION-CONTRACT.md
│   │   └── suites/targeted.json
│   ├── triggers/
│   │   ├── check_self_evaluation.py
│   │   ├── record_self_evaluation.py
│   │   └── verify_learning_gate.py
│   ├── state/
│   │   ├── state.json
│   │   └── self-evaluation.json
│   ├── memory/INDEX.md
│   └── ledger/
├── CLAUDE.md
├── .claude/{skills,agents}/
├── AGENTS.md
├── .agents/skills/
├── .codex/{agents,config.toml}
├── GEMINI.md
└── .gemini/{skills,agents}/
```

## Local checkout

Clone the repository when you want to test an unpublished revision or work offline:

```powershell
git clone https://github.com/HanyeolKo/harness-factory.git
cd harness-factory
```

Connect that checkout to a runtime:

```powershell
claude --plugin-dir D:\workspace\harness-factory
codex plugin marketplace add D:\workspace\harness-factory
codex plugin marketplace list
gemini extensions link D:\workspace\harness-factory
```

For Codex, install or enable `harness-factory` from Plugins after registering the local checkout, then start a new task.

For a fully offline first run, the checkout must include `schema/`, `providers/`, `templates/`, `scripts/`, and `skills/`. Set `HARNESS_FACTORY_HOME` to the repository root when automatic source discovery is unavailable. See the setup guide for version pinning, updates, and resolver settings.

## Documentation

- [Installation, updates, and version pinning](docs/SETUP.md)
- [Operations, evaluation, and improvement](docs/OPERATIONS.md)
- [Learning Assist](docs/LEARNING-ASSIST.md)
- [Reporting Contract](docs/REPORTING-CONTRACT.md)
- [Learning Gate](docs/LEARNING-GATE.md)
- [Migration from plugin 0.1 or schema 1.0](docs/MIGRATION.md)
- [Constructor protocol](docs/CONSTRUCTOR-PROTOCOL.md)
- [Evaluation contract](docs/SKILL-EVALUATION.md)
- [Delivery checklist](CHECKLIST.md)

## Repository checks

Run the repository contracts before publishing a change:

```powershell
python scripts\test_runtime_neutral_contract.py
python scripts\test_self_evaluation_trigger.py
python scripts\test_learning_gate_contract.py
python scripts\skill_smoke_build_harness.py
python scripts\validate_runtime_neutral.py <target-project>
```

These checks cover the plugin 0.2.1 manifests, all seven skills, Claude/Codex/Gemini adapters, schema 1.1, projection parity, the deterministic trigger policy, the Learning Assist/reporting contract, and the Learning Gate's disabled/enabled integrity contract. The final command validates a generated harness in a real target project.
