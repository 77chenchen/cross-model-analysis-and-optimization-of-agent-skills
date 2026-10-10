#!/usr/bin/env python3
"""Chain immutable S7 model schedules without changing their run semantics.

This is an operational supervisor, not an S7 runner.  It invokes the frozen
per-model schedule runners one at a time, stops on the first error, and never
edits a schedule or an existing run directory.
"""
from __future__ import annotations

import argparse
import csv
import fcntl
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from .s7_protocol import ROOT
except ImportError:
    from s7_protocol import ROOT


DEFAULT_OUTPUT_ROOT = ROOT / "data" / "s7_runs"
DEFAULT_STATE_DIR = DEFAULT_OUTPUT_ROOT / "_schedule_chain"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_schedule(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    required = {"run_id", "model"}
    if not rows or not required.issubset(rows[0]):
        raise SystemExit(f"invalid or empty S7 schedule: {path}")
    models = {row["model"] for row in rows}
    if len(models) != 1:
        raise SystemExit(f"schedule must contain exactly one model: {path}")
    return rows


def run_complete(run_dir: Path, model: str) -> bool:
    required = ["metadata.json", "verifier.json"]
    if model != "gpt-5.6-sol":
        required.append("process.json")
    return all((run_dir / name).is_file() for name in required)


def schedule_progress(path: Path, output_root: Path) -> tuple[str, int, int]:
    rows = read_schedule(path)
    model = rows[0]["model"]
    completed = sum(run_complete(output_root / row["run_id"], model) for row in rows)
    return model, completed, len(rows)


def write_state(state_path: Path, **fields: object) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"updated_at": utc_now(), **fields}
    temporary = state_path.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(state_path)


def wait_for_pid(pid: int, poll_seconds: int, state_path: Path) -> None:
    while True:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        except PermissionError as exc:
            raise SystemExit(f"cannot monitor PID {pid}: {exc}") from exc
        write_state(state_path, state="waiting_for_existing_scheduler", wait_pid=pid)
        time.sleep(poll_seconds)


def schedule_command(path: Path, model: str, output_root: Path) -> list[str]:
    script = "run_s7_codex_schedule.py" if model == "gpt-5.6-sol" else "run_s7_schedule.py"
    return [
        sys.executable,
        str(ROOT / "harness" / script),
        str(path),
        "--output-root",
        str(output_root),
        "--execute",
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schedules", nargs="+", type=Path, help="remaining immutable schedules in execution order")
    parser.add_argument("--wait-pid", type=int, help="wait for an already-running schedule process")
    parser.add_argument(
        "--barrier-schedule",
        type=Path,
        help="after --wait-pid exits, require this active schedule to be complete; never resume it",
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--state-dir", type=Path, default=DEFAULT_STATE_DIR)
    parser.add_argument("--poll-seconds", type=int, default=15)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("refusing to start the S7 schedule chain without --execute")
    if args.wait_pid and not args.barrier_schedule:
        raise SystemExit("--wait-pid requires --barrier-schedule")
    if args.poll_seconds < 1:
        raise SystemExit("--poll-seconds must be positive")

    args.state_dir.mkdir(parents=True, exist_ok=True)
    lock_path = args.state_dir / "chain.lock"
    state_path = args.state_dir / "state.json"
    with lock_path.open("w", encoding="utf-8") as lock_handle:
        try:
            fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise SystemExit(f"another S7 schedule chain already holds {lock_path}") from exc
        lock_handle.write(f"{os.getpid()}\n")
        lock_handle.flush()

        if args.wait_pid:
            wait_for_pid(args.wait_pid, args.poll_seconds, state_path)
            model, completed, planned = schedule_progress(args.barrier_schedule, args.output_root)
            if completed != planned:
                write_state(
                    state_path,
                    state="stopped_incomplete_barrier",
                    model=model,
                    completed=completed,
                    planned=planned,
                    schedule=str(args.barrier_schedule),
                )
                raise SystemExit(
                    f"existing scheduler exited but barrier is incomplete: {model} {completed}/{planned}; refusing to resume or skip"
                )

        for schedule in args.schedules:
            model, completed, planned = schedule_progress(schedule, args.output_root)
            write_state(
                state_path,
                state="starting" if completed < planned else "already_complete",
                model=model,
                completed=completed,
                planned=planned,
                schedule=str(schedule),
            )
            if completed == planned:
                continue
            command = schedule_command(schedule, model, args.output_root)
            result = subprocess.run(command, check=False)
            model, completed, planned = schedule_progress(schedule, args.output_root)
            if result.returncode != 0 or completed != planned:
                write_state(
                    state_path,
                    state="stopped_schedule_error",
                    model=model,
                    completed=completed,
                    planned=planned,
                    returncode=result.returncode,
                    schedule=str(schedule),
                )
                raise SystemExit(
                    f"schedule stopped: {model} {completed}/{planned}, return code {result.returncode}; refusing to continue"
                )
            write_state(
                state_path,
                state="model_complete",
                model=model,
                completed=completed,
                planned=planned,
                schedule=str(schedule),
            )

        write_state(state_path, state="all_requested_schedules_complete")


if __name__ == "__main__":
    main()
