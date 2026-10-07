#!/usr/bin/env python3
"""Run a command in a new process group and terminate the group on timeout."""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
from datetime import UTC, datetime
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-seconds", type=int, required=True)
    parser.add_argument("--stdout", type=Path, required=True)
    parser.add_argument("--outcome", type=Path, required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        raise SystemExit("command required after --")
    started = datetime.now(UTC).isoformat()
    timed_out = False
    with args.stdout.open("w") as output:
        process = subprocess.Popen(command, stdout=output, start_new_session=True)
        try:
            returncode = process.wait(timeout=args.timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                returncode = process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                returncode = process.wait()
    args.outcome.write_text(json.dumps({"started_at": started, "finished_at": datetime.now(UTC).isoformat(), "timeout_seconds": args.timeout_seconds, "timed_out": timed_out, "returncode": returncode, "command": command}) + "\n")
    return 124 if timed_out else returncode


if __name__ == "__main__":
    raise SystemExit(main())
