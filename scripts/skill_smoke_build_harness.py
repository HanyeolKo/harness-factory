#!/usr/bin/env python3
"""Run the runtime-neutral contract suite through the historical smoke entry point."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the generated-harness fixture and provider contract tests."
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="accepted for CLI compatibility; fixtures remain disposable",
    )
    parser.parse_args()

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/test_runtime_neutral_contract.py")],
        cwd=ROOT,
        check=False,
    )
    if result.returncode == 0:
        print("runtime-neutral contract suite passed via the smoke entry point")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())