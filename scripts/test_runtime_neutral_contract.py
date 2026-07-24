#!/usr/bin/env python3
"""Repository contracts for the provider-neutral harness factory."""
from __future__ import annotations

import json
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


def make_spec(schema_version: str = "1.1") -> dict[str, Any]:
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
    runtimes = ["claude", "codex", "gemini"]
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
    if schema_version == "1.1":
        spec["self_evaluation"] = self_evaluation_policy(runtimes, skills, spec["agents"])
    return spec


def codex_instructions(role_id: str) -> str:
    return (
        f"Read harness/harness-spec.json and harness/team/agents/{role_id}.md first.\n\n"
        "Treat the common role file as the canonical instructions. Follow its input, "
        "output, access, approval-gate, and handoff contract. Return evidence and any "
        "verification not run."
    )


def common_files(harness: Path, schema_version: str) -> None:
    files = {
        "HARNESS.md": "# Harness\n\nRead harness-spec.json first.",
        "ENVIRONMENT.md": "# Environment\n\nEvaluator: python -m unittest",
        "team/TEAM-ARCHITECTURE.md": "# Team\n\nThe spec is canonical.",
        "loops/EXECUTION-LOOP.md": "# Execution\n\nExecute, task-evaluate, then trigger-check.",
        "loops/EVAL-LOOP.md": "# Task evaluation\n\nPreserve raw evidence.",
        "loops/IMPROVE-LOOP.md": "# Improvement\n\nRequire full effect evidence.",
        "recovery/RECOVERY-PLAYBOOK.md": "# Recovery\n\nEscalate after bounded retry.",
        "recovery/CHECKPOINT.md": "# Checkpoint\n\nPersist next action.",
        "ledger/JOURNAL-FORMAT.md": "# Journal\n\nAppend only.",
        "ledger/DECISIONS.md": "# Decisions\n\nD-001 fixture.",
        "budget/CONTEXT-BUDGET.md": "# Budget\n\nEvaluation has a separate cap.",
    }
    if schema_version == "1.1":
        files.update(
            {
                "loops/HARNESS-EVAL-LOOP.md": "# Harness effect evaluation\n\nCompare baseline, control, treatment.",
                "evaluation/EVALUATION-CONTRACT.md": "# Evaluation contract\n\nSeparate task and harness scopes.",
            }
        )
    for relative, text in files.items():
        write_text(harness / relative, text)
    write_text(harness / "ledger/journal.jsonl", '{"event":"session_start","unit":"U-001"}')
    write_json(
        harness / "state/state.json",
        {
            "phase": "ready",
            "queue": [{"id": "U-001", "status": "todo", "evaluator": "task-tests"}],
            "next_action": "Run U-001",
            "improve": {
                "fail_counts": {},
                "units_since_retro": 0,
                "coldstart_fail": False,
                "last_retro_targets": [],
            },
        },
    )
    if schema_version == "1.1":
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
    for runtime in spec["runtime_targets"]:
        filename, template_path = blocks[runtime]
        block = render(
            (ROOT / template_path).read_text(encoding="utf-8"),
            {"SKILL_NAME": NAMESPACE, "HARNESS_ROOT": "harness"},
        )
        write_text(target / filename, f"# Existing {runtime} rules\n\n{block}")
    if "codex" in spec["runtime_targets"]:
        config = render(
            (ROOT / "templates/adapters/codex/config.toml.tmpl").read_text(encoding="utf-8"),
            {"CODEX_MAX_THREADS": "2", "CODEX_MAX_DEPTH": "2"},
        )
        write_text(target / ".codex/config.toml", config)


def build_fixture(target: Path, schema_version: str = "1.1") -> dict[str, Any]:
    spec = make_spec(schema_version)
    write_json(target / "harness/harness-spec.json", spec)
    common_files(target / "harness", schema_version)
    render_agents(target, spec)
    render_skills(target, spec)
    render_adapters(target, spec)
    return spec


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
        codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        gemini = json.loads((ROOT / "gemini-extension.json").read_text(encoding="utf-8"))
        self.assertEqual("harness-factory", claude["name"])
        self.assertEqual(claude["name"], codex["name"])
        self.assertEqual("0.2.0", claude["version"])
        self.assertEqual(claude["version"], codex["version"])
        self.assertEqual(claude["version"], gemini["version"])
        self.assertEqual("./skills/", codex["skills"])

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
                and "self_evaluation" in item.get("then", {}).get("required", [])
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

        expected = make_spec()
        rendered = render(
            (ROOT / "templates/harness-spec.json.tmpl").read_text(encoding="utf-8"),
            {
                "SKILL_NAME": NAMESPACE,
                "PURPOSE_JSON": json_scalar(expected["harness"]["purpose"]),
                "HARNESS_ROOT": "harness",
                "RUNTIME_TARGETS_JSON": json_scalar(expected["runtime_targets"]),
                "MAX_PARALLELISM": "2",
                "MAX_DELEGATION_DEPTH": "2",
                "DOMAINS_JSON": json_scalar(expected["domains"]),
                "AGENTS_JSON": json_scalar(expected["agents"]),
                "SKILLS_JSON": json_scalar(expected["skills"]),
                "APPROVAL_GATES_JSON": json_scalar(expected["approval_gates"]),
                "HANDOFFS_JSON": json_scalar(expected["orchestration"]["handoffs"]),
                "EVALUATORS_JSON": json_scalar(expected["evaluators"]),
                "IMPROVEMENT_OWNER": expected["loops"]["improvement_owner"],
                "FAIL_THRESHOLD": "3",
                "HARNESS_EVALUATOR_ID": "harness-effect",
                "SELF_EVAL_WATCHED_PATHS_JSON": json_scalar(
                    expected["self_evaluation"]["watched_paths"]
                ),
                "SELF_EVAL_SAMPLE_RATE": "0.05",
                "FULL_EVAL_INTERVAL": "20",
                "SELF_EVAL_COOLDOWN": "3",
                "SELF_EVAL_BUDGET_RATIO": "0.1",
                "SUCCESS_DROP_POINTS": "5",
                "COST_INCREASE_RATIO": "0.25",
                "SELF_EVAL_RETRY_THRESHOLD": "3",
                "SELF_EVAL_MINIMUM_SAMPLES": "5",
            },
        )
        self.assertNotIn("{{", rendered)
        self.assertEqual(expected, json.loads(rendered))

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
            self.assertIn("메인 오케스트레이터", (target / ".gemini/agents" / f"{NAMESPACE}-billing-router.md").read_text(encoding="utf-8"))

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
