#!/usr/bin/env python3
"""Repository contracts for the provider-neutral harness factory."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
import tomllib
import unittest
import uuid
from pathlib import Path
from typing import Any

from validate_runtime_neutral import Validator

ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = ROOT / ".test-work"
NAMESPACE = "billing-harness"
PROVIDERS = {
    "claude": {
        "root_guidance": "CLAUDE.md",
        "skill_root": ".claude/skills",
        "agent_root": ".claude/agents",
        "agent_extension": ".md",
    },
    "codex": {
        "root_guidance": "AGENTS.md",
        "skill_root": ".agents/skills",
        "agent_root": ".codex/agents",
        "agent_extension": ".toml",
        "config": ".codex/config.toml",
    },
    "gemini": {
        "root_guidance": "GEMINI.md",
        "skill_root": ".gemini/skills",
        "agent_root": ".gemini/agents",
        "agent_extension": ".md",
    },
}
FACTORY_SKILLS = (
    "build-harness",
    "build-agent",
    "build-skill",
    "build-evaluator",
    "verify-harness",
    "evaluate-harness",
    "improve-harness",
)
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
DEFAULT_COMMUNICATION = {
    "artifact_language": "en",
    "report_language": "en",
    "terminology": "technical-english",
}
PROFILES_12 = ("core", "adaptive", "governed")
MARKDOWN_BUDGET_EXCEPTION = (
    "<!-- document-budget exception: atomic-project-contract | "
    "Keep this bounded runtime contract whole. -->"
)
ENGLISH_MEMORY_INDEX = (
    "# Memory Index\n\n"
    "| ID | Path | Summary | Read when | Source | Last verified | Status |\n"
    "|---|---|---|---|---|---|---|\n"
    "| - | - | No durable memory registered | - | - | 2026-07-24 | empty |"
)
LEGACY_KOREAN_MEMORY_INDEX = (
    "# Memory Index\n\n"
    "| ID | 경로 | 한 줄 요약 | 언제 읽나 | 출처 | 마지막 검증 | 상태 |\n"
    "|---|---|---|---|---|---|---|\n"
    "| - | - | 등록된 지속 메모리 없음 | - | - | 2026-07-24 | empty |"
)
SPECIAL_DESCRIPTION = (
    'Route billing requests: preserve #tags and "quoted" context.\n'
    "Keep this second line intact."
)
ROLES = [
    {
        "id": "billing-router",
        "description": SPECIAL_DESCRIPTION,
        "lane": "control",
        "capabilities": ["routing"],
        "domains": ["billing"],
        "model_tier": "fast",
        "access": "read-only",
    },
    {
        "id": "api-worker",
        "description": "Implement billing API changes.",
        "lane": "execution",
        "capabilities": ["execution"],
        "domains": ["billing"],
        "model_tier": "balanced",
        "access": "workspace-write",
    },
    {
        "id": "evidence-runner",
        "description": "Run checks and retain raw evidence.",
        "lane": "evaluation",
        "capabilities": ["verification"],
        "domains": ["billing"],
        "model_tier": "fast",
        "access": "read-only",
    },
    {
        "id": "contract-evaluator",
        "description": "Judge task and harness-effect evidence.",
        "lane": "evaluation",
        "capabilities": ["verdict"],
        "domains": ["billing"],
        "model_tier": "deep",
        "access": "read-only",
    },
    {
        "id": "defect-analyst",
        "description": "Count stable failure keys.",
        "lane": "evaluation",
        "capabilities": ["defect-counting"],
        "domains": ["billing"],
        "model_tier": "fast",
        "access": "read-only",
    },
    {
        "id": "harness-improver",
        "description": "Propose evidence-backed harness improvements.",
        "lane": "improvement",
        "capabilities": ["improvement"],
        "domains": ["billing"],
        "model_tier": "balanced",
        "access": "workspace-write",
    },
]
SKILLS_11 = [
    {
        "id": NAMESPACE,
        "kind": "entry",
        "entry_agent": "billing-router",
        "domains": ["billing"],
        "instructions": f"harness/skills/{NAMESPACE}/SKILL.md",
        "evaluator": "task-tests",
    },
    {
        "id": f"{NAMESPACE}-eval",
        "kind": "evaluation",
        "entry_agent": "contract-evaluator",
        "domains": ["billing"],
        "instructions": f"harness/skills/{NAMESPACE}-eval/SKILL.md",
        "evaluator": "task-tests",
    },
    {
        "id": f"{NAMESPACE}-verify",
        "kind": "verification",
        "entry_agent": "evidence-runner",
        "domains": ["billing"],
        "instructions": f"harness/skills/{NAMESPACE}-verify/SKILL.md",
        "evaluator": "task-tests",
    },
    {
        "id": f"{NAMESPACE}-evaluate",
        "kind": "harness-evaluation",
        "entry_agent": "contract-evaluator",
        "domains": ["billing"],
        "instructions": f"harness/skills/{NAMESPACE}-evaluate/SKILL.md",
        "evaluator": "harness-effect",
    },
    {
        "id": f"{NAMESPACE}-improve",
        "kind": "improvement",
        "entry_agent": "harness-improver",
        "domains": ["billing"],
        "instructions": f"harness/skills/{NAMESPACE}-improve/SKILL.md",
        "evaluator": "harness-effect",
    },
    {
        "id": f"{NAMESPACE}-billing",
        "kind": "domain",
        "entry_agent": "api-worker",
        "domains": ["billing"],
        "instructions": f"harness/skills/{NAMESPACE}-billing/SKILL.md",
        "evaluator": "task-tests",
    },
]


class WorkspaceDirectory:
    """Disposable directory created without tempfile's restrictive Windows ACL."""

    def __enter__(self) -> Path:
        WORK_ROOT.mkdir(exist_ok=True)
        self.path = WORK_ROOT / f"runtime-contract-{uuid.uuid4().hex}"
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


def render(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def json_scalar(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2))


def watched_paths_for(
    runtime_targets: list[str], skills: list[dict[str, Any]], agents: list[dict[str, Any]]
) -> list[str]:
    paths: set[str] = set()
    for runtime in runtime_targets:
        provider = PROVIDERS[runtime]
        paths.add(provider["root_guidance"])
        if "config" in provider:
            paths.add(provider["config"])
        paths.update(
            f"{provider['skill_root']}/{skill['id']}/SKILL.md" for skill in skills
        )
        paths.update(
            f"{provider['agent_root']}/{NAMESPACE}-{agent['id']}"
            f"{provider['agent_extension']}"
            for agent in agents
        )
    return sorted(paths)


