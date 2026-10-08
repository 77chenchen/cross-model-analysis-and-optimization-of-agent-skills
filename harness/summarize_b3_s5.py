#!/usr/bin/env python3
"""Summarize the completed B3 r2 Qwen dev baseline without pooling CLI data."""
from __future__ import annotations
import csv, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = [json.loads(path.read_text(encoding="utf-8")) for path in (ROOT / "data/b3_s5_r2_runs").glob("pilot_*/metadata.json")]
groups = defaultdict(list)
for row in rows: groups[row["task_id"]].append(row)
table = []
for task, values in sorted(groups.items()):
    outcomes = Counter(value["outcome_category"] for value in values)
    flags = Counter(flag for value in values for flag, present in value.get("outcome_flags", {}).items() if present)
    table.append({"task_id": task, "runs": len(values), "passes": outcomes["pass"], "pass_rate": outcomes["pass"] / len(values), "mean_partial_score": sum((value.get("partial_score") or 0) for value in values) / len(values), "outcome_counts": json.dumps(dict(sorted(outcomes.items()))), "outcome_flags": json.dumps(dict(sorted(flags.items())))})
out = ROOT / "data/b3_s5_r2_results"; out.mkdir(exist_ok=True)
with (out / "task_summary.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(table[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(table)
def summary(values):
    return {"runs": len(values), "passes": sum(value["outcome_category"] == "pass" for value in values), "pass_rate": sum(value["outcome_category"] == "pass" for value in values) / len(values), "mean_partial_score": sum((value.get("partial_score") or 0) for value in values) / len(values), "outcomes": dict(sorted(Counter(value["outcome_category"] for value in values).items())), "flags": dict(sorted(Counter(flag for value in values for flag, present in value.get("outcome_flags", {}).items() if present).items()))}
(out / "summary.json").write_text(json.dumps({"including_a04": summary(rows), "excluding_a04": summary([row for row in rows if row["task_id"] != "pilot_a04_dependency_order"])}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"runs": len(rows), "output": str(out)}))
