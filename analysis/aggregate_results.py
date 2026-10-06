"""Print model-level aggregates for completed benchmark runs only."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "results" / "run_summary.csv"
OUTPUT = ROOT / "data" / "results" / "model_aggregate.csv"


def main() -> None:
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    with INPUT.open() as handle:
        for row in csv.DictReader(handle):
            if row["status"] == "success":
                groups[(row["task_id"], row["model"])].append(row)

    rows = []
    for (task_id, model), runs in sorted(groups.items()):
        rows.append({
            "task_id": task_id,
            "model": model,
            "completed_runs": len(runs),
            "success_rate": sum(row["status"] == "success" for row in runs) / len(runs),
            "mean_command_executions": round(sum(int(row["command_executions"]) for row in runs) / len(runs), 2),
            "mean_trajectory_events": round(sum(int(row["trajectory_events"]) for row in runs) / len(runs), 2),
        })

    with OUTPUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
