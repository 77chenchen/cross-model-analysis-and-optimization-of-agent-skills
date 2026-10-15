#!/usr/bin/env python3
"""Refresh the S8-b Markdown monitor from immutable run artifacts."""
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "data" / "s8b_runs"
SCHEDULE = ROOT / "config" / "s8b_schedule.tsv"
STATUS = ROOT / "S8B_STATUS.md"


def main() -> None:
    with SCHEDULE.open(newline="", encoding="utf-8") as handle:
        schedule = list(csv.DictReader(handle, delimiter="\t"))
    completed = []
    passes = Counter()
    provider_errors = 0
    timeouts = 0
    for row in schedule:
        run_dir = RUNS / row["run_id"]
        if not all((run_dir / name).is_file() for name in ("metadata.json", "process.json", "verifier.json")):
            continue
        metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
        verifier = json.loads((run_dir / "verifier.json").read_text(encoding="utf-8"))
        completed.append(row)
        if verifier.get("passed") is True:
            passes[row["condition"]] += 1
        flags = metadata.get("outcome_flags") or {}
        provider_errors += bool(flags.get("provider_error"))
        timeouts += bool(flags.get("timeout"))
    count = len(completed)
    next_row = schedule[count] if count < len(schedule) else None
    state = "complete; analysis pending" if count == len(schedule) else ("running" if count else "locked; ready")
    condition_counts = Counter(row["condition"] for row in completed)
    lines = [
        "# S8-b status monitor",
        "",
        f"Last updated: {datetime.now(ZoneInfo('Asia/Singapore')).isoformat(timespec='seconds')}",
        "",
        "## Current state",
        "",
        f"**{state}.**",
        "",
        "| Item | Planned | Completed | Remaining |",
        "|---|---:|---:|---:|",
        f"| qwen3.5:9b S8-b runs | 192 | {count} | {192-count} |",
        "",
        "| Condition | Completed | Verifier pass (monitoring only) |",
        "|---|---:|---:|",
    ]
    for condition in ("C1", "externalized", "imitation", "generic_control"):
        lines.append(f"| {condition} | {condition_counts[condition]} | {passes[condition]} |")
    lines += [
        "",
        f"Provider-error flags: {provider_errors}. Timeout flags: {timeouts}.",
        "",
        f"Next schedule row: `{next_row['position'] + ' / ' + next_row['run_id'] if next_row else 'none'}`.",
        "",
        "Monitoring counts are operational only. Task-paired analysis begins after 192/192.",
        "",
        "## Locked matrix",
        "",
        "`24 fresh tasks × 4 conditions × 2 repetitions = 192 runs`; concurrency is one.",
    ]
    STATUS.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
