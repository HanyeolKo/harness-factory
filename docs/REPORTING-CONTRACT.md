# Reporting Contract

Every completed work unit leaves a short reader-facing Change Report so a developer can understand the work without reading the full diff.

## Default report

Generate a project-owned canonical file under:

```text
harness/reports/<change-id>/CHANGE-REPORT.md
```

The report is supporting documentation, not a delivery gate. Keep it to one screen or roughly one page.

Include only:

1. what changed;
2. why it changed;
3. user- or runtime-visible impact;
4. the important execution flow, when useful;
5. key files and what each owns;
6. validation actually performed;
7. anything the developer should know before continuing.

## Readability

Use plain language first:

- concrete behavior before architecture terminology;
- natural teammate-to-teammate development wording;
- no literal translation-like nouns when ordinary development language is clearer;
- stable code tokens and conventional technical terms remain exact;
- explain a behavior before naming a new technical concept;
- do not turn the report into a second copy of the diff.

Apply `communication.terminology` deliberately. In `localized` mode, use natural report-language prose and introduce an exact technical token once only when it helps the reader find the same concept in source or configuration. Exact identifiers, paths, commands, keys, status values, and verdicts stay unchanged, but ordinary explanatory nouns should not remain untranslated by default.

## Reader destination

New harness setup asks the user to choose one reader-facing destination:

- `file` (default): the canonical report file is also the reader copy;
- `notion`: keep the canonical Git file and publish a reader copy to the selected Notion target;
- `slack`: keep the canonical Git file and publish a reader copy to the selected Slack target.

Store the selected destination and target in `harness/policies/reporting.json`. For `notion` or `slack`, the target must come from the user; agents must not guess it. Existing harnesses without this policy remain valid until the user chooses to add it.

The canonical evidence mode stays `file` regardless of reader destination. Notion and Slack are reader copies, not replacements for Git-bound Learning Gate evidence.

## Learning Assist

When deeper understanding is requested, or when an enabled Learning Gate applies, Learning Assist starts from the Change Report and reads only the relevant actual diff/source. It expands the explanation without changing the basic reporting style.

Durable ordinary Assist output uses `harness/learning-assist/<change-id>/`, with reusable templates under `harness/learning-assist/_templates/`. Learning Gate evidence remains in its separate `harness/learning/<change-id>/` path.
