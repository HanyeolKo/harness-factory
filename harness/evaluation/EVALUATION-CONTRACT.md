# Evaluation Contract

Task evaluator `factory-contract-tests` uses raw repository contract output and exit status. The read-only evidence runner owns the execution request and evidence validation; the main orchestrator executes and persists the exact request. Harness evaluator `harness-effect` is a baseline/control/treatment experiment. A task failure does not prove a harness defect. No validated raw evidence means no pass. Human approval remains a gate, not an evaluator.
