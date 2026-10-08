#!/usr/bin/env python3
"""Write the B3 r2 dev baseline matrix after committed S4 selection."""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
selected = json.loads((ROOT / "data/b3_s4_r2_results/selection.json").read_text())["selected_model"]
tasks = ["pilot_a01_label_parser", "pilot_a02_config_parser", "pilot_a03_record_deduplication", "pilot_a04_dependency_order", "pilot_a05_version_parser", "pilot_a06_path_safety", "pilot_b01_csv_cleaning", "pilot_b02_json_normalization", "pilot_b03_duplicate_audit", "pilot_b04_multifile_reconciliation", "pilot_b05_date_validation", "pilot_b06_schema_conversion"]
with (ROOT / "config/b3_s5_r2_matrix.tsv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
    writer.writerow(["task_id", "model_id", "repetition"])
    for task in tasks:
        for repetition in (1, 2, 3): writer.writerow([task, selected, repetition])
print(f"wrote {len(tasks) * 3} rows for {selected}")
