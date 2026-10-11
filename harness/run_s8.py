#!/usr/bin/env python3
"""Execute one frozen S8 dev-only schedule entry.

This wrapper intentionally calls the unchanged r2 agent.  It cannot address
formal tasks and refuses execution unless the checked-in schedule and prompt
manifest agree with the requested row.
"""
from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from outcomes import outcome_flags, python_compile_errors, verifier_summary
from record_run import digest, git_commit, source_unchanged
from s8_protocol import CONDITIONS, MODEL, TASKS, prompt_for, request_seed, sha256_text, stable_run_id

ROOT = Path(__file__).resolve().parent.parent
VERIFIER_TIMEOUT_SECONDS = 1200


def legacy_outcome(runtime: dict, process: dict, verifier: dict, compile_errors: list[str]) -> str:
    if process.get("timed_out") or runtime.get("deadline_exceeded") or verifier.get("verifier_timeout"):
        return "timeout"
    if runtime.get("context_budget_exceeded"):
        return "context_overflow"
    if runtime.get("provider_error"):
        return "provider_error"
    if runtime.get("max_steps_reached"):
        return "max_steps_reached"
    if not (runtime.get("final_text") or "").strip():
        return "empty_termination"
    if compile_errors:
        return "compile_error"
    return "pass" if verifier.get("passed") is True else "verifier_fail"


