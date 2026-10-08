#!/usr/bin/env python3
"""Summarize B3 r2 calibration and apply its pre-registered target rule."""
from __future__ import annotations
import csv, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = [json.loads(path.read_text(encoding="utf-8")) for path in (ROOT / "data/b3_s4_r2_runs").glob("pilot_*/metadata.json")]
groups = defaultdict(list)
for row in rows:
    groups[(row["requested_model_id"], row["task_id"])].append(row)
task_rows = []
for (model, task), values in sorted(groups.items()):
    counts = Counter(value["outcome_category"] for value in values)
    task_rows.append({"model": model, "task": task, "runs": len(values), "passes": counts["pass"], "pass_rate": counts["pass"] / len(values), "mean_partial_score": sum((value.get("partial_score") or 0) for value in values) / len(values), "outcome_counts": json.dumps(dict(sorted(counts.items())))})
model_rows = []
for model in sorted({row["model"] for row in task_rows}):
    values = [row for row in task_rows if row["model"] == model]
    overall = sum(row["passes"] for row in values) / sum(row["runs"] for row in values)
    middle = sum(.2 <= row["pass_rate"] <= .8 for row in values)
    model_rows.append({"model": model, "runs": sum(row["runs"] for row in values), "passes": sum(row["passes"] for row in values), "overall_pass_rate": overall, "mean_partial_score": sum(row["mean_partial_score"] for row in values) / len(values), "middle_task_count": middle, "eligible_for_s5": .2 <= overall <= .8})
eligible = [row for row in model_rows if row["eligible_for_s5"]]
selected = sorted(eligible, key=lambda row: (-row["middle_task_count"], row["overall_pass_rate"], row["model"]))[0] if eligible else None
out = ROOT / "data/b3_s4_r2_results"
out.mkdir(exist_ok=True)
for name, values in (("task_summary.csv", task_rows), ("model_summary.csv", model_rows)):
    with (out / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(values[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(values)
(out / "selection.json").write_text(json.dumps({"rule": "locked config/b3_r2_protocol.yaml", "selected_model": selected["model"] if selected else None, "selected_row": selected}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"runs": len(rows), "selected_model": selected["model"] if selected else None}))
