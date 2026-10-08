#!/usr/bin/env python3
"""Create a descriptive S4 calibration table; nulls are never imputed."""
import csv, json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = []
for meta_path in sorted((ROOT / "data/calibration_runs").glob("*/metadata.json")):
    meta = json.loads(meta_path.read_text())
    runtime_path = meta_path.parent / "runtime.json"
    runtime = json.loads(runtime_path.read_text()) if runtime_path.exists() else {}
    process_path = meta_path.parent / "process.json"
    process = json.loads(process_path.read_text()) if process_path.exists() else {}
    started, finished = process.get("started_at"), process.get("finished_at")
    duration_seconds = None
    if started and finished:
        duration_seconds = (datetime.fromisoformat(finished) - datetime.fromisoformat(started)).total_seconds()
    rows.append({
        "run_id": meta["run_id"], "model": meta["requested_model_id"], "task": meta["task_id"],
        "repetition": meta.get("repetition"), "outcome": meta.get("outcome_category"),
        "pass": meta.get("outcome_category") == "pass",
        "partial_score": meta.get("partial_score"), "steps": sum(1 for _ in (meta_path.parent / "actions.jsonl").open()) if (meta_path.parent / "actions.jsonl").exists() else None,
        "duration_seconds": duration_seconds,
        "input_tokens": runtime.get("usage", {}).get("input_tokens"),
        "cached_input_tokens": runtime.get("usage", {}).get("cached_input_tokens"),
        "output_tokens": runtime.get("usage", {}).get("output_tokens"),
        "reasoning_output_tokens": runtime.get("usage", {}).get("reasoning_output_tokens"),
        "cost_usd": None,
    })
out = ROOT / "data/calibration_runs/s4_run_table.csv"
out.parent.mkdir(exist_ok=True)
with out.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["run_id"])
    writer.writeheader(); writer.writerows(rows)
print(json.dumps({"run_count": len(rows), "output": str(out)}))
