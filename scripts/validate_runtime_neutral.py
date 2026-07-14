#!/usr/bin/env python3
"""Validate a generated runtime-neutral harness and its native adapters."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover - Python < 3.11
    raise SystemExit("Python 3.11 or newer is required (tomllib is missing)") from exc

ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MODEL_TIERS = {"fast", "balanced", "deep"}
RUNTIMES = {"claude", "codex"}
LANES = {"control", "execution", "evaluation", "improvement"}
ACCESS = {"read-only", "workspace-write"}
CLAUDE_READ_ONLY_TOOLS = {"Read", "Grep", "Glob"}
CLAUDE_READ_ONLY_DISALLOWED = {"Write", "Edit", "NotebookEdit", "Bash"}
CLAUDE_WORKSPACE_WRITE_TOOLS = {"Read", "Grep", "Glob", "Write", "Edit", "Bash"}
REQUIRED_CAPABILITIES = {
    "routing",
    "execution",
    "verification",
    "verdict",
    "defect-counting",
    "improvement",
}
TOP_LEVEL_KEYS = {
    "schema_version",
    "harness",
    "runtime_targets",
    "limits",
    "domains",
    "agents",
    "skills",
    "orchestration",
    "evaluators",
    "approval_gates",
    "memory",
    "loops",
}
REQUIRED_TOP_LEVEL_KEYS = TOP_LEVEL_KEYS - {"memory"}
MEMORY_STATUSES = {"active", "superseded", "archived", "empty"}


class Validator:
    def __init__(self, target: Path, spec_path: Path) -> None:
        self.target = target.resolve()
        self.spec_path = spec_path.resolve()
        self.errors: list[str] = []
        self.spec: dict = {}
        self.namespace = ""
        self.harness_root = self.target / "harness"
        self.agent_ids: set[str] = set()
        self.skill_ids: set[str] = set()
        self.domain_ids: set[str] = set()
        self.evaluator_ids: set[str] = set()
        self.gate_ids: set[str] = set()
        self.memory_index_path: Path | None = None
        self.memory_max_document_lines = 0

    def error(self, message: str) -> None:
        self.errors.append(message)

    def load(self) -> None:
        try:
            value = json.loads(self.spec_path.read_text(encoding="utf-8"))
        except OSError as exc:
            self.error(f"cannot read spec: {exc}")
            return
        except json.JSONDecodeError as exc:
            self.error(f"spec is not valid JSON: {exc}")
            return
        if not isinstance(value, dict):
            self.error("spec must be a JSON object")
            return
        self.spec = value

    def validate(self) -> list[str]:
        self.load()
        if not self.spec:
            return self.errors
        self.validate_shape()
        if self.namespace:
            self.validate_common_files()
            self.validate_adapters()
            self.validate_placeholders()
        return self.errors

    def validate_shape(self) -> None:
        schema_version = self.spec.get("schema_version")
        required_top_level = set(REQUIRED_TOP_LEVEL_KEYS)
        if schema_version == "1.1":
            required_top_level.add("memory")
        self.check_keys(self.spec, "spec", required_top_level, TOP_LEVEL_KEYS)
        if schema_version not in {"1.0", "1.1"}:
            self.error("schema_version must be '1.0' or '1.1'")

        harness = self.object(self.spec.get("harness"), "harness")
        self.check_keys(
            harness,
            "harness",
            {"id", "purpose", "root"},
            {"id", "purpose", "root"},
        )
        self.namespace = self.identifier(harness.get("id"), "harness.id")
        purpose = harness.get("purpose")
        if not isinstance(purpose, str) or not purpose.strip():
            self.error("harness.purpose must be a non-empty string")
        root = harness.get("root")
        if self.safe_relative(root, "harness.root"):
            self.harness_root = (self.target / root).resolve()
            if not self.harness_root.is_relative_to(self.target):
                self.error("harness.root escapes the target project")

        runtimes = self.string_list(self.spec.get("runtime_targets"), "runtime_targets")
        if not runtimes:
            self.error("runtime_targets must not be empty")
        invalid_runtimes = set(runtimes) - RUNTIMES
        if invalid_runtimes:
            self.error(f"unsupported runtime targets: {sorted(invalid_runtimes)}")
        if len(runtimes) != len(set(runtimes)):
            self.error("runtime_targets contains duplicates")

        limits = self.object(self.spec.get("limits"), "limits")
        self.check_keys(
            limits,
            "limits",
            {"max_parallelism", "max_delegation_depth"},
            {"max_parallelism", "max_delegation_depth"},
        )
        for key in ("max_parallelism", "max_delegation_depth"):
            value = limits.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                self.error(f"limits.{key} must be a positive integer")

        domains = self.list_of_objects(self.spec.get("domains"), "domains")
        self.domain_ids = self.unique_ids(domains, "domains")
        agents = self.list_of_objects(self.spec.get("agents"), "agents")
        self.agent_ids = self.unique_ids(agents, "agents")
        skills = self.list_of_objects(self.spec.get("skills"), "skills")
        self.skill_ids = self.unique_ids(skills, "skills")
        evaluators = self.list_of_objects(self.spec.get("evaluators"), "evaluators")
        self.evaluator_ids = self.unique_ids(evaluators, "evaluators")
        approval_gates = self.list_of_objects(
            self.spec.get("approval_gates"), "approval_gates"
        )
        self.gate_ids = self.unique_ids(approval_gates, "approval_gates")

        if not domains:
            self.error("domains must contain at least one domain")
        if len(agents) < 2:
            self.error("agents must contain at least two roles")
        if len(skills) < 3:
            self.error("skills must contain entry, evaluation, and improvement skills")
        if not evaluators:
            self.error("evaluators must contain at least one evaluator")

        for index, domain in enumerate(domains):
            label = f"domains[{index}]"
            self.check_keys(
                domain,
                label,
                {"id", "paths", "coordinator"},
                {"id", "paths", "coordinator"},
            )
            coordinator = domain.get("coordinator")
            if coordinator not in self.agent_ids:
                self.error(f"{label}.coordinator references unknown agent: {coordinator!r}")
            paths = self.string_list(domain.get("paths"), f"{label}.paths")
            if not paths:
                self.error(f"{label}.paths must not be empty")
            for path in paths:
                self.safe_relative(path, f"{label}.paths")

        capabilities: set[str] = set()
        agent_by_id = {agent.get("id"): agent for agent in agents}
        for index, agent in enumerate(agents):
            label = f"agents[{index}]"
            self.check_keys(
                agent,
                label,
                {
                    "id",
                    "description",
                    "lane",
                    "capabilities",
                    "domains",
                    "model_tier",
                    "access",
                },
                {
                    "id",
                    "description",
                    "lane",
                    "capabilities",
                    "domains",
                    "model_tier",
                    "access",
                },
            )
            lane = agent.get("lane")
            if lane not in LANES:
                self.error(f"{label}.lane must be one of {sorted(LANES)}")
            tier = agent.get("model_tier")
            if tier not in MODEL_TIERS:
                self.error(f"{label}.model_tier must be fast, balanced, or deep")
            if agent.get("access") not in ACCESS:
                self.error(f"{label}.access must be read-only or workspace-write")
            role_capabilities = self.string_list(
                agent.get("capabilities"), f"{label}.capabilities"
            )
            if not role_capabilities:
                self.error(f"{label}.capabilities must not be empty")
            if len(role_capabilities) != len(set(role_capabilities)):
                self.error(f"{label}.capabilities contains duplicates")
            for capability in role_capabilities:
                self.identifier(capability, f"{label}.capabilities")
            capabilities.update(role_capabilities)
            domains_for_agent = self.string_list(agent.get("domains"), f"{label}.domains")
            if len(domains_for_agent) != len(set(domains_for_agent)):
                self.error(f"{label}.domains contains duplicates")
            unknown_domains = set(domains_for_agent) - self.domain_ids
            if unknown_domains:
                self.error(f"{label}.domains references unknown domains: {sorted(unknown_domains)}")
            description = agent.get("description")
            if not isinstance(description, str) or not description.strip():
                self.error(f"{label}.description must be a non-empty string")
        missing_capabilities = REQUIRED_CAPABILITIES - capabilities
        if missing_capabilities:
            self.error(f"agent capability backbone is incomplete: {sorted(missing_capabilities)}")

        skill_kinds: set[str] = set()
        harness_root_value = harness.get("root")
        harness_root_text = (
            harness_root_value.replace("\\", "/").rstrip("/")
            if isinstance(harness_root_value, str)
            else ""
        )
        for index, skill in enumerate(skills):
            label = f"skills[{index}]"
            self.check_keys(
                skill,
                label,
                {"id", "kind", "entry_agent", "domains", "instructions"},
                {"id", "kind", "entry_agent", "domains", "instructions"},
            )
            kind = skill.get("kind")
            if kind not in {"entry", "evaluation", "improvement", "domain"}:
                self.error(f"{label}.kind is invalid: {kind!r}")
            else:
                skill_kinds.add(kind)
            if skill.get("entry_agent") not in self.agent_ids:
                self.error(f"{label}.entry_agent references unknown agent")
            skill_domains = self.string_list(skill.get("domains"), f"{label}.domains")
            if len(skill_domains) != len(set(skill_domains)):
                self.error(f"{label}.domains contains duplicates")
            unknown_domains = set(skill_domains) - self.domain_ids
            if unknown_domains:
                self.error(f"{label}.domains references unknown domains: {sorted(unknown_domains)}")
            instructions = skill.get("instructions")
            if self.safe_relative(instructions, f"{label}.instructions"):
                expected = f"{harness_root_text}/skills/{skill.get('id')}/SKILL.md"
                if instructions.replace("\\", "/") != expected:
                    self.error(
                        f"{label}.instructions must use canonical path {expected!r}"
                    )
        for required_kind in {"entry", "evaluation", "improvement"}:
            if required_kind not in skill_kinds:
                self.error(f"skills is missing kind: {required_kind}")

        orchestration = self.object(self.spec.get("orchestration"), "orchestration")
        self.check_keys(
            orchestration,
            "orchestration",
            {"entry_skill", "handoffs"},
            {"entry_skill", "handoffs"},
        )
        entry_skill = orchestration.get("entry_skill")
        if entry_skill not in self.skill_ids:
            self.error("orchestration.entry_skill references an unknown skill")
        else:
            matching = [s for s in skills if s.get("id") == entry_skill]
            if matching and matching[0].get("kind") != "entry":
                self.error("orchestration.entry_skill must reference an entry skill")
        handoffs = self.list_of_objects(
            orchestration.get("handoffs"), "orchestration.handoffs"
        )
        if not handoffs:
            self.error("orchestration.handoffs must contain at least one handoff")
        edges: list[tuple[str, str]] = []
        for index, handoff in enumerate(handoffs):
            label = f"orchestration.handoffs[{index}]"
            self.check_keys(
                handoff,
                label,
                {"from", "to", "when", "artifacts"},
                {"from", "to", "when", "artifacts"},
            )
            source = handoff.get("from")
            destination = handoff.get("to")
            if source not in self.agent_ids:
                self.error(f"{label}.from references unknown agent: {source!r}")
            if destination not in self.agent_ids:
                self.error(f"{label}.to references unknown agent: {destination!r}")
            if source in self.agent_ids and destination in self.agent_ids:
                edges.append((source, destination))
            when = handoff.get("when")
            if not isinstance(when, str) or not when.strip():
                self.error(f"{label}.when must be a non-empty string")
            for artifact in self.string_list(handoff.get("artifacts"), f"{label}.artifacts"):
                self.safe_relative(artifact, f"{label}.artifacts")
        self.validate_dag(edges)

        for index, evaluator in enumerate(evaluators):
            label = f"evaluators[{index}]"
            self.check_keys(
                evaluator,
                label,
                {"id", "owner", "runner", "type", "command", "pass_condition"},
                {"id", "owner", "runner", "type", "command", "pass_condition"},
            )
            owner = evaluator.get("owner")
            runner = evaluator.get("runner")
            if owner not in self.agent_ids:
                self.error(f"{label}.owner references unknown agent")
            if runner not in self.agent_ids:
                self.error(f"{label}.runner references unknown agent")
            if owner in agent_by_id and "verdict" not in agent_by_id[owner].get("capabilities", []):
                self.error(f"{label}.owner lacks verdict capability")
            if runner in agent_by_id and "verification" not in agent_by_id[runner].get("capabilities", []):
                self.error(f"{label}.runner lacks verification capability")
            if evaluator.get("type") not in {
                "deterministic",
                "manual-deterministic",
                "rubric",
            }:
                self.error(f"{label}.type is invalid")
            for field in ("command", "pass_condition"):
                value = evaluator.get(field)
                if not isinstance(value, str) or not value.strip():
                    self.error(f"{label}.{field} must be a non-empty string")

        for index, gate in enumerate(approval_gates):
            label = f"approval_gates[{index}]"
            self.check_keys(
                gate,
                label,
                {"id", "trigger", "owner", "required_action"},
                {"id", "trigger", "owner", "required_action"},
            )
            self.identifier(gate.get("owner"), f"{label}.owner")
            for field in ("trigger", "required_action"):
                value = gate.get(field)
                if not isinstance(value, str) or not value.strip():
                    self.error(f"{label}.{field} must be a non-empty string")

        memory_value = self.spec.get("memory")
        if memory_value is not None:
            memory = self.object(memory_value, "memory")
            self.check_keys(
                memory,
                "memory",
                {"index", "policy", "max_document_lines"},
                {"index", "policy", "max_document_lines"},
            )
            index_path = memory.get("index")
            if self.safe_relative(index_path, "memory.index"):
                expected_index = f"{harness_root_text}/memory/INDEX.md"
                if index_path.replace("\\", "/") != expected_index:
                    self.error(f"memory.index must use canonical path {expected_index!r}")
                resolved_index = (self.target / index_path).resolve()
                if not resolved_index.is_relative_to(self.target):
                    self.error("memory.index escapes the target project")
                else:
                    self.memory_index_path = resolved_index
            if memory.get("policy") != "preserve-and-reconcile":
                self.error("memory.policy must be 'preserve-and-reconcile'")
            max_lines = memory.get("max_document_lines")
            if not isinstance(max_lines, int) or isinstance(max_lines, bool) or max_lines < 1:
                self.error("memory.max_document_lines must be a positive integer")
            else:
                self.memory_max_document_lines = max_lines

        loops = self.object(self.spec.get("loops"), "loops")
        self.check_keys(
            loops,
            "loops",
            {
                "execution",
                "evaluation",
                "improvement",
                "improvement_owner",
                "fail_threshold",
                "retro_interval",
            },
            {
                "execution",
                "evaluation",
                "improvement",
                "improvement_owner",
                "fail_threshold",
                "retro_interval",
            },
        )
        improvement_owner = loops.get("improvement_owner")
        if improvement_owner not in self.agent_ids:
            self.error("loops.improvement_owner references unknown agent")
        elif "improvement" not in agent_by_id[improvement_owner].get("capabilities", []):
            self.error("loops.improvement_owner lacks improvement capability")
        for field in ("execution", "evaluation", "improvement"):
            self.safe_relative(loops.get(field), f"loops.{field}")
        for field in ("fail_threshold", "retro_interval"):
            value = loops.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                self.error(f"loops.{field} must be a positive integer")

    def validate_dag(self, edges: list[tuple[str, str]]) -> None:
        graph = {role: [] for role in self.agent_ids}
        indegree = {role: 0 for role in self.agent_ids}
        for source, destination in edges:
            graph[source].append(destination)
            indegree[destination] += 1
        queue = [role for role, degree in indegree.items() if degree == 0]
        visited = 0
        while queue:
            role = queue.pop()
            visited += 1
            for destination in graph[role]:
                indegree[destination] -= 1
                if indegree[destination] == 0:
                    queue.append(destination)
        if visited != len(self.agent_ids):
            self.error("orchestration.handoffs must be acyclic; improvement feedback belongs in loops")

    def validate_common_files(self) -> None:
        required = [
            "HARNESS.md",
            "harness-spec.json",
            "ENVIRONMENT.md",
            "team/TEAM-ARCHITECTURE.md",
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
        if self.spec.get("memory") is not None:
            required.append("memory/INDEX.md")
        for relative in required:
            if not (self.harness_root / relative).is_file():
                self.error(f"missing common harness file: {relative}")
        common_agents = self.harness_root / "team" / "agents"
        actual = {path.stem for path in common_agents.glob("*.md")} if common_agents.is_dir() else set()
        if actual != self.agent_ids:
            self.error(
                f"common agent parity mismatch: expected {sorted(self.agent_ids)}, got {sorted(actual)}"
            )
        agents_by_id = {agent["id"]: agent for agent in self.spec.get("agents", [])}
        for role in self.agent_ids:
            path = common_agents / f"{role}.md"
            if not path.is_file():
                continue
            fields = self.frontmatter_fields(path)
            self.check_keys(
                fields,
                f"common agent {path.name} frontmatter",
                {"id", "lane", "model-tier", "access"},
                {"id", "lane", "model-tier", "access"},
            )
            expected_fields = {
                "id": role,
                "lane": agents_by_id[role].get("lane"),
                "model-tier": agents_by_id[role].get("model_tier"),
                "access": agents_by_id[role].get("access"),
            }
            for key, expected in expected_fields.items():
                if fields.get(key) != expected:
                    self.error(
                        f"common agent {key} parity mismatch: {path.name}"
                    )
            description = agents_by_id[role].get("description")
            if isinstance(description, str) and description not in path.read_text(
                encoding="utf-8"
            ):
                self.error(f"common agent description parity mismatch: {path.name}")
        for skill in self.spec.get("skills", []):
            skill_id = skill.get("id")
            canonical = self.canonical_skill_path(skill)
            if canonical is None:
                continue
            if not canonical.is_file():
                self.error(f"missing canonical skill instructions: {skill_id}")
                continue
            if self.frontmatter_name(canonical) != skill_id:
                self.error(f"canonical skill frontmatter name mismatch: {skill_id}")
            self.check_keys(
                self.frontmatter_fields(canonical),
                f"canonical skill {skill_id} frontmatter",
                {"name", "description"},
                {"name", "description"},
            )
            self.require_json_frontmatter_string(
                canonical, "description", f"canonical skill {skill_id}"
            )
            spec_reference = f"{self.harness_root_text()}/harness-spec.json"
            if spec_reference not in canonical.read_text(encoding="utf-8"):
                self.error(f"canonical skill does not reference common spec: {skill_id}")
        state_path = self.harness_root / "state" / "state.json"
        if state_path.is_file():
            try:
                state = json.loads(state_path.read_text(encoding="utf-8"))
                if not state.get("next_action"):
                    self.error("state.next_action must not be empty")
                queue = state.get("queue")
                if not isinstance(queue, list) or not queue:
                    self.error("state.queue must contain at least one work unit")
                else:
                    for index, unit in enumerate(queue):
                        evaluator = unit.get("evaluator")
                        if not evaluator:
                            self.error(f"state.queue[{index}] is missing evaluator")
                        elif evaluator not in self.evaluator_ids:
                            self.error(
                                f"state.queue[{index}] references unknown evaluator: "
                                f"{evaluator!r}"
                            )
            except (OSError, json.JSONDecodeError) as exc:
                self.error(f"state/state.json is invalid: {exc}")
        journal = self.harness_root / "ledger" / "journal.jsonl"
        if journal.is_file() and not journal.read_text(encoding="utf-8").strip():
            self.error("ledger/journal.jsonl must contain an initial event")
        if self.memory_index_path is not None and self.memory_index_path.is_file():
            self.validate_memory_index(self.memory_index_path)

    def validate_memory_index(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8")
        self.validate_memory_document_budget(path, "memory index", text)
        required_headers = [
            "ID",
            "경로",
            "한 줄 요약",
            "언제 읽나",
            "출처",
            "마지막 검증",
            "상태",
        ]
        header = next(
            (
                line
                for line in text.splitlines()
                if line.lstrip().startswith("|")
                and all(marker in line for marker in required_headers)
            ),
            None,
        )
        if header is None:
            self.error("memory index is missing required table headers")
            return

        seen_ids: set[str] = set()
        seen_paths: set[str] = set()
        for line in text.splitlines():
            if not line.lstrip().startswith("|"):
                continue
            columns = [column.strip() for column in line.strip().strip("|").split("|")]
            if len(columns) != 7:
                self.error(f"memory index has a malformed table row: {line!r}")
                continue
            if columns[0] in {"ID", "---"}:
                continue
            if all(set(column) <= {"-", ":"} for column in columns):
                continue
            entry_id, relative, _summary, _read_when, _source, _verified, status = columns
            if status not in MEMORY_STATUSES:
                self.error(f"memory index has unsupported status {status!r}: {entry_id!r}")
                continue
            if status == "empty":
                if entry_id != "-" or relative != "-":
                    self.error("memory index empty row must use '-' for ID and path")
                continue
            if not self.identifier(entry_id, "memory index ID"):
                continue
            if entry_id in seen_ids:
                self.error(f"memory index contains duplicate ID: {entry_id!r}")
            seen_ids.add(entry_id)
            normalized = relative.replace("\\", "/")
            if normalized in seen_paths:
                self.error(f"memory index contains duplicate path: {relative!r}")
            seen_paths.add(normalized)
            if normalized in {"harness/state/state.json", "harness/ledger/journal.jsonl"}:
                self.error(f"memory index must not duplicate state or event history: {relative!r}")
            if status == "active" and self.safe_relative(relative, "memory index path"):
                candidate = (self.target / relative).resolve()
                if not candidate.is_relative_to(self.target) or not candidate.is_file():
                    self.error(f"memory index active path does not exist: {relative!r}")
                elif candidate.suffix.lower() == ".md":
                    try:
                        candidate_text = candidate.read_text(encoding="utf-8")
                    except UnicodeDecodeError:
                        self.error(f"memory index active Markdown is not UTF-8: {relative!r}")
                    else:
                        self.validate_memory_document_budget(
                            candidate, f"memory document {relative!r}", candidate_text
                        )

    def validate_memory_document_budget(
        self, path: Path, label: str, text: str
    ) -> None:
        if self.memory_max_document_lines < 1:
            return
        line_count = len(text.splitlines())
        if (
            line_count > self.memory_max_document_lines
            and "<!-- 문서규율 예외:" not in text
        ):
            self.error(
                f"{label} exceeds memory.max_document_lines "
                f"({line_count} > {self.memory_max_document_lines}): "
                f"{path.relative_to(self.target)!s}"
            )

    def validate_adapters(self) -> None:
        runtimes = set(self.spec.get("runtime_targets", []))
        if "claude" in runtimes:
            self.validate_claude()
        if "codex" in runtimes:
            self.validate_codex()

    def validate_claude(self) -> None:
        marker = f"<!-- harness-factory:start {self.namespace} -->"
        self.require_single_marker(self.target / "CLAUDE.md", marker)
        expected_agents = {f"{self.namespace}-{role}" for role in self.agent_ids}
        agent_root = self.target / ".claude" / "agents"
        actual_agents = (
            {path.stem for path in agent_root.glob(f"{self.namespace}-*.md")}
            if agent_root.is_dir()
            else set()
        )
        if actual_agents != expected_agents:
            self.error(
                "Claude managed-agent parity mismatch: "
                f"expected {sorted(expected_agents)}, got {sorted(actual_agents)}"
            )
        agents_by_id = {agent["id"]: agent for agent in self.spec.get("agents", [])}
        harness_root = self.harness_root_text()
        for role in self.agent_ids:
            agent_name = f"{self.namespace}-{role}"
            path = agent_root / f"{agent_name}.md"
            if not path.is_file():
                self.error(f"missing Claude agent: {path.relative_to(self.target)}")
                continue
            fields = self.frontmatter_fields(path)
            claude_frontmatter_keys = {
                "name",
                "description",
                "model",
                "tools",
                "disallowedTools",
                "permissionMode",
            }
            self.check_keys(
                fields,
                f"Claude agent {path.name} frontmatter",
                claude_frontmatter_keys,
                claude_frontmatter_keys,
            )
            if fields.get("name") != agent_name:
                self.error(f"Claude agent frontmatter does not match filename: {path.name}")
            if fields.get("description") != agents_by_id[role].get("description"):
                self.error(f"Claude agent description parity mismatch: {path.name}")
            self.require_json_frontmatter_string(
                path, "description", f"Claude agent {path.name}"
            )
            agent_text = path.read_text(encoding="utf-8")
            for common_reference in (
                f"{harness_root}/harness-spec.json",
                f"{harness_root}/team/agents/{role}.md",
            ):
                if common_reference not in agent_text:
                    self.error(
                        f"Claude agent does not reference common contract "
                        f"{common_reference!r}: {path.name}"
                    )
            if self.markdown_body(path) != self.expected_claude_agent_body(role):
                self.error(f"Claude agent thin-wrapper parity mismatch: {path.name}")
            if fields.get("permissionMode") == "bypassPermissions":
                self.error(f"Claude agent must not bypass permissions: {path.name}")
            if agents_by_id[role].get("access") == "read-only":
                tools = self.comma_values(fields.get("tools", ""))
                disallowed = self.comma_values(fields.get("disallowedTools", ""))
                if tools != CLAUDE_READ_ONLY_TOOLS:
                    self.error(f"Claude read-only tools mapping mismatch: {path.name}")
                if not CLAUDE_READ_ONLY_DISALLOWED.issubset(disallowed):
                    self.error(
                        f"Claude read-only disallowedTools mapping mismatch: {path.name}"
                    )
                if fields.get("permissionMode") != "plan":
                    self.error(
                        f"Claude read-only permissionMode must be plan: {path.name}"
                    )
            else:
                tools = self.comma_values(fields.get("tools", ""))
                disallowed = self.comma_values(fields.get("disallowedTools", ""))
                if tools != CLAUDE_WORKSPACE_WRITE_TOOLS:
                    self.error(
                        f"Claude workspace-write tools mapping mismatch: {path.name}"
                    )
                if "NotebookEdit" not in disallowed:
                    self.error(
                        f"Claude workspace-write disallowedTools mapping mismatch: {path.name}"
                    )
                if fields.get("permissionMode") != "default":
                    self.error(
                        f"Claude workspace-write permissionMode must be default: {path.name}"
                    )
        for skill_id in self.skill_ids:
            path = self.target / ".claude" / "skills" / skill_id / "SKILL.md"
            if not path.is_file():
                self.error(f"missing Claude skill: {skill_id}")
            elif self.frontmatter_name(path) != skill_id:
                self.error(f"Claude skill frontmatter name mismatch: {skill_id}")
            else:
                self.require_json_frontmatter_string(
                    path, "description", f"Claude skill {skill_id}"
                )
                canonical = self.canonical_skill_path_for_id(skill_id)
                if canonical and canonical.is_file() and path.read_bytes() != canonical.read_bytes():
                    self.error(f"Claude skill differs from canonical instructions: {skill_id}")
        skill_root = self.target / ".claude" / "skills"
        actual_skills = (
            {
                path.name
                for path in skill_root.glob(f"{self.namespace}*")
                if path.is_dir() and (path / "SKILL.md").is_file()
            }
            if skill_root.is_dir()
            else set()
        )
        if actual_skills != self.skill_ids:
            self.error(
                "Claude managed-skill parity mismatch: "
                f"expected {sorted(self.skill_ids)}, got {sorted(actual_skills)}"
            )

    def validate_codex(self) -> None:
        marker = f"<!-- harness-factory:start {self.namespace} -->"
        self.require_single_marker(self.target / "AGENTS.md", marker)
        for skill_id in self.skill_ids:
            path = self.target / ".agents" / "skills" / skill_id / "SKILL.md"
            if not path.is_file():
                self.error(f"missing Codex skill: {skill_id}")
            elif self.frontmatter_name(path) != skill_id:
                self.error(f"Codex skill frontmatter name mismatch: {skill_id}")
            else:
                self.require_json_frontmatter_string(
                    path, "description", f"Codex skill {skill_id}"
                )
                canonical = self.canonical_skill_path_for_id(skill_id)
                if canonical and canonical.is_file() and path.read_bytes() != canonical.read_bytes():
                    self.error(f"Codex skill differs from canonical instructions: {skill_id}")
        skill_root = self.target / ".agents" / "skills"
        actual_skills = (
            {
                path.name
                for path in skill_root.glob(f"{self.namespace}*")
                if path.is_dir() and (path / "SKILL.md").is_file()
            }
            if skill_root.is_dir()
            else set()
        )
        if actual_skills != self.skill_ids:
            self.error(
                "Codex managed-skill parity mismatch: "
                f"expected {sorted(self.skill_ids)}, got {sorted(actual_skills)}"
            )

        codex_agent_root = self.target / ".codex" / "agents"
        expected_agent_names = {f"{self.namespace}-{role}" for role in self.agent_ids}
        actual_agent_names = (
            {path.stem for path in codex_agent_root.glob(f"{self.namespace}-*.toml")}
            if codex_agent_root.is_dir()
            else set()
        )
        if actual_agent_names != expected_agent_names:
            self.error(
                "Codex managed-agent parity mismatch: "
                f"expected {sorted(expected_agent_names)}, got {sorted(actual_agent_names)}"
            )

        config_path = self.target / ".codex" / "config.toml"
        try:
            config = tomllib.loads(config_path.read_text(encoding="utf-8"))
        except OSError as exc:
            self.error(f"cannot read .codex/config.toml: {exc}")
            return
        except tomllib.TOMLDecodeError as exc:
            self.error(f".codex/config.toml is invalid TOML: {exc}")
            return
        agent_settings = config.get("agents")
        if not isinstance(agent_settings, dict):
            self.error(".codex/config.toml is missing [agents]")
            return
        limits = self.spec.get("limits", {})
        max_threads = agent_settings.get("max_threads")
        max_depth = agent_settings.get("max_depth")
        if not isinstance(max_threads, int) or isinstance(max_threads, bool):
            self.error("Codex max_threads must be an integer")
        elif max_threads < limits.get("max_parallelism", 1):
            self.error("Codex max_threads is lower than spec max_parallelism")
        if not isinstance(max_depth, int) or isinstance(max_depth, bool):
            self.error("Codex max_depth must be an integer")
        elif max_depth < limits.get("max_delegation_depth", 1):
            self.error("Codex max_depth is lower than spec max_delegation_depth")
        agents_by_id = {agent["id"]: agent for agent in self.spec.get("agents", [])}
        for role in self.agent_ids:
            agent_name = f"{self.namespace}-{role}"
            agent_path = codex_agent_root / f"{agent_name}.toml"
            try:
                agent_config = tomllib.loads(agent_path.read_text(encoding="utf-8"))
            except OSError as exc:
                self.error(f"missing Codex agent file {agent_path.name}: {exc}")
                continue
            except tomllib.TOMLDecodeError as exc:
                self.error(f"invalid Codex agent TOML {agent_path.name}: {exc}")
                continue
            if agent_config.get("name") != agent_name:
                self.error(f"Codex agent name mismatch: {agent_path.name}")
            codex_agent_keys = {
                "name",
                "description",
                "model",
                "model_reasoning_effort",
                "sandbox_mode",
                "developer_instructions",
            }
            self.check_keys(
                agent_config,
                f"Codex agent {agent_path.name}",
                codex_agent_keys,
                codex_agent_keys,
            )
            expected_description = agents_by_id[role].get("description")
            if agent_config.get("description") != expected_description:
                self.error(f"Codex agent description parity mismatch: {agent_path.name}")
            instructions = agent_config.get("developer_instructions")
            if not isinstance(instructions, str) or not instructions.strip():
                self.error(f"Codex agent lacks developer_instructions: {agent_path.name}")
            else:
                harness_root = self.harness_root_text()
                for common_reference in (
                    f"{harness_root}/harness-spec.json",
                    f"{harness_root}/team/agents/{role}.md",
                ):
                    if common_reference not in instructions:
                        self.error(
                            f"Codex agent does not reference common contract "
                            f"{common_reference!r}: {agent_path.name}"
                        )
                if instructions != self.expected_codex_agent_instructions(role):
                    self.error(
                        f"Codex agent thin-wrapper parity mismatch: {agent_path.name}"
                    )
            if agent_config.get("sandbox_mode") != agents_by_id[role].get("access"):
                self.error(f"Codex agent access parity mismatch: {agent_path.name}")

    def validate_placeholders(self) -> None:
        roots = [self.harness_root]
        if "claude" in self.spec.get("runtime_targets", []):
            roots.extend([self.target / ".claude", self.target / "CLAUDE.md"])
        if "codex" in self.spec.get("runtime_targets", []):
            roots.extend(
                [
                    self.target / ".agents",
                    self.target / ".codex",
                    self.target / "AGENTS.md",
                ]
            )
        for root in roots:
            paths = [root] if root.is_file() else list(root.rglob("*")) if root.exists() else []
            for path in paths:
                if not path.is_file():
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                if re.search(r"\{\{[^{}]+\}\}", text):
                    self.error(f"unrendered placeholder: {path.relative_to(self.target)}")

    def require_single_marker(self, path: Path, marker: str) -> None:
        try:
            count = path.read_text(encoding="utf-8").count(marker)
        except OSError:
            self.error(f"missing root guidance file: {path.name}")
            return
        if count != 1:
            self.error(f"{path.name} must contain exactly one {marker!r} marker, got {count}")

    def markdown_body(self, path: Path) -> str:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return ""
        if not text.startswith("---\n"):
            return ""
        end = text.find("\n---", 4)
        if end < 0:
            return ""
        return text[end + len("\n---") :].strip()

    def expected_claude_agent_body(self, role: str) -> str:
        harness_root = self.harness_root_text()
        return (
            f"# {role}\n\n"
            f"먼저 `{harness_root}/harness-spec.json`과 "
            f"`{harness_root}/team/agents/{role}.md`를 읽는다.\n\n"
            "공통 역할 파일을 이 agent의 지시 정본으로 따른다. 결과에 근거와 "
            "미실행 검증을 포함하고, 다음 역할은 "
            f"`{self.namespace}-<role-id>` namespaced agent로 지정한다."
        )

    def expected_codex_agent_instructions(self, role: str) -> str:
        harness_root = self.harness_root_text()
        return (
            f"Read {harness_root}/harness-spec.json and "
            f"{harness_root}/team/agents/{role}.md first.\n\n"
            "Treat the common role file as the canonical instructions. Follow its "
            "input, output, access, approval-gate, and handoff contract. Return "
            "evidence and any verification not run."
        )

    def frontmatter_raw_fields(self, path: Path) -> dict[str, str]:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return {}
        if not text.startswith("---\n"):
            return {}
        end = text.find("\n---", 4)
        if end < 0:
            return {}
        result: dict[str, str] = {}
        for line in text[4:end].splitlines():
            key, separator, value = line.partition(":")
            if separator:
                result[key.strip()] = value.strip()
        return result

    def frontmatter_fields(self, path: Path) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, raw in self.frontmatter_raw_fields(path).items():
            try:
                result[key] = json.loads(raw)
            except json.JSONDecodeError:
                result[key] = raw.strip("'\"")
        return result

    def frontmatter_name(self, path: Path) -> str:
        value = self.frontmatter_fields(path).get("name", "")
        return value if isinstance(value, str) else ""

    def require_json_frontmatter_string(
        self, path: Path, key: str, label: str
    ) -> None:
        raw = self.frontmatter_raw_fields(path).get(key)
        if raw is None:
            self.error(f"{label} is missing frontmatter {key}")
            return
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            self.error(f"{label} frontmatter {key} must be a JSON-quoted string")
            return
        if not isinstance(value, str):
            self.error(f"{label} frontmatter {key} must be a JSON string")

    def canonical_skill_path(self, skill: dict) -> Path | None:
        instructions = skill.get("instructions")
        if not isinstance(instructions, str) or not instructions:
            return None
        path = (self.target / instructions).resolve()
        if not path.is_relative_to(self.harness_root):
            self.error(
                f"skill instructions escape common harness root: {skill.get('id')!r}"
            )
            return None
        return path

    def canonical_skill_path_for_id(self, skill_id: str) -> Path | None:
        for skill in self.spec.get("skills", []):
            if skill.get("id") == skill_id:
                return self.canonical_skill_path(skill)
        return None

    def comma_values(self, value: object) -> set[str]:
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            return set(value)
        if isinstance(value, str):
            return {item.strip() for item in value.split(",") if item.strip()}
        return set()

    def harness_root_text(self) -> str:
        value = self.spec.get("harness", {}).get("root")
        return value.replace("\\", "/").rstrip("/") if isinstance(value, str) else ""

    def unique_ids(self, values: list[dict], label: str) -> set[str]:
        result: set[str] = set()
        for index, value in enumerate(values):
            item_id = self.identifier(value.get("id"), f"{label}[{index}].id")
            if item_id in result:
                self.error(f"duplicate {label} id: {item_id}")
            if item_id:
                result.add(item_id)
        return result

    def check_keys(
        self,
        value: dict,
        label: str,
        required: set[str],
        allowed: set[str],
    ) -> None:
        missing = required - set(value)
        unknown = set(value) - allowed
        if missing:
            self.error(f"{label} is missing keys: {sorted(missing)}")
        if unknown:
            self.error(f"{label} has unsupported keys: {sorted(unknown)}")

    def identifier(self, value: object, label: str) -> str:
        if not isinstance(value, str) or ID_RE.fullmatch(value) is None:
            self.error(f"{label} must be lower-kebab-case")
            return ""
        return value

    def safe_relative(self, value: object, label: str) -> bool:
        if not isinstance(value, str) or not value:
            self.error(f"{label} must be a non-empty relative path")
            return False
        normalized = value.replace("\\", "/")
        if normalized.startswith("/") or re.match(r"^[A-Za-z]:/", normalized):
            self.error(f"{label} must not be absolute: {value!r}")
            return False
        if ".." in normalized.split("/"):
            self.error(f"{label} must not traverse outside the target: {value!r}")
            return False
        return True

    def object(self, value: object, label: str) -> dict:
        if not isinstance(value, dict):
            self.error(f"{label} must be an object")
            return {}
        return value

    def list_of_objects(self, value: object, label: str) -> list[dict]:
        if not isinstance(value, list):
            self.error(f"{label} must be an array")
            return []
        if not all(isinstance(item, dict) for item in value):
            self.error(f"{label} must contain only objects")
            return []
        return value

    def string_list(self, value: object, label: str) -> list[str]:
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            self.error(f"{label} must be an array of strings")
            return []
        return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path, help="target project containing harness/")
    parser.add_argument(
        "--spec",
        type=Path,
        help="explicit spec path (default: <target>/harness/harness-spec.json)",
    )
    args = parser.parse_args()
    target = args.target.expanduser().resolve()
    spec_path = (
        args.spec.expanduser().resolve()
        if args.spec
        else target / "harness" / "harness-spec.json"
    )
    errors = Validator(target, spec_path).validate()
    if errors:
        print("runtime-neutral harness validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"runtime-neutral harness validation passed: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
