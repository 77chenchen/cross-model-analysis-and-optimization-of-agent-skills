#!/usr/bin/env python3
"""Run the locked uncontrolled GPT reference-anchor schedule in TSV order."""
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
    return (run_dir / "metadata.json").is_file() and (run_dir / "verifier.json").is_file()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schedule", type=Path)
    parser.add_argument("--output-root", type=Path, default=ROOT / "data" / "s7_runs")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("refusing to execute a formal schedule without --execute")
    with args.schedule.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows or any(row.get("model") != "gpt-5.6-sol" for row in rows):
        raise SystemExit("this adapter accepts only the locked GPT reference-anchor schedule")
    for row in rows:
        run_dir = args.output_root / row["run_id"]
        if complete(run_dir):
            continue
        command = [sys.executable, str(ROOT / "harness" / "run_codex_formal.py"), row["task_id"], row["condition"], row["repetition"], row["run_id"], "--schedule-seed", row["schedule_seed"], "--output-root", str(args.output_root), "--execute"]
        subprocess.run(command, check=False)
        if not complete(run_dir):
            raise SystemExit(f"schedule entry did not leave complete artifacts: {row['run_id']}")
        subprocess.run([sys.executable, str(ROOT / "harness" / "update_status.py")], check=True)


if __name__ == "__main__":
    main()
