# Learning Assist

Learning Assist is the shared comprehension layer for ordinary change reporting and the optional Learning Gate.

It exists to reduce the cost of understanding AI-authored changes. It must not make routine work heavier than the implementation itself.

## Normal task flow

Every completed work unit leaves a short Change Report. The report explains what changed, why, the important runtime flow, key files, validation, and anything the developer should know next.

The Change Report is lightweight and never blocks delivery.

If the user asks for deeper explanation, Learning Assist expands only the relevant parts of the actual diff and source code. It uses the same plain-language-first rules as the Change Report.

## Learning Gate dependency

When the Learning Gate is enabled and applicable, it must use Learning Assist before asking quiz questions:

```text
implementation -> validation -> Change Report
                         -> Learning Assist explanation
                         -> developer reads explanation
                         -> Learning Gate quiz
                         -> pass or hint-based retry
```

The gate must not create a second, denser explanation vocabulary. Its `diff-explanation.md` is rendered with the Learning Assist explanation contract.

## Explanation contract

1. Explain concrete behavior first: what changed and what now happens.
2. Explain why the behavior changed.
3. Show the important control or data flow in execution order.
4. Point to only the files that materially help understanding.
5. Introduce technical terminology only after the behavior is understandable.
6. Define unfamiliar terms on first use.
7. Prefer wording a developer would naturally use when explaining the change to a teammate.
8. Avoid literal translation-like nouns and unnecessary abstraction.
9. Keep code tokens, identifiers, commands, API names, table names, and conventional technical terms exact.
10. Do not restate the full diff.

Preferred order:

```text
what changed -> why -> execution flow -> relevant code -> technical term if useful
```

Avoid:

```text
abstract term -> another abstract term -> force the reader to infer the code behavior
```

## Comprehension check

A user may request a quiz even when the Learning Gate is disabled. In that case the quiz is advisory and never blocks delivery.

Questions test the mental model, not vocabulary recall. Prefer cause/effect, runtime scenarios, failure paths, and responsibility questions.

For a wrong answer:

1. First miss: give a directional hint; do not reveal the answer.
2. Second miss: give a concrete scenario or counterexample; still do not reveal the final answer.
3. Final miss: explain the concept directly after the attempt is recorded.

If confusing wording or an undefined term caused the miss, rewrite the question or explanation before counting it as a comprehension failure.

## Optional session artifacts

When the user requests durable Learning Assist output, use:

```text
harness/learning-assist/<change-id>/
├── explanation.md
├── quiz.json
└── comprehension.json
```

These artifacts are advisory and do not block ordinary delivery. Generated harnesses keep reusable templates under `harness/learning-assist/_templates/`.

When the Learning Gate is enabled and applicable, do not duplicate this session into a second evidence set. Apply the same explanation contract directly to the Gate-owned `learning/<change-id>/diff-explanation.md` and keep Gate evidence under its existing path.

## Reader-facing report destination

During new-harness setup, ask where reader-facing change and learning documents should be organized. Store the answer in `harness/policies/reporting.json`.

- `file` — default; store under `harness/reports/`.
- `notion` — publish the reader copy to a user-selected Notion page or database.
- `slack` — publish the reader copy to a user-selected Slack channel or conversation.

For `notion` or `slack`, ask for the target identifier or URL. Do not guess it.

The project-owned Git files remain the canonical verification source even when reader copies are published externally. External publishing failure must be reported, but it must not invalidate already valid local evidence unless the user explicitly makes publication a delivery requirement.

## Relationship to Learning Gate

Learning Assist explains. Learning Gate verifies understanding and may block delivery according to its existing policy. The gate depends on the Assist explanation contract; Assist does not depend on the gate.
