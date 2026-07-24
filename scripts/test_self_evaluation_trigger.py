#!/usr/bin/env python3
"""Contract tests for the deterministic harness self-evaluation lifecycle."""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
import unittest
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_self_evaluation.py"
RECORDER = ROOT / "scripts" / "record_self_evaluation.py"
CHECKER_TEMPLATE = ROOT / "templates" / "triggers" / "check_self_evaluation.py.tmpl"
RECORDER_TEMPLATE = ROOT / "templates" / "triggers" / "record_self_evaluation.py.tmpl"
WORK_ROOT = ROOT / ".test-work"
WATCHED_PATHS = [
    ".claude/skills/harness/SKILL.md",
    ".codex/skills/harness/SKILL.md",
    ".gemini/skills/harness/SKILL.md",
]


def load_checker():
    spec = importlib.util.spec_from_file_location("harness_self_evaluation", CHECKER)
    if spec is None or spec.loader is None:  # pragma: no cover - import guard
        raise RuntimeError(f"cannot load {CHECKER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER_MODULE = load_checker()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


class WorkspaceDirectory:
    """Windows-safe disposable directory rooted in the writable workspace."""

    def __enter__(self) -> Path:
        WORK_ROOT.mkdir(exist_ok=True)
        self.path = WORK_ROOT / f"self-eval-{uuid.uuid4().hex}"
        self.path.mkdir()
        return self.path

    def __exit__(self, exc_type, exc, traceback) -> None:
        resolved = self.path.resolve()
        if resolved.parent != WORK_ROOT.resolve():  # pragma: no cover - safety guard
            raise RuntimeError(f"refusing cleanup outside {WORK_ROOT}: {resolved}")
        shutil.rmtree(resolved, ignore_errors=False)
        try:
            WORK_ROOT.rmdir()
        except OSError:
            pass


def policy() -> dict[str, Any]:
    return {
        "mode": "event-driven",
        "checker": "harness/triggers/check_self_evaluation.py",
        "state": "harness/state/self-evaluation.json",
        "evaluation_loop": "harness/loops/HARNESS-EVAL-LOOP.md",
        "evaluator": "harness-effect",
        "targeted_suite": "harness/evaluation/suites/targeted.json",
        "watched_paths": list(WATCHED_PATHS),
        "targeted_sample_rate": 0.0,
        "full_interval_units": 20,
        "cooldown_units": 3,
        "budget_ratio": 0.1,
        "success_rate_drop_points": 5,
        "cost_increase_ratio": 0.25,
        "retry_threshold": 3,
        "minimum_samples": 5,
        "mandatory_events": [
            "canonical-contract-change",
            "agent-change",
            "skill-change",
            "evaluator-change",
            "adapter-change",
            "coldstart-fail",
            "parity-fail",
        ],
    }


def main_state() -> dict[str, Any]:
    return {
        "phase": "ready",
        "queue": [{"id": "U-001", "status": "todo", "evaluator": "task-tests"}],
        "next_action": "Run U-001",
        "improve": {
            "fail_counts": {},
            "coldstart_fail": False,
        },
    }


def self_state() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "current_unit": "U-001",
        "units_since_full": 0,
        "last_full_at": None,
        "cooldown_remaining_units": 0,
        "pending_events": [],
        "baseline": {"success_rate": 0.9, "cost_per_unit": 10.0},
        "recent": {"samples": 5, "success_rate": 0.9, "cost_per_unit": 10.0},
        "rolling": {
            "window_units": 10,
            "passed": 5,
            "failed": 0,
            "retries": 0,
            "operation_cost": 100.0,
            "evaluation_cost": 0.0,
        },
        "hashes": {"canonical": "", "adapters": ""},
        "acknowledged": {"coldstart_fail": False, "fail_counts": {}},
        "last_decision": {"decision": "none", "reasons": [], "verdict": None},
    }


