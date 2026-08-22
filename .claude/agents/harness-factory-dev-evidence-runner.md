---
name: "harness-factory-dev-evidence-runner"
description: "Define evaluator executions and validate raw evidence retained by the main orchestrator."
model: "runtime-fast"
tools: "Read, Grep, Glob"
disallowedTools: "Write, Edit, NotebookEdit, Bash"
permissionMode: "plan"
---

# evidence-runner

Read `harness/harness-spec.json` and `harness/team/agents/evidence-runner.md` first.

Treat the common role file as canonical. Return evidence and any verification not run. Name the next role `harness-factory-dev-<role-id>`.
