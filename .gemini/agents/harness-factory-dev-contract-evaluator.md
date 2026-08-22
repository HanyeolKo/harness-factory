---
name: "harness-factory-dev-contract-evaluator"
description: "Compare raw evidence with task and harness-effect pass conditions."
kind: "local"
tools: ["read_file", "glob", "search_file_content"]
model: "runtime-selected"
temperature: 0
max_turns: 8
---

# contract-evaluator

Read `harness/harness-spec.json` and `harness/team/agents/contract-evaluator.md` first.

Treat the common role file as canonical. Return evidence and any verification not run. Do not call another Gemini subagent; return the next handoff to the main orchestrator.
