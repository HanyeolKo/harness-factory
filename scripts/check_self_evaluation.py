#!/usr/bin/env python3
"""Return a compact, deterministic self-evaluation decision for a generated harness."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

DECISIONS = {"none", "targeted", "full"}
EXCLUDED_PREFIXES = (
    "budget/",
    "evaluation/reports/",
    "evaluation/runs/",
    "ledger/",
    "state/",
)


def load_object(path: Path, label: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{label}-not-object")
    return value


def finite_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label}-not-number")
    number = float(value)
    if number != number or number in (float("inf"), float("-inf")):
        raise ValueError(f"{label}-not-finite")
    return number


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


def canonical_hash(harness_root: Path) -> str:
    """Hash canonical harness files while excluding operationally-mutated state."""
    harness_root = harness_root.resolve()
    digest = hashlib.sha256()
    digest.update(b"harness-canonical-v1\0")
    for path in sorted(item for item in harness_root.rglob("*") if item.is_file()):
        relative = path.relative_to(harness_root).as_posix()
        if relative.endswith((".pyc", ".pyo")) or relative.startswith(EXCLUDED_PREFIXES):
            continue
        resolved = path.resolve()
        if not resolved.is_relative_to(harness_root):
            raise ValueError("canonical-path-escapes-harness")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0file\0")
        digest.update(resolved.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def target_relative_path(target: Path, value: object, label: str) -> tuple[str, Path]:
    """Resolve a required target-relative path and reject lexical or symlink escape."""
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label}-missing")
    raw = Path(value)
    if raw.is_absolute():
        raise ValueError(f"{label}-not-target-relative")
    resolved = (target / raw).resolve()
    if not resolved.is_relative_to(target):
        raise ValueError(f"{label}-escapes-target")
    relative = resolved.relative_to(target).as_posix()
    if not relative or relative == ".":
        raise ValueError(f"{label}-targets-root")
    return relative, resolved


def contract_path(target: Path, value: object, label: str) -> Path:
    return target_relative_path(target, value, label)[1]


def _hash_file(digest: Any, label: str, path: Path) -> None:
    digest.update(label.encode("utf-8"))
    digest.update(b"\0file\0")
    digest.update(path.read_bytes())
    digest.update(b"\0")


def _iter_tree(root: Path) -> Iterable[Path]:
    return sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix())


def adapter_hash(target: Path, watched_paths: object, harness_root: Path | None = None) -> str:
    """Hash declared adapter paths, including stable markers for missing paths."""
    target = target.resolve()
    if not isinstance(watched_paths, list) or not watched_paths:
        raise ValueError("watched-paths-invalid")

    declared: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for index, value in enumerate(watched_paths):
        relative, resolved = target_relative_path(target, value, f"watched-path-{index}")
        if relative in seen:
            raise ValueError("watched-paths-duplicate")
        seen.add(relative)
        if harness_root is not None:
            canonical = harness_root.resolve()
            if resolved == canonical or resolved.is_relative_to(canonical):
                raise ValueError("watched-path-is-canonical")
        declared.append((relative, resolved))

    digest = hashlib.sha256()
    digest.update(b"harness-adapters-v1\0")
    for relative, resolved in sorted(declared):
        digest.update(relative.encode("utf-8"))
        if not resolved.exists():
            # resolve() above still catches a broken symlink whose target escapes.
            digest.update(b"\0missing\0")
            continue
        if resolved.is_file():
            _hash_file(digest, "", resolved)
            continue
        if not resolved.is_dir():
            raise ValueError("watched-path-type-invalid")

        digest.update(b"\0dir\0")
        for entry in _iter_tree(resolved):
            entry_resolved = entry.resolve()
            if not entry_resolved.is_relative_to(target):
                raise ValueError("watched-symlink-escapes-target")
            nested = entry.relative_to(resolved).as_posix()
            if entry.is_dir():
                digest.update(nested.encode("utf-8"))
                digest.update(b"\0dir\0")
            elif entry.is_file():
                _hash_file(digest, nested, entry_resolved)
            else:
                raise ValueError("watched-entry-type-invalid")
    return digest.hexdigest()


def deterministic_sample(harness_id: str, unit_id: str, rate: float) -> bool:
    if not unit_id or rate <= 0:
        return False
    point = int.from_bytes(
        hashlib.sha256(f"{harness_id}:{unit_id}".encode("utf-8")).digest(), "big"
    ) / float(1 << 256)
    return point < rate


def decide(harness_root: Path) -> dict[str, object]:
    harness_root = harness_root.resolve()
    if not harness_root.is_dir():
        raise ValueError("harness-root-invalid")
    target = harness_root.parent.resolve()
    spec = load_object(harness_root / "harness-spec.json", "spec")
    policy = spec.get("self_evaluation")
    if not isinstance(policy, dict) or policy.get("mode") != "event-driven":
        raise ValueError("self-evaluation-policy-invalid")
    targeted_suite = contract_path(target, policy.get("targeted_suite"), "targeted-suite")
    if not targeted_suite.is_file():
        raise ValueError("targeted-suite-missing")

    state_path = contract_path(target, policy.get("state"), "self-evaluation-state")
    state = load_object(state_path, "self-evaluation-state")
    main_state = load_object(harness_root / "state" / "state.json", "state")

    sample_rate = finite_number(policy.get("targeted_sample_rate"), "sample-rate")
    budget_ratio = finite_number(policy.get("budget_ratio"), "budget-ratio")
    drop_points = finite_number(
        policy.get("success_rate_drop_points"), "success-rate-drop-points"
    )
    cost_ratio = finite_number(policy.get("cost_increase_ratio"), "cost-increase-ratio")
    full_interval = int(policy.get("full_interval_units"))
    retry_threshold = int(policy.get("retry_threshold"))
    minimum_samples = int(policy.get("minimum_samples"))
    fail_threshold = int(spec.get("loops", {}).get("fail_threshold"))
    if not 0 <= sample_rate <= 1 or not 0 < budget_ratio <= 1:
        raise ValueError("self-evaluation-ratio-out-of-range")
    if min(full_interval, retry_threshold, minimum_samples, fail_threshold) < 1:
        raise ValueError("self-evaluation-threshold-out-of-range")

    mandatory_events = policy.get("mandatory_events")
    if not isinstance(mandatory_events, list) or not all(
        isinstance(item, str) for item in mandatory_events
    ):
        raise ValueError("mandatory-events-invalid")
    pending_events = state.get("pending_events", [])
    if not isinstance(pending_events, list) or not all(
        isinstance(item, str) for item in pending_events
    ):
        raise ValueError("pending-events-invalid")

    current_canonical = canonical_hash(harness_root)
    current_adapters = adapter_hash(target, policy.get("watched_paths"), harness_root)
    hashes = state.get("hashes")
    if not isinstance(hashes, dict):
        raise ValueError("hashes-invalid")
    stored_canonical = hashes.get("canonical", "")
    stored_adapters = hashes.get("adapters", "")
    if not isinstance(stored_canonical, str) or not isinstance(stored_adapters, str):
        raise ValueError("stored-hash-invalid")

    mandatory_reasons = sorted(set(pending_events) & set(mandatory_events))
    if stored_canonical != current_canonical:
        mandatory_reasons.append("canonical-contract-change")
    if stored_adapters != current_adapters:
        mandatory_reasons.append("adapter-change")

    acknowledged = state.get("acknowledged")
    if not isinstance(acknowledged, dict):
        raise ValueError("acknowledged-invalid")
    acknowledged_coldstart = acknowledged.get("coldstart_fail")
    if not isinstance(acknowledged_coldstart, bool):
        raise ValueError("acknowledged-coldstart-invalid")
    acknowledged_counts = nonnegative_counts(
        acknowledged.get("fail_counts"), "acknowledged-fail-counts"
    )

    improve = main_state.get("improve", {})
    if not isinstance(improve, dict):
        raise ValueError("improve-state-invalid")
    coldstart_fail = improve.get("coldstart_fail", False)
    if not isinstance(coldstart_fail, bool):
        raise ValueError("coldstart-fail-invalid")
    # A pending coldstart-fail event always wins above. This boolean is the legacy
    # fallback and only represents a new incident while it remains unacknowledged.
    if coldstart_fail and not acknowledged_coldstart:
        mandatory_reasons.append("coldstart-fail")
    fail_counts = nonnegative_counts(improve.get("fail_counts", {}), "fail-counts")
    for key, count in sorted(fail_counts.items()):
        acknowledged_count = acknowledged_counts.get(key, 0)
        effective_ack = 0 if count < acknowledged_count else acknowledged_count
        if count >= fail_threshold and count > effective_ack:
            mandatory_reasons.append(f"repeat-failure:{key}")

    baseline = state.get("baseline", {})
    recent = state.get("recent", {})
    rolling = state.get("rolling", {})
    if not all(isinstance(value, dict) for value in (baseline, recent, rolling)):
        raise ValueError("metric-state-invalid")
    samples = recent.get("samples", 0)
    if not isinstance(samples, int) or isinstance(samples, bool) or samples < 0:
        raise ValueError("recent-samples-invalid")

    full_reasons: list[str] = []
    targeted_reasons: list[str] = []
    baseline_success = baseline.get("success_rate")
    recent_success = recent.get("success_rate")
    if samples >= minimum_samples and baseline_success is not None and recent_success is not None:
        drop = (
            finite_number(baseline_success, "baseline-success")
            - finite_number(recent_success, "recent-success")
        ) * 100
        if drop >= drop_points:
            full_reasons.append("success-rate-regression")

    baseline_cost = baseline.get("cost_per_unit")
    recent_cost = recent.get("cost_per_unit")
    if samples >= minimum_samples and baseline_cost is not None and recent_cost is not None:
        old_cost = finite_number(baseline_cost, "baseline-cost")
        new_cost = finite_number(recent_cost, "recent-cost")
        if old_cost > 0 and new_cost >= old_cost * (1 + cost_ratio):
            targeted_reasons.append("cost-regression")

    retries = rolling.get("retries", 0)
    if not isinstance(retries, int) or isinstance(retries, bool) or retries < 0:
        raise ValueError("rolling-retries-invalid")
    if retries >= retry_threshold:
        targeted_reasons.append("retry-pressure")

    units_since_full = state.get("units_since_full", 0)
    if not isinstance(units_since_full, int) or isinstance(units_since_full, bool):
        raise ValueError("units-since-full-invalid")
    if units_since_full < 0:
        raise ValueError("units-since-full-invalid")
    if units_since_full >= full_interval:
        full_reasons.append("full-interval")

    harness_id = spec.get("harness", {}).get("id", "")
    unit_id = state.get("current_unit", "")
    if isinstance(harness_id, str) and isinstance(unit_id, str) and deterministic_sample(
        harness_id, unit_id, sample_rate
    ):
        targeted_reasons.append("deterministic-sample")

    operation_cost = finite_number(rolling.get("operation_cost", 0), "operation-cost")
    evaluation_cost = finite_number(rolling.get("evaluation_cost", 0), "evaluation-cost")
    if operation_cost < 0 or evaluation_cost < 0:
        raise ValueError("cost-negative")
    over_budget = operation_cost > 0 and evaluation_cost / operation_cost >= budget_ratio
    cooldown = state.get("cooldown_remaining_units", 0)
    if not isinstance(cooldown, int) or isinstance(cooldown, bool) or cooldown < 0:
        raise ValueError("cooldown-invalid")

    deferred: list[str] = []
    mandatory_reasons = sorted(set(mandatory_reasons))
    full_reasons = sorted(set(full_reasons))
    targeted_reasons = sorted(set(targeted_reasons))
    if mandatory_reasons:
        decision = "full"
        reasons = mandatory_reasons + full_reasons + targeted_reasons
        mandatory = True
    elif full_reasons or targeted_reasons:
        if over_budget:
            decision = "none"
            reasons = full_reasons + targeted_reasons
            deferred.append("evaluation-budget")
        elif cooldown > 0:
            decision = "none"
            reasons = full_reasons + targeted_reasons
            deferred.append("cooldown")
        elif full_reasons:
            decision = "full"
            reasons = full_reasons + targeted_reasons
        else:
            decision = "targeted"
            reasons = targeted_reasons
        mandatory = False
    else:
        decision = "none"
        reasons = []
        mandatory = False

    if decision not in DECISIONS:  # pragma: no cover - defensive contract assertion
        raise AssertionError("invalid decision")
    return {
        "decision": decision,
        "mandatory": mandatory,
        "reasons": reasons,
        "deferred_reasons": deferred,
        "current_canonical_hash": current_canonical,
        "current_adapter_hash": current_adapters,
        "acknowledgement": {
            "coldstart_fail": coldstart_fail,
            "fail_counts": dict(sorted(fail_counts.items())),
        },
    }


def invalid_result(exc: BaseException) -> dict[str, object]:
    return {
        "decision": "full",
        "mandatory": True,
        "reasons": [f"input-invalid:{type(exc).__name__}"],
        "deferred_reasons": [],
        "current_canonical_hash": None,
        "current_adapter_hash": None,
        "acknowledgement": None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("harness_root", type=Path)
    args = parser.parse_args()
    try:
        result = decide(args.harness_root)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        result = invalid_result(exc)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
