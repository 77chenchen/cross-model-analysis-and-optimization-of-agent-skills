#!/usr/bin/env python3
"""Write reproducible pilot metadata and a conservative normalized trajectory."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
try:
    from .outcomes import classify, load_json, outcome_flags, python_compile_errors, verifier_summary
except ImportError:  # Direct script execution from harness/run_pilot.sh.
    from outcomes import classify, load_json, outcome_flags, python_compile_errors, verifier_summary


def digest(path: Path) -> str:
    h = hashlib.sha256()
    if path.is_dir():
        for entry in sorted(p for p in path.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
            h.update(str(entry.relative_to(path)).encode())
            h.update(entry.read_bytes())
    else:
        h.update(path.read_bytes())
    return h.hexdigest()


def git_commit(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def source_unchanged(template: Path, workspace: Path) -> bool:
    """True only when every template Python source remains byte-identical."""
    sources = list(template.glob("*.py"))
    return bool(sources) and all((workspace / item.name).exists() and (workspace / item.name).read_bytes() == item.read_bytes() for item in sources)


def phase_of(event_type: str, item_type: str, text: str) -> str:
    value = f"{event_type} {item_type} {text}".lower()
    if any(word in value for word in ("test", "verify", "validate", "pytest", "unittest")):
        return "validate"
    if item_type == "command_execution" or any(word in value for word in ("rg ", "sed ", "ls ", "cat ", "pwd")):
        return "inspect"
    if any(word in value for word in ("edit", "write", "patch", "implement", "fix")):
        return "implement"
    if "agent_message" in item_type:
        return "plan"
    if "completed" in value or "final" in value:
        return "report"
    return "unknown"


def normalize(raw: Path, output: Path, run_id: str) -> dict:
    runtime = {"finish_reason": None, "finish_reason_available": False, "usage": {"input_tokens": None, "cached_input_tokens": None, "output_tokens": None, "reasoning_output_tokens": None}, "malformed_tool_calls": 0, "turn_completed": False}
    with raw.open() as src, output.open("w") as dst:
        for sequence, line in enumerate(src):
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            item = event.get("item", {}) if isinstance(event.get("item"), dict) else {}
            raw_type = str(event.get("type", ""))
            usage = event.get("usage") if isinstance(event.get("usage"), dict) else {}
            if usage:
                for key in runtime["usage"]:
                    runtime["usage"][key] = usage.get(key, runtime["usage"][key])
            if raw_type == "turn.completed": runtime["turn_completed"] = True
            finish_reason = event.get("finish_reason") or item.get("finish_reason")
            if finish_reason is not None:
                runtime["finish_reason"] = finish_reason; runtime["finish_reason_available"] = True
            error_text = str(item.get("error") or item.get("message") or "").lower()
            if "unsupported call" in error_text or "requires an explicit" in error_text:
                runtime["malformed_tool_calls"] += 1
            item_type = str(item.get("type", ""))
            command = item.get("command") if item_type == "command_execution" else None
            text = item.get("text") or item.get("message")
            if item_type == "command_execution":
                event_type = "command"
            elif item_type == "agent_message":
                event_type = "message"
            elif raw_type.endswith("error") or item_type == "error":
                event_type = "error"
            elif raw_type in {"thread.started", "turn.started", "turn.completed"}:
                event_type = "lifecycle"
            else:
                event_type = "other"
            normalized = {
                "run_id": run_id, "sequence": sequence, "event_type": event_type,
                "phase": phase_of(raw_type, item_type, str(text or command or "")),
                "raw_event_type": raw_type, "tool_name": item_type or None,
                "status": item.get("status"), "command": command, "text": text,
                "finish_reason": finish_reason, "input_tokens": usage.get("input_tokens"),
                "cached_input_tokens": usage.get("cached_input_tokens"),
                "output_tokens": usage.get("output_tokens"),
                "reasoning_output_tokens": usage.get("reasoning_output_tokens"),
                "malformed_tool_call": "unsupported call" in error_text or "requires an explicit" in error_text,
            }
            dst.write(json.dumps(normalized, ensure_ascii=False) + "\n")
    return runtime


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--skill-id", choices=("A", "B", "C"), required=True)
    parser.add_argument("--skill-version", choices=("v0", "v1"), required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--trajectory", type=Path, required=True)
    parser.add_argument("--process-outcome", type=Path, required=True)
    parser.add_argument("--final-message", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--run-cohort", default="pilot")
    parser.add_argument("--repetition", type=int, default=None)
    parser.add_argument("--runner", default="codex-cli")
    args = parser.parse_args()
    task = args.root / "tasks" / "pilot" / args.task_id / "template"
    verifier = args.root / "verifiers" / f"{args.task_id}.py"
    skill = args.root / "skills" / args.skill_id / f"{args.skill_version}.md"
    run_id = args.run_dir.name
    runtime = normalize(args.trajectory, args.run_dir / "actions.jsonl", run_id)
    process = load_json(args.process_outcome)
    verifier_result = load_json(args.run_dir / "verifier.json")
    summary = verifier_summary(verifier_result)
    verifier_result["summary"] = summary
    (args.run_dir / "verifier.json").write_text(json.dumps(verifier_result) + "\n")
    final_text = args.final_message.read_text() if args.final_message.exists() else ""
    compile_errors = python_compile_errors(args.workspace)
    outcome = classify(process, args.trajectory.read_text(), final_text, verifier_result, compile_errors)
    flags = outcome_flags(process, args.trajectory.read_text(), final_text, verifier_result, compile_errors, source_unchanged(task, args.workspace))
    runtime.update({"outcome_category": outcome, "legacy_outcome_category": outcome, "outcome_flags": flags, "compile_errors": compile_errors, "final_message_chars": len(final_text)})
    (args.run_dir / "runtime.json").write_text(json.dumps(runtime, indent=2) + "\n")
    metadata = {
        "run_id": run_id, "timestamp": datetime.now(UTC).isoformat(), "runner": args.runner,
        "model_provider": args.provider, "requested_model_id": args.model,
        "returned_model_id": None, "model_snapshot": None, "temperature": None,
        "temperature_requested": 0.5, "temperature_effective": None,
        "sampling_control": "unsupported_by_cli", "seed": None,
        "seed_requested": None, "seed_effective": None,
        "context_limit": 65536, "max_steps": 40, "timeout_minutes": 20,
        "reasoning_setting": None, "max_output_tokens": None, "task_id": args.task_id,
        "task_hash": digest(task), "split": "pilot", "skill_id": args.skill_id,
        "skill_version": args.skill_version, "skill_hash": digest(skill), "tool_schema_version": 1,
        "verifier_hash": digest(verifier), "harness_git_commit": git_commit(args.root),
        "container_image": None,
        "outcome_category": outcome, "partial_score": summary["partial_score"],
        "legacy_outcome_category": outcome, "outcome_flags": flags,
        "verifier_check_count": summary["check_count"], "verifier_checks_passed": summary["checks_passed"],
        "finish_reason": runtime["finish_reason"], "finish_reason_available": runtime["finish_reason_available"],
        "process_timed_out": process.get("timed_out", False),
        "run_cohort": args.run_cohort,
        "repetition": args.repetition,
    }
    (args.run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")


if __name__ == "__main__":
    main()
