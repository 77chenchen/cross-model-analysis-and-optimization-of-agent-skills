#!/usr/bin/env python3
"""Materialize the fixed, interleaved S8 schedule and prompt manifest."""
from __future__ import annotations

import csv
import json
import random
from pathlib import Path

from s8_protocol import CONDITIONS, MODEL, REPETITIONS, SCHEDULE_SEED, TASKS, prompt_for, request_seed, sha256_text, stable_run_id

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    rows = [
        {"task_id": task, "condition": condition, "repetition": repetition,
         "model": MODEL, "run_id": stable_run_id(task, condition, repetition)}
        for task in TASKS for condition in CONDITIONS for repetition in range(1, REPETITIONS + 1)
    ]
    random.Random(SCHEDULE_SEED).shuffle(rows)
    for order, row in enumerate(rows, 1):
        row["order"] = order
        row["request_seed"] = request_seed(row["run_id"])
        row["schedule_seed"] = SCHEDULE_SEED
    schedule = ROOT / "config" / "s8_dev_validate_schedule.tsv"
    with schedule.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("order", "task_id", "condition", "repetition", "model", "run_id", "request_seed", "schedule_seed"), delimiter="\t")
        writer.writeheader(); writer.writerows(rows)
    prompts = {}
    for task in TASKS:
        for condition in CONDITIONS:
            prompt, semantic, block = prompt_for(condition, task)
            prompts[f"{task}/{condition}"] = {
                "task_id": task, "condition": condition, "semantic_condition": semantic,
                "prompt_sha256": sha256_text(prompt), "guidance_sha256": sha256_text(block),
                "guidance_whitespace_word_count": len(block.split()), "prompt": prompt,
            }
    manifest = {"protocol": "s8-dev-only-v1", "model": MODEL, "schedule_seed": SCHEDULE_SEED,
                "tasks": list(TASKS), "conditions": list(CONDITIONS), "repetitions": REPETITIONS,
                "scheduled_runs": len(rows), "schedule_sha256": sha256_text(schedule.read_text(encoding="utf-8")),
                "prompts": prompts}
    (ROOT / "config" / "s8_prompt_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(schedule)


if __name__ == "__main__":
    main()