def build_harness(target: Path) -> Path:
    harness = target / "harness"
    spec = {
        "schema_version": "1.1",
        "harness": {"id": "trigger-fixture", "purpose": "test", "root": "harness"},
        "loops": {"fail_threshold": 3},
        "self_evaluation": policy(),
    }
    write_json(harness / "harness-spec.json", spec)
    write_json(harness / "state/state.json", main_state())
    write_json(harness / "state/self-evaluation.json", self_state())
    write_text(harness / "team/agents/router.md", "# router")
    write_text(harness / "loops/HARNESS-EVAL-LOOP.md", "# effect evaluation")
    write_text(harness / "evaluation/EVALUATION-CONTRACT.md", "# contract")
    write_json(harness / "evaluation/suites/targeted.json", {"schema_version": "1.0"})

    for relative in WATCHED_PATHS:
        write_text(target / relative, f"# adapter {relative}")

    trigger = harness / "triggers/check_self_evaluation.py"
    recorder = harness / "triggers/record_self_evaluation.py"
    trigger.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(CHECKER, trigger)
    shutil.copyfile(RECORDER, recorder)
    acknowledge_hashes(harness)
    return harness


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_state(harness: Path) -> dict[str, Any]:
    return read_json(harness / "state/self-evaluation.json")


def replace_state(harness: Path, **updates: Any) -> None:
    state = read_state(harness)
    state.update(updates)
    write_json(harness / "state/self-evaluation.json", state)


def acknowledge_hashes(harness: Path) -> None:
    spec = read_json(harness / "harness-spec.json")
    state = read_state(harness)
    state["hashes"]["canonical"] = CHECKER_MODULE.canonical_hash(harness)
    state["hashes"]["adapters"] = CHECKER_MODULE.adapter_hash(
        harness.parent, spec["self_evaluation"]["watched_paths"], harness
    )
    write_json(harness / "state/self-evaluation.json", state)


