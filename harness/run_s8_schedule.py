#!/usr/bin/env python3
"""Resume the frozen S8 schedule in its single, immutable interleaved order."""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def complete(run_dir: Path) -> bool:
    return all((run_dir / name).is_file() for name in ("metadata.json", "process.json", "verifier.json"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, default=ROOT / "config" / "s8_dev_validate_schedule.tsv")
    parser.add_argument("--output-root", type=Path, default=ROOT / "data" / "s8_runs")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("refusing to execute without --execute")
    with args.schedule.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 192:
        raise SystemExit(f"frozen S8 schedule must have 192 rows, got {len(rows)}")
    for row in rows:
        run_dir = args.output_root / row["run_id"]
        if complete(run_dir):
            continue
        command = [sys.executable, str(ROOT / "harness" / "run_s8.py"), row["task_id"], row["condition"], row["repetition"], row["run_id"], "--schedule-seed", row["schedule_seed"], "--request-seed", row["request_seed"], "--output-root", str(args.output_root), "--execute"]
        subprocess.run(command, check=False)
        if not complete(run_dir):
            raise SystemExit(f"entry did not leave complete artifacts: {row['run_id']}")
        subprocess.run([sys.executable, str(ROOT / "harness" / "update_status.py")], check=True)


if __name__ == "__main__":
    main()
