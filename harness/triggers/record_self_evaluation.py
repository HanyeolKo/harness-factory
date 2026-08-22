#!/usr/bin/env python3
"""Atomically record completion of a targeted or full harness self-evaluation."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any

DECISIONS = {"targeted", "full"}
ALL_DECISIONS = {"none", *DECISIONS}
VERDICTS = {"improved", "neutral", "regressed", "inconclusive"}
DIGEST = re.compile(r"^[0-9a-f]{64}$")
EXPLICIT_OVERRIDE_REASON = "explicit-user-request"
RAW_FULL_REASONS = {"full-interval", "success-rate-regression"}


def compact(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_object(path: Path, label: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{label}-not-object")
    return value


def contract_path(target: Path, value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label}-missing")
    raw = Path(value)
    if raw.is_absolute():
        raise ValueError(f"{label}-not-target-relative")
    path = (target / raw).resolve()
    if not path.is_relative_to(target):
        raise ValueError(f"{label}-escapes-target")
    if path == target:
        raise ValueError(f"{label}-targets-root")
    return path


def internal_path(target: Path, value: Path, label: str) -> Path:
    path = value.resolve() if value.is_absolute() else (target / value).resolve()
    if not path.is_relative_to(target):
        raise ValueError(f"{label}-escapes-target")
    if path == target:
        raise ValueError(f"{label}-targets-root")
    return path


def nonnegative_counts(value: object, label: str) -> dict[str, int]:
    if not isinstance(value, dict):
        raise ValueError(f"{label}-invalid")
    result: dict[str, int] = {}
    for key, count in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError(f"{label}-key-invalid")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError(f"{label}-count-invalid")
        result[key] = count
    return result


def normalized_timestamp(value: str | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("at-invalid") from exc
    if parsed.tzinfo is None:
        raise ValueError("at-timezone-required")
    return parsed.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def validate_decision(
    result: object,
    label: str,
    allowed: set[str],
    *,
    allow_override: bool = False,
) -> dict[str, Any]:
    if not isinstance(result, dict):
        raise ValueError(f"{label}-not-object")
    decision = result.get("decision")
    if decision not in allowed:
        raise ValueError(f"{label}-decision-invalid")
    mandatory = result.get("mandatory")
    if not isinstance(mandatory, bool):
        raise ValueError(f"{label}-mandatory-invalid")
    if mandatory and decision != "full":
        raise ValueError(f"{label}-mandatory-decision-invalid")
    for field in ("reasons", "deferred_reasons"):
        values = result.get(field)
        if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
            raise ValueError(f"{label}-{field}-invalid")
    if any(reason.startswith("input-invalid:") for reason in result["reasons"]):
        raise ValueError(f"{label}-input-invalid")
    for field in ("current_canonical_hash", "current_adapter_hash"):
        value = result.get(field)
        if not isinstance(value, str) or DIGEST.fullmatch(value) is None:
            raise ValueError(f"{label}-{field}-invalid")
    acknowledgement = result.get("acknowledgement")
    if not isinstance(acknowledgement, dict) or set(acknowledgement) != {
        "coldstart_fail",
        "fail_counts",
    }:
        raise ValueError(f"{label}-acknowledgement-invalid")
    coldstart = acknowledgement.get("coldstart_fail")
    if not isinstance(coldstart, bool):
        raise ValueError(f"{label}-acknowledgement-coldstart-invalid")
    counts = nonnegative_counts(
        acknowledgement.get("fail_counts"), f"{label}-acknowledgement-fail-counts"
    )
    result["acknowledgement"] = {
        "coldstart_fail": coldstart,
        "fail_counts": counts,
    }

    if "override" in result:
        if not allow_override:
            raise ValueError(f"{label}-override-not-allowed")
        override = result.get("override")
        if not isinstance(override, dict) or set(override) != {"kind", "original"}:
            raise ValueError(f"{label}-override-invalid")
        if override.get("kind") != EXPLICIT_OVERRIDE_REASON:
            raise ValueError(f"{label}-override-kind-invalid")
        original = validate_decision(
            override.get("original"),
            f"{label}-override-original",
            {"none", "targeted"},
        )
        if original["mandatory"]:
            raise ValueError(f"{label}-override-original-mandatory")
        if decision != "full" or mandatory:
            raise ValueError(f"{label}-override-full-required")
        if EXPLICIT_OVERRIDE_REASON in original["reasons"]:
            raise ValueError(f"{label}-override-original-reason-invalid")
        if result["reasons"] != [*original["reasons"], EXPLICIT_OVERRIDE_REASON]:
            raise ValueError(f"{label}-override-reasons-mismatch")
        if result["deferred_reasons"] != original["deferred_reasons"]:
            raise ValueError(f"{label}-override-deferred-reasons-mismatch")
        for field in (
            "current_canonical_hash",
            "current_adapter_hash",
            "acknowledgement",
        ):
            if result[field] != original[field]:
                raise ValueError(f"{label}-override-{field}-mismatch")
        result["override"] = {
            "kind": EXPLICIT_OVERRIDE_REASON,
            "original": original,
        }
    elif decision == "full" and not mandatory:
        if result["deferred_reasons"] or not (
            set(result["reasons"]) & RAW_FULL_REASONS
        ):
            raise ValueError(f"{label}-unmarked-full-override")
    return result


def run_checker(checker: Path, harness_root: Path) -> dict[str, Any]:
    if not checker.is_file():
        raise ValueError("checker-missing")
    completed = subprocess.run(
        [sys.executable, str(checker), str(harness_root)],
        cwd=harness_root.parent,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise ValueError("checker-nonzero")
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("checker-output-invalid") from exc
    return validate_decision(result, "checker", ALL_DECISIONS)


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = handle.name
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            try:
                Path(temporary).unlink()
            except FileNotFoundError:
                pass


def record(
    harness_root: Path,
    expected_decision: str,
    decision_file: Path,
    verdict: str,
    at: str | None = None,
) -> dict[str, object]:
    if expected_decision not in DECISIONS:
        raise ValueError("decision-invalid")
    if verdict not in VERDICTS:
        raise ValueError("verdict-invalid")

    harness_root = harness_root.resolve()
    if not harness_root.is_dir():
        raise ValueError("harness-root-invalid")
    target = harness_root.parent.resolve()
    spec = load_object(harness_root / "harness-spec.json", "spec")
    policy = spec.get("self_evaluation")
    if not isinstance(policy, dict) or policy.get("mode") != "event-driven":
        raise ValueError("self-evaluation-policy-invalid")
    cooldown = policy.get("cooldown_units")
    if isinstance(cooldown, bool) or not isinstance(cooldown, int) or cooldown < 0:
        raise ValueError("cooldown-units-invalid")

    frozen_path = internal_path(target, decision_file, "decision-file")
    if not frozen_path.is_file():
        raise ValueError("decision-file-missing")
    frozen = validate_decision(
        load_object(frozen_path, "decision-file"),
        "decision-file",
        DECISIONS,
        allow_override=True,
    )
    if frozen["decision"] != expected_decision:
        raise ValueError(
            f"decision-mismatch:expected-{expected_decision}:frozen-{frozen['decision']}"
        )

    checker_path = contract_path(target, policy.get("checker"), "checker")
    state_path = contract_path(target, policy.get("state"), "self-evaluation-state")
    current = run_checker(checker_path, harness_root)
    for field in ("current_canonical_hash", "current_adapter_hash"):
        if current[field] != frozen[field]:
            raise ValueError(f"decision-file-stale:{field}")

    state = load_object(state_path, "self-evaluation-state")
    reasons = list(frozen["reasons"])
    recorded_at = normalized_timestamp(at)
    state["cooldown_remaining_units"] = cooldown
    state["last_decision"] = {
        "decision": expected_decision,
        "reasons": reasons,
        "verdict": verdict,
    }

    if expected_decision == "full":
        frozen_acknowledgement = frozen["acknowledgement"]
        hashes = state.get("hashes")
        if not isinstance(hashes, dict):
            raise ValueError("hashes-invalid")
        hashes["canonical"] = frozen["current_canonical_hash"]
        hashes["adapters"] = frozen["current_adapter_hash"]
        pending_events = state.get("pending_events")
        if not isinstance(pending_events, list) or not all(
            isinstance(item, str) for item in pending_events
        ):
            raise ValueError("pending-events-invalid")
        consumed_events = set(reasons)
        state["pending_events"] = [
            event for event in pending_events if event not in consumed_events
        ]
        state["units_since_full"] = 0
        state["last_full_at"] = recorded_at
        state["acknowledged"] = {
            "coldstart_fail": frozen_acknowledgement["coldstart_fail"],
            "fail_counts": dict(
                sorted(frozen_acknowledgement["fail_counts"].items())
            ),
        }

    atomic_write_json(state_path, state)
    return {
        "at": recorded_at,
        "decision": expected_decision,
        "recorded": True,
        "verdict": verdict,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("harness_root", type=Path)
    parser.add_argument("--decision", choices=sorted(DECISIONS), required=True)
    parser.add_argument("--decision-file", type=Path, required=True)
    parser.add_argument("--verdict", choices=sorted(VERDICTS), required=True)
    parser.add_argument("--at")
    args = parser.parse_args()
    try:
        result = record(
            args.harness_root,
            args.decision,
            args.decision_file,
            args.verdict,
            args.at,
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(compact({"error": str(exc), "recorded": False}))
        return 2
    print(compact(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
