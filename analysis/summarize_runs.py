"""Create a reproducible run-level summary from raw Codex JSONL trajectories."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "results" / "run_summary.csv"


def classify(run_dir: Path, event_count: int, evaluation: str, runner_log: str) -> str:
    if event_count == 0:
        if "usage limit" in runner_log.lower():
            return "blocked_usage_limit"
        return "incomplete"
    if "OK" in evaluation and "FAILED" not in evaluation:
        return "success"
    return "failed_evaluation"


def main() -> None:
    rows = []
    for run_dir in sorted(path for path in RAW.iterdir() if path.is_dir()):
        match = re.fullmatch(r"(cr_\d+)__(.+)__rep_(\d+)__v(\d+)", run_dir.name)
        if not match:
            continue
        task_id, model, replicate, skill_version = match.groups()
        trajectory = run_dir / "trajectory.jsonl"
        event_count = 0
        commands = 0
        if trajectory.exists():
            for line in trajectory.read_text().splitlines():
                event_count += 1
                event = json.loads(line)
                item = event.get("item", {})
                if event.get("type") == "item.completed" and item.get("type") == "command_execution":
                    commands += 1
        evaluation = (run_dir / "evaluation.txt").read_text() if (run_dir / "evaluation.txt").exists() else ""
        runner_log = (run_dir / "runner.log").read_text() if (run_dir / "runner.log").exists() else ""
        tests = re.search(r"Ran (\d+) tests?", evaluation)
        rows.append({
            "run_id": run_dir.name,
            "task_id": task_id,
            "model": model,
            "replicate": int(replicate),
            "skill_version": f"v{skill_version}",
            "status": classify(run_dir, event_count, evaluation, runner_log),
            "tests_run": int(tests.group(1)) if tests else "",
            "trajectory_events": event_count,
            "command_executions": commands,
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
