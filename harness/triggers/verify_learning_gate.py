#!/usr/bin/env python3
"""Deterministically verify an enabled project-owned learning gate."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


CHANGE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def file_hash(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return f"sha256:{digest}"


def run_git(project_root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(project_root), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def current_head(project_root: Path) -> str:
    result = run_git(project_root, "rev-parse", "HEAD")
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def canonical_commit(project_root: Path, revision: str) -> str:
    result = run_git(project_root, "rev-parse", "--verify", f"{revision}^" + "{commit}")
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def tracked_at(project_root: Path, revision: str, relative_path: str) -> bool:
    result = run_git(project_root, "cat-file", "-e", f"{revision}:{relative_path}")
    return result.returncode == 0


def changed_paths(project_root: Path, older: str, newer: str) -> list[str] | None:
    result = run_git(
        project_root,
        "diff",
        "--name-only",
        "--no-renames",
        f"{older}..{newer}",
    )
    if result.returncode != 0:
        return None
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def worktree_changes(project_root: Path) -> list[str] | None:
    result = run_git(
        project_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if result.returncode != 0:
        return None
    return [line.rstrip() for line in result.stdout.splitlines() if line.strip()]


def emit(status: str, **payload: Any) -> None:
    print(json.dumps({"status": status, **payload}, ensure_ascii=False, sort_keys=True))


def non_negative_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def positive_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 1


def percentage(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and 0 <= value <= 100
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("harness_root", type=Path)
    parser.add_argument("--change-id")
    parser.add_argument("--changed-lines", type=int, default=0)
    parser.add_argument("--risk-tag", action="append", default=[])
    parser.add_argument("--change-kind", action="append", default=[])
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    harness_root = args.harness_root.resolve()
    project_root = harness_root.parent
    policy_path = harness_root / "policies" / "learning-gate.json"

    try:
        policy = load_json(policy_path)
    except ValueError as exc:
        emit("fail", errors=[str(exc)])
        return 1

    control = policy.get("control")
    control_errors: list[str] = []
    if not isinstance(control, dict):
        control_errors.append("control must be an object")
    else:
        if control.get("owner") != "user":
            control_errors.append("control.owner must be 'user'")
        if control.get("agents_may_change_enabled") is not False:
            control_errors.append("control.agents_may_change_enabled must be false")
        if control.get("activation_requires_explicit_user_instruction") is not True:
            control_errors.append(
                "control.activation_requires_explicit_user_instruction must be true"
            )
    if control_errors:
        emit("fail", errors=control_errors)
        return 1

    enabled = policy.get("enabled")
    if not isinstance(enabled, bool):
        emit("fail", errors=["enabled must be a boolean"])
        return 1
    if not enabled:
        emit("skip", reason="learning-gate-disabled")
        return 0

    scope = policy.get("scope")
    if not isinstance(scope, dict):
        emit("fail", errors=["scope must be an object"])
        return 1
    threshold = scope.get("changed_lines_gte", 0)
    if not non_negative_integer(threshold):
        emit("fail", errors=["scope.changed_lines_gte must be a non-negative integer"])
        return 1
    if args.changed_lines < 0:
        emit("fail", errors=["--changed-lines must be a non-negative integer"])
        return 1
    configured_risks = scope.get("risk_tags", [])
    if not isinstance(configured_risks, list) or not all(
        isinstance(item, str) and item for item in configured_risks
    ):
        emit("fail", errors=["scope.risk_tags must be a string array"])
        return 1
    exemptions = policy.get("exemptions", [])
    if not isinstance(exemptions, list) or not all(
        isinstance(item, str) and item for item in exemptions
    ):
        emit("fail", errors=["exemptions must be a string array"])
        return 1

    supplied_kinds = set(args.change_kind)
    exempt = bool(supplied_kinds) and supplied_kinds.issubset(set(exemptions))
    matching_risks = sorted(set(args.risk_tag) & set(configured_risks))
    applicable = (
        args.apply
        or bool(matching_risks)
        or (not exempt and args.changed_lines >= threshold)
    )
    if not applicable:
        emit(
            "skip",
            reason="learning-gate-not-applicable",
            changed_lines=args.changed_lines,
            matching_risk_tags=matching_risks,
        )
        return 0

    if not args.change_id:
        emit("fail", errors=["--change-id is required when the gate applies"])
        return 1
    if not CHANGE_ID_PATTERN.fullmatch(args.change_id):
        emit(
            "fail",
            errors=[
                "--change-id must start with an alphanumeric character and contain "
                "only alphanumerics, '.', '_', or '-' (maximum 128 characters)"
            ],
        )
        return 1

    learning_root = (harness_root / "learning").resolve()
    if learning_root.parent != harness_root:
        emit("fail", errors=["harness/learning resolves outside the harness root"])
        return 1
    change_root = (learning_root / args.change_id).resolve()
    if change_root.parent != learning_root:
        emit("fail", errors=["--change-id resolves outside harness/learning"])
        return 1

    quiz_policy = policy.get("quiz")
    policy_errors: list[str] = []
    if not isinstance(quiz_policy, dict):
        policy_errors.append("quiz policy must be an object")
        quiz_policy = {}
    expected_count = quiz_policy.get("question_count", 5)
    min_free_text = quiz_policy.get("minimum_free_text_questions", 3)
    minimum_score = quiz_policy.get("minimum_score", 80)
    required_score = quiz_policy.get("required_concepts_score", 100)
    max_attempts = quiz_policy.get("max_attempts", 3)
    if not positive_integer(expected_count):
        policy_errors.append("quiz.question_count must be a positive integer")
    if not non_negative_integer(min_free_text):
        policy_errors.append(
            "quiz.minimum_free_text_questions must be a non-negative integer"
        )
    elif positive_integer(expected_count) and min_free_text > expected_count:
        policy_errors.append(
            "quiz.minimum_free_text_questions must not exceed quiz.question_count"
        )
    if not percentage(minimum_score):
        policy_errors.append("quiz.minimum_score must be a number from 0 to 100")
    if not percentage(required_score):
        policy_errors.append(
            "quiz.required_concepts_score must be a number from 0 to 100"
        )
    if not positive_integer(max_attempts):
        policy_errors.append("quiz.max_attempts must be a positive integer")

    configured_verification = policy.get("verification")
    if not isinstance(configured_verification, dict):
        policy_errors.append("verification policy must be an object")
        configured_verification = {}
    for field in (
        "require_source_commit_binding",
        "require_quiz_hash_match",
        "require_answers_hash_match",
    ):
        if field in configured_verification and not isinstance(
            configured_verification[field], bool
        ):
            policy_errors.append(f"verification.{field} must be a boolean")
    if policy_errors:
        emit("fail", errors=policy_errors)
        return 1

    required_paths = {
        "brief": change_root / "brief.md",
        "diff_explanation": change_root / "diff-explanation.md",
        "quiz": change_root / "quiz.json",
        "answers": change_root / "answers.json",
        "verification": change_root / "verification.json",
    }
    errors: list[str] = []
    for label, path in required_paths.items():
        if not path.is_file():
            errors.append(f"missing {label}: {path}")
    if errors:
        emit("fail", errors=errors)
        return 1

    for label in ("brief", "diff_explanation"):
        if not required_paths[label].read_text(encoding="utf-8").strip():
            errors.append(f"{label} must not be empty")

    try:
        quiz = load_json(required_paths["quiz"])
        answers = load_json(required_paths["answers"])
        verification = load_json(required_paths["verification"])
    except ValueError as exc:
        errors.append(str(exc))
        emit("fail", errors=errors)
        return 1

    questions = quiz.get("questions")
    if not isinstance(questions, list):
        errors.append("quiz.questions must be an array")
        questions = []
    if len(questions) != expected_count:
        errors.append(
            f"quiz must contain exactly {expected_count} questions, found {len(questions)}"
        )

    question_ids: list[str] = []
    free_text_count = 0
    for index, question in enumerate(questions):
        if not isinstance(question, dict):
            errors.append(f"quiz.questions[{index}] must be an object")
            continue
        question_id = question.get("id")
        if not isinstance(question_id, str) or not question_id:
            errors.append(f"quiz.questions[{index}].id must be a non-empty string")
            continue
        question_ids.append(question_id)
        if question.get("type") == "free-text":
            free_text_count += 1
        text = question.get("question")
        if not isinstance(text, str) or not text.strip():
            errors.append(f"quiz question {question_id} must have text")
        concepts = question.get("required_concepts")
        if not isinstance(concepts, list) or not concepts or not all(
            isinstance(item, str) and item for item in concepts
        ):
            errors.append(
                f"quiz question {question_id} must declare required_concepts"
            )
    if len(question_ids) != len(set(question_ids)):
        errors.append("quiz question IDs must be unique")
    if free_text_count < min_free_text:
        errors.append(
            f"quiz requires at least {min_free_text} free-text questions, found {free_text_count}"
        )

    answer_items = answers.get("answers")
    answer_map: dict[str, str] = {}
    if not isinstance(answer_items, list):
        errors.append("answers.answers must be an array")
        answer_items = []
    for index, answer in enumerate(answer_items):
        if not isinstance(answer, dict):
            errors.append(f"answers.answers[{index}] must be an object")
            continue
        question_id = answer.get("question_id")
        text = answer.get("answer")
        if not isinstance(question_id, str) or not question_id:
            errors.append(f"answers.answers[{index}].question_id is invalid")
            continue
        if question_id in answer_map:
            errors.append(f"duplicate answer for {question_id}")
        if not isinstance(text, str) or not text.strip():
            errors.append(f"answer for {question_id} must not be empty")
            text = ""
        answer_map[question_id] = text
    if set(answer_map) != set(question_ids):
        errors.append("answers must cover every quiz question exactly once")

    if quiz.get("change_id") != args.change_id:
        errors.append("quiz.change_id does not match --change-id")
    if answers.get("change_id") != args.change_id:
        errors.append("answers.change_id does not match --change-id")
    if verification.get("change_id") != args.change_id:
        errors.append("verification.change_id does not match --change-id")

    head_sha = current_head(project_root)
    source_sha = verification.get("source_commit_sha")
    if configured_verification.get("require_source_commit_binding", True):
        if not head_sha:
            errors.append("cannot resolve current commit SHA")
        if not isinstance(source_sha, str) or not source_sha:
            errors.append("verification.source_commit_sha must be a commit SHA")
        else:
            resolved_source_sha = canonical_commit(project_root, source_sha)
            if not resolved_source_sha or resolved_source_sha != source_sha:
                errors.append(
                    "verification.source_commit_sha must be a full valid commit SHA"
                )
            elif head_sha:
                ancestor = run_git(
                    project_root,
                    "merge-base",
                    "--is-ancestor",
                    source_sha,
                    head_sha,
                )
                if ancestor.returncode != 0:
                    errors.append(
                        "verification.source_commit_sha must be an ancestor of HEAD"
                    )
                else:
                    relative_paths: dict[str, str] = {}
                    for label, path in required_paths.items():
                        try:
                            relative_paths[label] = path.relative_to(
                                project_root
                            ).as_posix()
                        except ValueError:
                            errors.append(f"{label} resolves outside the project root")
                    for label in ("brief", "diff_explanation", "quiz", "answers"):
                        relative_path = relative_paths.get(label)
                        if relative_path and not tracked_at(
                            project_root, source_sha, relative_path
                        ):
                            errors.append(
                                f"{label} must be committed in source_commit_sha"
                            )
                    verification_path = relative_paths.get("verification")
                    if verification_path and not tracked_at(
                        project_root, head_sha, verification_path
                    ):
                        errors.append("verification.json must be committed at HEAD")
                    paths_after_source = changed_paths(
                        project_root, source_sha, head_sha
                    )
                    if paths_after_source is None:
                        errors.append("cannot compare source_commit_sha with HEAD")
                    elif verification_path and set(paths_after_source) != {
                        verification_path
                    }:
                        errors.append(
                            "changes after source_commit_sha must be limited to "
                            f"{verification_path}"
                        )
                    dirty_paths = worktree_changes(project_root)
                    if dirty_paths is None:
                        errors.append("cannot inspect project worktree state")
                    elif dirty_paths:
                        errors.append("project worktree must be clean during verification")

    score = verification.get("score")
    if not percentage(score) or score < minimum_score:
        errors.append(f"verification.score must be at least {minimum_score}")
    concept_score = verification.get("required_concepts_score")
    if not percentage(concept_score) or concept_score < required_score:
        errors.append(
            f"verification.required_concepts_score must be at least {required_score}"
        )
    if verification.get("required_concepts_passed") is not True:
        errors.append("verification.required_concepts_passed must be true")
    attempt_count = verification.get("attempt_count")
    if (
        not isinstance(attempt_count, int)
        or isinstance(attempt_count, bool)
        or attempt_count < 1
        or attempt_count > max_attempts
    ):
        errors.append(f"verification.attempt_count must be between 1 and {max_attempts}")

    if configured_verification.get("require_quiz_hash_match", True):
        if verification.get("quiz_hash") != file_hash(required_paths["quiz"]):
            errors.append("verification.quiz_hash does not match quiz.json")
    if configured_verification.get("require_answers_hash_match", True):
        if verification.get("answers_hash") != file_hash(required_paths["answers"]):
            errors.append("verification.answers_hash does not match answers.json")

    if errors:
        emit("fail", errors=errors)
        return 1

    emit(
        "pass",
        change_id=args.change_id,
        source_commit_sha=source_sha,
        evidence_commit_sha=head_sha,
        score=score,
        required_concepts_score=concept_score,
        matching_risk_tags=matching_risks,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
