#!/usr/bin/env python3
"""Materialize the locked S5 dev-only v0 baseline matrix."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS = [
    "pilot_a01_label_parser", "pilot_a02_config_parser", "pilot_a03_record_deduplication",
    "pilot_a04_dependency_order", "pilot_a05_version_parser", "pilot_a06_path_safety",
    "pilot_b01_csv_cleaning", "pilot_b02_json_normalization", "pilot_b03_duplicate_audit",
    "pilot_b04_multifile_reconciliation", "pilot_b05_date_validation", "pilot_b06_schema_conversion",
]
MODELS = [("gpt-5.6-sol", "gpt"), ("gemma4:26b", "soclaas")]
output = ROOT / "config/s5_dev_baseline_matrix.tsv"
with output.open("w", newline="") as handle:
    writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
    writer.writerow(["task_id", "model_id", "provider", "repetition"])
    for task in TASKS:
        for model, provider in MODELS:
            for repetition in (1, 2, 3):
                writer.writerow([task, model, provider, repetition])
print(f"wrote {len(TASKS) * len(MODELS) * 3} S5 observations")
