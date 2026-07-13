#!/usr/bin/env python3
"""Resolve a compatible harness-factory root, fetching the official repo if needed."""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

OFFICIAL_REPO = "https://github.com/HanyeolKo/harness-factory.git"
REQUIRED_PATHS = (
    "README.md",
    "CHECKLIST.md",
    "docs/CONSTRUCTOR-PROTOCOL.md",
    "interview/QUESTION-BANK.md",
    "templates/HARNESS.md.tmpl",
    "templates/team/TEAM-ARCHITECTURE.md.tmpl",
    "templates/skills/SKILL-TEMPLATE.md",
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
    return slug or "main"


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
        raise RuntimeError("git is required for GitHub fallback") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}") from exc


def fetch_factory(repo_url: str, ref: str, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
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
        if destination.exists():
            if is_factory_root(destination):
                return git(["rev-parse", "HEAD"], cwd=destination).stdout.strip()
            raise RuntimeError(
                f"invalid cache entry exists at {destination}; remove it explicitly and retry"
            )
        shutil.move(str(checkout), destination)
        return commit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--factory-root", type=Path)
    parser.add_argument(
        "--repo-url", default=os.environ.get("HARNESS_FACTORY_REPO", OFFICIAL_REPO)
    )
    parser.add_argument(
        "--ref", default=os.environ.get("HARNESS_FACTORY_REF", "main")
    )
    parser.add_argument("--cache-dir", type=Path, default=default_cache_dir())
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    cache_target = args.cache_dir.expanduser() / ref_slug(args.ref)
    candidates: list[Path] = []
    if args.factory_root:
        candidates.append(args.factory_root.expanduser())
    if os.environ.get("HARNESS_FACTORY_HOME"):
        candidates.append(Path(os.environ["HARNESS_FACTORY_HOME"]).expanduser())
    candidates.extend(ancestors(Path(__file__).parent))
    candidates.extend(ancestors(Path.cwd()))
    candidates.append(cache_target)

    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if is_factory_root(resolved):
            print(resolved)
            return 0

    if args.offline:
        raise RuntimeError(
            "no compatible local harness-factory root found while offline; "
            "set HARNESS_FACTORY_HOME or install the repository"
        )

    commit = fetch_factory(args.repo_url, args.ref, cache_target)
    print(f"fetched {args.repo_url}@{commit}", file=sys.stderr)
    print(cache_target.resolve())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"resolve_factory: {exc}", file=sys.stderr)
        raise SystemExit(2)
