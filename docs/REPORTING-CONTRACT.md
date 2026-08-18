# REPORTING CONTRACT

Every completed work unit leaves a short Change Report so a developer can understand what was done without reading the full diff.

## Default report

Write `harness/reports/<change-id>/CHANGE-REPORT.md` after implementation and task verification.

The report is supporting documentation, not a delivery gate. It must not delay normal execution for additional design prose.

Keep it to one screen or roughly one page. Include only:

1. what changed;
2. why it changed;
3. user- or runtime-visible impact;
4. the important execution flow, when useful;
5. key files and what each owns;
6. validation actually performed;
7. anything the developer should know before continuing.

## Readability

Read `harness/reports/report-style.json` when rendering the report or Learning Assist material.

Use plain language first:

- Explain concrete behavior before architecture terminology.
- Prefer wording a developer would naturally use when explaining the change to a teammate.
- Avoid literal or translation-like nouns when ordinary development language is clearer.
- Keep stable code tokens, identifiers, commands, API names, table names, and conventional technical terms exact.
- Introduce a technical term only when it helps future code reading; explain the behavior first, then name the term.
- Do not turn the Change Report into a second copy of the diff.

## Relationship to Learning Assist

The Change Report is always lightweight. If the user asks for deeper explanation or a comprehension check, Learning Assist starts from this report and then reads only the relevant diff and source files.
