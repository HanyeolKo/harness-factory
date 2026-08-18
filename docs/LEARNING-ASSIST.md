# LEARNING ASSIST

Learning Assist is an optional, user-requested comprehension tool. It does not replace or modify the existing Learning Gate and never blocks normal execution, review, pull request creation, or merge.

## Activation

Start Learning Assist only when the user explicitly asks to understand, explain, study, or check comprehension of a completed or in-progress change.

Examples:

- "Explain this change."
- "Help me understand this flow."
- "Quiz me on what changed."
- "Check whether I understood this implementation."

Do not start a learning session automatically because a change is large, risky, unfamiliar, or because the Learning Gate is enabled or disabled.

## Explanation contract

Explain the actual change before testing comprehension.

1. Start with concrete behavior: what changed, what now happens, and why it matters.
2. Use the user's configured report language and terminology.
3. Prefer plain language before technical terminology.
4. Introduce at most three core concepts in one learning round.
5. Define an unfamiliar term when it first appears and connect it to the concrete behavior already explained.
6. Avoid vocabulary that is not needed to understand the code or design.
7. Do not require the user to infer meaning from abstract architecture vocabulary.
8. Point to a small reading order only when source inspection would materially improve understanding.

Bad order:

```text
orchestration boundary -> invariant -> infer what the code does
```

Preferred order:

```text
what the code does -> why responsibility is located there -> technical term, if useful
```

## Quiz contract

The quiz measures the user's mental model, not vocabulary recall.

- Use 3 to 5 questions.
- Prefer scenario, cause/effect, data-flow, failure-path, and design-intent questions.
- Do not ask for definitions merely to test terminology.
- Keep question wording simpler than the concept being tested.
- Track comprehension by concept rather than only by aggregate score.

Suggested concept states:

- `understood`
- `hint-needed`
- `needs-explanation`

## Wrong-answer remediation

Do not reveal the final answer immediately after an incorrect response.

1. First miss: give a directional hint that identifies what relationship or boundary to reconsider.
2. Second miss: give a concrete scenario or counterexample that narrows the reasoning path.
3. Third miss: explain the concept directly, including why the earlier reasoning failed.

A wrong answer caused by confusing wording or undefined terminology is a documentation failure, not evidence of poor comprehension. Rewrite the question or explanation before retrying.

## Session artifacts

Learning Assist artifacts are optional and project-owned. When durable session output is useful, store it under:

```text
harness/learning-assist/<change-id>/
├── explanation.md
├── quiz.json
└── comprehension.json
```

Do not require these files for ordinary task completion. Do not bind them to commits or delivery gates unless the user explicitly asks for that policy.

## Relationship to Learning Gate

Learning Gate and Learning Assist are independent:

- Learning Gate: existing user-controlled delivery gate with its current policy and verification semantics.
- Learning Assist: on-demand explanation and comprehension support with no delivery-blocking semantics.

A project may use either, both, or neither. Do not silently convert Learning Assist results into Learning Gate evidence.