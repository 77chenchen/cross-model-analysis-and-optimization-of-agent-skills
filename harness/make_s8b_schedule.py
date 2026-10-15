#!/usr/bin/env python3
"""Create the deterministic interleaved S8-b schedule and prompt manifest."""
from __future__ import annotations

import csv
import json
import random
from pathlib import Path

from record_run import digest
from s8b_protocol import (
    ARM_TEXT, CONDITIONS, MODEL, REPETITIONS, ROOT, SCHEDULE_SEED, TASKS,
    prompt_for, request_seed, sha256_text, stable_run_id,
)


def main() -> None:
    rows = []
    for task_id in TASKS:
        for condition in CONDITIONS:
            for repetition in range(1, REPETITIONS + 1):
                run_id = stable_run_id(task_id, condition, repetition)
                rows.append({
                    "run_id": run_id,
                    "task_id": task_id,
                    "condition": condition,
                    "repetition": repetition,
                    "schedule_seed": SCHEDULE_SEED,
                    "request_seed": request_seed(run_id),
                })
    random.Random(SCHEDULE_SEED).shuffle(rows)
    for position, row in enumerate(rows, 1):
        row["position"] = position

    schedule = ROOT / "config" / "s8b_schedule.tsv"
    with schedule.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("position", "run_id", "task_id", "condition", "repetition", "schedule_seed", "request_seed"),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    prompts = {}
    for task_id in TASKS:
        for condition in CONDITIONS:
            prompt, semantic, guidance = prompt_for(condition, task_id)
            prompts[f"{task_id}/{condition}"] = {
                "semantic_condition": semantic,
                "prompt_sha256": sha256_text(prompt),
                "guidance_sha256": sha256_text(guidance),
                "guidance_word_count": len(guidance.split()),
            }
    manifest = {
        "protocol": "s8b-dev-only-v1",
        "model": MODEL,
        "schedule_seed": SCHEDULE_SEED,
        "task_count": len(TASKS),
        "conditions": list(CONDITIONS),
        "repetitions": REPETITIONS,
        "total_runs": len(rows),
        "arm_word_counts": {key: len(value.split()) for key, value in ARM_TEXT.items()},
        "task_tree_hashes": {task: digest(ROOT / "tasks" / "s8b" / task / "template") for task in TASKS},
        "contract_hashes": {task: digest(ROOT / "verifiers" / "s8b_contracts" / f"{task}.json") for task in TASKS},
        "prompts": prompts,
    }
    (ROOT / "config" / "s8b_prompt_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"schedule": str(schedule), "runs": len(rows), "prompts": len(prompts)}))


if __name__ == "__main__":
    main()
