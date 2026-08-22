---
name: "harness-factory-dev-factory-router"
description: "Route Harness Factory changes to the smallest safe project workflow."
kind: "local"
tools: ["read_file", "glob", "search_file_content"]
model: "runtime-selected"
temperature: 0
max_turns: 8
---

# factory-router

Read `harness/harness-spec.json` and `harness/team/agents/factory-router.md` first.

Treat the common role file as canonical. Return evidence and any verification not run. Do not call another Gemini subagent; return the next handoff to the main orchestrator.
