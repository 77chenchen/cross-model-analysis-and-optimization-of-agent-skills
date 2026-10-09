#!/usr/bin/env python3
"""Run one locked direct-provider S7 schedule in its immutable TSV order."""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

try:
    from .s7_protocol import ROOT
except ImportError:
    from s7_protocol import ROOT


def complete(run_dir: Path) -> bool:
    """A classified timeout is complete even when the killed agent wrote no runtime."""
    return all((run_dir / name).is_file() for name in ("metadata.json", "process.json", "verifier.json"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schedule", type=Path)
    parser.add_argument("--output-root", type=Path, default=ROOT / "data" / "s7_runs")
    parser.add_argument("--execute", action="store_true", help="required guard before any schedule entry can run")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("refusing to execute a formal schedule without --execute")
    with args.schedule.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows:
        raise SystemExit("empty S7 schedule")
    if rows[0].get("model") == "gpt-5.6-sol":
        raise SystemExit("use run_codex_formal.py for the uncontrolled GPT reference-anchor schedule")
    for row in rows:
        run_dir = args.output_root / row["run_id"]
        if complete(run_dir):
            continue
        command = [sys.executable, str(ROOT / "harness" / "run_r2_formal.py"), row["task_id"], row["model"], row["condition"], row["repetition"], row["run_id"], "--schedule-seed", row["schedule_seed"], "--request-seed", row["request_seed"], "--output-root", str(args.output_root), "--worker-concurrency", "1", "--execute"]
        subprocess.run(command, check=False)
        if not complete(run_dir):
            raise SystemExit(f"schedule entry did not leave complete artifacts: {row['run_id']}")
        subprocess.run([sys.executable, str(ROOT / "harness" / "update_status.py")], check=True)


if __name__ == "__main__":
    main()
