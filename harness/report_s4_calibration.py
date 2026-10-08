#!/usr/bin/env python3
"""Produce descriptive task-by-model calibration summaries for S4."""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
raw = []
for path in sorted((ROOT / "data/calibration_runs").glob("*/metadata.json")):
    meta = json.loads(path.read_text())
    runtime_path = path.parent / "runtime.json"
    runtime = json.loads(runtime_path.read_text()) if runtime_path.exists() else {}
    raw.append({
        "model": meta["requested_model_id"], "task": meta["task_id"],
        "outcome": meta["outcome_category"], "partial_score": meta.get("partial_score"),
        "steps": sum(1 for _ in (path.parent / "actions.jsonl").open()) if (path.parent / "actions.jsonl").exists() else None,
        "input_tokens": runtime.get("usage", {}).get("input_tokens"),
        "output_tokens": runtime.get("usage", {}).get("output_tokens"),
        "reasoning_output_tokens": runtime.get("usage", {}).get("reasoning_output_tokens"),
    })

def avg(rows, field):
    values = [r[field] for r in rows if r[field] is not None]
    return mean(values) if values else None

groups = defaultdict(list)
for row in raw:
    groups[(row["model"], row["task"])].append(row)
summary = []
for (model, task), rows in sorted(groups.items()):
    outcomes = Counter(r["outcome"] for r in rows)
    summary.append({
        "model": model, "task": task, "runs": len(rows), "passes": outcomes["pass"],
        "pass_rate": outcomes["pass"] / len(rows), "mean_partial_score": avg(rows, "partial_score"),
        "outcome_counts": json.dumps(dict(sorted(outcomes.items()))), "mean_steps": avg(rows, "steps"),
        "mean_input_tokens": avg(rows, "input_tokens"), "mean_output_tokens": avg(rows, "output_tokens"),
        "mean_reasoning_output_tokens": avg(rows, "reasoning_output_tokens"), "mean_cost_usd": None,
    })

out = ROOT / "data/calibration_runs/s4_model_task_summary.csv"
with out.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(summary[0])); writer.writeheader(); writer.writerows(summary)

by_model = defaultdict(list)
for row in summary:
    by_model[row["model"]].append(row)
lines = [
    "# S4 calibration results", "",
    "Descriptive calibration only: frozen Skill v0, 12 frozen pilot tasks, and three fresh runs per model-task condition (216 runs total). Tasks—not repeats—are the intended statistical unit. Temperature and seed could not be set through the current CLI; costs are null because a verified provider price card was unavailable.", "",
    "| Model | Runs | Passes | Pass rate | Mean partial score | Outcome counts | Tasks with 20%–80% pass rate |",
    "|---|---:|---:|---:|---:|---|---:|",
]
for model, rows in sorted(by_model.items()):
    runs, passes = sum(r["runs"] for r in rows), sum(r["passes"] for r in rows)
    outcomes = Counter()
    for row in rows:
        outcomes.update(json.loads(row["outcome_counts"]))
    partial = mean(r["mean_partial_score"] for r in rows if r["mean_partial_score"] is not None)
    middle = sum(.2 <= r["pass_rate"] <= .8 for r in rows)
    lines.append(f"| `{model}` | {runs} | {passes} | {passes/runs:.3f} | {partial:.3f} | `{dict(sorted(outcomes.items()))}` | {middle}/12 |")
lines += [
    "", "## Calibration decision", "",
    "`gemma4:26b` is the recommended primary weak target for the next dev-only phase: it has 5/12 task conditions with observed pass rates from 20% to 80%, while retaining a 0.750 aggregate pass rate and a 0.889 mean partial score. This is a calibration selection, not a cross-model ranking.",
    "", "`qwen3.5:9b` is at a floor on this pool: 0/36 passes, with 35/36 recorded as `empty_termination` and one `verifier_fail`. Skill text alone is unlikely to resolve that operational termination pattern; retain it only as a documented floor condition or use a simpler pool / runtime-guardrail condition. `llama3.1:8b` is also at a floor (0/36), but its failures are all `verifier_fail`, not empty terminations.",
    "", "The full task-by-model descriptive table is `data/calibration_runs/s4_model_task_summary.csv`; individual-run values, including tokens and action counts, are in `s4_run_table.csv`.",
]
(ROOT / "docs/s4_calibration_results.md").write_text("\n".join(lines) + "\n")
print(json.dumps({"conditions": len(summary), "runs": len(raw), "summary": str(out)}))
