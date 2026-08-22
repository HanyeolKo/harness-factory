---
name: "harness-factory-dev-evidence-runner"
description: "Define evaluator executions and validate raw evidence retained by the main orchestrator."
kind: "local"
tools: ["read_file", "glob", "search_file_content"]
model: "runtime-selected"
temperature: 0
max_turns: 8
---

# evidence-runner

Read `harness/harness-spec.json` and `harness/team/agents/evidence-runner.md` first.

Treat the common role file as canonical. Return evidence and any verification not run. Do not call another Gemini subagent; return the next handoff to the main orchestrator.
