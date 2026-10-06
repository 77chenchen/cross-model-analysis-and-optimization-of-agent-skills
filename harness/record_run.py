#!/usr/bin/env python3
"""Write reproducible pilot metadata and a conservative normalized trajectory."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path


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


def normalize(raw: Path, output: Path, run_id: str) -> None:
    with raw.open() as src, output.open("w") as dst:
        for sequence, line in enumerate(src):
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            item = event.get("item", {}) if isinstance(event.get("item"), dict) else {}
            item_type = str(item.get("type", ""))
            raw_type = str(event.get("type", ""))
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
            }
            dst.write(json.dumps(normalized, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--skill-id", choices=("A", "B", "C"), required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--trajectory", type=Path, required=True)
    args = parser.parse_args()
    task = args.root / "tasks" / "pilot" / args.task_id / "template"
    verifier = args.root / "verifiers" / f"{args.task_id}.py"
    skill = args.root / "skills" / args.skill_id / "v0.md"
    run_id = args.run_dir.name
    metadata = {
        "run_id": run_id, "timestamp": datetime.now(UTC).isoformat(),
        "model_provider": args.provider, "requested_model_id": args.model,
        "returned_model_id": None, "model_snapshot": None, "temperature": 0,
        "seed": None, "context_limit": 65536, "max_steps": 40, "timeout_minutes": 20,
        "reasoning_setting": None, "max_output_tokens": None, "task_id": args.task_id,
        "task_hash": digest(task), "split": "pilot", "skill_id": args.skill_id,
        "skill_version": "v0", "skill_hash": digest(skill), "tool_schema_version": 1,
        "verifier_hash": digest(verifier), "harness_git_commit": git_commit(args.root),
        "container_image": None,
    }
    (args.run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    normalize(args.trajectory, args.run_dir / "actions.jsonl", run_id)


if __name__ == "__main__":
    main()
