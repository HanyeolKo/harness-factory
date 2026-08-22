#!/usr/bin/env python3
"""Contract tests for Learning Assist, the optional Learning Gate, and reporting."""
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
REPORTING_TEMPLATE = ROOT / "templates" / "policies" / "reporting.json.tmpl"
GATE_DOC_TEMPLATE = ROOT / "templates" / "policies" / "LEARNING-GATE.md.tmpl"
CHANGE_REPORT_TEMPLATE = ROOT / "templates" / "reports" / "CHANGE-REPORT.md.tmpl"
ASSIST_EXPLANATION_TEMPLATE = ROOT / "templates" / "learning-assist" / "explanation.md.tmpl"
ASSIST_QUIZ_TEMPLATE = ROOT / "templates" / "learning-assist" / "quiz.json.tmpl"
ASSIST_COMPREHENSION_TEMPLATE = ROOT / "templates" / "learning-assist" / "comprehension.json.tmpl"
VERIFIER_TEMPLATE = ROOT / "templates" / "triggers" / "verify_learning_gate.py.tmpl"


def run_verifier(
    script: Path, harness_root: Path, *args: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), str(harness_root), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def run_git(project_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(project_root), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} failed: {result.stdout} {result.stderr}"
        )
    return result.stdout.strip()


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def expect_status(
    result: subprocess.CompletedProcess[str], code: int, status: str
) -> dict:
    if result.returncode != code:
        raise AssertionError(
            f"expected exit {code}, got {result.returncode}: "
            f"{result.stdout} {result.stderr}"
        )
    payload = json.loads(result.stdout)
    if payload.get("status") != status:
        raise AssertionError(f"expected status {status}, got {payload}")
    return payload


def expect_error(payload: dict, fragment: str) -> None:
    if not any(fragment in error for error in payload.get("errors", [])):
        raise AssertionError(f"expected error containing {fragment!r}, got {payload}")


def initialize_repository(project_root: Path) -> None:
    run_git(project_root, "init")
    run_git(project_root, "config", "user.name", "Learning Gate Test")
    run_git(project_root, "config", "user.email", "learning-gate@example.invalid")


def assert_learning_assist_contract() -> None:
    required = (
        REPORTING_TEMPLATE,
        GATE_DOC_TEMPLATE,
        CHANGE_REPORT_TEMPLATE,
        ASSIST_EXPLANATION_TEMPLATE,
        ASSIST_QUIZ_TEMPLATE,
        ASSIST_COMPREHENSION_TEMPLATE,
        ROOT / "docs" / "LEARNING-ASSIST.md",
        ROOT / "docs" / "REPORTING-CONTRACT.md",
    )
    for path in required:
        if not path.is_file():
            raise AssertionError(f"missing {path}")

    reporting_text = REPORTING_TEMPLATE.read_text(encoding="utf-8")
    reporting = json.loads(
        reporting_text.replace("{{REPORT_DESTINATION}}", "file").replace(
            "{{REPORT_TARGET_JSON}}", json.dumps("harness/reports")
        )
    )
    assert reporting["reader_destination"] == "file"
    assert reporting["reader_target"] == "harness/reports"
    assert reporting["canonical_evidence"] == "file"
    assert reporting["style"] == "plain-language-first"

    change_report = CHANGE_REPORT_TEMPLATE.read_text(encoding="utf-8")
    assert "Explain concrete behavior" in change_report
    assert "Do not copy the full diff" in change_report

    explanation = ASSIST_EXPLANATION_TEMPLATE.read_text(encoding="utf-8")
    assert "Explain concrete behavior first" in explanation
    assert "at most three core concepts" in explanation
    assert "natural report-language prose" in explanation
    assert "exact technical token once" in explanation
    assert "Preserve machine tokens, not surrounding jargon" in explanation

    assist_doc = (ROOT / "docs" / "LEARNING-ASSIST.md").read_text(encoding="utf-8")
    assert "one main idea per sentence" in assist_doc
    assert "no unexplained mixed-language nouns" in assist_doc
    assert "`localized` mode" in assist_doc

    assist_quiz = json.loads(
        ASSIST_QUIZ_TEMPLATE.read_text(encoding="utf-8")
        .replace("{{CHANGE_ID}}", "CHG-ASSIST-001")
        .replace("{{CONCEPT_1}}", "flow")
        .replace("{{CONCEPT_2}}", "failure")
        .replace("{{CONCEPT_3}}", "responsibility")
        .replace("{{QUESTION_1}}", "What changed?")
        .replace("{{QUESTION_2}}", "What happens in this scenario?")
        .replace("{{QUESTION_3}}", "What happens on failure?")
    )
    assert assist_quiz["blocking"] is False
    assert assist_quiz["remediation"] == {
        "first_miss": "directional-hint",
        "second_miss": "concrete-scenario",
        "final_miss": "record-then-explain",
    }

    comprehension = json.loads(
        ASSIST_COMPREHENSION_TEMPLATE.read_text(encoding="utf-8")
        .replace("{{CHANGE_ID}}", "CHG-ASSIST-001")
        .replace("{{CONCEPT_ID}}", "flow")
    )
    assert comprehension["concepts"][0]["state"] == "needs-explanation"
    assert comprehension["concepts"][0]["attempts"] == 0

    gate_doc = GATE_DOC_TEMPLATE.read_text(encoding="utf-8")
    for marker in (
        "Learning Assist explanation",
        "developer reads the explanation",
        "directional hint",
        "confusing wording or an undefined term",
    ):
        assert marker in gate_doc

    for path in (
        ROOT / "docs" / "LEARNING-ASSIST.md",
        ROOT / "skills" / "build-harness" / "references" / "RUNTIME-CONTRACT.md",
    ):
        assert "learning-assist" in path.read_text(encoding="utf-8")

    harness_template = (ROOT / "templates" / "HARNESS.md.tmpl").read_text(
        encoding="utf-8"
    )
    assert "Learning Assist explanation" in harness_template
    assert "no unexplained mixed-language nouns" in harness_template


