#!/usr/bin/env python3
"""Materialize the locked 216-observation S4 calibration matrix."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
tasks = [
    "pilot_a01_label_parser", "pilot_a02_config_parser", "pilot_a03_record_deduplication",
    "pilot_a04_dependency_order", "pilot_a05_version_parser", "pilot_a06_path_safety",
    "pilot_b01_csv_cleaning", "pilot_b02_json_normalization", "pilot_b03_duplicate_audit",
    "pilot_b04_multifile_reconciliation", "pilot_b05_date_validation", "pilot_b06_schema_conversion",
]
models = [
    ("gpt-5.6-sol", "gpt"), ("qwen3.8:27b", "soclaas"), ("qwen3.5:9b", "soclaas"),
    ("gemma4:26b", "soclaas"), ("llama3.1:8b", "soclaas"), ("qwen3-coder-next", "soclaas"),
]
output = ROOT / "config/s4_calibration_matrix.tsv"
with output.open("w", newline="") as handle:
    writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
    writer.writerow(["task_id", "model_id", "provider", "repetition"])
    for task in tasks:
        for model, provider in models:
            for repetition in (1, 2, 3):
                writer.writerow([task, model, provider, repetition])
print(f"wrote {len(tasks) * len(models) * 3} observations to {output}")