def self_evaluation_policy(
    runtime_targets: list[str], skills: list[dict[str, Any]], agents: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "mode": "event-driven",
        "checker": "harness/triggers/check_self_evaluation.py",
        "state": "harness/state/self-evaluation.json",
        "evaluation_loop": "harness/loops/HARNESS-EVAL-LOOP.md",
        "evaluator": "harness-effect",
        "watched_paths": watched_paths_for(runtime_targets, skills, agents),
        "targeted_suite": "harness/evaluation/suites/targeted.json",
        "targeted_sample_rate": 0.05,
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


def make_spec(
    schema_version: str = "1.1",
    profile: str | None = None,
    runtime_targets: list[str] | None = None,
) -> dict[str, Any]:
    skills = json.loads(json.dumps(SKILLS_11))
    evaluators = [
        {
            "id": "task-tests",
            "scope": "task",
            "owner": "contract-evaluator",
            "runner": "evidence-runner",
            "type": "deterministic",
            "command": "python -m unittest",
            "pass_condition": "exit code is zero",
        },
        {
            "id": "harness-effect",
            "scope": "harness",
            "owner": "contract-evaluator",
            "runner": "evidence-runner",
            "type": "experiment",
            "command": "compare baseline control treatment",
            "pass_condition": "no regression within declared tolerance",
        },
    ]
    loops: dict[str, Any] = {
        "execution": "harness/loops/EXECUTION-LOOP.md",
        "evaluation": "harness/loops/EVAL-LOOP.md",
        "improvement": "harness/loops/IMPROVE-LOOP.md",
        "improvement_owner": "harness-improver",
        "fail_threshold": 3,
    }
    runtimes = list(runtime_targets or ["claude", "codex", "gemini"])
    if schema_version == "1.0":
        skills = [
            skill
            for skill in skills
            if skill["kind"] != "harness-evaluation"
        ]
        for skill in skills:
            skill.pop("evaluator", None)
            if skill["kind"] == "improvement":
                skill["id"] = f"{NAMESPACE}-retro"
                skill["instructions"] = f"harness/skills/{NAMESPACE}-retro/SKILL.md"
        evaluators = [
            {key: value for key, value in evaluators[0].items() if key != "scope"}
        ]
        loops["retro_interval"] = 10
        if runtime_targets is None:
            runtimes = ["claude", "codex"]
    spec: dict[str, Any] = {
        "schema_version": schema_version,
        "harness": {
            "id": NAMESPACE,
            "purpose": "Validate a provider-neutral generated harness.",
            "root": "harness",
        },
        "runtime_targets": runtimes,
        "limits": {"max_parallelism": 2, "max_delegation_depth": 2},
        "domains": [
            {"id": "billing", "paths": ["src/billing"], "coordinator": "api-worker"}
        ],
        "agents": json.loads(json.dumps(ROLES)),
        "skills": skills,
        "orchestration": {
            "entry_skill": NAMESPACE,
            "handoffs": [
                {
                    "from": "billing-router",
                    "to": "api-worker",
                    "when": "request is in the billing domain",
                    "artifacts": ["harness/ledger/journal.jsonl"],
                },
                {
                    "from": "api-worker",
                    "to": "evidence-runner",
                    "when": "implementation is ready for verification",
                    "artifacts": ["harness/state/state.json"],
                },
                {
                    "from": "evidence-runner",
                    "to": "contract-evaluator",
                    "when": "raw evidence is available",
                    "artifacts": ["harness/ledger/journal.jsonl"],
                },
                {
                    "from": "contract-evaluator",
                    "to": "defect-analyst",
                    "when": "verdict is fail",
                    "artifacts": ["harness/ledger/journal.jsonl"],
                },
            ],
        },
        "evaluators": evaluators,
        "approval_gates": [
            {
                "id": "production-change",
                "trigger": "a change targets production",
                "owner": "human",
                "required_action": "obtain explicit approval",
            }
        ],
        "loops": loops,
    }
    if schema_version in {"1.1", "1.2"}:
        spec["limits"]["max_instruction_lines"] = (
            100 if schema_version == "1.2" else 120
        )
        spec["communication"] = dict(DEFAULT_COMMUNICATION)
        if schema_version == "1.2":
            selected_profile = profile or "adaptive"
            spec["profile"] = selected_profile
            spec["harness"]["construction_receipt"] = (
                "harness/maintenance/runs/create-fixture/delta-plan.json"
            )
            spec["limits"].update(
                {"target_markdown_lines": 50, "max_markdown_lines": 100}
            )
            if selected_profile == "core":
                retained_agents = {
                    "billing-router",
                    "api-worker",
                    "contract-evaluator",
                }
                spec["agents"] = [
                    agent for agent in spec["agents"] if agent["id"] in retained_agents
                ]
                contract_evaluator = next(
                    agent
                    for agent in spec["agents"]
                    if agent["id"] == "contract-evaluator"
                )
                contract_evaluator["capabilities"] = [
                    "verification",
                    "verdict",
                    "defect-counting",
                ]
                spec["skills"] = [
                    skill
                    for skill in spec["skills"]
                    if skill["kind"] not in {"harness-evaluation", "improvement"}
                ]
                for skill in spec["skills"]:
                    if skill["kind"] in {"evaluation", "verification"}:
                        skill["entry_agent"] = "contract-evaluator"
                spec["evaluators"] = [
                    evaluator
                    for evaluator in spec["evaluators"]
                    if evaluator["scope"] == "task"
                ]
                spec["evaluators"][0]["runner"] = "contract-evaluator"
                spec["orchestration"]["handoffs"] = [
                    handoff
                    for handoff in spec["orchestration"]["handoffs"]
                    if handoff["from"] in retained_agents
                    and handoff["to"] in retained_agents
                ]
                spec["orchestration"]["handoffs"].append(
                    {
                        "from": "api-worker",
                        "to": "contract-evaluator",
                        "when": "implementation is ready for verification",
                        "artifacts": ["harness/state/state.json"],
                    }
                )
                spec["loops"].pop("improvement")
                spec["loops"].pop("improvement_owner")
                return spec

        spec["memory"] = {
            "index": "harness/memory/INDEX.md",
            "policy": "preserve-and-reconcile",
            "max_document_lines": 80,
            "max_summary_chars": 160,
        }
        spec["self_evaluation"] = self_evaluation_policy(
            runtimes, spec["skills"], spec["agents"]
        )
    return spec


def codex_instructions(role_id: str) -> str:
    return (
        f"Read harness/harness-spec.json and harness/team/agents/{role_id}.md first.\n\n"
        "Treat the common role file as the canonical instructions. Follow its input, "
        "output, access, approval-gate, and handoff contract. Return evidence and any "
        "verification not run."
    )


def common_files(
    harness: Path, schema_version: str, profile: str | None = None
) -> None:
    files = {
        "HARNESS.md": "# Harness\n\nRead harness-spec.json first.",
        "ENVIRONMENT.md": "# Environment\n\nEvaluator: python -m unittest",
        "team/TEAM-ARCHITECTURE.md": "# Team\n\nThe spec is canonical.",
        "loops/EXECUTION-LOOP.md": "# Execution\n\nExecute, task-evaluate, then trigger-check.",
        "loops/EVAL-LOOP.md": "# Task evaluation\n\nPreserve raw evidence.",
        "recovery/RECOVERY-PLAYBOOK.md": "# Recovery\n\nEscalate after bounded retry.",
        "recovery/CHECKPOINT.md": "# Checkpoint\n\nPersist next action.",
        "ledger/JOURNAL-FORMAT.md": "# Journal\n\nAppend only.",
        "ledger/DECISIONS.md": "# Decisions\n\nD-001 fixture.",
        "budget/CONTEXT-BUDGET.md": "# Budget\n\nEvaluation has a separate cap.",
    }
    if schema_version != "1.2" or profile != "core":
        files["loops/IMPROVE-LOOP.md"] = (
            "# Improvement\n\nRequire full effect evidence."
        )
    if schema_version in {"1.1", "1.2"} and profile != "core":
        files.update(
            {
                "loops/HARNESS-EVAL-LOOP.md": "# Harness effect evaluation\n\nCompare baseline, control, treatment.",
                "evaluation/EVALUATION-CONTRACT.md": "# Evaluation contract\n\nSeparate task and harness scopes.",
                "memory/INDEX.md": ENGLISH_MEMORY_INDEX,
            }
        )
    if schema_version == "1.2":
        files["reports/_templates/CHANGE-REPORT.md.tmpl"] = render(
            (ROOT / "templates/reports/CHANGE-REPORT.md.tmpl").read_text(
                encoding="utf-8"
            ),
            {
                "CHANGE_ID": "CHG-001",
                "CHANGE_SUMMARY": "Summarize the bounded change.",
                "CHANGE_REASON": "State the evidence-backed reason.",
                "CHANGE_IMPACT": "Describe the observable impact.",
                "FLOW_SUMMARY": "request -> change -> validation",
                "KEY_FILES": "List only relevant files.",
                "VALIDATION_SUMMARY": "List checks actually run.",
                "NEED_TO_KNOW": "Record the immediate next fact.",
            },
        )
        write_json(
            harness / "policies/reporting.json",
            {
                "schema_version": "1.0",
                "reader_destination": "file",
                "reader_target": "harness/reports",
                "canonical_evidence": "file",
                "style": "plain-language-first",
            },
        )
    if schema_version == "1.2" and profile in {"adaptive", "governed"}:
        files["maintenance/COMPONENT-MUTATION-PROTOCOL.md"] = (
            ROOT / "templates/maintenance/COMPONENT-MUTATION-PROTOCOL.md.tmpl"
        ).read_text(encoding="utf-8").replace("{{TARGET}}", NAMESPACE)
    if schema_version == "1.2" and profile == "governed":
        files.update(
            {
                "learning-assist/_templates/explanation.md.tmpl": (
                    "# Learning Assist explanation\n\n"
                    "Explain changed behavior from the actual diff and evidence."
                ),
                "policies/LEARNING-GATE.md": (
                    ROOT / "templates/policies/LEARNING-GATE.md.tmpl"
                ).read_text(encoding="utf-8").replace("{{HARNESS_ROOT}}", "harness"),
                "learning/_templates/brief.md.tmpl": (
                    "# Change Brief\n\nDescribe current behavior and the planned change."
                ),
                "learning/_templates/diff-explanation.md.tmpl": (
                    "# Diff Explanation\n\nExplain the actual behavior change."
                ),
            }
        )
        write_json(
            harness / "learning-assist/_templates/quiz.json.tmpl",
            {"purpose": "comprehension", "blocking": False, "questions": []},
        )
        write_json(
            harness / "learning-assist/_templates/comprehension.json.tmpl",
            {"status": "in-progress", "concepts": [], "notes": []},
        )
        for name, payload in {
            "quiz.json": {"questions": []},
            "answers.json": {"author": "developer", "answers": []},
            "verification.json": {"required_concepts_passed": False},
        }.items():
            write_json(harness / "learning/_templates" / f"{name}.tmpl", payload)
        learning_gate = json.loads(
            (ROOT / "templates/policies/learning-gate.json.tmpl").read_text(
                encoding="utf-8"
            )
        )
        write_json(harness / "policies/learning-gate.json", learning_gate)
        write_text(
            harness / "triggers/verify_learning_gate.py",
            "#!/usr/bin/env python3\n\"\"\"Verify governed Learning Gate evidence.\"\"\"",
        )
    for relative, text in files.items():
        write_text(harness / relative, text)
    write_text(harness / "ledger/journal.jsonl", '{"event":"session_start","unit":"U-001"}')
    state: dict[str, Any] = {
        "phase": "ready",
        "queue": [{"id": "U-001", "status": "todo", "evaluator": "task-tests"}],
        "next_action": "Run U-001",
    }
    if schema_version != "1.2" or profile != "core":
        state["improve"] = {
            "fail_counts": {},
            "units_since_retro": 0,
            "coldstart_fail": False,
            "last_retro_targets": [],
        }
    write_json(harness / "state/state.json", state)
    if schema_version in {"1.1", "1.2"} and profile != "core":
        (harness / "triggers").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(
            ROOT / "scripts/check_self_evaluation.py",
            harness / "triggers/check_self_evaluation.py",
        )
        shutil.copyfile(
            ROOT / "scripts/record_self_evaluation.py",
            harness / "triggers/record_self_evaluation.py",
        )
        targeted_suite = json.loads(
            (ROOT / "templates/evaluation/TARGETED-SUITE.json.tmpl").read_text(
                encoding="utf-8"
            )
        )
        write_json(harness / "evaluation/suites/targeted.json", targeted_suite)
        state = json.loads(
            (ROOT / "templates/state/self-evaluation.json.tmpl").read_text(
                encoding="utf-8"
            )
        )
        state["hashes"] = {"canonical": "", "adapters": ""}
        state["acknowledged"] = {"coldstart_fail": False, "fail_counts": {}}
        state["last_decision"] = {
            "decision": "none",
            "reasons": [],
            "verdict": None,
        }
        write_json(harness / "state/self-evaluation.json", state)


def render_agents(target: Path, spec: dict[str, Any]) -> None:
    common_template = (ROOT / "templates/team/agents/AGENT.md.tmpl").read_text(encoding="utf-8")
    claude_template = (ROOT / "templates/adapters/claude/agent.md.tmpl").read_text(encoding="utf-8")
    codex_template = (ROOT / "templates/adapters/codex/agent.toml.tmpl").read_text(encoding="utf-8")
    gemini_template = (ROOT / "templates/adapters/gemini/agent.md.tmpl").read_text(encoding="utf-8")
    for role in spec["agents"]:
        name = f"{NAMESPACE}-{role['id']}"
        is_read_only = role["access"] == "read-only"
        values = {
            "ROLE_ID": role["id"],
            "ROLE_LANE": role["lane"],
            "MODEL_TIER": role["model_tier"],
            "ROLE_ACCESS": role["access"],
            "ROLE_DESCRIPTION": role["description"],
            "ROLE_DOMAINS": ", ".join(role["domains"]),
            "ROLE_CAPABILITIES": ", ".join(role["capabilities"]),
            "ROLE_READ_SCOPE": "target project and harness",
            "ROLE_WRITE_SCOPE": "declared access only",
            "ROLE_INPUT_CONTRACT": "A bounded handoff.",
            "ROLE_OUTPUT_CONTRACT": "Evidence and next handoff.",
            "ROLE_INSTRUCTIONS": "Follow the canonical role contract.",
            "HARNESS_ROOT": "harness",
            "SKILL_NAME": NAMESPACE,
            "AGENT_NAME_JSON": json_scalar(name),
            "ROLE_DESCRIPTION_JSON": json_scalar(role["description"]),
            "CLAUDE_MODEL_JSON": json_scalar(
                {"fast": "runtime-fast", "balanced": "runtime-balanced", "deep": "runtime-deep"}[role["model_tier"]]
            ),
            "CLAUDE_TOOLS_JSON": json_scalar(
                "Read, Grep, Glob" if is_read_only else "Read, Grep, Glob, Write, Edit, Bash"
            ),
            "CLAUDE_DISALLOWED_TOOLS_JSON": json_scalar(
                "Write, Edit, NotebookEdit, Bash" if is_read_only else "NotebookEdit"
            ),
            "CLAUDE_PERMISSION_MODE_JSON": json_scalar("plan" if is_read_only else "default"),
            "CODEX_MODEL_JSON": json_scalar("runtime-selected"),
            "CODEX_REASONING_EFFORT_JSON": json_scalar(
                {"fast": "low", "balanced": "medium", "deep": "high"}[role["model_tier"]]
            ),
            "CODEX_SANDBOX_MODE_JSON": json_scalar(role["access"]),
            "CODEX_DEVELOPER_INSTRUCTIONS_JSON": json_scalar(codex_instructions(role["id"])),
            "GEMINI_TOOLS_JSON": json_scalar(
                ["read_file", "glob", "search_file_content"]
                if is_read_only
                else ["read_file", "glob", "search_file_content", "write_file", "replace", "run_shell_command"]
            ),
            "GEMINI_MODEL_JSON": json_scalar("runtime-selected"),
            "GEMINI_MAX_TURNS": "8",
        }
        write_text(target / "harness/team/agents" / f"{role['id']}.md", render(common_template, values))
        if "claude" in spec["runtime_targets"]:
            write_text(target / ".claude/agents" / f"{name}.md", render(claude_template, values))
        if "codex" in spec["runtime_targets"]:
            write_text(target / ".codex/agents" / f"{name}.toml", render(codex_template, values))
        if "gemini" in spec["runtime_targets"]:
            write_text(target / ".gemini/agents" / f"{name}.md", render(gemini_template, values))


def render_skills(target: Path, spec: dict[str, Any]) -> None:
    template = (ROOT / "templates/adapters/shared/SKILL.md.tmpl").read_text(encoding="utf-8")
    bodies = {
        "entry": "Route through the declared DAG, task-evaluate, then run the trigger checker.",
        "evaluation": "Run the task evaluator and preserve raw evidence.",
        "verification": "Validate structure and provider parity without changing the harness.",
        "harness-evaluation": "Run only at targeted or full trigger level; compare effects.",
        "improvement": "Require full evidence, change the common contract, then re-evaluate.",
        "domain": "Handle billing work through the declared entry agent.",
    }
    destinations = {
        "claude": ".claude/skills",
        "codex": ".agents/skills",
        "gemini": ".gemini/skills",
    }
    for skill in spec["skills"]:
        content = render(
            template,
            {
                "SKILL_ID": skill["id"],
                "SKILL_ID_JSON": json_scalar(skill["id"]),
                "SKILL_DESCRIPTION_JSON": json_scalar(f"Execute the {skill['kind']} fixture workflow."),
                "SKILL_KIND": skill["kind"],
                "ENTRY_AGENT": skill["entry_agent"],
                "SKILL_DOMAINS": ", ".join(skill["domains"]),
                "HARNESS_ROOT": "harness",
                "EVALUATOR_ID": skill.get("evaluator", "task-tests"),
                "SKILL_BODY": bodies[skill["kind"]],
            },
        )
        canonical = target / skill["instructions"]
        write_text(canonical, content)
        for runtime in spec["runtime_targets"]:
            destination = target / destinations[runtime] / skill["id"] / "SKILL.md"
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(canonical, destination)


def render_adapters(target: Path, spec: dict[str, Any]) -> None:
    blocks = {
        "claude": ("CLAUDE.md", "templates/adapters/claude/CLAUDE.md.block.tmpl"),
        "codex": ("AGENTS.md", "templates/adapters/codex/AGENTS.md.block.tmpl"),
        "gemini": ("GEMINI.md", "templates/adapters/gemini/GEMINI.md.block.tmpl"),
    }
    profile = spec.get("profile")
    profile_workflows = ""
    if profile in {"adaptive", "governed"} or spec["schema_version"] != "1.2":
        profile_workflows = (
            f"- Harness effect evaluation: `/{NAMESPACE}-evaluate`\n"
            f"- Evidence-gated improvement: `/{NAMESPACE}-improve`"
        )
    profile_runtime_rules = {
        "core": (
            "Keep work bounded to execution, task evidence, verdict, and structural "
            "verification. Do not activate memory, harness-effect evaluation, "
            "improvement, or installed learning files. Leave the short Change Report."
        ),
        "adaptive": (
            "Use durable memory, the mutation protocol, Change Reports, and "
            "event-driven harness evaluation only when their trigger applies."
        ),
        "governed": (
            "Use the adaptive lifecycle plus Learning Assist. Read the Learning Gate "
            "policy at review boundaries; only explicit user instruction may change it."
        ),
    }.get(profile, "Follow the installed lifecycle declared by the canonical spec.")
    for runtime in spec["runtime_targets"]:
        filename, template_path = blocks[runtime]
        block = render(
            (ROOT / template_path).read_text(encoding="utf-8"),
            {
                "SKILL_NAME": NAMESPACE,
                "HARNESS_ROOT": "harness",
                "PROFILE": profile or f"legacy-{spec['schema_version']}",
                "PROFILE_WORKFLOWS": profile_workflows,
                "PROFILE_RUNTIME_RULES": profile_runtime_rules,
            },
        )
        write_text(target / filename, f"# Existing {runtime} rules\n\n{block}")
    if "codex" in spec["runtime_targets"]:
        config = render(
            (ROOT / "templates/adapters/codex/config.toml.tmpl").read_text(encoding="utf-8"),
            {"CODEX_MAX_THREADS": "2", "CODEX_MAX_DEPTH": "2"},
        )
        write_text(target / ".codex/config.toml", config)


def build_fixture(
    target: Path,
    schema_version: str = "1.1",
    profile: str | None = None,
    runtime_targets: list[str] | None = None,
) -> dict[str, Any]:
    spec = make_spec(schema_version, profile, runtime_targets)
    write_json(target / "harness/harness-spec.json", spec)
    common_files(target / "harness", schema_version, spec.get("profile"))
    render_agents(target, spec)
    render_skills(target, spec)
    render_adapters(target, spec)
    if schema_version == "1.2":
        write_delta_plan(
            target,
            spec["profile"],
            runtime_targets=spec["runtime_targets"],
        )
    return spec


def interview_receipt(
    profile: str,
    runtime_targets: list[str] | None = None,
) -> dict[str, Any]:
    def decision(value: Any, source: str) -> dict[str, Any]:
        return {"value": value, "source": source}

    return {
        "status": "complete",
        "decisions": {
            "purpose": decision(
                "Validate a provider-neutral generated harness.", "request"
            ),
            "deliverable_type": decision("project harness", "request"),
            "task_evaluator": decision(
                "task-tests", "repository-confirmed"
            ),
            "operation_mode": decision("attended", "default-delegated"),
            "cost_sensitivity": decision("balanced", "default-delegated"),
            "report_language": decision("en", "default-delegated"),
            "terminology": decision("technical-english", "default-delegated"),
            "runtime_targets": decision(
                list(runtime_targets or ["claude", "codex", "gemini"]), "request"
            ),
            "approval_gates": decision(
                ["production-change"], "repository-confirmed"
            ),
            "reporting": {
                "enabled": decision(True, "default-delegated"),
                "reader_destination": decision("file", "default-delegated"),
                "reader_target": decision(
                    "harness/reports", "default-delegated"
                ),
            },
        },
        "profile": {
            "current": None,
            "recommended": profile,
            "selected": profile,
            "reason_codes": {
                "core": ["bounded-task-work"],
                "adaptive": ["durable-memory-needed"],
                "governed": ["learning-gate-requested"],
            }[profile],
            "confirmation_source": "user-answer",
            "override_reason": None,
        },
    }


def write_delta_plan(
    target: Path,
    profile: str,
    receipt: dict[str, Any] | None = None,
    runtime_targets: list[str] | None = None,
) -> Path:
    path = target / "harness/maintenance/runs/create-fixture/delta-plan.json"
    write_json(
        path,
        {
            "schema_version": "1.0",
            "change_id": "create-fixture",
            "mode": "create",
            "interview_receipt": receipt
            or interview_receipt(profile, runtime_targets),
            "deltas": [],
            "conflicts": [],
            "approval_required": [],
        },
    )
    return path


def validator_cli(
    target: Path,
    *extra_args: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/validate_runtime_neutral.py"),
            str(target),
            *extra_args,
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def markdown_document(line_count: int, exception: str | None = None) -> str:
    lines = [exception] if exception else []
    lines.extend(
        "# Runtime contract" if index == 0 else f"Bounded rule {index}."
        for index in range(line_count - len(lines))
    )
    assert len(lines) == line_count
    return "\n".join(lines)


def root_guidance_document(
    managed_line_count: int,
    exception: str | None = None,
    user_prefix_lines: int = 1,
    user_suffix_lines: int = 1,
) -> str:
    start = f"<!-- harness-factory:start {NAMESPACE} -->"
    end = f"<!-- harness-factory:end {NAMESPACE} -->"
    managed = [start]
    if exception:
        managed.append(exception)
    remaining = managed_line_count - len(managed) - 1
    if remaining < 0:
        raise ValueError("managed line count is too small")
    managed.extend(f"Managed rule {index}." for index in range(remaining))
    managed.append(end)
    prefix = [f"User prefix {index}." for index in range(user_prefix_lines)]
    suffix = [f"User suffix {index}." for index in range(user_suffix_lines)]
    lines = prefix + managed + suffix
    assert len(managed) == managed_line_count
    return "\n".join(lines)


def sync_canonical_skill(target: Path, spec: dict[str, Any], skill_id: str) -> None:
    skill = next(item for item in spec["skills"] if item["id"] == skill_id)
    canonical = target / skill["instructions"]
    provider_roots = {
        "claude": ".claude/skills",
        "codex": ".agents/skills",
        "gemini": ".gemini/skills",
    }
    for runtime in spec["runtime_targets"]:
        shutil.copyfile(
            canonical,
            target / provider_roots[runtime] / skill_id / "SKILL.md",
        )


class RuntimeNeutralContractTests(unittest.TestCase):
    def test_provider_registry_and_plugin_manifests(self) -> None:
        actual = {
            path.parent.name
            for path in (ROOT / "providers").glob("*/contract.json")
        }
        self.assertEqual(set(PROVIDERS), actual)
        for provider_id, expected in PROVIDERS.items():
            contract = json.loads(
                (ROOT / "providers" / provider_id / "contract.json").read_text(encoding="utf-8")
            )
            self.assertEqual(provider_id, contract["id"])
            for key, value in expected.items():
                self.assertEqual(value, contract[key])
            self.assertEqual(len(contract["capabilities"]), len(set(contract["capabilities"])))

        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        marketplace = json.loads(
            (ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
        )
        codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        gemini = json.loads((ROOT / "gemini-extension.json").read_text(encoding="utf-8"))
        self.assertEqual("harness-factory", claude["name"])
        self.assertEqual(claude["name"], codex["name"])
        self.assertEqual("0.3.0", claude["version"])
        self.assertEqual(claude["version"], codex["version"])
        self.assertEqual(claude["version"], gemini["version"])
        self.assertEqual(claude["version"], marketplace["metadata"]["version"])
        self.assertEqual(claude["version"], marketplace["plugins"][0]["version"])
        self.assertEqual("./skills/", codex["skills"])

    def test_internal_instruction_sources_are_english(self) -> None:
        sources = [
            *(
                path
                for path in (ROOT / "templates").rglob("*")
                if path.is_file()
            ),
            *(ROOT / "skills" / skill_id / "SKILL.md" for skill_id in FACTORY_SKILLS),
            ROOT / "skills/build-harness/references/RUNTIME-CONTRACT.md",
            *((ROOT / "principles").glob("*.md")),
            ROOT / "docs/CONSTRUCTOR-PROTOCOL.md",
            ROOT / "interview/QUESTION-BANK.md",
            ROOT / "CHECKLIST.md",
        ]
        violations = []
        for path in sorted(set(sources)):
            for line_number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1
            ):
                if HANGUL_RE.search(line):
                    violations.append(
                        f"{path.relative_to(ROOT).as_posix()}:{line_number}: {line.strip()}"
                    )
        self.assertEqual([], violations, "\n".join(violations))

    def test_bilingual_readmes_keep_english_as_the_default(self) -> None:
        english_path = ROOT / "README.md"
        korean_path = ROOT / "README.ko.md"
        self.assertTrue(english_path.is_file())
        self.assertTrue(korean_path.is_file())
        english = english_path.read_text(encoding="utf-8")
        korean = korean_path.read_text(encoding="utf-8")
        language_nav = "[English](README.md) | [한국어](README.ko.md)"
        self.assertIn(language_nav, english)
        self.assertIn(language_nav, korean)
        self.assertIsNone(HANGUL_RE.search(english.replace("[한국어]", "")))
        self.assertIsNotNone(HANGUL_RE.search(korean))
        for marker in (
            "/plugin marketplace add HanyeolKo/harness-factory",
            "codex plugin marketplace add HanyeolKo/harness-factory --ref main",
            "gemini extensions install https://github.com/HanyeolKo/harness-factory --ref main",
            "build-harness",
        ):
            self.assertIn(marker, english)
            self.assertIn(marker, korean)

    def test_report_terminology_and_legacy_fallback_are_forward_contracts(self) -> None:
        runtime_contract = (
            ROOT / "skills/build-harness/references/RUNTIME-CONTRACT.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "`technical-english` uses `report_language` grammar",
            "stable technical nouns",
            "`localized` translates explanatory technical nouns",
            "`pass|fail` exactly",
        ):
            self.assertIn(marker, runtime_contract)

        english_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        korean_readme = (ROOT / "README.ko.md").read_text(encoding="utf-8")
        for text in (english_readme, korean_readme):
            self.assertIn("ko + technical-english", text)
            self.assertIn("`baseline`", text)
            self.assertIn("`treatment`", text)
            self.assertIn("`pass`", text)

        harness_template = (ROOT / "templates/HARNESS.md.tmpl").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "Format user-facing reports with `communication`",
            harness_template,
        )

        shared_skill = (
            ROOT / "templates/adapters/shared/SKILL.md.tmpl"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "If `communication` is absent, use `en` reports with "
            "`technical-english`",
            shared_skill,
        )
        for provider_template in (
            "templates/adapters/claude/CLAUDE.md.block.tmpl",
            "templates/adapters/codex/AGENTS.md.block.tmpl",
            "templates/adapters/gemini/GEMINI.md.block.tmpl",
        ):
            text = (ROOT / provider_template).read_text(encoding="utf-8")
            self.assertIn(
                "if absent, use `en` and `technical-english`",
                text,
                provider_template,
            )
            self.assertIn("`technical-english`:", text, provider_template)
            self.assertIn("`localized`:", text, provider_template)

    def test_reporting_policy_is_optional_but_strict_when_present(self) -> None:
        valid_policy = {
            "schema_version": "1.0",
            "reader_destination": "file",
            "reader_target": "harness/reports",
            "canonical_evidence": "file",
            "style": "plain-language-first",
        }
        cases = (
            ("destination", {**valid_policy, "reader_destination": "email"}, "reader_destination"),
            ("external-target", {**valid_policy, "reader_destination": "notion", "reader_target": ""}, "reader_target"),
            ("file-target", {**valid_policy, "reader_target": "harness/other"}, "reader_target must be 'harness/reports'"),
            ("evidence", {**valid_policy, "canonical_evidence": "notion"}, "canonical_evidence"),
            ("style", {**valid_policy, "style": "dense"}, "style"),
        )
        with WorkspaceDirectory() as target:
            build_fixture(target)
            policy_path = target / "harness/policies/reporting.json"
            self.assertFalse(policy_path.exists())
            self.assertEqual(
                [], Validator(target, target / "harness/harness-spec.json").validate()
            )
            write_json(policy_path, valid_policy)
            self.assertEqual(
                [], Validator(target, target / "harness/harness-spec.json").validate()
            )
            for name, policy, expected_error in cases:
                with self.subTest(case=name):
                    write_json(policy_path, policy)
                    errors = Validator(
                        target, target / "harness/harness-spec.json"
                    ).validate()
                    self.assertTrue(
                        any(expected_error in error for error in errors),
                        "\n".join(errors),
                    )

    def test_all_seven_factory_skills_have_runtime_parity(self) -> None:
        actual = {
            path.name
            for path in (ROOT / "skills").iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        }
        self.assertEqual(set(FACTORY_SKILLS), actual)
        for skill_id in FACTORY_SKILLS:
            canonical_dir = ROOT / "skills" / skill_id
            canonical_path = canonical_dir / "SKILL.md"
            canonical = canonical_path.read_bytes()
            text = canonical.decode("utf-8")
            frontmatter = text.split("---", 2)[1]
            fields = {
                key.strip(): value.strip()
                for line in frontmatter.splitlines()
                if (key := line.partition(":")[0])
                and (value := line.partition(":")[2])
            }
            self.assertEqual(skill_id, fields.get("name"))
            description = fields.get("description", "")
            self.assertTrue(description)
            self.assertLessEqual(len(description), 1024)
            self.assertNotIn("<", description)
            self.assertNotIn(">", description)
            if skill_id == "build-harness":
                for marker in (
                    "create",
                    "improve",
                    "reconcile",
                    "preserve-and-reconcile",
                    "artifact_language",
                    "report_language",
                    "terminology",
                ):
                    self.assertIn(marker, text)
            metadata = (canonical_dir / "agents/openai.yaml").read_text(encoding="utf-8")
            self.assertIn(f"${skill_id}", metadata)
            self.assertEqual(
                canonical,
                (ROOT / ".claude/skills" / skill_id / "SKILL.md").read_bytes(),
                f"Claude parity: {skill_id}",
            )
            self.assertEqual(
                canonical,
                (ROOT / ".codex/skills" / skill_id / "SKILL.md").read_bytes(),
                f"Codex parity: {skill_id}",
            )
            resolver = canonical_dir / "scripts/resolve_factory.py"
            self.assertTrue(resolver.is_file(), f"missing resolver: {skill_id}")
            for runtime_root in (".claude/skills", ".codex/skills"):
                self.assertEqual(
                    resolver.read_bytes(),
                    (ROOT / runtime_root / skill_id / "scripts/resolve_factory.py").read_bytes(),
                    f"resolver parity: {runtime_root}/{skill_id}",
                )
                self.assertEqual(
                    (canonical_dir / "agents/openai.yaml").read_bytes(),
                    (ROOT / runtime_root / skill_id / "agents/openai.yaml").read_bytes(),
                    f"metadata parity: {runtime_root}/{skill_id}",
                )
            result = subprocess.run(
                [sys.executable, str(resolver), "--factory-root", str(ROOT), "--offline"],
                cwd=ROOT,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(ROOT.resolve(), Path(result.stdout.strip()).resolve())

    def test_schema_and_template_encode_version_11_policy(self) -> None:
        schema = json.loads((ROOT / "schema/harness-spec.schema.json").read_text(encoding="utf-8"))
        self.assertIn("1.1", schema["properties"]["schema_version"]["enum"])
        self.assertEqual(
            {"claude", "codex", "gemini"},
            set(schema["properties"]["runtime_targets"]["items"]["enum"]),
        )
        limits_schema = schema["properties"]["limits"]["properties"]
        self.assertEqual(
            {"type": "integer", "minimum": 1},
            limits_schema["max_instruction_lines"],
        )
        self.assertNotIn("communication", schema["required"])
        communication_schema = schema["properties"]["communication"]
        self.assertFalse(communication_schema["additionalProperties"])
        self.assertEqual(
            {"artifact_language", "report_language", "terminology"},
            set(communication_schema["required"]),
        )
        self.assertEqual(
            "en",
            communication_schema["properties"]["artifact_language"]["const"],
        )
        self.assertEqual(
            {"technical-english", "localized"},
            set(communication_schema["properties"]["terminology"]["enum"]),
        )
        self.assertEqual(DEFAULT_COMMUNICATION, communication_schema["default"])
        self.assertEqual(
            {"type": "integer", "minimum": 1},
            schema["properties"]["memory"]["properties"]["max_summary_chars"],
        )
        self.assertIn(
            "harness-evaluation",
            schema["properties"]["skills"]["items"]["properties"]["kind"]["enum"],
        )
        self.assertIn(
            "verification",
            schema["properties"]["skills"]["items"]["properties"]["kind"]["enum"],
        )
        self.assertIn(
            "experiment",
            schema["properties"]["evaluators"]["items"]["properties"]["type"]["enum"],
        )
        self.assertIn(
            "evaluator",
            schema["properties"]["skills"]["items"]["properties"],
        )
        self.assertIn(
            "watched_paths",
            schema["properties"]["self_evaluation"]["required"],
        )
        self.assertIn(
            "targeted_suite",
            schema["properties"]["self_evaluation"]["required"],
        )
        self.assertTrue(
            any(
                item.get("if", {}).get("properties", {}).get("schema_version", {}).get("const") == "1.1"
                and {"memory", "self_evaluation"}.issubset(
                    set(item.get("then", {}).get("required", []))
                )
                for item in schema["allOf"]
            )
        )
        self.assertTrue(
            any(
                item.get("if", {}).get("properties", {}).get("schema_version", {}).get("const") == "1.0"
                and "retro_interval"
                in item.get("then", {})
                .get("properties", {})
                .get("loops", {})
                .get("required", [])
                for item in schema["allOf"]
            )
        )

        expected = make_spec("1.2", "adaptive")
        profile_optional_fields = (
            ",\n  \"memory\": "
            + json_scalar(expected["memory"])
            + ",\n  \"self_evaluation\": "
            + json_scalar(expected["self_evaluation"])
        )
        rendered = render(
            (ROOT / "templates/harness-spec.json.tmpl").read_text(encoding="utf-8"),
            {
                "PROFILE": expected["profile"],
                "CHANGE_ID": "create-fixture",
                "SKILL_NAME": NAMESPACE,
                "PURPOSE_JSON": json_scalar(expected["harness"]["purpose"]),
                "HARNESS_ROOT": "harness",
                "RUNTIME_TARGETS_JSON": json_scalar(expected["runtime_targets"]),
                "MAX_PARALLELISM": "2",
                "MAX_DELEGATION_DEPTH": "2",
                "REPORT_LANGUAGE": expected["communication"]["report_language"],
                "REPORT_TERMINOLOGY": expected["communication"]["terminology"],
                "DOMAINS_JSON": json_scalar(expected["domains"]),
                "AGENTS_JSON": json_scalar(expected["agents"]),
                "SKILLS_JSON": json_scalar(expected["skills"]),
                "APPROVAL_GATES_JSON": json_scalar(expected["approval_gates"]),
                "HANDOFFS_JSON": json_scalar(expected["orchestration"]["handoffs"]),
                "EVALUATORS_JSON": json_scalar(expected["evaluators"]),
                "LOOPS_JSON": json_scalar(expected["loops"]),
                "PROFILE_OPTIONAL_FIELDS": profile_optional_fields,
            },
        )
        self.assertNotIn("{{", rendered)
        self.assertEqual(expected, json.loads(rendered))

    def test_release_030_declares_profile_and_interview_contracts(self) -> None:
        schema = json.loads(
            (ROOT / "schema/harness-spec.schema.json").read_text(encoding="utf-8")
        )
        self.assertIn("1.2", schema["properties"]["schema_version"]["enum"])
        self.assertEqual(
            {"core", "adaptive", "governed"},
            set(schema["properties"]["profile"]["enum"]),
        )
        limits = schema["properties"]["limits"]["properties"]
        self.assertEqual(50, limits["target_markdown_lines"]["default"])
        self.assertEqual(100, limits["max_markdown_lines"]["default"])

        spec_template = (ROOT / "templates/harness-spec.json.tmpl").read_text(
            encoding="utf-8"
        )
        self.assertIn('\"schema_version\": \"1.2\"', spec_template)
        self.assertIn('\"profile\": \"{{PROFILE}}\"', spec_template)
        self.assertIn('\"construction_receipt\"', spec_template)

        delta_plan = (
            ROOT / "templates/maintenance/DELTA-PLAN.json.tmpl"
        ).read_text(encoding="utf-8")
        for marker in (
            '\"interview_receipt\"',
            '\"recommended\"',
            '\"selected\"',
            '\"reason_codes\"',
            '\"confirmation_source\"',
        ):
            self.assertIn(marker, delta_plan)

        build_skill = (ROOT / "skills/build-harness/SKILL.md").read_text(
            encoding="utf-8"
        )
        question_bank = (ROOT / "interview/QUESTION-BANK.md").read_text(
            encoding="utf-8"
        )
        for text in (build_skill, question_bank):
            self.assertIn("interview_receipt", text)
            self.assertIn("default-delegated", text)
            self.assertIn("core", text)
            self.assertIn("adaptive", text)
            self.assertIn("governed", text)

        harness_template = (ROOT / "templates/HARNESS.md.tmpl").read_text(
            encoding="utf-8"
        )
        self.assertIn("Only the user may confirm a profile change", harness_template)
        self.assertLessEqual(len(harness_template.splitlines()), 100)
        self.assertFalse((ROOT / "templates/policies/profile.json.tmpl").exists())

    def test_factory_runtime_markdown_respects_the_50_100_contract(self) -> None:
        runtime_sources = [
            ROOT / "skills/build-harness/SKILL.md",
            *(ROOT / "templates").rglob("*.md.tmpl"),
        ]
        marker = re.compile(
            r"^<!-- document-budget exception: "
            r"(?:required-sequential-instruction|atomic-project-contract|"
            r"higher-routing-overhead) \| \S(?:.*\S)? -->$"
        )
        for path in runtime_sources:
            with self.subTest(path=path.relative_to(ROOT)):
                lines = path.read_text(encoding="utf-8").splitlines()
                self.assertLessEqual(len(lines), 100)
                if len(lines) <= 50:
                    continue
                marker_index = 0
                if lines and lines[0] == "---":
                    marker_index = lines.index("---", 1) + 1
                while marker_index < len(lines) and not lines[marker_index].strip():
                    marker_index += 1
                self.assertLess(marker_index, len(lines))
                self.assertRegex(lines[marker_index], marker)

    def test_schema_12_profiles_install_only_their_declared_topology(self) -> None:
        common = {
            "policies/reporting.json",
            "reports/_templates/CHANGE-REPORT.md.tmpl",
        }
        adaptive = {
            "memory/INDEX.md",
            "loops/IMPROVE-LOOP.md",
            "loops/HARNESS-EVAL-LOOP.md",
            "evaluation/EVALUATION-CONTRACT.md",
            "triggers/check_self_evaluation.py",
            "triggers/record_self_evaluation.py",
            "state/self-evaluation.json",
            "maintenance/COMPONENT-MUTATION-PROTOCOL.md",
        }
        governed = {
            "learning-assist/_templates/explanation.md.tmpl",
            "learning-assist/_templates/quiz.json.tmpl",
            "learning-assist/_templates/comprehension.json.tmpl",
            "policies/learning-gate.json",
            "policies/LEARNING-GATE.md",
            "learning/_templates/brief.md.tmpl",
            "learning/_templates/diff-explanation.md.tmpl",
            "learning/_templates/quiz.json.tmpl",
            "learning/_templates/answers.json.tmpl",
            "learning/_templates/verification.json.tmpl",
            "triggers/verify_learning_gate.py",
        }

        for profile in PROFILES_12:
            with self.subTest(profile=profile), WorkspaceDirectory() as target:
                spec = build_fixture(target, "1.2", profile)
                errors = Validator(
                    target, target / "harness/harness-spec.json"
                ).validate()
                self.assertEqual([], errors, "\n".join(errors))
                for relative in common:
                    self.assertTrue((target / "harness" / relative).is_file(), relative)
                for relative in adaptive:
                    self.assertEqual(
                        profile in {"adaptive", "governed"},
                        (target / "harness" / relative).is_file(),
                        relative,
                    )
                for relative in governed:
                    self.assertEqual(
                        profile == "governed",
                        (target / "harness" / relative).is_file(),
                        relative,
                    )
                if profile == "core":
                    self.assertEqual(3, len(spec["agents"]))
                    evaluator = next(
                        agent
                        for agent in spec["agents"]
                        if agent["id"] == "contract-evaluator"
                    )
                    self.assertEqual(
                        {"verification", "verdict", "defect-counting"},
                        set(evaluator["capabilities"]),
                    )

    def test_schema_12_profile_files_reject_missing_and_forbidden_layers(self) -> None:
        missing_cases = {
            "core": "reports/_templates/CHANGE-REPORT.md.tmpl",
            "adaptive": "maintenance/COMPONENT-MUTATION-PROTOCOL.md",
            "governed": "policies/learning-gate.json",
        }
        for profile, relative in missing_cases.items():
            with self.subTest(profile=profile, missing=relative), WorkspaceDirectory() as target:
                build_fixture(target, "1.2", profile)
                (target / "harness" / relative).unlink()
                errors = Validator(
                    target, target / "harness/harness-spec.json"
                ).validate()
                self.assertTrue(
                    any(relative in error and "missing" in error for error in errors),
                    errors,
                )

        with WorkspaceDirectory() as target:
            build_fixture(target, "1.2", "core")
            write_text(target / "harness/memory/INDEX.md", ENGLISH_MEMORY_INDEX)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(
                any(
                    "core" in error and "memory/INDEX.md" in error
                    for error in errors
                ),
                errors,
            )

        with WorkspaceDirectory() as target:
            build_fixture(target, "1.2", "adaptive")
            gate = json.loads(
                (ROOT / "templates/policies/learning-gate.json.tmpl").read_text(
                    encoding="utf-8"
                )
            )
            write_json(target / "harness/policies/learning-gate.json", gate)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(
                any(
                    "adaptive" in error and "policies/learning-gate.json" in error
                    for error in errors
                ),
                errors,
            )

    def test_schema_12_profile_shape_rejects_missing_or_forbidden_spec_fields(self) -> None:
        with WorkspaceDirectory() as target:
            spec = build_fixture(target, "1.2", "adaptive")
            spec.pop("profile")
            write_json(target / "harness/harness-spec.json", spec)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(any("profile" in error for error in errors), errors)

        for profile, field in (("adaptive", "memory"), ("governed", "self_evaluation")):
            with self.subTest(profile=profile, missing=field), WorkspaceDirectory() as target:
                spec = build_fixture(target, "1.2", profile)
                spec.pop(field)
                write_json(target / "harness/harness-spec.json", spec)
                errors = Validator(
                    target, target / "harness/harness-spec.json"
                ).validate()
                self.assertTrue(any(field in error for error in errors), errors)

        with WorkspaceDirectory() as target:
            spec = build_fixture(target, "1.2", "core")
            spec["memory"] = {
                "index": "harness/memory/INDEX.md",
                "policy": "preserve-and-reconcile",
                "max_document_lines": 80,
                "max_summary_chars": 160,
            }
            write_json(target / "harness/harness-spec.json", spec)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(
                any("core" in error and "memory" in error for error in errors),
                errors,
            )

    def test_schema_12_projects_only_selected_runtime_adapters(self) -> None:
        for runtime in PROVIDERS:
            with self.subTest(runtime=runtime), WorkspaceDirectory() as target:
                spec = build_fixture(
                    target, "1.2", "adaptive", runtime_targets=[runtime]
                )
                errors = Validator(
                    target, target / "harness/harness-spec.json"
                ).validate()
                self.assertEqual([], errors, "\n".join(errors))
                self.assertEqual(
                    watched_paths_for([runtime], spec["skills"], spec["agents"]),
                    spec["self_evaluation"]["watched_paths"],
                )
                for provider_id, provider in PROVIDERS.items():
                    self.assertEqual(
                        provider_id == runtime,
                        (target / provider["root_guidance"]).is_file(),
                        provider_id,
                    )

    def test_schema_12_construction_receipt_auto_and_cli_parity(self) -> None:
        for profile in PROFILES_12:
            with self.subTest(profile=profile), WorkspaceDirectory() as target:
                spec = build_fixture(target, "1.2", profile)
                delta_plan = target / spec["harness"]["construction_receipt"]
                result = validator_cli(
                    target,
                    "--construction-mode",
                    "create",
                    "--delta-plan",
                    str(delta_plan),
                )
                self.assertEqual(
                    0, result.returncode, result.stdout + result.stderr
                )

        with WorkspaceDirectory() as target:
            spec = build_fixture(target, "1.2", "adaptive")
            delta_plan = target / spec["harness"]["construction_receipt"]
            plan = json.loads(delta_plan.read_text(encoding="utf-8"))
            plan["interview_receipt"]["profile"].update(
                {
                    "recommended": "core",
                    "selected": "adaptive",
                    "reason_codes": ["bounded-task-work"],
                    "confirmation_source": "user-answer",
                    "override_reason": "Durable memory is explicitly required.",
                }
            )
            write_json(delta_plan, plan)
            result = validator_cli(
                target,
                "--construction-mode",
                "create",
                "--delta-plan",
                str(delta_plan),
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_schema_12_construction_receipt_rejects_missing_decisions_and_mismatch(self) -> None:
        with WorkspaceDirectory() as target:
            spec = build_fixture(target, "1.2", "core")
            delta_plan = target / spec["harness"]["construction_receipt"]
            receipt = interview_receipt("core")
            receipt["decisions"] = {}
            write_delta_plan(target, "core", receipt)
            result = validator_cli(
                target,
                "--construction-mode",
                "create",
                "--delta-plan",
                str(delta_plan),
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("decisions", result.stderr)

        with WorkspaceDirectory() as target:
            spec = build_fixture(target, "1.2", "core")
            delta_plan = target / spec["harness"]["construction_receipt"]
            plan = json.loads(delta_plan.read_text(encoding="utf-8"))
            plan["interview_receipt"]["profile"]["selected"] = "adaptive"
            plan["interview_receipt"]["profile"]["override_reason"] = (
                "The user selected the larger profile."
            )
            write_json(delta_plan, plan)
            result = validator_cli(
                target,
                "--construction-mode",
                "create",
                "--delta-plan",
                str(delta_plan),
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("spec.profile", result.stderr)

    def test_construction_cli_requires_exact_mode_and_receipt_path_pair(self) -> None:
        with WorkspaceDirectory() as target:
            spec = build_fixture(target, "1.2", "adaptive")
            delta_plan = target / spec["harness"]["construction_receipt"]
            wrong_path = target / "harness/maintenance/runs/other/delta-plan.json"
            write_json(
                wrong_path,
                json.loads(delta_plan.read_text(encoding="utf-8")),
            )
            wrong_mode = validator_cli(
                target,
                "--construction-mode",
                "improve",
                "--delta-plan",
                str(delta_plan),
            )
            wrong_receipt = validator_cli(
                target,
                "--construction-mode",
                "create",
                "--delta-plan",
                str(wrong_path),
            )
            only_mode = validator_cli(
                target, "--construction-mode", "create"
            )
            only_receipt = validator_cli(
                target, "--delta-plan", str(delta_plan)
            )
            self.assertNotEqual(0, wrong_mode.returncode)
            self.assertNotEqual(0, wrong_receipt.returncode)
            self.assertNotEqual(0, only_mode.returncode)
            self.assertNotEqual(0, only_receipt.returncode)

    def test_legacy_cli_without_construction_arguments_remains_compatible(self) -> None:
        for schema_version in ("1.0", "1.1"):
            with self.subTest(schema_version=schema_version), WorkspaceDirectory() as target:
                build_fixture(target, schema_version)
                result = validator_cli(target)
                self.assertEqual(
                    0, result.returncode, result.stdout + result.stderr
                )

    def test_schema_12_markdown_budget_boundaries_50_51_100_101(self) -> None:
        cases = (
            (50, None, True),
            (51, None, False),
            (51, MARKDOWN_BUDGET_EXCEPTION, True),
            (100, MARKDOWN_BUDGET_EXCEPTION, True),
            (101, MARKDOWN_BUDGET_EXCEPTION, False),
        )
        for line_count, exception, valid in cases:
            with self.subTest(
                line_count=line_count, exception=bool(exception)
            ), WorkspaceDirectory() as target:
                build_fixture(target, "1.2", "core", runtime_targets=["claude"])
                write_text(
                    target / "harness/ENVIRONMENT.md",
                    markdown_document(line_count, exception),
                )
                errors = Validator(
                    target, target / "harness/harness-spec.json"
                ).validate()
                if valid:
                    self.assertEqual([], errors, "\n".join(errors))
                else:
                    self.assertTrue(
                        any("ENVIRONMENT.md" in error for error in errors),
                        errors,
                    )

    def test_schema_12_markdown_exception_marker_placement_and_type(self) -> None:
        invalid_documents = {
            "mid-body": "\n".join(
                markdown_document(51, MARKDOWN_BUDGET_EXCEPTION).splitlines()[1:3]
                + [MARKDOWN_BUDGET_EXCEPTION]
                + markdown_document(51, MARKDOWN_BUDGET_EXCEPTION).splitlines()[3:]
            ),
            "duplicate": "\n".join(
                [MARKDOWN_BUDGET_EXCEPTION, MARKDOWN_BUDGET_EXCEPTION]
                + markdown_document(50).splitlines()
            ),
            "invalid-type": markdown_document(
                51,
                "<!-- document-budget exception: convenient | "
                "Keep this bounded runtime contract whole. -->",
            ),
            "empty-reason": markdown_document(
                51,
                "<!-- document-budget exception: atomic-project-contract |  -->",
            ),
        }
        for name, document in invalid_documents.items():
            with self.subTest(name=name), WorkspaceDirectory() as target:
                build_fixture(target, "1.2", "core", runtime_targets=["claude"])
                write_text(target / "harness/ENVIRONMENT.md", document)
                errors = Validator(
                    target, target / "harness/harness-spec.json"
                ).validate()
                self.assertTrue(
                    any("ENVIRONMENT.md" in error for error in errors),
                    errors,
                )

    def test_schema_12_markdown_marker_follows_frontmatter(self) -> None:
        with WorkspaceDirectory() as target:
            spec = build_fixture(
                target, "1.2", "core", runtime_targets=["claude"]
            )
            skill_id = NAMESPACE
            header = [
                "---",
                f"name: {json_scalar(skill_id)}",
                f"description: {json_scalar('Execute the entry fixture workflow.')}",
                "---",
            ]
            body = [
                MARKDOWN_BUDGET_EXCEPTION,
                f"# {skill_id}",
                "Read `harness/harness-spec.json` first.",
            ]
            body.extend(
                f"Bounded skill rule {index}."
                for index in range(51 - len(header) - len(body))
            )
            canonical = target / f"harness/skills/{skill_id}/SKILL.md"
            write_text(canonical, "\n".join(header + body))
            sync_canonical_skill(target, spec, skill_id)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertEqual([], errors, "\n".join(errors))

            invalid_body = [body[1], body[0], *body[2:]]
            write_text(canonical, "\n".join(header + invalid_body))
            sync_canonical_skill(target, spec, skill_id)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(
                any(skill_id in error and "budget" in error.lower() for error in errors),
                errors,
            )

    def test_schema_12_root_budget_counts_only_the_managed_block(self) -> None:
        cases = (
            (50, None, True),
            (51, None, False),
            (51, MARKDOWN_BUDGET_EXCEPTION, True),
            (100, MARKDOWN_BUDGET_EXCEPTION, True),
            (101, MARKDOWN_BUDGET_EXCEPTION, False),
        )
        for managed_lines, exception, valid in cases:
            with self.subTest(
                managed_lines=managed_lines, exception=bool(exception)
            ), WorkspaceDirectory() as target:
                build_fixture(target, "1.2", "core", runtime_targets=["claude"])
                write_text(
                    target / "CLAUDE.md",
                    root_guidance_document(
                        managed_lines,
                        exception,
                        user_prefix_lines=125,
                        user_suffix_lines=125,
                    ),
                )
                errors = Validator(
                    target, target / "harness/harness-spec.json"
                ).validate()
                if valid:
                    self.assertEqual([], errors, "\n".join(errors))
                else:
                    self.assertTrue(
                        any("CLAUDE.md" in error for error in errors),
                        errors,
                    )

    def test_schema_12_root_marker_scope_and_managed_boundaries(self) -> None:
        with WorkspaceDirectory() as target:
            build_fixture(target, "1.2", "core", runtime_targets=["claude"])
            scoped_outside = root_guidance_document(51, None).splitlines()
            scoped_outside.insert(0, MARKDOWN_BUDGET_EXCEPTION)
            write_text(target / "CLAUDE.md", "\n".join(scoped_outside))
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(any("CLAUDE.md" in error for error in errors), errors)

        with WorkspaceDirectory() as target:
            build_fixture(target, "1.2", "core", runtime_targets=["claude"])
            misplaced = root_guidance_document(
                51, MARKDOWN_BUDGET_EXCEPTION
            ).splitlines()
            marker_index = misplaced.index(MARKDOWN_BUDGET_EXCEPTION)
            misplaced[marker_index], misplaced[marker_index + 1] = (
                misplaced[marker_index + 1],
                misplaced[marker_index],
            )
            write_text(target / "CLAUDE.md", "\n".join(misplaced))
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(any("CLAUDE.md" in error for error in errors), errors)

        with WorkspaceDirectory() as target:
            build_fixture(target, "1.2", "core", runtime_targets=["claude"])
            missing_end = root_guidance_document(50).splitlines()
            missing_end.remove(f"<!-- harness-factory:end {NAMESPACE} -->")
            write_text(target / "CLAUDE.md", "\n".join(missing_end))
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(
                any("CLAUDE.md" in error and "managed" in error for error in errors),
                errors,
            )

    def test_schema_12_markdown_budget_excludes_reports_runs_and_user_files(self) -> None:
        with WorkspaceDirectory() as target:
            build_fixture(target, "1.2", "adaptive", runtime_targets=["claude"])
            for relative in (
                "harness/reports/CHG-001/CHANGE-REPORT.md",
                "harness/evaluation/runs/run-001/ASSESSMENT.md",
                ".claude/skills/user-owned/SKILL.md",
            ):
                write_text(target / relative, markdown_document(101))
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertEqual([], errors, "\n".join(errors))

    def test_communication_contract_is_optional_and_strict(self) -> None:
        with WorkspaceDirectory() as target:
            spec = build_fixture(target)
            spec.pop("communication")
            write_json(target / "harness/harness-spec.json", spec)
            write_text(
                target / "harness/HARNESS.md",
                "# 하네스\n\n기존 프로젝트 소유 문서는 자동 번역하지 않는다.",
            )
            write_text(target / "harness/memory/INDEX.md", LEGACY_KOREAN_MEMORY_INDEX)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertEqual([], errors, "\n".join(errors))

        with WorkspaceDirectory() as target:
            spec = build_fixture(target)
            spec["communication"] = {
                "artifact_language": "en",
                "report_language": "ko",
                "terminology": "localized",
            }
            write_json(target / "harness/harness-spec.json", spec)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertEqual([], errors, "\n".join(errors))

        invalid_cases = (
            (
                "artifact-language",
                {
                    "artifact_language": "ko",
                    "report_language": "ko",
                    "terminology": "localized",
                },
                "communication.artifact_language must be 'en'",
            ),
            (
                "report-language",
                {
                    "artifact_language": "en",
                    "report_language": "korean",
                    "terminology": "localized",
                },
                "communication.report_language must be a supported language tag",
            ),
            (
                "terminology",
                {
                    "artifact_language": "en",
                    "report_language": "en",
                    "terminology": "hybrid",
                },
                "communication.terminology must be technical-english or localized",
            ),
            (
                "missing-field",
                {"artifact_language": "en", "report_language": "en"},
                "communication is missing keys: ['terminology']",
            ),
            (
                "unsupported-field",
                {**DEFAULT_COMMUNICATION, "dialect": "formal"},
                "communication has unsupported keys: ['dialect']",
            ),
        )
        for label, communication, expected_error in invalid_cases:
            with self.subTest(case=label), WorkspaceDirectory() as target:
                spec = build_fixture(target)
                spec["communication"] = communication
                write_json(target / "harness/harness-spec.json", spec)
                errors = Validator(
                    target, target / "harness/harness-spec.json"
                ).validate()
                self.assertIn(expected_error, errors)

    def test_default_render_passes_english_prose_validation(self) -> None:
        with WorkspaceDirectory() as target:
            spec = build_fixture(target)
            self.assertEqual("en", spec["communication"]["artifact_language"])
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertEqual([], errors, "\n".join(errors))

    def test_english_artifact_prose_rejects_non_english_text(self) -> None:
        with WorkspaceDirectory() as target:
            build_fixture(target)
            write_text(
                target / "harness/HARNESS.md",
                "# Harness\n\nThis line is English.\n\n이 문장은 영문 정본이 아니다.",
            )
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(
                any(
                    "canonical prose must be English" in error
                    and "HARNESS.md:5" in error
                    for error in errors
                ),
                "\n".join(errors),
            )

    def test_english_artifact_prose_allows_code_and_machine_tokens(self) -> None:
        with WorkspaceDirectory() as target:
            build_fixture(target)
            write_text(
                target / "harness/HARNESS.md",
                (
                    "# Harness\n\n"
                    "Keep the inline token `상태=완료` unchanged.\n"
                    "Keep the machine path harness/메모리.md unchanged.\n"
                    "Keep the [source](docs/한글-참조.md) unchanged.\n\n"
                    "```powershell\n"
                    "Write-Output '검증 명령'\n"
                    "```\n"
                ),
            )
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertEqual([], errors, "\n".join(errors))

    def test_english_spec_prose_is_enforced_without_breaking_legacy(self) -> None:
        cases = (
            ("harness.purpose", ("harness", "purpose")),
            ("agents[0].description", ("agents", 0, "description")),
            (
                "orchestration.handoffs[0].when",
                ("orchestration", "handoffs", 0, "when"),
            ),
            (
                "evaluators[0].pass_condition",
                ("evaluators", 0, "pass_condition"),
            ),
            (
                "approval_gates[0].trigger",
                ("approval_gates", 0, "trigger"),
            ),
            (
                "approval_gates[0].required_action",
                ("approval_gates", 0, "required_action"),
            ),
        )
        for label, path in cases:
            with self.subTest(field=label), WorkspaceDirectory() as target:
                spec = build_fixture(target)
                parent = spec
                for key in path[:-1]:
                    parent = parent[key]
                parent[path[-1]] = "한글 설명"
                write_json(target / "harness/harness-spec.json", spec)
                errors = Validator(
                    target, target / "harness/harness-spec.json"
                ).validate()
                self.assertTrue(
                    any(
                        "canonical spec prose must be English" in error
                        and label in error
                        for error in errors
                    ),
                    "\n".join(errors),
                )

        with WorkspaceDirectory() as target:
            spec = build_fixture(target)
            spec["harness"]["purpose"] = "Preserve `한글-프로젝트` exactly."
            write_json(target / "harness/harness-spec.json", spec)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertEqual([], errors, "\n".join(errors))

            spec["harness"]["purpose"] = "한글 목적"
            spec.pop("communication")
            write_json(target / "harness/harness-spec.json", spec)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertEqual([], errors, "\n".join(errors))

    def test_schema_11_fixture_passes_all_three_provider_adapters(self) -> None:
        with WorkspaceDirectory() as target:
            spec = build_fixture(target)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertEqual([], errors, "\n".join(errors))
            preflight = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/validate_runtime_neutral.py"),
                    str(target),
                    "--provider-path-preflight",
                ],
                cwd=ROOT,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(0, preflight.returncode, preflight.stderr)
            self.assertIn("provider path preflight passed", preflight.stdout)
            expected_agents = {f"{NAMESPACE}-{role['id']}" for role in ROLES}
            self.assertEqual(
                expected_agents,
                {path.stem for path in (target / ".claude/agents").glob("*.md")},
            )
            self.assertEqual(
                expected_agents,
                {path.stem for path in (target / ".codex/agents").glob("*.toml")},
            )
            self.assertEqual(
                expected_agents,
                {path.stem for path in (target / ".gemini/agents").glob("*.md")},
            )
            for skill in spec["skills"]:
                canonical = (target / skill["instructions"]).read_bytes()
                for root in (".claude/skills", ".agents/skills", ".gemini/skills"):
                    self.assertEqual(
                        canonical,
                        (target / root / skill["id"] / "SKILL.md").read_bytes(),
                    )
            gemini_fields = json_frontmatter(
                target / ".gemini/agents" / f"{NAMESPACE}-billing-router.md"
            )
            self.assertEqual("local", gemini_fields["kind"])
            self.assertEqual(0, gemini_fields["temperature"])
            self.assertIsInstance(gemini_fields["tools"], list)
            self.assertIn(
                "main orchestrator",
                (target / ".gemini/agents" / f"{NAMESPACE}-billing-router.md").read_text(encoding="utf-8"),
            )

    def test_provider_path_preflight_rejects_resolved_escape_fail_closed(self) -> None:
        class EscapingProviderValidator(Validator):
            def __init__(self, target: Path, spec_path: Path) -> None:
                super().__init__(target, spec_path)
                self.adapter_validation_called = False
                self.placeholder_validation_called = False

            def load_provider_contracts(self) -> None:
                super().load_provider_contracts()
                escaped = dict(self.provider_contracts["claude"])
                escaped["root_guidance"] = "../outside-provider/CLAUDE.md"
                self.provider_contracts["claude"] = escaped

            def validate_adapters(self) -> None:
                self.adapter_validation_called = True
                super().validate_adapters()

            def validate_placeholders(self) -> None:
                self.placeholder_validation_called = True
                super().validate_placeholders()

        with WorkspaceDirectory() as target:
            build_fixture(target)
            validator = EscapingProviderValidator(
                target, target / "harness/harness-spec.json"
            )
            errors = validator.validate()
            self.assertTrue(validator.provider_path_preflight_failed)
            self.assertTrue(
                any(
                    "provider 'claude' path field 'root_guidance' resolves outside target"
                    in error
                    for error in errors
                ),
                "\n".join(errors),
            )
            self.assertFalse(validator.adapter_validation_called)
            self.assertFalse(validator.placeholder_validation_called)

    def test_provider_path_preflight_rejects_symlink_escape(self) -> None:
        with WorkspaceDirectory() as target:
            build_fixture(target)
            provider_link = target / ".claude"
            outside = target.parent / f"outside-provider-{uuid.uuid4().hex}"
            shutil.rmtree(provider_link)
            outside.mkdir()
            try:
                provider_link.symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                shutil.rmtree(outside)
                self.skipTest(f"directory symlink unavailable: {exc}")
            try:
                validator = Validator(target, target / "harness/harness-spec.json")
                errors = validator.validate_provider_path_preflight()
                self.assertTrue(validator.provider_path_preflight_failed)
                self.assertTrue(
                    any(
                        "provider 'claude' path field 'skill_root' resolves outside target"
                        in error
                        or "provider 'claude' path field 'agent_root' resolves outside target"
                        in error
                        for error in errors
                    ),
                    "\n".join(errors),
                )
            finally:
                provider_link.unlink(missing_ok=True)
                shutil.rmtree(outside)

    def test_schema_10_fixture_remains_compatible(self) -> None:
        with WorkspaceDirectory() as target:
            build_fixture(target, "1.0")
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertEqual([], errors, "\n".join(errors))

    def test_memory_index_contract(self) -> None:
        with WorkspaceDirectory() as target:
            build_fixture(target)
            index = target / "harness/memory/INDEX.md"
            write_text(
                index,
                (
                    "# Memory Index\n\n"
                    "| ID | Path | Summary | Read when | Source | Last verified | Status |\n"
                    "|---|---|---|---|---|---|---|\n"
                    "| durable-note | harness/memory/missing.md | missing | task | user | 2026-07-24 | active |"
                ),
            )
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(any("active path does not exist" in error for error in errors), errors)

            long_memory = target / "harness/memory/long.md"
            write_text(long_memory, "\n".join(["line"] * 81))
            write_text(
                index,
                (
                    "# Memory Index\n\n"
                    "| ID | Path | Summary | Read when | Source | Last verified | Status |\n"
                    "|---|---|---|---|---|---|---|\n"
                    "| durable-note | harness/memory/long.md | long | task | user | 2026-07-24 | active |"
                ),
            )
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(
                any("exceeds memory.max_document_lines" in error for error in errors),
                errors,
            )

            short_memory = target / "harness/memory/short.md"
            write_text(short_memory, "short")
            write_text(
                index,
                (
                    "# Memory Index\n\n"
                    "| ID | Path | Summary | Read when | Source | Last verified | Status |\n"
                    "|---|---|---|---|---|---|---|\n"
                    f"| durable-note | harness/memory/short.md | {'s' * 161} | task | user | 2026-07-24 | active |"
                ),
            )
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(
                any("exceeds memory.max_summary_chars" in error for error in errors),
                errors,
            )

    def test_legacy_korean_memory_index_remains_compatible(self) -> None:
        with WorkspaceDirectory() as target:
            spec = build_fixture(target)
            spec.pop("communication")
            write_json(target / "harness/harness-spec.json", spec)
            write_text(target / "harness/memory/INDEX.md", LEGACY_KOREAN_MEMORY_INDEX)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertEqual([], errors, "\n".join(errors))

    def test_english_memory_index_rejects_non_english_routing_prose(self) -> None:
        with WorkspaceDirectory() as target:
            build_fixture(target)
            note = target / "harness/memory/note.md"
            write_text(note, "# Durable note\n\nKeep verified project context.")
            index = target / "harness/memory/INDEX.md"
            write_text(
                index,
                (
                    "# Memory Index\n\n"
                    "| ID | Path | Summary | Read when | Source | Last verified | Status |\n"
                    "|---|---|---|---|---|---|---|\n"
                    "| durable-note | harness/memory/note.md | 결제 규칙 | 결제 작업 때 | user | 2026-07-24 | active |"
                ),
            )
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(
                any(
                    "memory index Summary must use English prose" in error
                    for error in errors
                ),
                "\n".join(errors),
            )
            self.assertTrue(
                any(
                    "memory index Read when must use English prose" in error
                    for error in errors
                ),
                "\n".join(errors),
            )

            write_text(
                index,
                (
                    "# Memory Index\n\n"
                    "| ID | Path | Summary | Read when | Source | Last verified | Status |\n"
                    "|---|---|---|---|---|---|---|\n"
                    "| durable-note | harness/memory/note.md | Preserve `결제-rule` | Read when `상태=완료` | user | 2026-07-24 | active |"
                ),
            )
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertEqual([], errors, "\n".join(errors))

    def test_english_memory_index_requires_english_headers(self) -> None:
        with WorkspaceDirectory() as target:
            build_fixture(target)
            write_text(target / "harness/memory/INDEX.md", LEGACY_KOREAN_MEMORY_INDEX)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertIn(
                "memory index must use English table headers when "
                "communication.artifact_language is 'en'",
                errors,
            )

    def test_canonical_skill_instruction_budget(self) -> None:
        with WorkspaceDirectory() as target:
            spec = build_fixture(target)
            skill = spec["skills"][0]
            canonical = target / skill["instructions"]
            write_text(
                canonical,
                canonical.read_text(encoding="utf-8")
                + "\n"
                + "\n".join(["Bounded instruction."] * 121),
            )
            for runtime in spec["runtime_targets"]:
                projection = (
                    target
                    / PROVIDERS[runtime]["skill_root"]
                    / skill["id"]
                    / "SKILL.md"
                )
                shutil.copyfile(canonical, projection)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(
                any("exceeds limits.max_instruction_lines" in error for error in errors),
                errors,
            )
    def test_schema_10_requires_retro_interval(self) -> None:
        with WorkspaceDirectory() as target:
            spec = build_fixture(target, "1.0")
            spec["loops"].pop("retro_interval")
            write_json(target / "harness/harness-spec.json", spec)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertIn("loops is missing keys: ['retro_interval']", errors)

    def test_validator_rejects_each_provider_skill_drift(self) -> None:
        locations = {
            "Claude": ".claude/skills",
            "Codex": ".agents/skills",
            "Gemini": ".gemini/skills",
        }
        for provider, root in locations.items():
            with self.subTest(provider=provider), WorkspaceDirectory() as target:
                build_fixture(target)
                skill = target / root / NAMESPACE / "SKILL.md"
                skill.write_text(skill.read_text(encoding="utf-8") + "drift\n", encoding="utf-8")
                errors = Validator(target, target / "harness/harness-spec.json").validate()
                self.assertTrue(
                    any(provider in error and "differs from canonical" in error for error in errors),
                    "\n".join(errors),
                )

    def test_validator_rejects_gemini_write_tool_on_read_only_agent(self) -> None:
        with WorkspaceDirectory() as target:
            build_fixture(target)
            path = target / ".gemini/agents" / f"{NAMESPACE}-billing-router.md"
            text = path.read_text(encoding="utf-8")
            text = text.replace(
                'tools: ["read_file", "glob", "search_file_content"]',
                'tools: ["read_file", "glob", "search_file_content", "write_file"]',
            )
            path.write_text(text, encoding="utf-8")
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(
                any("Gemini agent tool access parity mismatch" in error for error in errors),
                "\n".join(errors),
            )

    def test_validator_rejects_missing_mandatory_event(self) -> None:
        with WorkspaceDirectory() as target:
            spec = build_fixture(target)
            spec["self_evaluation"]["mandatory_events"].remove("parity-fail")
            write_json(target / "harness/harness-spec.json", spec)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(
                any("missing required events" in error for error in errors),
                "\n".join(errors),
            )

    def test_validator_rejects_non_experiment_harness_evaluator(self) -> None:
        with WorkspaceDirectory() as target:
            spec = build_fixture(target)
            harness_evaluator = next(
                item for item in spec["evaluators"] if item["id"] == "harness-effect"
            )
            harness_evaluator["type"] = "deterministic"
            write_json(target / "harness/harness-spec.json", spec)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(
                any("must have experiment type" in error for error in errors),
                "\n".join(errors),
            )

    def test_harness_skills_must_use_self_evaluation_evaluator(self) -> None:
        for kind in ("harness-evaluation", "improvement"):
            with self.subTest(kind=kind), WorkspaceDirectory() as target:
                spec = build_fixture(target)
                alternate = dict(
                    next(
                        evaluator
                        for evaluator in spec["evaluators"]
                        if evaluator["id"] == "harness-effect"
                    )
                )
                alternate["id"] = "alternate-harness-effect"
                spec["evaluators"].append(alternate)
                skill = next(item for item in spec["skills"] if item["kind"] == kind)
                skill["evaluator"] = alternate["id"]
                write_json(target / "harness/harness-spec.json", spec)
                errors = Validator(target, target / "harness/harness-spec.json").validate()
                self.assertTrue(
                    any(
                        "must match self_evaluation.evaluator 'harness-effect'" in error
                        and f"kind {kind!r}" in error
                        for error in errors
                    ),
                    "\n".join(errors),
                )

    def test_schema_11_requires_verification_skill_kind(self) -> None:
        with WorkspaceDirectory() as target:
            spec = build_fixture(target)
            verification = next(
                skill for skill in spec["skills"] if skill["kind"] == "verification"
            )
            verification["kind"] = "domain"
            write_json(target / "harness/harness-spec.json", spec)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertIn("skills is missing kind: verification", errors)
    def test_validator_rejects_skill_evaluator_reference_and_scope(self) -> None:
        cases = (("unknown-evaluator", "unknown evaluator"), ("harness-effect", "task scope"))
        for evaluator_id, expected_error in cases:
            with self.subTest(evaluator=evaluator_id), WorkspaceDirectory() as target:
                spec = build_fixture(target)
                spec["skills"][0]["evaluator"] = evaluator_id
                write_json(target / "harness/harness-spec.json", spec)
                errors = Validator(target, target / "harness/harness-spec.json").validate()
                self.assertTrue(
                    any(expected_error in error for error in errors),
                    "\n".join(errors),
                )

    def test_validator_rejects_watched_path_directory_expansion(self) -> None:
        with WorkspaceDirectory() as target:
            spec = build_fixture(target)
            spec["self_evaluation"]["watched_paths"].append(".gemini/skills")
            write_json(target / "harness/harness-spec.json", spec)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(
                any("exactly match selected provider artifacts" in error for error in errors),
                "\n".join(errors),
            )

    def test_validator_rejects_invalid_targeted_suite_shape(self) -> None:
        with WorkspaceDirectory() as target:
            build_fixture(target)
            suite_path = target / "harness/evaluation/suites/targeted.json"
            suite = json.loads(suite_path.read_text(encoding="utf-8"))
            del suite["checks"]["retry-pressure"]
            write_json(suite_path, suite)
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(
                any("targeted suite checks is missing keys" in error for error in errors),
                "\n".join(errors),
            )

    def test_validator_rejects_missing_self_evaluation_contract_file(self) -> None:
        with WorkspaceDirectory() as target:
            build_fixture(target)
            (target / "harness/loops/HARNESS-EVAL-LOOP.md").unlink()
            errors = Validator(target, target / "harness/harness-spec.json").validate()
            self.assertTrue(
                any("HARNESS-EVAL-LOOP.md" in error for error in errors),
                "\n".join(errors),
            )


def json_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"missing frontmatter: {path}")
    end = text.find("\n---", 4)
    if end < 0:
        raise AssertionError(f"unterminated frontmatter: {path}")
    values: dict[str, Any] = {}
    for line in text[4:end].splitlines():
        key, separator, raw = line.partition(":")
        if not separator:
            raise AssertionError(f"invalid frontmatter line: {line!r}")
        values[key.strip()] = json.loads(raw.strip())
    return values


if __name__ == "__main__":
    unittest.main(verbosity=2)
