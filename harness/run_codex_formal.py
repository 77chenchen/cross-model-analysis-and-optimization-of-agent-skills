#!/usr/bin/env python3
"""One guarded, uncontrolled Codex-CLI reference-anchor execution for S7."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

try:
    from .outcomes import outcome_flags, python_compile_errors, verifier_summary
    from .record_run import digest, git_commit
    from .s7_protocol import ROOT, prompt_for, sha256_text, skill_id_for, split_for
except ImportError:
    from outcomes import outcome_flags, python_compile_errors, verifier_summary
    from record_run import digest, git_commit
    from s7_protocol import ROOT, prompt_for, sha256_text, skill_id_for, split_for


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id")
    parser.add_argument("condition", choices=("C0", "C1"))
    parser.add_argument("repetition", type=int)
    parser.add_argument("run_id")
    parser.add_argument("--schedule-seed", required=True, type=int)
    parser.add_argument("--output-root", type=Path, default=ROOT / "data" / "s7_runs")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("refusing to execute without --execute")
    split = split_for(args.task_id)
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
    (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    # Codex CLI owns sampling and tool execution. No unsupported sampling flag
    # is sent; its stdout JSONL is retained as the raw anchor trajectory.
    completed = subprocess.run(["codex", "exec", "--json", "--skip-git-repo-check", prompt], cwd=workspace, capture_output=True, text=True, check=False, timeout=1200)
    (run_dir / "codex_stdout.jsonl").write_text(completed.stdout, encoding="utf-8")
    (run_dir / "codex_stderr.log").write_text(completed.stderr, encoding="utf-8")
    try:
        verified = subprocess.run(["python3", str(ROOT / "verifiers" / "contract_verifier.py"), args.task_id, str(workspace)], capture_output=True, text=True, check=False, timeout=1200)
        try:
            verifier = json.loads(verified.stdout)
        except json.JSONDecodeError:
            verifier = {"passed": False, "checks": {}, "verifier_stdout": verified.stdout, "verifier_stderr": verified.stderr}
    except subprocess.TimeoutExpired as error:
        verifier = {"passed": False, "checks": {}, "verifier_stdout": error.stdout or "", "verifier_stderr": error.stderr or "", "verifier_timeout": True}
    verifier["summary"] = verifier_summary(verifier)
    (run_dir / "verifier.json").write_text(json.dumps(verifier, indent=2) + "\n", encoding="utf-8")
    compile_errors = python_compile_errors(workspace)
    final_empty = not completed.stdout.strip()
    flags = outcome_flags({"timed_out": False, "returncode": completed.returncode}, completed.stdout, completed.stdout, verifier, compile_errors, False)
    flags.update({"final_empty": final_empty, "verifier_timeout": bool(verifier.get("verifier_timeout")), "timeout": bool(verifier.get("verifier_timeout"))})
    if verifier.get("verifier_timeout"):
        run_outcome = "timeout"
    elif completed.returncode != 0:
        run_outcome = "provider_error"
    elif compile_errors:
        run_outcome = "compile_error"
    else:
        run_outcome = "pass" if verifier.get("passed") else "verifier_fail"
    metadata = {
        "run_id": args.run_id, "timestamp": datetime.now(UTC).isoformat(), "runner": "codex-cli", "runner_version": "s7-codex-reference-anchor-1", "model_provider": "codex_chatgpt", "requested_model_id": "gpt-5.6-sol", "returned_model_id": None, "model_snapshot": None,
        "temperature": None, "temperature_requested": None, "temperature_effective": None, "sampling_control": "uncontrolled_reference_anchor", "sampling_parameter_echo": None, "seed": None, "seed_requested": None, "seed_effective": None,
        "context_limit": 65536, "max_steps": 40, "timeout_minutes": 20, "reasoning_setting": None, "max_output_tokens": None, "task_id": args.task_id, "task_hash": digest(template), "split": split, "skill_id": skill_id_for(args.task_id), "skill_version": skill_version, "skill_hash": sha256_text(skill_text) if skill_text else sha256_text("S7:C0:no-skill"), "condition": args.condition, "prompt_hash": sha256_text(prompt), "schedule_seed": args.schedule_seed,
        "tool_schema_version": 2, "verifier_hash": digest(ROOT / "verifiers" / "contract_verifier.py"), "harness_git_commit": git_commit(ROOT), "container_image": None, "outcome_category": run_outcome, "legacy_outcome_category": run_outcome, "outcome_flags": flags, "partial_score": verifier["summary"]["partial_score"], "verifier_check_count": verifier["summary"]["check_count"], "verifier_checks_passed": verifier["summary"]["checks_passed"], "verifier_timeout": bool(verifier.get("verifier_timeout")), "verifier_timeout_seconds": 1200, "codex_returncode": completed.returncode, "worker_concurrency": 1,
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(run_dir)


if __name__ == "__main__":
    main()
