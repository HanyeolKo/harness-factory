# Principle 7 — Index-First Document Discipline

## Statement

Every runtime-facing Markdown file consumes reading budget. Schema 1.2 harnesses target 50 lines and never exceed 100 lines per generated Markdown file. Use concise English canonical prose, one source of truth, and index-first progressive disclosure instead of bilingual or repeated copies.

## Default budgets

| Content | Field | Schema 1.2 default |
|---|---|---|
| Any generated Markdown | `limits.target_markdown_lines` | 50 lines |
| Any generated Markdown hard limit | `limits.max_markdown_lines` | 100 lines |
| Canonical skill instructions | `limits.max_instruction_lines` | 100 lines |
| Memory documents | `memory.max_document_lines` | 80 lines |
| Memory index summary | `memory.max_summary_chars` | 160 characters |

The 50-line value is the normal design target, not permission to remove required semantics. Split before 100 lines. Existing schema 1.0/1.1 fields and legacy exception markers remain compatible; migrations add limits only through an explicit preservation-aware delta.

## Rules

1. Keep required procedure in the canonical file and move optional detail, examples, and variants into a directly linked reference.
2. Use `HARNESS.md` as the top index. Read an index first, then only the documents required for the current action.
3. Keep one `memory/INDEX.md` with `ID | Path | Summary | Read when | Source | Last verified | Status`. Do not duplicate state or events from `state/state.json` and `ledger/journal.jsonl`.
4. Create, move, supersede, archive, and index-update a document set in one transaction. Active paths exist; IDs and paths are unique.
5. Prefer `superseded` or `archived`. Never delete, move, or overwrite user-owned, unknown-origin, or evidence files without exact-path approval.
6. Keep report language and terminology separate from canonical prose. Do not create translated canonical copies or include presentation-only fields in the harness-effect hash.
7. Count lines after placeholder substitution. A template that is short but renders beyond the configured hard limit fails.

A schema 1.2 Markdown file with 51–100 lines requires exactly one `<!-- document-budget exception: <type> | <reason> -->` marker at the first nonblank line, or immediately after YAML frontmatter. A file with 101 or more lines always fails.

## Exceptions and migration

Schema 1.2 constructors split generated Markdown rather than creating a new over-100-line exception. Validators may recognize legacy `instruction-budget exception` and `reading-budget exception` markers for schema 1.0/1.1 compatibility, but new schema 1.2 output does not rely on them.

When reconciling a legacy harness, inventory documents in place before adding an index. Preserve useful evidence and context; reduce runtime reading by routing, not by silent deletion.
