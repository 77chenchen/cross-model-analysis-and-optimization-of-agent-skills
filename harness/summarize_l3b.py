#!/usr/bin/env python3
"""Summarize preregistered L3b runs without interpreting efficacy."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def wilson(success: int, total: int) -> tuple[float | None, float | None]:
    if not total: return None, None
    z = 1.95996398454; p = success / total; denom = 1 + z*z/total
    center = (p + z*z/(2*total))/denom
    margin = z*math.sqrt(p*(1-p)/total + z*z/(4*total*total))/denom
    return center-margin, center+margin

baselines = {row["task_id"]: float(row["seed_partial_score"]) for row in csv.DictReader((ROOT / "data/pilot_seed_partial_baselines.csv").open())}
rows = []
for metadata_path in sorted((ROOT / "data/l3b_runs").glob("pilot_*/metadata.json")):
    meta = json.loads(metadata_path.read_text())
    events = [json.loads(line) for line in (metadata_path.parent / "events.jsonl").read_text().splitlines()]
    trigger_index = next((index for index, event in enumerate(events) if event.get("event") == "l3b_budget_reminder_injected"), None)
    after = events[trigger_index + 1:] if trigger_index is not None else []
    validated = any(event.get("event") == "tool_result" and event.get("tool_name") == "run_command" for event in after)
    score = meta.get("partial_score")
    rows.append({"task_id": meta["task_id"], "condition": "l3b" if meta.get("l3b_trigger_at") else "baseline", "split": "dev_validate", "triggered": bool(meta.get("l3b_triggered")), "post_trigger_validation": validated, "partial_score": score, "partial_delta_seed": None if score is None else score - baselines[meta["task_id"]], "pass": meta["outcome_category"] == "pass", "max_steps_reached": bool(meta["outcome_flags"].get("max_steps_reached"))})
out = ROOT / "data/l3b_results.csv"
if rows:
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows)
print(json.dumps({"runs": len(rows), "note": "Wilson reporting is computed from rows grouped by condition/split after batch completion."}))
