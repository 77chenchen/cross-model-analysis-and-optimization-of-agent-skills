#!/usr/bin/env python3
"""Execute one hash-locked S8-b schedule entry with runner r2."""
from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from outcomes import outcome_flags, python_compile_errors, verifier_summary
from record_run import digest, git_commit, source_unchanged
from s8b_protocol import (
    CONDITIONS, MODEL, REPETITIONS, ROOT, SCHEDULE_SEED, TASKS,
    prompt_for, request_seed, sha256_text, stable_run_id,
)


VERIFIER_TIMEOUT_SECONDS = 1200
RUNNER_VERSION = "r2-s8b-wrapper-1"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_execution_lock() -> dict:
    lock_path = ROOT / "config" / "s8b_execution_lock.yaml"
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as error:
        raise SystemExit(f"S8-b execution lock unavailable: {error}")
    if lock.get("protocol") != "s8b-dev-only-v1" or lock.get("total_runs") != 192:
        raise SystemExit("S8-b execution lock identity is invalid")
    for relative, expected in (lock.get("sha256") or {}).items():
        path = ROOT / relative
        if not path.is_file() or file_sha256(path) != expected:
            raise SystemExit(f"S8-b locked asset mismatch: {relative}")
    return lock


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
    command = [
        sys.executable,
        str(ROOT / "verifiers" / "s8b_contract_verifier.py"),
        task_id,
        str(workspace),
    ]
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, check=False,
            timeout=VERIFIER_TIMEOUT_SECONDS,
        )
        try:
            return json.loads(completed.stdout)
        except json.JSONDecodeError:
            return {
                "passed": False,
                "checks": {},
                "verifier_stdout": completed.stdout,
                "verifier_stderr": completed.stderr,
                "verifier_returncode": completed.returncode,
            }
    except subprocess.TimeoutExpired as error:
        return {
            "passed": False,
            "checks": {},
            "verifier_stdout": error.stdout or "",
            "verifier_stderr": error.stderr or "",
            "verifier_timeout": True,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id", choices=TASKS)
    parser.add_argument("condition", choices=CONDITIONS)
    parser.add_argument("repetition", type=int, choices=range(1, REPETITIONS + 1))
    parser.add_argument("run_id")
    parser.add_argument("--schedule-seed", type=int, required=True)
    parser.add_argument("--request-seed", type=int, required=True)
    parser.add_argument("--output-root", type=Path, default=ROOT / "data" / "s8b_runs")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("refusing to execute without --execute")
    verify_execution_lock()
    expected_id = stable_run_id(args.task_id, args.condition, args.repetition)
    if args.run_id != expected_id or args.request_seed != request_seed(expected_id):
        raise SystemExit("run identity or request seed differs from locked convention")
    if args.schedule_seed != SCHEDULE_SEED:
        raise SystemExit("schedule seed differs from locked S8-b protocol")

    manifest = json.loads((ROOT / "config" / "s8b_prompt_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("protocol") != "s8b-dev-only-v1" or manifest.get("schedule_seed") != SCHEDULE_SEED:
        raise SystemExit("prompt manifest does not match locked S8-b protocol")
    prompt, semantic_condition, guidance = prompt_for(args.condition, args.task_id)
    prompt_entry = manifest["prompts"].get(f"{args.task_id}/{args.condition}")
    if not prompt_entry or prompt_entry.get("prompt_sha256") != sha256_text(prompt):
        raise SystemExit("serialized prompt hash differs from locked prompt manifest")

    template = ROOT / "tasks" / "s8b" / args.task_id / "template"
    contract = ROOT / "verifiers" / "s8b_contracts" / f"{args.task_id}.json"
    if digest(template) != manifest["task_tree_hashes"][args.task_id]:
        raise SystemExit("task tree differs from locked prompt manifest")
    if digest(contract) != manifest["contract_hashes"][args.task_id]:
        raise SystemExit("verifier contract differs from locked prompt manifest")

    run_dir = args.output_root / args.run_id
    if all((run_dir / name).is_file() for name in ("metadata.json", "process.json", "verifier.json")):
        print(run_dir)
        return
    if run_dir.exists():
        raise SystemExit(f"partial run directory requires manual audit: {run_dir}")
    workspace = run_dir / "workspace"
    run_dir.mkdir(parents=True)
    shutil.copytree(template, workspace)
    prompt_path = run_dir / "prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")

    agent = [
        sys.executable, str(ROOT / "harness" / "r2_agent.py"),
        "--workspace", str(workspace), "--output", str(run_dir),
        "--model", MODEL, "--prompt-file", str(prompt_path),
        "--temperature", "0.5", "--seed", str(args.request_seed),
        "--max-steps", "40", "--context-limit", "65536",
        "--timeout-seconds", "1200",
    ]
    login_command = "exec " + " ".join(shlex.quote(part) for part in agent)
    subprocess.run([
        sys.executable, str(ROOT / "harness" / "run_with_timeout.py"),
        "--timeout-seconds", "1200", "--stdout", str(run_dir / "agent_stdout.log"),
        "--outcome", str(run_dir / "process.json"), "--",
        "zsh", "-lic", login_command,
    ], check=False)

    result = verifier_result(args.task_id, workspace)
    result["summary"] = verifier_summary(result)
    (run_dir / "verifier.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    runtime_path = run_dir / "runtime_r2.json"
    runtime = json.loads(runtime_path.read_text(encoding="utf-8")) if runtime_path.is_file() else {
        "provider_error": "r2 process did not produce runtime"
    }
    process = json.loads((run_dir / "process.json").read_text(encoding="utf-8"))
    compile_errors = python_compile_errors(workspace)
    events = (run_dir / "events.jsonl").read_text(encoding="utf-8") if (run_dir / "events.jsonl").is_file() else ""
    final = (run_dir / "final.md").read_text(encoding="utf-8") if (run_dir / "final.md").is_file() else ""
    flags = outcome_flags(process, events, final, result, compile_errors, source_unchanged(template, workspace))
    flags.update({
        "timeout": bool(flags["timeout"] or runtime.get("deadline_exceeded") or result.get("verifier_timeout")),
        "context_overflow": bool(flags["context_overflow"] or runtime.get("context_budget_exceeded")),
        "provider_error": bool(flags["provider_error"] or runtime.get("provider_error")),
        "max_steps_reached": bool(runtime.get("max_steps_reached")),
        "verifier_timeout": bool(result.get("verifier_timeout")),
    })
    sampling = runtime.get("sampling") or {}
    outcome = legacy_outcome(runtime, process, result, compile_errors)
    metadata = {
        "run_id": args.run_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "runner": "r2-direct-chat-completions",
        "runner_version": RUNNER_VERSION,
        "runner_base_version": "r2-s7-formal-patch-1",
        "model_provider": "soclaas",
        "requested_model_id": MODEL,
        "returned_model_id": runtime.get("returned_model_id"),
        "temperature": 0.5,
        "temperature_requested": 0.5,
        "temperature_effective": 0.5 if runtime.get("response_count", 0) else None,
        "sampling_control": "supported" if runtime.get("response_count", 0) else "unknown",
        "sampling_parameter_echo": {"temperature": None, "seed": sampling.get("seed_provider_echo")},
        "seed": args.request_seed,
        "seed_requested": args.request_seed,
        "seed_effective": args.request_seed if sampling.get("seed_accepted_by_transport") else None,
        "context_limit": 65536,
        "max_steps": 40,
        "timeout_minutes": 20,
        "task_id": args.task_id,
        "task_hash": digest(template),
        "split": "dev_validate_fresh",
        "skill_id": args.task_id[0].upper(),
        "skill_version": "v0" if args.condition == "C1" else "s8b-candidate",
        "skill_hash": sha256_text(guidance),
        "condition": args.condition,
        "semantic_condition": semantic_condition,
        "prompt_hash": sha256_text(prompt),
        "schedule_seed": args.schedule_seed,
        "tool_schema_version": 2,
        "verifier_hash": digest(ROOT / "verifiers" / "s8b_contract_verifier.py"),
        "verifier_contract_hash": digest(contract),
        "harness_git_commit": git_commit(ROOT),
        "outcome_category": outcome,
        "legacy_outcome_category": outcome,
        "outcome_flags": flags,
        "partial_score": result["summary"]["partial_score"],
        "verifier_check_count": result["summary"]["check_count"],
        "verifier_checks_passed": result["summary"]["checks_passed"],
        "verifier_timeout": bool(result.get("verifier_timeout")),
        "verifier_timeout_seconds": VERIFIER_TIMEOUT_SECONDS,
        "finish_reason": runtime.get("finish_reason"),
        "finish_reason_available": runtime.get("finish_reason") is not None,
        "process_timed_out": process.get("timed_out", False),
        "run_cohort": "s8b-dev-only",
        "repetition": args.repetition,
        "r2_response_count": runtime.get("response_count", 0),
        "r2_tool_call_count": runtime.get("tool_call_count", 0),
        "r2_tool_parse": runtime.get("tool_parse", {}),
        "r2_usage": runtime.get("usage", {}),
        "r2_process_returncode": process.get("returncode", 1),
        "request_retry_events": runtime.get("retry_events", []),
        "request_retry_count": len(runtime.get("retry_events", [])),
        "worker_concurrency": 1,
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(run_dir)


if __name__ == "__main__":
    main()
