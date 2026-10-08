#!/usr/bin/env python3
"""Compare frozen S5 v0 and S6 L3 on locked dev_validate tasks."""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
TASKS = {"pilot_a02_config_parser", "pilot_a04_dependency_order", "pilot_a06_path_safety", "pilot_b02_json_normalization", "pilot_b04_multifile_reconciliation", "pilot_b06_schema_conversion"}

def load(directory):
    rows = []
    for path in (ROOT / directory).glob("*/metadata.json"):
        item = json.loads(path.read_text())
        if item["task_id"] in TASKS and item["requested_model_id"] == "gemma4:26b":
            rows.append(item)
    return rows

baseline, l3 = load("data/s5_runs"), load("data/s6_l3_runs")
guardrails = [json.loads(p.read_text()) for p in (ROOT / "data/s6_l3_runs").glob("*/guardrail.json")]
rows = []
for task in sorted(TASKS):
    for name, items in (("S5_v0", baseline), ("S6_L3", l3)):
        current = [x for x in items if x["task_id"] == task]
        rows.append({"task": task, "condition": name, "runs": len(current), "passes": sum(x["outcome_category"] == "pass" for x in current), "mean_partial_score": mean(x["partial_score"] for x in current), "outcomes": json.dumps(dict(Counter(x["outcome_category"] for x in current)))})
out = ROOT / "data/s6_l3_runs/s6_dev_validate_comparison.csv"
with out.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
summary = {
    "baseline": {"runs": len(baseline), "passes": sum(x["outcome_category"] == "pass" for x in baseline), "mean_partial_score": mean(x["partial_score"] for x in baseline)},
    "l3": {"runs": len(l3), "passes": sum(x["outcome_category"] == "pass" for x in l3), "mean_partial_score": mean(x["partial_score"] for x in l3), "guardrail_triggers": sum(x["guardrail_fired"] for x in guardrails)},
}
(ROOT / "data/s6_l3_runs/s6_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary))
