#!/usr/bin/env python3
"""Create deterministic, interleaved S7 schedules; this script never runs a model."""
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter
from pathlib import Path

try:
    from .s7_protocol import ROOT, SCHEDULE_SEEDS, request_seed, split_for, stable_run_id
except ImportError:  # Direct script execution from the repository root.
    from s7_protocol import ROOT, SCHEDULE_SEEDS, request_seed, split_for, stable_run_id


def tasks() -> list[str]:
    return sorted(path.name for split in ("test_in", "test_out") for path in (ROOT / "tasks" / split).iterdir() if path.is_dir())


def cells_for(model: str, all_tasks: list[str]) -> list[dict[str, object]]:
    repetitions = 5 if model == "qwen3.5:9b" else 3
    rows: list[dict[str, object]] = []
    for condition in ("C0", "C1"):
        for task in all_tasks:
            for repetition in range(1, repetitions + 1):
                rows.append({"task_id": task, "split": split_for(task), "condition": condition, "repetition": repetition})
    if model == "qwen3.5:9b":
        for condition, scoped_tasks in (("v1", [task for task in all_tasks if split_for(task) == "test_in"]), ("l3b", all_tasks)):
            for task in scoped_tasks:
                for repetition in range(1, repetitions + 1):
                    rows.append({"task_id": task, "split": split_for(task), "condition": condition, "repetition": repetition})
    return rows


def interleave(rows: list[dict[str, object]], seed: int) -> list[dict[str, object]]:
    """Fairly alternate conditions while randomizing task/repetition within each."""
    rng = random.Random(seed)
    by_condition: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_condition.setdefault(str(row["condition"]), []).append(row)
    for values in by_condition.values():
        rng.shuffle(values)
    emitted = Counter()
    last = None
    ordered: list[dict[str, object]] = []
    while any(by_condition.values()):
        available = [name for name, values in by_condition.items() if values]
        minimum = min(emitted[name] / (emitted[name] + len(by_condition[name])) for name in available)
        candidates = [name for name in available if emitted[name] / (emitted[name] + len(by_condition[name])) == minimum]
        if last in candidates and len(candidates) > 1:
            candidates.remove(last)
        chosen = rng.choice(sorted(candidates))
        row = by_condition[chosen].pop()
        emitted[chosen] += 1
        ordered.append(row)
        last = chosen
    for order, row in enumerate(ordered, start=1):
        row["order"] = order
    return ordered


def balance_report(rows: list[dict[str, object]]) -> dict[str, object]:
    conditions = [str(row["condition"]) for row in rows]
    max_same_run = 0
    current = 0
    previous = None
    for condition in conditions:
        current = current + 1 if condition == previous else 1
        max_same_run = max(max_same_run, current)
        previous = condition
    return {
        "count": len(rows),
        "by_condition": dict(Counter(conditions)),
        "by_split": dict(Counter(str(row["split"]) for row in rows)),
        "max_adjacent_same_condition": max_same_run,
        "unique_run_ids": len({str(row["run_id"]) for row in rows}) == len(rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "config" / "s7_schedules")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    reports = {}
    all_tasks = tasks()
    for model, seed in SCHEDULE_SEEDS.items():
        rows = interleave(cells_for(model, all_tasks), seed)
        for row in rows:
            row["model"] = model
            row["schedule_seed"] = seed
            row["run_id"] = stable_run_id(model, str(row["task_id"]), str(row["condition"]), int(row["repetition"]))
            row["request_seed"] = request_seed(str(row["run_id"]))
        filename = "".join(char if char.isalnum() else "_" for char in model) + ".tsv"
        with (args.output_dir / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["order", "run_id", "model", "schedule_seed", "request_seed", "task_id", "split", "condition", "repetition"], delimiter="\t")
            writer.writeheader(); writer.writerows(rows)
        reports[model] = balance_report(rows)
    (args.output_dir / "balance_report.json").write_text(json.dumps(reports, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
