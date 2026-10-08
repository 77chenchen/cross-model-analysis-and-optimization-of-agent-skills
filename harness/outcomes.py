"""Outcome classification and verifier aggregation for benchmark runs."""
from __future__ import annotations

import json
import py_compile
from pathlib import Path


OUTCOMES = {"empty_termination", "max_steps_reached", "compile_error", "verifier_fail", "timeout", "context_overflow", "provider_error", "pass"}


def verifier_summary(verifier: dict) -> dict:
    checks = verifier.get("checks") if isinstance(verifier.get("checks"), dict) else {}
    values = [value for value in checks.values() if isinstance(value, bool)]
    return {"check_count": len(values), "checks_passed": sum(values), "partial_score": (sum(values) / len(values)) if values else None}


def python_compile_errors(workspace: Path) -> list[str]:
    errors = []
    for source in workspace.glob("*.py"):
        try:
            py_compile.compile(str(source), doraise=True)
        except py_compile.PyCompileError as error:
            errors.append(f"{source.name}: {error.msg}")
    return errors


def classify(process: dict, raw_text: str, final_text: str, verifier: dict, compile_errors: list[str]) -> str:
    lower = raw_text.lower()
    if process.get("timed_out"):
        return "timeout"
    if any(marker in lower for marker in ("context length", "context window", "maximum context", "context_overflow")):
        return "context_overflow"
    if process.get("returncode") not in (0, None) and not '"type":"turn.completed"' in raw_text:
        return "provider_error"
    if not final_text.strip():
        return "empty_termination"
    if compile_errors:
        return "compile_error"
    if verifier.get("passed") is True:
        return "pass"
    return "verifier_fail"


def outcome_flags(process: dict, raw_text: str, final_text: str, verifier: dict, compile_errors: list[str], no_edit: bool) -> dict[str, bool]:
    """Non-exclusive outcome evidence; legacy `classify` remains unchanged."""
    lower = raw_text.lower()
    provider_error = process.get("returncode") not in (0, None) and '"type":"turn.completed"' not in raw_text
    return {
        "final_empty": not final_text.strip(),
        "no_edit": no_edit,
        "compile_error": bool(compile_errors),
        "verifier_fail": verifier.get("passed") is False,
        "timeout": bool(process.get("timed_out")),
        "context_overflow": any(marker in lower for marker in ("context length", "context window", "maximum context", "context_overflow")),
        "provider_error": provider_error,
    }


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
