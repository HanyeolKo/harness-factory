# Environment

- Target: Harness Factory repository root.
- Python: 3.11 or later; use a known executable when `python` is a Windows Store shim.
- Primary task evaluator: `python scripts/test_runtime_neutral_contract.py`.
- Additional repository checks: `python scripts/test_self_evaluation_trigger.py`, `python scripts/test_learning_gate_contract.py`, and `python scripts/skill_smoke_build_harness.py`.
- Target validator: `python scripts/validate_runtime_neutral.py .`.
- Source areas: `schema/`, `providers/`, `templates/`, `scripts/`, `skills/`, `docs/`, `principles/`, `interview/`, and `examples/`.
- Do not publish, release, rewrite history, delete evidence, or change compatibility semantics without the matching approval gate.
