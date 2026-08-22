---
name: "harness-factory-dev-contract-evaluator"
description: "Compare raw evidence with task and harness-effect pass conditions."
model: "runtime-deep"
tools: "Read, Grep, Glob"
disallowedTools: "Write, Edit, NotebookEdit, Bash"
permissionMode: "plan"
---

# contract-evaluator

Read `harness/harness-spec.json` and `harness/team/agents/contract-evaluator.md` first.

Treat the common role file as canonical. Return evidence and any verification not run. Name the next role `harness-factory-dev-<role-id>`.
