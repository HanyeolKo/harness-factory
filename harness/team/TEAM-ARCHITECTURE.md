# Team Architecture

`factory-router` selects the smallest workflow and records the evaluator. `factory-builder` changes canonical source. `evidence-runner` owns the check request and validates raw evidence while remaining read-only. The main orchestrator executes the exact request and persists evidence. `contract-evaluator` owns the task verdict. `defect-analyst` records stable failure keys without treating a task failure as a harness defect. `harness-improver` may act only after full attribution.

Normal DAG: `factory-router -> factory-builder -> evidence-runner -> contract-evaluator`, with failed or blocked verdicts handed to `defect-analyst`. Retry and improvement feedback live in loop contracts, not reverse DAG edges. Claude, Codex, and Gemini adapters project this same meaning.

## Evidence handoff

`evidence-runner` follows `harness/evaluation/EVIDENCE-CONTRACT.md`. It returns an exact execution request to the main orchestrator, then validates the resulting manifest and raw paths. It never writes project files or owns a verdict. The main orchestrator persists only evaluation evidence, and `contract-evaluator` blocks on missing, stale, escaped, or hash-mismatched evidence.
