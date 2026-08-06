#!/usr/bin/env python3
"""Contract tests for the optional learning gate templates and verifier."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_TEMPLATE = ROOT / "templates" / "policies" / "learning-gate.json.tmpl"
VERIFIER_TEMPLATE = ROOT / "templates" / "triggers" / "verify_learning_gate.py.tmpl"


def run_verifier(script: Path, harness_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), str(harness_root), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def expect_status(result: subprocess.CompletedProcess[str], code: int, status: str) -> dict:
    if result.returncode != code:
        raise AssertionError(
            f"expected exit {code}, got {result.returncode}: {result.stdout} {result.stderr}"
        )
    payload = json.loads(result.stdout)
    if payload.get("status") != status:
        raise AssertionError(f"expected status {status}, got {payload}")
    return payload


def main() -> int:
    if not POLICY_TEMPLATE.is_file():
        raise AssertionError(f"missing {POLICY_TEMPLATE}")
    if not VERIFIER_TEMPLATE.is_file():
        raise AssertionError(f"missing {VERIFIER_TEMPLATE}")

    policy = json.loads(POLICY_TEMPLATE.read_text(encoding="utf-8"))
    assert policy["enabled"] is False
    assert policy["control"]["owner"] == "user"
    assert policy["control"]["agents_may_change_enabled"] is False
    compile(VERIFIER_TEMPLATE.read_text(encoding="utf-8"), str(VERIFIER_TEMPLATE), "exec")

    with tempfile.TemporaryDirectory() as temporary:
        project_root = Path(temporary) / "project"
        harness_root = project_root / "harness"
        policy_path = harness_root / "policies" / "learning-gate.json"
        verifier_path = harness_root / "triggers" / "verify_learning_gate.py"
        write_json(policy_path, policy)
        verifier_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(VERIFIER_TEMPLATE, verifier_path)

        disabled = run_verifier(verifier_path, harness_root)
        expect_status(disabled, 0, "skip")

        policy["enabled"] = True
        write_json(policy_path, policy)
        missing = run_verifier(
            verifier_path,
            harness_root,
            "--apply",
            "--change-id",
            "CHG-TEST-001",
            "--head-sha",
            "abc123",
        )
        expect_status(missing, 1, "fail")

        change_root = harness_root / "learning" / "CHG-TEST-001"
        change_root.mkdir(parents=True, exist_ok=True)
        (change_root / "brief.md").write_text("# Brief\n", encoding="utf-8")
        (change_root / "diff-explanation.md").write_text(
            "# Diff explanation\n", encoding="utf-8"
        )
        questions = []
        for number in range(1, 6):
            questions.append(
                {
                    "id": f"q{number}",
                    "type": "free-text" if number <= 3 else "scenario",
                    "question": f"Question {number}",
                    "required_concepts": [f"concept-{number}"],
                }
            )
        quiz_path = change_root / "quiz.json"
        answers_path = change_root / "answers.json"
        write_json(quiz_path, {"change_id": "CHG-TEST-001", "questions": questions})
        write_json(
            answers_path,
            {
                "change_id": "CHG-TEST-001",
                "author": "developer",
                "answers": [
                    {"question_id": f"q{number}", "answer": f"Answer {number}"}
                    for number in range(1, 6)
                ],
            },
        )
        write_json(
            change_root / "verification.json",
            {
                "change_id": "CHG-TEST-001",
                "commit_sha": "abc123",
                "developer": "developer",
                "score": 90,
                "required_concepts_score": 100,
                "required_concepts_passed": True,
                "attempt_count": 1,
                "completed_at": "2026-08-06T00:00:00Z",
                "quiz_hash": digest(quiz_path),
                "answers_hash": digest(answers_path),
            },
        )

        passed = run_verifier(
            verifier_path,
            harness_root,
            "--apply",
            "--change-id",
            "CHG-TEST-001",
            "--head-sha",
            "abc123",
        )
        expect_status(passed, 0, "pass")

        answers = json.loads(answers_path.read_text(encoding="utf-8"))
        answers["answers"][0]["answer"] = "Changed after verification"
        write_json(answers_path, answers)
        stale = run_verifier(
            verifier_path,
            harness_root,
            "--apply",
            "--change-id",
            "CHG-TEST-001",
            "--head-sha",
            "abc123",
        )
        payload = expect_status(stale, 1, "fail")
        if not any("answers_hash" in error for error in payload.get("errors", [])):
            raise AssertionError(f"expected answers hash failure, got {payload}")

    print("learning gate contract: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
