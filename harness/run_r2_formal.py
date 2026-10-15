#!/usr/bin/env python3
"""Execute exactly one locked S7 direct-provider schedule entry.

This program performs no work unless invoked with ``--execute``.  It is not a
batch runner: schedule order and resume decisions belong to the locked S7
orchestrator so an interrupted batch cannot be silently reshuffled.
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

try:
    from .outcomes import outcome_flags, python_compile_errors, verifier_summary
    from .record_run import digest, git_commit, source_unchanged
    from .s7_protocol import OPEN_MODELS, ROOT, prompt_for, request_seed, sha256_text, skill_id_for, split_for
except ImportError:
    from outcomes import outcome_flags, python_compile_errors, verifier_summary
    from record_run import digest, git_commit, source_unchanged
    from s7_protocol import OPEN_MODELS, ROOT, prompt_for, request_seed, sha256_text, skill_id_for, split_for


VERIFIER_TIMEOUT_SECONDS = 1200


def outcome(runtime: dict, process: dict, verifier: dict, compile_errors: list[str]) -> str:
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
    command = [sys.executable, str(ROOT / "verifiers" / "contract_verifier.py"), task_id, str(workspace)]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False, timeout=VERIFIER_TIMEOUT_SECONDS)
        try:
            result = json.loads(completed.stdout)
        except json.JSONDecodeError:
            result = {"passed": False, "checks": {}, "verifier_stdout": completed.stdout, "verifier_stderr": completed.stderr}
        return result
    except subprocess.TimeoutExpired as error:
        return {"passed": False, "checks": {}, "verifier_stdout": error.stdout or "", "verifier_stderr": error.stderr or "", "verifier_timeout": True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id")
    parser.add_argument("model")
    parser.add_argument("condition", choices=("C0", "C1", "v1", "l3b"))
    parser.add_argument("repetition", type=int)
    parser.add_argument("run_id")
    parser.add_argument("--schedule-seed", required=True, type=int)
    parser.add_argument("--request-seed", type=int)
    parser.add_argument("--output-root", type=Path, default=ROOT / "data" / "s7_runs")
    parser.add_argument("--worker-concurrency", type=int, default=1)
    parser.add_argument("--execute", action="store_true", help="required guard before a model request")
    args = parser.parse_args()

    if not args.execute:
        raise SystemExit("refusing to execute without --execute")
    if args.model == "gpt-5.6-sol":
        raise SystemExit("GPT reference-anchor execution uses its separately locked Codex adapter")
    if args.model not in OPEN_MODELS:
        raise SystemExit("model is not a locked direct S7 model")
    split = split_for(args.task_id)
    if args.condition == "v1" and (args.model != "qwen3.5:9b" or split != "test_in"):
        raise SystemExit("v1 is locked to qwen3.5:9b test_in only")
    if args.condition == "l3b" and args.model != "qwen3.5:9b":
        raise SystemExit("L3b is locked to qwen3.5:9b only")
    template = ROOT / "tasks" / split / args.task_id / "template"
    if not template.is_dir():
        raise SystemExit("frozen formal task template is missing")
    run_dir = args.output_root / args.run_id
    if (run_dir / "metadata.json").exists():
        print(run_dir)
        return
    workspace = run_dir / "workspace"
    shutil.copytree(template, workspace)
    prompt, skill_version, skill_text = prompt_for(args.condition, args.task_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = run_dir / "prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    provider_seed = args.request_seed if args.request_seed is not None else request_seed(args.run_id)
    agent = [sys.executable, str(ROOT / "harness" / "r2_agent.py"), "--workspace", str(workspace), "--output", str(run_dir), "--model", args.model, "--prompt-file", str(prompt_path), "--temperature", "0.5", "--max-steps", "40", "--context-limit", "65536", "--timeout-seconds", "1200"]
    agent.extend(["--seed", str(provider_seed)])
    if args.condition == "l3b":
        agent.extend(["--l3b-trigger-at", "32"])
    login_command = "exec " + " ".join(shlex.quote(part) for part in agent)
    subprocess.run([sys.executable, str(ROOT / "harness" / "run_with_timeout.py"), "--timeout-seconds", "1200", "--stdout", str(run_dir / "agent_stdout.log"), "--outcome", str(run_dir / "process.json"), "--", "zsh", "-lic", login_command], check=False)
    result = verifier_result(args.task_id, workspace)
    result["summary"] = verifier_summary(result)
    (run_dir / "verifier.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    runtime_path = run_dir / "runtime_r2.json"
    runtime = json.loads(runtime_path.read_text(encoding="utf-8")) if runtime_path.exists() else {"provider_error": "r2 process did not produce runtime"}
    process_path = run_dir / "process.json"
    process = json.loads(process_path.read_text(encoding="utf-8")) if process_path.exists() else {"timed_out": False, "returncode": 1}
    compile_errors = python_compile_errors(workspace)
    events = (run_dir / "events.jsonl").read_text(encoding="utf-8") if (run_dir / "events.jsonl").exists() else ""
    final = (run_dir / "final.md").read_text(encoding="utf-8") if (run_dir / "final.md").exists() else ""
    flags = outcome_flags(process, events, final, result, compile_errors, source_unchanged(template, workspace))
    flags.update({"timeout": bool(flags["timeout"] or runtime.get("deadline_exceeded") or result.get("verifier_timeout")), "context_overflow": bool(flags["context_overflow"] or runtime.get("context_budget_exceeded")), "provider_error": bool(flags["provider_error"] or runtime.get("provider_error")), "max_steps_reached": bool(runtime.get("max_steps_reached")), "verifier_timeout": bool(result.get("verifier_timeout"))})
    result_summary = result["summary"]
    semantic_skill_hash = sha256_text(skill_text) if skill_text else sha256_text("S7:C0:no-skill")
    sampling = runtime.get("sampling") or {}
    metadata = {
        "run_id": args.run_id, "timestamp": datetime.now(UTC).isoformat(), "runner": "r2-direct-chat-completions", "runner_version": "r2-s7-formal-patch-1", "model_provider": "soclaas", "requested_model_id": args.model, "returned_model_id": runtime.get("returned_model_id"), "model_snapshot": None,
        "temperature": 0.5, "temperature_requested": 0.5, "temperature_effective": 0.5 if runtime.get("response_count", 0) else None, "sampling_control": "supported" if runtime.get("response_count", 0) else "unknown", "sampling_parameter_echo": {"temperature": None, "seed": sampling.get("seed_provider_echo")}, "seed": provider_seed, "seed_requested": provider_seed, "seed_effective": provider_seed if sampling.get("seed_accepted_by_transport") else None,
        "context_limit": 65536, "max_steps": 40, "timeout_minutes": 20, "reasoning_setting": None, "max_output_tokens": None, "task_id": args.task_id, "task_hash": digest(template), "split": split, "skill_id": skill_id_for(args.task_id), "skill_version": skill_version, "skill_hash": semantic_skill_hash, "condition": args.condition, "prompt_hash": sha256_text(prompt), "schedule_seed": args.schedule_seed,
        "tool_schema_version": 2, "verifier_hash": digest(ROOT / "verifiers" / "contract_verifier.py"), "harness_git_commit": git_commit(ROOT), "container_image": None, "outcome_category": outcome(runtime, process, result, compile_errors), "legacy_outcome_category": outcome(runtime, process, result, compile_errors), "outcome_flags": flags, "partial_score": result_summary["partial_score"], "verifier_check_count": result_summary["check_count"], "verifier_checks_passed": result_summary["checks_passed"], "verifier_timeout": bool(result.get("verifier_timeout")), "verifier_timeout_seconds": VERIFIER_TIMEOUT_SECONDS,
        "finish_reason": runtime.get("finish_reason"), "finish_reason_available": runtime.get("finish_reason") is not None, "process_timed_out": process.get("timed_out", False), "run_cohort": "s7", "repetition": args.repetition, "r2_response_count": runtime.get("response_count", 0), "r2_tool_call_count": runtime.get("tool_call_count", 0), "r2_tool_parse": runtime.get("tool_parse", {}), "r2_usage": runtime.get("usage", {}), "r2_process_returncode": process.get("returncode", 1), "request_retry_events": runtime.get("retry_events", []), "request_retry_count": len(runtime.get("retry_events", [])), "l3b_trigger_at": 32 if args.condition == "l3b" else None, "l3b_triggered": runtime.get("l3b_triggered", False), "replacement_of": None, "worker_concurrency": args.worker_concurrency,
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(run_dir)


if __name__ == "__main__":
    main()
