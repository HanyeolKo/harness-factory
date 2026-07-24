#!/usr/bin/env python3
"""Resolve a compatible harness-factory root with source-isolated caching."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

OFFICIAL_REPO = "https://github.com/HanyeolKo/harness-factory.git"
PROVENANCE_FILE = ".harness-factory-provenance.json"
REQUIRED_PATHS = (
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    "gemini-extension.json",
    "README.md",
    "CHECKLIST.md",
    "docs/CONSTRUCTOR-PROTOCOL.md",
    "interview/QUESTION-BANK.md",
    "principles/01-evaluation-first.md",
    "principles/02-context-budget.md",
    "principles/03-deterministic-offloading.md",
    "principles/04-failure-recovery.md",
    "principles/05-environment-readability.md",
    "principles/06-self-improvement.md",
    "principles/07-document-discipline.md",
    "providers/claude/contract.json",
    "providers/codex/contract.json",
    "providers/gemini/contract.json",
    "schema/harness-spec.schema.json",
    "scripts/check_self_evaluation.py",
    "scripts/record_self_evaluation.py",
    "scripts/validate_runtime_neutral.py",
    "skills/build-agent/SKILL.md",
    "skills/build-evaluator/SKILL.md",
    "skills/build-harness/SKILL.md",
    "skills/build-harness/references/RUNTIME-CONTRACT.md",
    "skills/build-harness/scripts/resolve_factory.py",
    "skills/build-skill/SKILL.md",
    "skills/evaluate-harness/SKILL.md",
    "skills/improve-harness/SKILL.md",
    "skills/verify-harness/SKILL.md",
    "templates/ENVIRONMENT.md.tmpl",
    "templates/HARNESS.md.tmpl",
    "templates/harness-spec.json.tmpl",
    "templates/adapters/claude/agent.md.tmpl",
    "templates/adapters/claude/CLAUDE.md.block.tmpl",
    "templates/adapters/codex/agent.toml.tmpl",
    "templates/adapters/codex/AGENTS.md.block.tmpl",
    "templates/adapters/codex/config.toml.tmpl",
    "templates/adapters/gemini/agent.md.tmpl",
    "templates/adapters/gemini/GEMINI.md.block.tmpl",
    "templates/adapters/shared/SKILL-TEMPLATE.md",
    "templates/adapters/shared/SKILL.md.tmpl",
    "templates/budget/CONTEXT-BUDGET.md.tmpl",
    "templates/evaluation/EVALUATION-CONTRACT.md.tmpl",
    "templates/evaluation/TARGETED-SUITE.json.tmpl",
    "templates/ledger/DECISIONS.md.tmpl",
    "templates/ledger/JOURNAL-FORMAT.md.tmpl",
    "templates/loops/EVAL-LOOP.md.tmpl",
    "templates/loops/EXECUTION-LOOP.md.tmpl",
    "templates/loops/HARNESS-EVAL-LOOP.md.tmpl",
    "templates/loops/IMPROVE-LOOP.md.tmpl",
    "templates/maintenance/COMPONENT-MUTATION-PROTOCOL.md.tmpl",
    "templates/recovery/CHECKPOINT.md.tmpl",
    "templates/recovery/RECOVERY-PLAYBOOK.md.tmpl",
    "templates/state/self-evaluation.json.tmpl",
    "templates/team/TEAM-ARCHITECTURE.md.tmpl",
    "templates/team/agents/AGENT.md.tmpl",
    "templates/triggers/check_self_evaluation.py.tmpl",
    "templates/triggers/record_self_evaluation.py.tmpl",
)
def is_factory_root(path: Path) -> bool:
    return path.is_dir() and all((path / rel).is_file() for rel in REQUIRED_PATHS)


def ancestors(path: Path):
    path = path.resolve()
    yield path
    yield from path.parents


def default_cache_dir() -> Path:
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "harness-factory" / "cache"
    return Path.home() / ".cache" / "harness-factory"


def ref_slug(ref: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", ref).strip("-")
    return slug[:48] or "main"


def source_fingerprint(repo_url: str, ref: str) -> str:
    payload = f"{repo_url.strip()}\0{ref}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def cache_target_for(cache_dir: Path, repo_url: str, ref: str) -> Path:
    fingerprint = source_fingerprint(repo_url, ref)
    return cache_dir.expanduser() / f"{ref_slug(ref)}-{fingerprint[:16]}"


def read_provenance(path: Path) -> dict[str, str] | None:
    try:
        value = json.loads((path / PROVENANCE_FILE).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict):
        return None
    return value


def cache_matches(path: Path, repo_url: str, ref: str) -> bool:
    provenance = read_provenance(path)
    return (
        is_factory_root(path)
        and provenance is not None
        and provenance.get("source_fingerprint") == source_fingerprint(repo_url, ref)
        and provenance.get("ref") == ref
        and bool(provenance.get("commit"))
    )


def git(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("git is required for repository fallback") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}") from exc


def fetch_factory(repo_url: str, ref: str, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if cache_matches(destination, repo_url, ref):
            provenance = read_provenance(destination)
            assert provenance is not None
            return provenance["commit"]
        raise RuntimeError(
            f"cache entry provenance mismatch at {destination}; "
            "remove that exact entry explicitly and retry"
        )

    with tempfile.TemporaryDirectory(
        prefix="harness-factory-fetch-", dir=destination.parent
    ) as temp_dir:
        checkout = Path(temp_dir) / "repo"
        git(["init", "--quiet", str(checkout)])
        git(["remote", "add", "origin", repo_url], cwd=checkout)
        git(["fetch", "--quiet", "--depth", "1", "origin", ref], cwd=checkout)
        git(["checkout", "--quiet", "--detach", "FETCH_HEAD"], cwd=checkout)
        if not is_factory_root(checkout):
            missing = [rel for rel in REQUIRED_PATHS if not (checkout / rel).is_file()]
            raise RuntimeError(
                "downloaded repository does not satisfy the template contract: "
                + ", ".join(missing)
            )
        commit = git(["rev-parse", "HEAD"], cwd=checkout).stdout.strip()
        provenance = {
            "source_fingerprint": source_fingerprint(repo_url, ref),
            "ref": ref,
            "commit": commit,
        }
        (checkout / PROVENANCE_FILE).write_text(
            json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
        )
        shutil.move(str(checkout), destination)
        return commit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--factory-root", type=Path)
    parser.add_argument(
        "--repo-url", default=os.environ.get("HARNESS_FACTORY_REPO", OFFICIAL_REPO)
    )
    parser.add_argument("--ref", default=os.environ.get("HARNESS_FACTORY_REF", "main"))
    parser.add_argument("--cache-dir", type=Path, default=default_cache_dir())
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    candidates: list[Path] = []
    if args.factory_root:
        candidates.append(args.factory_root.expanduser())
    if os.environ.get("HARNESS_FACTORY_HOME"):
        candidates.append(Path(os.environ["HARNESS_FACTORY_HOME"]).expanduser())
    candidates.extend(ancestors(Path(__file__).parent))
    candidates.extend(ancestors(Path.cwd()))

    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if is_factory_root(resolved):
            print(resolved)
            return 0

    cache_target = cache_target_for(args.cache_dir, args.repo_url, args.ref)
    if cache_matches(cache_target, args.repo_url, args.ref):
        print(cache_target.resolve())
        return 0

    if args.offline:
        raise RuntimeError(
            "no compatible local harness-factory root or matching source cache found "
            "while offline; set HARNESS_FACTORY_HOME or install the requested source"
        )

    commit = fetch_factory(args.repo_url, args.ref, cache_target)
    print(f"fetched source fingerprint {source_fingerprint(args.repo_url, args.ref)[:12]}@{commit}", file=sys.stderr)
    print(cache_target.resolve())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"resolve_factory: {exc}", file=sys.stderr)
        raise SystemExit(2)
