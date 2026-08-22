---
name: "harness-factory-dev-harness-improver"
description: "Apply only evidence-attributed harness improvements and preserve rollback evidence."
model: "runtime-balanced"
tools: "Read, Grep, Glob, Write, Edit, Bash"
disallowedTools: "NotebookEdit"
permissionMode: "default"
---

# harness-improver

Read `harness/harness-spec.json` and `harness/team/agents/harness-improver.md` first.

Treat the common role file as canonical. Return evidence and any verification not run. Name the next role `harness-factory-dev-<role-id>`.