def verifier_result(task_id: str, workspace: Path) -> dict:
    verifier = ROOT / "verifiers" / f"{task_id}.py"
    try:
        completed = subprocess.run([sys.executable, str(verifier), str(workspace)], capture_output=True, text=True, check=False, timeout=VERIFIER_TIMEOUT_SECONDS)
        try:
            return json.loads(completed.stdout)
        except json.JSONDecodeError:
            return {"passed": False, "checks": {}, "verifier_stdout": completed.stdout, "verifier_stderr": completed.stderr}
    except subprocess.TimeoutExpired as error:
        return {"passed": False, "checks": {}, "verifier_stdout": error.stdout or "", "verifier_stderr": error.stderr or "", "verifier_timeout": True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id", choices=TASKS)
    parser.add_argument("condition", choices=CONDITIONS)
    parser.add_argument("repetition", type=int, choices=range(1, 9))
    parser.add_argument("run_id")
    parser.add_argument("--schedule-seed", required=True, type=int)
    parser.add_argument("--request-seed", required=True, type=int)
    parser.add_argument("--output-root", type=Path, default=ROOT / "data" / "s8_runs")
    parser.add_argument("--execute", action="store_true", help="required guard before a model request")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("refusing to execute without --execute")
    expected_id = stable_run_id(args.task_id, args.condition, args.repetition)
    if args.run_id != expected_id or args.request_seed != request_seed(expected_id):
        raise SystemExit("run ID or request seed differs from the frozen S8 convention")
    manifest = json.loads((ROOT / "config" / "s8_prompt_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("protocol") != "s8-dev-only-v1" or manifest.get("schedule_seed") != args.schedule_seed:
        raise SystemExit("S8 prompt manifest is absent or does not match frozen schedule")
    prompt, semantic_condition, guidance = prompt_for(args.condition, args.task_id)
    prompt_entry = manifest["prompts"].get(f"{args.task_id}/{args.condition}")
    if not prompt_entry or prompt_entry.get("prompt_sha256") != sha256_text(prompt):
        raise SystemExit("serialized prompt hash differs from frozen prompt manifest")
    template = ROOT / "tasks" / "pilot" / args.task_id / "template"
    run_dir = args.output_root / args.run_id
    if (run_dir / "metadata.json").is_file():
        print(run_dir); return
    workspace = run_dir / "workspace"
    run_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template, workspace)
    (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    agent = [sys.executable, str(ROOT / "harness" / "r2_agent.py"), "--workspace", str(workspace), "--output", str(run_dir), "--model", MODEL, "--prompt-file", str(run_dir / "prompt.md"), "--temperature", "0.5", "--seed", str(args.request_seed), "--max-steps", "40", "--context-limit", "65536", "--timeout-seconds", "1200"]
    login_command = "exec " + " ".join(shlex.quote(part) for part in agent)
    subprocess.run([sys.executable, str(ROOT / "harness" / "run_with_timeout.py"), "--timeout-seconds", "1200", "--stdout", str(run_dir / "agent_stdout.log"), "--outcome", str(run_dir / "process.json"), "--", "zsh", "-lic", login_command], check=False)
    result = verifier_result(args.task_id, workspace)
    result["summary"] = verifier_summary(result)
    (run_dir / "verifier.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    runtime_path = run_dir / "runtime_r2.json"
    runtime = json.loads(runtime_path.read_text(encoding="utf-8")) if runtime_path.is_file() else {"provider_error": "r2 process did not produce runtime"}
    process_path = run_dir / "process.json"
    process = json.loads(process_path.read_text(encoding="utf-8")) if process_path.is_file() else {"timed_out": False, "returncode": 1}
    compile_errors = python_compile_errors(workspace)
    events = (run_dir / "events.jsonl").read_text(encoding="utf-8") if (run_dir / "events.jsonl").is_file() else ""
    final = (run_dir / "final.md").read_text(encoding="utf-8") if (run_dir / "final.md").is_file() else ""
    flags = outcome_flags(process, events, final, result, compile_errors, source_unchanged(template, workspace))
    flags.update({"timeout": bool(flags["timeout"] or runtime.get("deadline_exceeded") or result.get("verifier_timeout")), "context_overflow": bool(flags["context_overflow"] or runtime.get("context_budget_exceeded")), "provider_error": bool(flags["provider_error"] or runtime.get("provider_error")), "max_steps_reached": bool(runtime.get("max_steps_reached")), "verifier_timeout": bool(result.get("verifier_timeout"))})
    sampling = runtime.get("sampling") or {}
    metadata = {
        "run_id": args.run_id, "timestamp": datetime.now(UTC).isoformat(), "runner": "r2-direct-chat-completions", "runner_version": "r2-s8-wrapper-1", "runner_base_version": "r2-s7-formal-patch-1", "model_provider": "soclaas", "requested_model_id": MODEL, "returned_model_id": runtime.get("returned_model_id"),
        "temperature": 0.5, "temperature_requested": 0.5, "temperature_effective": 0.5 if runtime.get("response_count", 0) else None, "sampling_control": "supported" if runtime.get("response_count", 0) else "unknown", "sampling_parameter_echo": {"temperature": None, "seed": sampling.get("seed_provider_echo")}, "seed": args.request_seed, "seed_requested": args.request_seed, "seed_effective": args.request_seed if sampling.get("seed_accepted_by_transport") else None,
        "context_limit": 65536, "max_steps": 40, "timeout_minutes": 20, "task_id": args.task_id, "task_hash": digest(template), "split": "dev_validate", "skill_id": args.task_id[6].upper(), "skill_version": "v0" if args.condition == "C1" else "s8-candidate", "skill_hash": sha256_text(guidance), "condition": args.condition, "semantic_condition": semantic_condition, "prompt_hash": sha256_text(prompt), "schedule_seed": args.schedule_seed, "tool_schema_version": 2,
        "verifier_hash": digest(ROOT / "verifiers" / f"{args.task_id}.py"), "harness_git_commit": git_commit(ROOT), "outcome_category": legacy_outcome(runtime, process, result, compile_errors), "legacy_outcome_category": legacy_outcome(runtime, process, result, compile_errors), "outcome_flags": flags, "partial_score": result["summary"]["partial_score"], "verifier_check_count": result["summary"]["check_count"], "verifier_checks_passed": result["summary"]["checks_passed"], "verifier_timeout": bool(result.get("verifier_timeout")), "verifier_timeout_seconds": VERIFIER_TIMEOUT_SECONDS,
        "finish_reason": runtime.get("finish_reason"), "finish_reason_available": runtime.get("finish_reason") is not None, "process_timed_out": process.get("timed_out", False), "run_cohort": "s8-dev-only", "repetition": args.repetition, "r2_response_count": runtime.get("response_count", 0), "r2_tool_call_count": runtime.get("tool_call_count", 0), "r2_tool_parse": runtime.get("tool_parse", {}), "r2_usage": runtime.get("usage", {}), "r2_process_returncode": process.get("returncode", 1), "request_retry_events": runtime.get("retry_events", []), "request_retry_count": len(runtime.get("retry_events", [])), "worker_concurrency": 1,
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(run_dir)


if __name__ == "__main__":
    main()
