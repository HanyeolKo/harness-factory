# Korean Output Policy

This policy applies the `fluent-korean` coding output style to every Korean output produced by the main agent, subagents, reports, explanations, documentation, and other generated artifacts.

## Authority and scope

- Source: `https://github.com/snflkd/fluent-korean/blob/main/plugins/fluent-korean/output-styles/fluent-korean.md`, ref `main`, blob `bce347c1db5566b1fbabebb2540efa1b8ba8b256`.
- Apply these rules whenever text is written in Korean. Do not translate text that must remain in another language.
- Do not apply them to quotations, code, code comments, identifiers, commit messages, log strings, or other project-convention text.
- Prefer an established Korean translation or transliteration for a proper noun or technical term. Keep the original term when no established Korean form exists.
- Do not imitate unclear, abbreviated, or highly colloquial wording from user input.
- A more specific artifact style explicitly requested by the user overrides this policy only for that artifact.

## Sentence construction

- Preserve every sentence element needed to identify the actor, action, object, condition, and result without relying on guesswork.
- Avoid excessive possessive constructions that hide omitted relationships.
- Except in headings and compact list labels, finish sentences with a predicate and a complete ending. Do not end prose as a loose noun phrase, adverbial phrase, or connective ending.
- Keep particles and endings when they clarify grammatical relationships. Use adverbs, auxiliary particles, prefinal endings, and auxiliary predicates when they make timing, intent, certainty, or responsibility explicit.

## Vocabulary and punctuation

- Combine precise Sino-Korean vocabulary with natural Korean syntax and explicit particles. Do not create compressed strings of technical nouns.
- Prefer literal, commonly used words. Do not replace ordinary nouns or verbs with figurative, metaphorical, field-inappropriate, or obscure dictionary words.
- Keep an established idiom only when replacing it would make the sentence less natural or less precise.
- Avoid the em dash because it compresses the relationship between clauses. Use a colon, conjunction, or separate sentence instead.

## Agent and delivery checks

- Before sending a Korean prompt to a subagent, check that the prompt follows this policy.
- Reapply this policy when integrating a subagent's result into any Korean output.
- Apply this policy to all Korean results, not only direct reports to the user.
- Immediately before delivery, check for omitted sentence elements, missing particles or endings, telegraphic noun strings, unclear metaphor, and compressed punctuation, then revise any violation.

## Honorific avoidance

This is a separate project override requested by the user.

- Avoid honorific Korean by default, including honorific titles, the subject-honorific marker `-시-`, deferential address, and polite or deferential sentence endings.
- Use a neutral written style such as `한다`, `이다`, and `있다`. Keep the tone professional, direct, and non-insulting rather than conversationally rude.
- Do not address the user by a title unless identification is necessary.
- An explicit user request for a particular tone or an artifact-specific convention overrides this rule for that output.
