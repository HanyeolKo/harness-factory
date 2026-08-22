# Task Evaluation Loop

The read-only evidence runner defines the exact `python scripts/test_runtime_neutral_contract.py` request or affected declared checks. The main orchestrator executes that request and stores raw output only under the declared evidence root. The evidence runner validates the request binding, paths, manifest, and hashes. The contract evaluator compares validated exit status and required evidence with the pass condition. Missing, stale, escaped, or mismatched evidence is `blocked`, never `pass`.