def run_checker(harness: Path) -> tuple[dict[str, Any], str]:
    result = subprocess.run(
        [sys.executable, str(CHECKER), str(harness)],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    output = result.stdout.strip()
    return json.loads(output), output


def freeze_decision(harness: Path, result: dict[str, Any] | None = None) -> Path:
    if result is None:
        result, _ = run_checker(harness)
    path = harness / "evaluation/runs" / uuid.uuid4().hex / "trigger.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return path


def explicit_full_override(original: dict[str, Any]) -> dict[str, Any]:
    frozen_original = json.loads(json.dumps(original))
    result = json.loads(json.dumps(original))
    result["decision"] = "full"
    result["mandatory"] = False
    result["reasons"] = [*frozen_original["reasons"], "explicit-user-request"]
    result["override"] = {
        "kind": "explicit-user-request",
        "original": frozen_original,
    }
    return result


def run_recorder(
    harness: Path,
    decision: str,
    verdict: str = "neutral",
    at: str = "2026-07-24T12:00:00+09:00",
    decision_file: Path | None = None,
) -> tuple[int, dict[str, Any], str]:
    if decision_file is None:
        decision_file = freeze_decision(harness)
    decision_argument = decision_file.relative_to(harness.parent)
    result = subprocess.run(
        [
            sys.executable,
            str(harness / "triggers/record_self_evaluation.py"),
            str(harness),
            "--decision",
            decision,
            "--decision-file",
            str(decision_argument),
            "--verdict",
            verdict,
            "--at",
            at,
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output = result.stdout.strip()
    return result.returncode, json.loads(output), output


def update_main_improve(harness: Path, **updates: Any) -> None:
    state_path = harness / "state/state.json"
    state = read_json(state_path)
    state["improve"].update(updates)
    write_json(state_path, state)


class SelfEvaluationTriggerTests(unittest.TestCase):
    def assert_decision(self, result: dict[str, Any], expected: str) -> None:
        self.assertIn(result["decision"], {"none", "targeted", "full"})
        self.assertNotEqual("improve", result["decision"])
        self.assertEqual(expected, result["decision"])

    def test_templates_are_byte_identical_to_runtime_scripts(self) -> None:
        self.assertEqual(CHECKER.read_bytes(), CHECKER_TEMPLATE.read_bytes())
        self.assertEqual(RECORDER.read_bytes(), RECORDER_TEMPLATE.read_bytes())

    def test_stable_boundary_returns_none_without_writing(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            before = {
                path.relative_to(target).as_posix(): path.read_bytes()
                for path in target.rglob("*")
                if path.is_file()
            }
            result, output = run_checker(harness)
            after = {
                path.relative_to(target).as_posix(): path.read_bytes()
                for path in target.rglob("*")
                if path.is_file()
            }
            self.assert_decision(result, "none")
            self.assertFalse(result["mandatory"])
            self.assertEqual([], result["reasons"])
            self.assertRegex(result["current_canonical_hash"], r"^[0-9a-f]{64}$")
            self.assertRegex(result["current_adapter_hash"], r"^[0-9a-f]{64}$")
            self.assertEqual(before, after)
            self.assertEqual(
                output,
                json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
            )

    def test_targeted_signals_are_deterministic(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            state = read_state(harness)
            state["recent"]["cost_per_unit"] = 12.5
            state["rolling"]["retries"] = 3
            write_json(harness / "state/self-evaluation.json", state)
            first, _ = run_checker(harness)
            second, _ = run_checker(harness)
            self.assert_decision(first, "targeted")
            self.assertEqual(first, second)
            self.assertEqual(["cost-regression", "retry-pressure"], first["reasons"])

    def test_sample_rate_one_selects_targeted_and_zero_does_not(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            spec_path = harness / "harness-spec.json"
            spec = read_json(spec_path)
            spec["self_evaluation"]["targeted_sample_rate"] = 1.0
            write_json(spec_path, spec)
            acknowledge_hashes(harness)
            sampled, _ = run_checker(harness)
            self.assert_decision(sampled, "targeted")
            self.assertIn("deterministic-sample", sampled["reasons"])

            spec["self_evaluation"]["targeted_sample_rate"] = 0.0
            write_json(spec_path, spec)
            acknowledge_hashes(harness)
            unsampled, _ = run_checker(harness)
            self.assert_decision(unsampled, "none")

    def test_full_for_success_regression_and_interval(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            state = read_state(harness)
            state["recent"]["success_rate"] = 0.84
            state["units_since_full"] = 20
            write_json(harness / "state/self-evaluation.json", state)
            result, _ = run_checker(harness)
            self.assert_decision(result, "full")
            self.assertFalse(result["mandatory"])
            self.assertEqual(["full-interval", "success-rate-regression"], result["reasons"])

    def test_mandatory_event_bypasses_budget_and_cooldown(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            state = read_state(harness)
            state["pending_events"] = ["agent-change"]
            state["cooldown_remaining_units"] = 3
            state["rolling"]["evaluation_cost"] = 20.0
            write_json(harness / "state/self-evaluation.json", state)
            result, _ = run_checker(harness)
            self.assert_decision(result, "full")
            self.assertTrue(result["mandatory"])
            self.assertIn("agent-change", result["reasons"])
            self.assertEqual([], result["deferred_reasons"])

    def test_repeated_failure_and_coldstart_are_mandatory(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            update_main_improve(
                harness, fail_counts={"stable-key": 3}, coldstart_fail=True
            )
            result, _ = run_checker(harness)
            self.assert_decision(result, "full")
            self.assertTrue(result["mandatory"])
            self.assertIn("coldstart-fail", result["reasons"])
            self.assertIn("repeat-failure:stable-key", result["reasons"])

    def test_budget_and_cooldown_defer_nonmandatory_signals(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            state = read_state(harness)
            state["rolling"]["retries"] = 3
            state["rolling"]["evaluation_cost"] = 10.0
            write_json(harness / "state/self-evaluation.json", state)
            budgeted, _ = run_checker(harness)
            self.assert_decision(budgeted, "none")
            self.assertEqual(["evaluation-budget"], budgeted["deferred_reasons"])
            self.assertIn("retry-pressure", budgeted["reasons"])

            state["rolling"]["evaluation_cost"] = 0.0
            state["cooldown_remaining_units"] = 1
            write_json(harness / "state/self-evaluation.json", state)
            cooling, _ = run_checker(harness)
            self.assert_decision(cooling, "none")
            self.assertEqual(["cooldown"], cooling["deferred_reasons"])

    def test_canonical_hash_excludes_operational_churn_only(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            baseline = CHECKER_MODULE.canonical_hash(harness)
            excluded = {
                "budget/usage.json": "{}",
                "evaluation/reports/R-001.json": "{}",
                "evaluation/runs/U-001.log": "done",
                "ledger/journal.jsonl": "{}",
                "state/transient.json": "{}",
            }
            for relative, content in excluded.items():
                write_text(harness / relative, content)
                self.assertEqual(baseline, CHECKER_MODULE.canonical_hash(harness), relative)

            write_text(harness / "evaluation/EVALUATION-CONTRACT.md", "changed")
            changed = CHECKER_MODULE.canonical_hash(harness)
            self.assertNotEqual(baseline, changed)
            result, _ = run_checker(harness)
            self.assert_decision(result, "full")
            self.assertTrue(result["mandatory"])
            self.assertIn("canonical-contract-change", result["reasons"])

    def test_adapter_drift_and_deletion_are_mandatory_full(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            write_text(target / WATCHED_PATHS[0], "changed")
            changed, _ = run_checker(harness)
            self.assert_decision(changed, "full")
            self.assertTrue(changed["mandatory"])
            self.assertEqual(["adapter-change"], changed["reasons"])

        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            (target / WATCHED_PATHS[1]).unlink()
            deleted, _ = run_checker(harness)
            self.assert_decision(deleted, "full")
            self.assertTrue(deleted["mandatory"])
            self.assertEqual(["adapter-change"], deleted["reasons"])

    def test_full_record_acknowledges_same_mandatory_signal(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            update_main_improve(
                harness, fail_counts={"stable-key": 3}, coldstart_fail=True
            )
            before, _ = run_checker(harness)
            self.assert_decision(before, "full")

            code, recorded, output = run_recorder(harness, "full", "neutral")
            self.assertEqual(0, code)
            self.assertTrue(recorded["recorded"])
            self.assertNotIn("\n", output)
            state = read_state(harness)
            self.assertEqual("2026-07-24T03:00:00Z", state["last_full_at"])
            self.assertEqual(
                {"coldstart_fail": True, "fail_counts": {"stable-key": 3}},
                state["acknowledged"],
            )
            self.assertEqual([], state["pending_events"])
            self.assertEqual("neutral", state["last_decision"]["verdict"])

            after, _ = run_checker(harness)
            self.assert_decision(after, "none")
            self.assertFalse(after["mandatory"])

            state["pending_events"] = ["coldstart-fail"]
            write_json(harness / "state/self-evaluation.json", state)
            new_incident, _ = run_checker(harness)
            self.assert_decision(new_incident, "full")
            self.assertIn("coldstart-fail", new_incident["reasons"])

    def test_full_record_acknowledges_only_frozen_failure_count(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            state_path = harness / "state/self-evaluation.json"
            state = read_state(harness)
            state["pending_events"] = ["agent-change"]
            write_json(state_path, state)
            update_main_improve(harness, fail_counts={"stable-key": 2})
            frozen_result, _ = run_checker(harness)
            self.assert_decision(frozen_result, "full")
            self.assertEqual(
                {"coldstart_fail": False, "fail_counts": {"stable-key": 2}},
                frozen_result["acknowledgement"],
            )
            frozen = freeze_decision(harness, frozen_result)

            update_main_improve(harness, fail_counts={"stable-key": 3})
            code, result, _ = run_recorder(
                harness, "full", "neutral", decision_file=frozen
            )
            self.assertEqual(0, code)
            self.assertTrue(result["recorded"])
            self.assertEqual(
                {"coldstart_fail": False, "fail_counts": {"stable-key": 2}},
                read_state(harness)["acknowledged"],
            )
            next_boundary, _ = run_checker(harness)
            self.assert_decision(next_boundary, "full")
            self.assertIn("repeat-failure:stable-key", next_boundary["reasons"])

    def test_full_record_does_not_ack_coldstart_created_after_freeze(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            state_path = harness / "state/self-evaluation.json"
            state = read_state(harness)
            state["pending_events"] = ["evaluator-change"]
            write_json(state_path, state)
            frozen_result, _ = run_checker(harness)
            self.assert_decision(frozen_result, "full")
            self.assertFalse(frozen_result["acknowledgement"]["coldstart_fail"])
            frozen = freeze_decision(harness, frozen_result)

            update_main_improve(harness, coldstart_fail=True)
            code, result, _ = run_recorder(
                harness, "full", "neutral", decision_file=frozen
            )
            self.assertEqual(0, code)
            self.assertTrue(result["recorded"])
            self.assertFalse(read_state(harness)["acknowledged"]["coldstart_fail"])
            next_boundary, _ = run_checker(harness)
            self.assert_decision(next_boundary, "full")
            self.assertIn("coldstart-fail", next_boundary["reasons"])

    def test_new_failure_increment_retriggers_after_full_ack(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            update_main_improve(harness, fail_counts={"stable-key": 3})
            code, _, _ = run_recorder(harness, "full")
            self.assertEqual(0, code)
            stable, _ = run_checker(harness)
            self.assert_decision(stable, "none")

            update_main_improve(harness, fail_counts={"stable-key": 4})
            incremented, _ = run_checker(harness)
            self.assert_decision(incremented, "full")
            self.assertIn("repeat-failure:stable-key", incremented["reasons"])

    def test_failure_reset_below_ack_uses_zero_effective_ack(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            state = read_state(harness)
            state["acknowledged"]["fail_counts"] = {"stable-key": 5}
            write_json(harness / "state/self-evaluation.json", state)
            update_main_improve(harness, fail_counts={"stable-key": 3})
            result, _ = run_checker(harness)
            self.assert_decision(result, "full")
            self.assertIn("repeat-failure:stable-key", result["reasons"])

    def test_targeted_record_sets_cooldown_without_acknowledging_hashes(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            state = read_state(harness)
            state["recent"]["cost_per_unit"] = 12.5
            write_json(harness / "state/self-evaluation.json", state)
            before_hashes = dict(state["hashes"])
            code, recorded, _ = run_recorder(harness, "targeted", "inconclusive")
            self.assertEqual(0, code)
            self.assertEqual("targeted", recorded["decision"])

            state = read_state(harness)
            self.assertEqual(3, state["cooldown_remaining_units"])
            self.assertEqual(before_hashes, state["hashes"])
            self.assertEqual("inconclusive", state["last_decision"]["verdict"])
            immediate, _ = run_checker(harness)
            self.assert_decision(immediate, "none")
            self.assertEqual(["cooldown"], immediate["deferred_reasons"])
            self.assertIn("cost-regression", immediate["reasons"])

    def test_full_recorder_does_not_create_operational_hash_loop(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            state = read_state(harness)
            state["units_since_full"] = 20
            write_json(harness / "state/self-evaluation.json", state)
            before, _ = run_checker(harness)
            self.assert_decision(before, "full")
            code, _, _ = run_recorder(harness, "full", "improved")
            self.assertEqual(0, code)
            after, _ = run_checker(harness)
            self.assert_decision(after, "none")
            self.assertEqual([], after["reasons"])

    def test_recorder_rejects_decision_mismatch_without_writing(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            state_path = harness / "state/self-evaluation.json"
            state = read_state(harness)
            state["units_since_full"] = 20
            write_json(state_path, state)
            frozen = freeze_decision(harness)
            before = state_path.read_bytes()
            code, result, output = run_recorder(
                harness, "targeted", decision_file=frozen
            )
            self.assertNotEqual(0, code)
            self.assertFalse(result["recorded"])
            self.assertIn("decision-mismatch", result["error"])
            self.assertNotIn("\n", output)
            self.assertEqual(before, state_path.read_bytes())

    def test_recorder_rejects_unmarked_full_decision_mutation(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            state_path = harness / "state/self-evaluation.json"
            original, _ = run_checker(harness)
            self.assert_decision(original, "none")
            mutated = json.loads(json.dumps(original))
            mutated["decision"] = "full"
            frozen = freeze_decision(harness, mutated)
            before = state_path.read_bytes()

            code, result, _ = run_recorder(
                harness, "full", decision_file=frozen
            )
            self.assertNotEqual(0, code)
            self.assertFalse(result["recorded"])
            self.assertIn("unmarked-full-override", result["error"])
            self.assertEqual(before, state_path.read_bytes())

    def test_recorder_rejects_direct_cooldown_bypass(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            state_path = harness / "state/self-evaluation.json"
            state = read_state(harness)
            state["units_since_full"] = 20
            state["cooldown_remaining_units"] = 1
            write_json(state_path, state)
            original, _ = run_checker(harness)
            self.assert_decision(original, "none")
            self.assertEqual(["cooldown"], original["deferred_reasons"])
            mutated = json.loads(json.dumps(original))
            mutated["decision"] = "full"
            frozen = freeze_decision(harness, mutated)
            before = state_path.read_bytes()

            code, result, _ = run_recorder(
                harness, "full", decision_file=frozen
            )
            self.assertNotEqual(0, code)
            self.assertFalse(result["recorded"])
            self.assertIn("unmarked-full-override", result["error"])
            self.assertEqual(before, state_path.read_bytes())

    def test_recorder_rejects_direct_budget_bypass(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            state_path = harness / "state/self-evaluation.json"
            state = read_state(harness)
            state["units_since_full"] = 20
            state["rolling"]["evaluation_cost"] = 20.0
            write_json(state_path, state)
            original, _ = run_checker(harness)
            self.assert_decision(original, "none")
            self.assertEqual(["evaluation-budget"], original["deferred_reasons"])
            mutated = json.loads(json.dumps(original))
            mutated["decision"] = "full"
            frozen = freeze_decision(harness, mutated)
            before = state_path.read_bytes()

            code, result, _ = run_recorder(
                harness, "full", decision_file=frozen
            )
            self.assertNotEqual(0, code)
            self.assertFalse(result["recorded"])
            self.assertIn("unmarked-full-override", result["error"])
            self.assertEqual(before, state_path.read_bytes())

    def test_explicit_full_override_preserves_original_and_records(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            state_path = harness / "state/self-evaluation.json"
            state = read_state(harness)
            state["units_since_full"] = 20
            state["cooldown_remaining_units"] = 1
            write_json(state_path, state)
            original, _ = run_checker(harness)
            self.assert_decision(original, "none")
            self.assertEqual(["full-interval"], original["reasons"])
            self.assertEqual(["cooldown"], original["deferred_reasons"])
            override = explicit_full_override(original)
            frozen = freeze_decision(harness, override)

            code, result, _ = run_recorder(
                harness, "full", "neutral", decision_file=frozen
            )
            self.assertEqual(0, code)
            self.assertTrue(result["recorded"])
            persisted = read_json(frozen)
            self.assertEqual(original, persisted["override"]["original"])
            self.assertEqual(
                ["full-interval", "explicit-user-request"],
                read_state(harness)["last_decision"]["reasons"],
            )
            self.assertEqual(0, read_state(harness)["units_since_full"])

    def test_targeted_record_uses_frozen_decision_after_metrics_change(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            state_path = harness / "state/self-evaluation.json"
            state = read_state(harness)
            state["recent"]["cost_per_unit"] = 12.5
            write_json(state_path, state)
            frozen_result, _ = run_checker(harness)
            self.assert_decision(frozen_result, "targeted")
            frozen = freeze_decision(harness, frozen_result)

            state = read_state(harness)
            state["recent"]["cost_per_unit"] = 10.0
            state["rolling"]["evaluation_cost"] = 50.0
            write_json(state_path, state)
            current, _ = run_checker(harness)
            self.assert_decision(current, "none")

            code, result, _ = run_recorder(
                harness, "targeted", "neutral", decision_file=frozen
            )
            self.assertEqual(0, code)
            self.assertTrue(result["recorded"])
            recorded = read_state(harness)
            self.assertEqual(["cost-regression"], recorded["last_decision"]["reasons"])
            self.assertEqual(3, recorded["cooldown_remaining_units"])

    def test_recorder_rejects_stale_hash_without_writing(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            state_path = harness / "state/self-evaluation.json"
            state = read_state(harness)
            state["recent"]["cost_per_unit"] = 12.5
            write_json(state_path, state)
            frozen = freeze_decision(harness)
            before = state_path.read_bytes()

            write_text(target / WATCHED_PATHS[0], "adapter changed during evaluation")
            code, result, _ = run_recorder(
                harness, "targeted", decision_file=frozen
            )
            self.assertNotEqual(0, code)
            self.assertFalse(result["recorded"])
            self.assertIn("decision-file-stale:current_adapter_hash", result["error"])
            self.assertEqual(before, state_path.read_bytes())

    def test_full_record_preserves_events_added_after_frozen_decision(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            state_path = harness / "state/self-evaluation.json"
            state = read_state(harness)
            state["pending_events"] = ["agent-change"]
            write_json(state_path, state)
            frozen = freeze_decision(harness)

            state = read_state(harness)
            state["pending_events"].append("skill-change")
            write_json(state_path, state)
            code, result, _ = run_recorder(
                harness, "full", "neutral", decision_file=frozen
            )
            self.assertEqual(0, code)
            self.assertTrue(result["recorded"])
            self.assertEqual(["skill-change"], read_state(harness)["pending_events"])
            next_boundary, _ = run_checker(harness)
            self.assert_decision(next_boundary, "full")
            self.assertIn("skill-change", next_boundary["reasons"])

    def test_watched_target_escape_fails_closed(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            spec_path = harness / "harness-spec.json"
            spec = read_json(spec_path)
            spec["self_evaluation"]["watched_paths"] = ["../outside-adapter"]
            write_json(spec_path, spec)
            result, _ = run_checker(harness)
            self.assert_decision(result, "full")
            self.assertTrue(result["mandatory"])
            self.assertRegex(result["reasons"][0], r"^input-invalid:")
            self.assertIsNone(result["current_canonical_hash"])
            self.assertIsNone(result["current_adapter_hash"])

    def test_watched_symlink_escape_fails_closed_when_supported(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            link = target / ".claude/escape"
            link.parent.mkdir(parents=True, exist_ok=True)
            try:
                os.symlink(ROOT / "README.md", link)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink unavailable: {exc}")
            spec_path = harness / "harness-spec.json"
            spec = read_json(spec_path)
            spec["self_evaluation"]["watched_paths"] = [".claude/escape"]
            write_json(spec_path, spec)
            result, _ = run_checker(harness)
            self.assert_decision(result, "full")
            self.assertRegex(result["reasons"][0], r"^input-invalid:")
            self.assertIsNone(result["current_adapter_hash"])

    def test_malformed_input_fails_closed_with_compact_json(self) -> None:
        with WorkspaceDirectory() as target:
            harness = build_harness(target)
            (harness / "harness-spec.json").write_text("{", encoding="utf-8")
            result, output = run_checker(harness)
            self.assert_decision(result, "full")
            self.assertTrue(result["mandatory"])
            self.assertRegex(result["reasons"][0], r"^input-invalid:")
            self.assertIsNone(result["current_canonical_hash"])
            self.assertIsNone(result["current_adapter_hash"])
            self.assertIsNone(result["acknowledgement"])
            self.assertNotIn("\n", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
