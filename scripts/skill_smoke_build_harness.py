#!/usr/bin/env python3
"""Compatibility entry point for the runtime-neutral harness contract tests.

The historical helper functions below remain temporarily for older callers;
main delegates to the Claude/Codex/Gemini fixture and parity test suite.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_HARNESS_FILES = [
    "HARNESS.md",
    "ENVIRONMENT.md",
    "team/TEAM-ARCHITECTURE.md",
    "team/agents/01-request-router.md",
    "team/agents/02-impact-analyst.md",
    "team/agents/03-task-coordinator.md",
    "team/agents/04-task-worker.md",
    "team/agents/05-evaluation-lead.md",
    "team/agents/06-verification-runner.md",
    "team/agents/07-defect-counter.md",
    "team/agents/08-improvement-coordinator.md",
    "loops/EXECUTION-LOOP.md",
    "loops/EVAL-LOOP.md",
    "loops/IMPROVE-LOOP.md",
    "recovery/RECOVERY-PLAYBOOK.md",
    "recovery/CHECKPOINT.md",
    "ledger/JOURNAL-FORMAT.md",
    "ledger/DECISIONS.md",
    "ledger/journal.jsonl",
    "budget/CONTEXT-BUDGET.md",
    "state/state.json",
]
TEAM_AGENT_FILES = {
    "01-request-router.md": "request-router",
    "02-impact-analyst.md": "impact-analyst",
    "03-task-coordinator.md": "task-coordinator",
    "04-task-worker.md": "task-worker",
    "05-evaluation-lead.md": "evaluation-lead",
    "06-verification-runner.md": "verification-runner",
    "07-defect-counter.md": "defect-counter",
    "08-improvement-coordinator.md": "improvement-coordinator",
}
FIELDS = {
    "TARGET": "skill-smoke-target",
    "PURPOSE": "스킬 경유 하네스 생성 경로를 검증하는 최소 문서 작업 하네스.",
    "CREATED_DATE": "2026-07-12",
    "DESIGN_ORIENTATION": "코스트 기반 자동검증·보완 — 기본형 유지",
    "COMMIT_POLICY": "스모크 검증에서는 커밋 생략, 실제 운영은 작업 단위 pass마다 1커밋",
    "WORK_UNIT": "문서 검증 단위",
    "EVALUATOR_PRIMARY": "python3 scripts/check_harness.py",
    "RETRO_INTERVAL": "작업 단위 10개",
    "JOURNAL_LEVEL": "작업 단위 시작/종료 + 판정 + 실패 + 결정",
    "BUDGET_POLICY": "보통 — 80% 경고 / 100% 체크포인트 후 교체",
    "OPERATION_MODE": "상주 세션형",
    "GATES": "없음",
    "HARNESS_ROOT": "harness",
    "RETRY_POLICY": "3회, 백오프 2s/4s/8s",
    "FAIL_THRESHOLD": "3",
    "ESCALATION_RULES": "재시도 상한 도달, 스코프 불명확, 세션 예산 소진 시 중지하고 사용자에게 보고한다.",
    "BUDGET_UNIT": "작업 단위 수",
    "UNIT_BUDGET": "세션당 1개 단위",
    "EVALUATOR_TYPE": "결정적-자동",
    "EVALUATOR_COMMANDS": "python3 scripts/check_harness.py",
    "PASS_CONDITION": "커맨드 exit 0",
    "RUBRIC": "결정적 evaluator 사용 — 루브릭 미사용.",
    "DETERMINISTIC_BOUNDARY": "형식·구조 검증은 스크립트, 개선 판단은 LLM",
    "PARALLELISM": "없음",
    "BUILD_COMMAND": "없음",
    "RUN_COMMAND": "없음",
    "LINT_COMMAND": "python3 scripts/check_harness.py",
    "PROJECT_TREE": "skill-smoke-target/\n├── harness/\n└── scripts/check_harness.py",
    "EXISTING_SCRIPTS": "scripts/check_harness.py",
    "FORBIDDEN": "하네스 검증 없이 pass 처리 금지",
    "INTERVIEW_SUMMARY": "스모크 검증 목적의 기본값 적용. 대상은 disposable target, 산출물은 문서.",
    "VERIFY_ROUND_1": "스모크 검증 스크립트 전 항목 pass",
    "SKILL_NAME": "skill-smoke-harness",
    "TEAM_ARCHITECTURE": "실행 팀 + 평가 레인 기본형",
}


def render(text: str) -> str:
    for key, value in FIELDS.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def copy_templates(target: Path) -> Path:
    harness = target / "harness"
    for template in (ROOT / "templates").rglob("*.tmpl"):
        rel = template.relative_to(ROOT / "templates")
        out = harness / rel.with_suffix("")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(template.read_text(encoding="utf-8")), encoding="utf-8")

    (harness / "ledger" / "journal.jsonl").write_text(
        json.dumps(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "event": "session_start",
                "unit": "U-001",
                "result": "created-by-skill-smoke",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    state = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "phase": "생성 완료 — 스모크 검증 대기",
        "queue": [
            {
                "id": "U-001",
                "desc": "생성된 하네스의 산출물 계약과 콜드스타트 필수값 검증",
                "evaluator": FIELDS["EVALUATOR_COMMANDS"],
                "status": "todo",
            }
        ],
        "current": {
            "id": "U-001",
            "step": "SELECT",
            "refs": ["harness/HARNESS.md", "harness/state/state.json"],
        },
        "next_action": "U-001 EVAL 실행: python3 scripts/check_harness.py",
        "improve": {
            "fail_counts": {},
            "units_since_retro": 0,
            "coldstart_fail": False,
            "last_retro_targets": [],
        },
        "budget": {"units_done": 0, "note": "스모크 검증용 disposable harness"},
    }
    (harness / "state" / "state.json").parent.mkdir(exist_ok=True)
    (harness / "state" / "state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return harness


def extract_skill_blocks() -> list[str]:
    rendered = render((ROOT / "templates" / "skills" / "SKILL-TEMPLATE.md").read_text(encoding="utf-8"))
    return re.findall(r"```markdown\n(.*?)\n```", rendered, flags=re.S)


def skill_name(block: str) -> str:
    match = re.search(r"^name:\s*(\S+)\s*$", block, flags=re.M)
    if not match:
        raise AssertionError("skill block is missing frontmatter name")
    return match.group(1)


def install_skills(target: Path) -> None:
    blocks = extract_skill_blocks()
    if len(blocks) != 3:
        raise AssertionError(f"expected 3 skill blocks, found {len(blocks)}")
    for block in blocks:
        name = skill_name(block)
        for base in [target / ".codex" / "skills", target / ".claude" / "skills"]:
            skill_dir = base / name
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(block + "\n", encoding="utf-8")


def install_runtime_agents(target: Path) -> None:
    """Install canonical team definitions as discoverable Claude subagents."""
    destination = target / ".claude" / "agents"
    destination.mkdir(parents=True, exist_ok=True)
    for source_name, role in TEAM_AGENT_FILES.items():
        text = (target / "harness" / "team" / "agents" / source_name).read_text(
            encoding="utf-8"
        )
        expected_name = f"{FIELDS['SKILL_NAME']}-{role}"
        if not text.startswith(f"---\nname: {expected_name}\n"):
            raise AssertionError(f"invalid agent frontmatter: {source_name}")
        (destination / f"{expected_name}.md").write_text(text, encoding="utf-8")


def write_target_checker(target: Path) -> None:
    scripts = target / "scripts"
    scripts.mkdir(exist_ok=True)
    checker = r'''
from pathlib import Path
import json
required = [
    "HARNESS.md", "ENVIRONMENT.md", "team/TEAM-ARCHITECTURE.md",
    "team/agents/01-request-router.md", "team/agents/02-impact-analyst.md",
    "team/agents/03-task-coordinator.md", "team/agents/04-task-worker.md",
    "team/agents/05-evaluation-lead.md", "team/agents/06-verification-runner.md",
    "team/agents/07-defect-counter.md", "team/agents/08-improvement-coordinator.md",
    "loops/EXECUTION-LOOP.md", "loops/EVAL-LOOP.md", "loops/IMPROVE-LOOP.md",
    "recovery/RECOVERY-PLAYBOOK.md", "recovery/CHECKPOINT.md",
    "ledger/JOURNAL-FORMAT.md", "ledger/DECISIONS.md",
    "ledger/journal.jsonl", "budget/CONTEXT-BUDGET.md", "state/state.json",
]
root = Path("harness")
missing = [p for p in required if not (root / p).exists()]
if missing:
    raise SystemExit(f"missing harness files: {missing}")
for path in root.rglob("*"):
    if path.is_file() and "{{" in path.read_text(encoding="utf-8"):
        raise SystemExit(f"unrendered placeholder: {path}")
state = json.loads((root / "state/state.json").read_text(encoding="utf-8"))
if not state.get("next_action"):
    raise SystemExit("state.next_action is empty")
if not state.get("queue") or not state["queue"][0].get("evaluator"):
    raise SystemExit("queue[0].evaluator is missing")
if not (root / "ledger/journal.jsonl").read_text(encoding="utf-8").strip():
    raise SystemExit("journal.jsonl has no initial line")
print("harness smoke target passes")
'''.strip()
    (scripts / "check_harness.py").write_text(checker + "\n", encoding="utf-8")


def validate_repo_build_harness_skills() -> None:
    """Validate downloadable build-harness skill copies for supported runtimes."""
    resolver_copies = []
    for runtime_dir in [".claude", ".codex"]:
        skill_dir = ROOT / runtime_dir / "skills" / "build-harness"
        skill = skill_dir / "SKILL.md"
        if not skill.exists():
            raise AssertionError(f"missing build-harness skill for {runtime_dir}")
        text = skill.read_text(encoding="utf-8")
        if not text.startswith("---\nname: build-harness"):
            raise AssertionError(f"invalid build-harness frontmatter for {runtime_dir}")
        for marker in ["Phase 0", "Phase 1", "Phase 2", "Phase 3", "Phase 4"]:
            if marker not in text:
                raise AssertionError(f"{runtime_dir} build-harness skill is missing {marker}")
        for marker in ["resolve_factory.py", ".claude/agents/", "실제 위임"]:
            if marker not in text:
                raise AssertionError(
                    f"{runtime_dir} build-harness skill is missing runtime marker: {marker}"
                )
        if "AskUserQuestion`으로 질의" in text:
            raise AssertionError(f"{runtime_dir} build-harness skill is Claude-specific")
        resolver = skill_dir / "scripts" / "resolve_factory.py"
        if not resolver.exists():
            raise AssertionError(f"missing resolver for {runtime_dir}")
        resolver_copies.append(resolver.read_bytes())
        result = subprocess.run(
            [sys.executable, str(resolver), "--factory-root", str(ROOT), "--offline"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        if Path(result.stdout.strip()).resolve() != ROOT.resolve():
            raise AssertionError(f"{runtime_dir} resolver returned the wrong local root")
    if resolver_copies[0] != resolver_copies[1]:
        raise AssertionError("Claude and Codex resolver copies differ")
    with tempfile.TemporaryDirectory(prefix="harness-factory-resolver-offline-") as tmp:
        isolated = Path(tmp)
        resolver = isolated / "skill" / "scripts" / "resolve_factory.py"
        resolver.parent.mkdir(parents=True)
        resolver.write_bytes(resolver_copies[0])
        cwd = isolated / "target"
        cwd.mkdir()
        env = os.environ.copy()
        env.pop("HARNESS_FACTORY_HOME", None)
        env.pop("HARNESS_FACTORY_REPO", None)
        env.pop("HARNESS_FACTORY_REF", None)
        result = subprocess.run(
            [
                sys.executable,
                str(resolver),
                "--offline",
                "--cache-dir",
                str(isolated / "empty-cache"),
            ],
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 2 or "offline" not in result.stderr:
            raise AssertionError("standalone resolver did not fail closed while offline")


def validate(target: Path) -> None:
    validate_repo_build_harness_skills()

    harness = target / "harness"
    missing = [p for p in REQUIRED_HARNESS_FILES if not (harness / p).exists()]
    if missing:
        raise AssertionError(f"missing files: {missing}")
    generated_paths = (
        list(harness.rglob("*"))
        + list((target / ".codex").rglob("*"))
        + list((target / ".claude").rglob("*"))
    )
    for path in generated_paths:
        if path.is_file() and "{{" in path.read_text(encoding="utf-8"):
            raise AssertionError(f"unrendered placeholder in {path}")
    state = json.loads((harness / "state" / "state.json").read_text(encoding="utf-8"))
    assert state["next_action"], "next_action is empty"
    assert state["queue"][0]["evaluator"], "first queued unit is missing evaluator"
    assert (harness / "ledger" / "journal.jsonl").read_text(encoding="utf-8").strip()
    team_text = (harness / "team/TEAM-ARCHITECTURE.md").read_text(encoding="utf-8")
    for marker in [
        "request-router",
        "impact-analyst",
        "task-coordinator",
        "task-worker",
        "verification-runner",
        "evaluation-lead",
        "defect-counter",
        "improvement-coordinator",
    ]:
        assert marker in team_text, f"missing team marker: {marker}"
    eval_loop = (harness / "loops/EVAL-LOOP.md").read_text(encoding="utf-8")
    assert "평가 팀 레인" in eval_loop, "EVAL-LOOP does not expose the evaluation team lane"
    improve_loop = (harness / "loops/IMPROVE-LOOP.md").read_text(encoding="utf-8")
    assert "자동 적용" in improve_loop, "IMPROVE-LOOP does not define automatic amendment"
    for role in TEAM_AGENT_FILES.values():
        agent_name = f"{FIELDS['SKILL_NAME']}-{role}"
        agent = target / ".claude" / "agents" / f"{agent_name}.md"
        text = agent.read_text(encoding="utf-8")
        assert text.startswith(f"---\nname: {agent_name}\n"), (
            f"invalid installed Claude agent: {agent_name}"
        )
        assert "{{" not in text, f"unrendered Claude agent placeholder: {agent_name}"
    skill_markers = {
        FIELDS["SKILL_NAME"]: [
            FIELDS["SKILL_NAME"] + "-request-router",
            FIELDS["SKILL_NAME"] + "-task-worker",
            FIELDS["SKILL_NAME"] + "-eval",
            "자동 실행",
        ],
        FIELDS["SKILL_NAME"] + "-eval": [
            FIELDS["SKILL_NAME"] + "-verification-runner",
            FIELDS["SKILL_NAME"] + "-evaluation-lead",
            FIELDS["SKILL_NAME"] + "-retro",
        ],
        FIELDS["SKILL_NAME"] + "-retro": [
            FIELDS["SKILL_NAME"] + "-improvement-coordinator",
            "자동 적용",
            "최대 3회",
        ],
    }
    for name, markers in skill_markers.items():
        for base in [target / ".codex" / "skills", target / ".claude" / "skills"]:
            text = (base / name / "SKILL.md").read_text(encoding="utf-8")
            assert text.startswith("---\nname: "), f"invalid skill frontmatter: {name}"
            assert "{{" not in text, f"unrendered skill placeholder: {name}"
            for marker in markers:
                assert marker in text, f"missing {marker!r} in generated skill: {name}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--keep",
        action="store_true",
        help="retained for CLI compatibility; runtime-neutral fixtures are always disposable",
    )
    parser.parse_args()

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/test_runtime_neutral_contract.py")],
        cwd=ROOT,
        check=False,
    )
    if result.returncode == 0:
        print("runtime-neutral build-harness smoke validation passed")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
