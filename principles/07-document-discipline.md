# Principle 7 — Index-First Document Discipline

## Statement

Every runtime-facing instruction and memory document consumes reading budget. New harnesses therefore use concise English canonical prose, explicit line and summary limits, and index-first progressive disclosure. Do not store bilingual copies of internal content.

## Default budgets for new harnesses

| Content | Field | Default |
|---|---|---|
| Canonical skill instructions | `limits.max_instruction_lines` | 120 lines |
| Memory documents and `memory/INDEX.md` | `memory.max_document_lines` | 80 lines |
| Memory index summary | `memory.max_summary_chars` | 160 characters |

These fields are optional in existing schema 1.0 and 1.1 specs for backward compatibility. Missing fields do not invalidate or auto-translate project-owned content. New harnesses include them, and migrations add them only as an explicit, preservation-aware delta.

## Rules

1. **Split before exceeding a limit** — Keep required procedure in the canonical file and move optional detail, examples, and variants into references loaded only when relevant.
2. **Index every document set** — An index row records routing metadata, not a second copy of the document. Read the index first, then selected documents.
3. **Use `HARNESS.md` as the top index** — Every generated document or sub-index appears in its file map.
4. **Use one durable-memory index** — `memory/INDEX.md` uses `ID | Path | Summary | Read when | Source | Last verified | Status`. Current state and events remain in `state/state.json` and `ledger/journal.jsonl` rather than memory.
5. **Update lifecycle atomically** — Create, move, rename, supersede, archive, and index updates occur in one transaction. Active paths exist; IDs and paths are unique.
6. **Preserve before deleting** — Prefer `superseded` or `archived`. Do not overwrite, rename, move, or delete user-owned or unknown-origin memory without explicit approval.
7. **Keep presentation separate** — `communication.report_language` and `communication.terminology` change user-facing narrative only. They do not create translated canonical copies and are excluded from the effect hash.

## Budget exceptions

Keep a document whole only when splitting would reduce correctness or cost more than it saves:

| Exception | Examples | Reason |
|---|---|---|
| Required sequential instruction | A procedure that must be followed without a file boundary | Splitting risks skipped steps |
| Atomic project contract | Schema, API contract, evaluation rubric, domain glossary | Partial reading risks a wrong verdict |
| Higher routing overhead | A boundary-sized file with dense cross-references | Extra index reads cost more than they save |

Mark an instruction exception at the top of the file:

```text
<!-- instruction-budget exception: <type> — <reason> -->
```

Mark a memory exception at the top of the file:

```text
<!-- reading-budget exception: <type> — <reason> -->
```

Record the exception in the relevant index. An over-budget file without the correct marker fails deterministic validation. The validator may continue to recognize legacy exception markers for compatibility; all new writes use the English markers above. A budget failure can create an evaluation signal, but improvement still requires attribution.

## Constructor requirements

- Apply these budgets to generated output after placeholder substitution, not only to templates.
- Store discovery material as an index and concise summaries; reference large source material at its existing path.
- When reconciling a legacy harness without an index, inventory memory in place before adding `memory/INDEX.md`. Do not move files merely to satisfy the new layout.
- The goal is smaller reading units, not deletion of useful evidence or context.
