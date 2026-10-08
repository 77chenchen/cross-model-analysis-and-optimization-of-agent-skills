#!/usr/bin/env python3
"""Materialize the locked, interleaved L3b schedule."""
from __future__ import annotations

import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
tasks = ["pilot_a02_config_parser", "pilot_a04_dependency_order", "pilot_a06_path_safety", "pilot_b02_json_normalization", "pilot_b04_multifile_reconciliation", "pilot_b06_schema_conversion"]
rows = [{"task_id": task, "condition": condition, "repetition": repetition, "model_id": "qwen3.5:9b", "seed": ""} for task in tasks for condition in ("baseline", "l3b") for repetition in range(1, 7)]
random.Random(20261008).shuffle(rows)
for order, row in enumerate(rows, 1):
    row["order"] = order
output = ROOT / "config/l3b_dev_validate_matrix.tsv"
with output.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=["order", "task_id", "condition", "repetition", "model_id", "seed"], delimiter="\t")
    writer.writeheader(); writer.writerows(rows)
print(output)
