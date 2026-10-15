#!/usr/bin/env python3
"""Versioned verifier-pass outcome reader for retained r2 and S7 records."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

VERSION = "verifier-pass-v2.0.0"
ROOT = Path(__file__).resolve().parent.parent
KNOWN_SENSITIVITY_TASKS = {"pilot_a04_dependency_order", "test_in_b09_phone"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def provider_error_protocol(metadata: dict, runtime: dict) -> bool:
    """Retry-exhausted transport only; broad legacy provider flags do not count."""
    return bool(runtime.get("provider_error") or metadata.get("outcome_category") == "provider_error")


def read_record(run_dir: Path) -> dict:
    metadata = load(run_dir / "metadata.json")
    verifier = load(run_dir / "verifier.json")
    runtime = load(run_dir / "runtime_r2.json") or load(run_dir / "runtime.json")
    process = load(run_dir / "process.json")
    flags = metadata.get("outcome_flags") or {}
    return {
        "run_id": metadata.get("run_id", run_dir.name),
        "model": metadata.get("requested_model_id"),
        "condition": metadata.get("condition", metadata.get("skill_version")),
        "task": metadata.get("task_id"),
        "split": metadata.get("split"),
        "verifier_available": isinstance(verifier.get("passed"), bool),
        "verifier_pass": verifier.get("passed") is True,
        "legacy_pass": metadata.get("legacy_outcome_category", metadata.get("outcome_category")) == "pass",
        "provider_error_protocol": provider_error_protocol(metadata, runtime),
        "provider_error_flag_legacy": bool(flags.get("provider_error")),
        "timeout": bool(flags.get("timeout") or process.get("timed_out")),
        "max_steps_reached": bool(flags.get("max_steps_reached") or runtime.get("max_steps_reached")),
        "final_empty": bool(flags.get("final_empty")),
    }


def read_records(root: Path) -> list[dict]:
    return [read_record(path.parent) for path in sorted(root.glob("*/metadata.json"))]


def summarize(rows: list[dict], exclude_tasks: set[str] | None = None) -> dict:
    exclude_tasks = exclude_tasks or set()
    selected = [row for row in rows if row.get("task") not in exclude_tasks]
    primary = [row for row in selected if not row["provider_error_protocol"]]
    return {
        "scheduled": len(selected),
        "provider_error_protocol": len(selected) - len(primary),
        "primary_n": len(primary),
        "verifier_pass": sum(row["verifier_pass"] for row in primary),
        "verifier_pass_rate": sum(row["verifier_pass"] for row in primary) / len(primary) if primary else None,
        "legacy_pass": sum(row["legacy_pass"] for row in primary),
        "sensitivity_n_provider_as_failure": len(selected),
        "sensitivity_verifier_pass": sum(row["verifier_pass"] and not row["provider_error_protocol"] for row in selected),
        "sensitivity_pass_rate": sum(row["verifier_pass"] and not row["provider_error_protocol"] for row in selected) / len(selected) if selected else None,
        "timeouts_in_primary_denominator": sum(row["timeout"] and not row["provider_error_protocol"] for row in selected),
        "max_steps_in_primary_denominator": sum(row["max_steps_reached"] and not row["provider_error_protocol"] for row in selected),
    }


def sensitivity_views(rows: list[dict]) -> dict:
    return {
        "all": summarize(rows),
        "exclude_A04": summarize(rows, {"pilot_a04_dependency_order"}),
        "exclude_b09_phone": summarize(rows, {"test_in_b09_phone"}),
        "exclude_A04_and_b09_phone": summarize(rows, KNOWN_SENSITIVITY_TASKS),
    }


def completed_s7(status_path: Path) -> tuple[int, int]:
    text = status_path.read_text(encoding="utf-8")
    match = re.search(r"\| S7 locked formal benchmark \|\s*(\d+)\s*\|\s*(\d+)\s*\|", text)
    if not match:
        raise RuntimeError("S7 status row not found")
    return int(match.group(1)), int(match.group(2))


def enforce_formal_s7_gate(status_path: Path, manifest_path: Path) -> dict:
    planned, completed = completed_s7(status_path)
    if (planned, completed) != (1086, 1086):
        raise RuntimeError(f"formal S7 analysis blocked: STATUS.md is {completed}/{planned}, expected 1086/1086")
    manifest = load(manifest_path)
    expected = manifest.get("verifier_pass_module_sha256")
    actual = sha256(Path(__file__))
    if not expected or expected != actual:
        raise RuntimeError("formal S7 analysis blocked: verifier-pass patch hash absent or mismatched")
    return manifest
