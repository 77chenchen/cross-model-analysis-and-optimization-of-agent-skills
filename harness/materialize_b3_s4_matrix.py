#!/usr/bin/env python3
"""Write the locked B3 r2 S4 matrix (open models only)."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS = [
    "pilot_a01_label_parser", "pilot_a02_config_parser", "pilot_a03_record_deduplication", "pilot_a04_dependency_order", "pilot_a05_version_parser", "pilot_a06_path_safety",
    "pilot_b01_csv_cleaning", "pilot_b02_json_normalization", "pilot_b03_duplicate_audit", "pilot_b04_multifile_reconciliation", "pilot_b05_date_validation", "pilot_b06_schema_conversion",
]
MODELS = ["qwen3.8:27b", "qwen3.5:9b", "gemma4:26b", "llama3.1:8b", "qwen3-coder-next"]
output = ROOT / "config/b3_s4_r2_matrix.tsv"
with output.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
    writer.writerow(["task_id", "model_id", "repetition"])
    for task in TASKS:
        for model in MODELS:
            for repetition in (1, 2, 3):
                writer.writerow([task, model, repetition])
print(f"wrote {len(TASKS) * len(MODELS) * 3} B3 S4 observations")