def main() -> int:
    if not POLICY_TEMPLATE.is_file():
        raise AssertionError(f"missing {POLICY_TEMPLATE}")
    if not VERIFIER_TEMPLATE.is_file():
        raise AssertionError(f"missing {VERIFIER_TEMPLATE}")

    assert_learning_assist_contract()

    policy = json.loads(POLICY_TEMPLATE.read_text(encoding="utf-8"))
    assert policy["enabled"] is False
    assert policy["control"]["owner"] == "user"
    assert policy["control"]["agents_may_change_enabled"] is False
    assert policy["verification"]["require_source_commit_binding"] is True
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
        )
        expect_status(missing, 1, "fail")

        high_risk_exemption = run_verifier(
            verifier_path,
            harness_root,
            "--change-id",
            "CHG-RISK-001",
            "--changed-lines",
            "1",
            "--change-kind",
            "typo",
            "--risk-tag",
            "authentication-change",
        )
        high_risk_payload = expect_status(high_risk_exemption, 1, "fail")
        expect_error(high_risk_payload, "missing brief")

        invalid_change_id = run_verifier(
            verifier_path,
            harness_root,
            "--apply",
            "--change-id",
            "../outside",
        )
        invalid_id_payload = expect_status(invalid_change_id, 1, "fail")
        expect_error(invalid_id_payload, "--change-id must start")

        policy["quiz"]["minimum_score"] = "80"
        write_json(policy_path, policy)
        malformed_policy = run_verifier(
            verifier_path,
            harness_root,
            "--apply",
            "--change-id",
            "CHG-POLICY-001",
        )
        malformed_payload = expect_status(malformed_policy, 1, "fail")
        expect_error(malformed_payload, "quiz.minimum_score")
        policy["quiz"]["minimum_score"] = 80
        write_json(policy_path, policy)

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

        initialize_repository(project_root)
        run_git(project_root, "add", ".")
        run_git(project_root, "commit", "-m", "source change and learning evidence")
        source_sha = run_git(project_root, "rev-parse", "HEAD")

        verification_path = change_root / "verification.json"
        write_json(
            verification_path,
            {
                "change_id": "CHG-TEST-001",
                "source_commit_sha": source_sha,
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
        run_git(project_root, "add", verification_path.relative_to(project_root).as_posix())
        run_git(project_root, "commit", "-m", "record learning verification")

        passed = run_verifier(
            verifier_path,
            harness_root,
            "--apply",
            "--change-id",
            "CHG-TEST-001",
        )
        pass_payload = expect_status(passed, 0, "pass")
        assert pass_payload["source_commit_sha"] == source_sha
        assert pass_payload["evidence_commit_sha"] == run_git(
            project_root, "rev-parse", "HEAD"
        )

        answers = json.loads(answers_path.read_text(encoding="utf-8"))
        answers["answers"][0]["answer"] = "Changed after verification"
        write_json(answers_path, answers)
        stale_answers = run_verifier(
            verifier_path,
            harness_root,
            "--apply",
            "--change-id",
            "CHG-TEST-001",
        )
        stale_answers_payload = expect_status(stale_answers, 1, "fail")
        expect_error(stale_answers_payload, "answers_hash")
        expect_error(stale_answers_payload, "worktree must be clean")
        run_git(project_root, "restore", answers_path.relative_to(project_root).as_posix())

        (project_root / "application.txt").write_text("changed code\n", encoding="utf-8")
        run_git(project_root, "add", "application.txt")
        run_git(project_root, "commit", "-m", "change code after verification")
        stale_code = run_verifier(
            verifier_path,
            harness_root,
            "--apply",
            "--change-id",
            "CHG-TEST-001",
        )
        stale_code_payload = expect_status(stale_code, 1, "fail")
        expect_error(stale_code_payload, "changes after source_commit_sha")

    print("learning assist and learning gate contract: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
