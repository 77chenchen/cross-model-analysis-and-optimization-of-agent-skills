#!/usr/bin/env python3
"""Create one fresh pilot workspace and execute it with the r2 direct runner.

Only `tasks/pilot` is addressable here.  This makes test splits unreachable by
this entry point until a separately reviewed formal runner exists.
"""
from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

from outcomes import outcome_flags, python_compile_errors, verifier_summary
from record_run import digest, git_commit, source_unchanged

ROOT = Path(__file__).resolve().parent.parent


def prompt_for(skill_text: str) -> str:
    return f"""You have been supplied the following benchmark skill protocol. Follow it as operational guidance, then complete the task in task.md. You have at most 40 tool steps.

--- skill protocol begin ---
{skill_text}
--- skill protocol end ---

Read task.md, fix the implementation, and validate your result. Do not create or modify benchmark-owned verifier files."""


def r2_outcome(runtime: dict, process: dict, verifier: dict, compile_errors: list[str]) -> str:
    if process.get("timed_out") or runtime.get("deadline_exceeded"):
        return "timeout"
    if runtime.get("context_budget_exceeded"):
        return "context_overflow"
    if runtime.get("provider_error"):
        return "provider_error"
    if not (runtime.get("final_text") or "").strip():
        return "empty_termination"
    if compile_errors:
        return "compile_error"
    return "pass" if verifier.get("passed") is True else "verifier_fail"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id")
    parser.add_argument("model")
    parser.add_argument("--skill-version", choices=("v0", "v1"), default="v0")
    parser.add_argument("--run-cohort", default="r2-pilot")
    parser.add_argument("--split", choices=("pilot", "dev"), default="pilot")
    parser.add_argument("--repetition", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--output-root", type=Path, default=ROOT / "data/r2_runs")
    args = parser.parse_args()

    template = ROOT / "tasks/pilot" / args.task_id / "template"
    verifier = ROOT / "verifiers" / f"{args.task_id}.py"
    if not template.is_dir() or not verifier.is_file():
        raise SystemExit("pilot task and verifier are required; formal test tasks are not supported")
    skill_id = args.task_id[6:7].upper()
    skill = ROOT / "skills" / skill_id / f"{args.skill_version}.md"
    if not skill.is_file():
        raise SystemExit("skill protocol missing")
    safe_model = "".join(char if char.isalnum() or char in "._-" else "_" for char in args.model)
    run_dir = args.output_root / f"{args.task_id}__{safe_model}__{args.skill_version}__{datetime.now(UTC):%Y%m%dT%H%M%SZ}__{uuid.uuid4().hex[:10]}"
    workspace = run_dir / "workspace"
    shutil.copytree(template, workspace)
    prompt_path = run_dir / "prompt.md"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt_for(skill.read_text(encoding="utf-8")), encoding="utf-8")

    command = [sys.executable, str(ROOT / "harness/r2_agent.py"), "--workspace", str(workspace), "--output", str(run_dir), "--model", args.model, "--prompt-file", str(prompt_path), "--temperature", "0.5", "--max-steps", "40", "--context-limit", "65536", "--timeout-seconds", "1200"]
    if args.seed is not None:
        command.extend(["--seed", str(args.seed)])
    # A login shell inherits SOCLAAS_API_KEY without serializing it into code,
    # logs, command metadata, or artifacts.
    login_command = "exec " + " ".join(shlex.quote(part) for part in command)
    process = subprocess.run([sys.executable, str(ROOT / "harness/run_with_timeout.py"), "--timeout-seconds", "1200", "--stdout", str(run_dir / "agent_stdout.log"), "--outcome", str(run_dir / "process.json"), "--", "zsh", "-lic", login_command], check=False)
    verifier_process = subprocess.run([sys.executable, str(verifier), str(workspace)], capture_output=True, text=True, check=False)
    try:
        verifier_result = json.loads(verifier_process.stdout)
    except json.JSONDecodeError:
        verifier_result = {"passed": False, "checks": {}, "verifier_stdout": verifier_process.stdout, "verifier_stderr": verifier_process.stderr}
    summary = verifier_summary(verifier_result)
    verifier_result["summary"] = summary
    (run_dir / "verifier.json").write_text(json.dumps(verifier_result, indent=2) + "\n", encoding="utf-8")
    runtime_path = run_dir / "runtime_r2.json"
    runtime = json.loads(runtime_path.read_text(encoding="utf-8")) if runtime_path.exists() else {"provider_error": "r2 process did not produce runtime"}
    compile_errors = python_compile_errors(workspace)
    events_text = (run_dir / "events.jsonl").read_text(encoding="utf-8") if (run_dir / "events.jsonl").exists() else ""
    final_text = (run_dir / "final.md").read_text(encoding="utf-8") if (run_dir / "final.md").exists() else ""
    process_data = json.loads((run_dir / "process.json").read_text(encoding="utf-8"))
    flags = outcome_flags(process_data, events_text, final_text, verifier_result, compile_errors, source_unchanged(template, workspace))
    flags["timeout"] = bool(flags["timeout"] or runtime.get("deadline_exceeded"))
    flags["context_overflow"] = bool(flags["context_overflow"] or runtime.get("context_budget_exceeded"))
    flags["provider_error"] = bool(flags["provider_error"] or runtime.get("provider_error"))
    outcome = r2_outcome(runtime, process_data, verifier_result, compile_errors)
    sampling = runtime.get("sampling") or {}
    metadata = {
        "run_id": run_dir.name, "timestamp": datetime.now(UTC).isoformat(), "runner": "r2-direct-chat-completions", "runner_version": "r2",
        "model_provider": "soclaas", "requested_model_id": args.model, "returned_model_id": runtime.get("returned_model_id"), "model_snapshot": None,
        "temperature": 0.5, "temperature_requested": 0.5, "temperature_effective": 0.5 if runtime.get("response_count", 0) else None,
        "sampling_control": "supported" if runtime.get("response_count", 0) else "unknown", "sampling_parameter_echo": {"temperature": None, "seed": sampling.get("seed_provider_echo")},
        "seed": args.seed, "seed_requested": args.seed, "seed_effective": args.seed if sampling.get("seed_accepted_by_transport") else None,
        "context_limit": 65536, "max_steps": 40, "timeout_minutes": 20, "reasoning_setting": None, "max_output_tokens": None,
        "task_id": args.task_id, "task_hash": digest(template), "split": args.split, "skill_id": skill_id, "skill_version": args.skill_version, "skill_hash": digest(skill), "tool_schema_version": 2,
        "verifier_hash": digest(verifier), "harness_git_commit": git_commit(ROOT), "container_image": None,
        "outcome_category": outcome, "legacy_outcome_category": outcome, "outcome_flags": flags, "partial_score": summary["partial_score"],
        "verifier_check_count": summary["check_count"], "verifier_checks_passed": summary["checks_passed"], "finish_reason": runtime.get("finish_reason"),
        "finish_reason_available": runtime.get("finish_reason") is not None, "process_timed_out": process_data.get("timed_out", False), "run_cohort": args.run_cohort,
        "repetition": args.repetition, "r2_response_count": runtime.get("response_count", 0), "r2_tool_call_count": runtime.get("tool_call_count", 0),
        "r2_tool_parse": runtime.get("tool_parse", {}), "r2_usage": runtime.get("usage", {}), "r2_process_returncode": process.returncode,
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(run_dir)


if __name__ == "__main__":
    main()
