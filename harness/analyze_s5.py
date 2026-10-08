#!/usr/bin/env python3
"""Join validated blind labels to private metadata and write S5 summaries."""
import csv
import json
import random
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
PACKETS = ROOT / "data/s5_blinded_packets"
ANN = ROOT / "data/s5_blinded_annotations"
RESULTS = ROOT / "data/s5_results"
REVIEW = ROOT / "data/s5_manual_review"
RESULTS.mkdir(exist_ok=True); REVIEW.mkdir(exist_ok=True)
manifest = {x["packet_id"]: x for x in json.loads((PACKETS / "manifest_private.json").read_text())["packets"]}
metrics = {r["run_id"]: r for r in csv.DictReader((ROOT / "data/s5_runs/s5_run_metrics.csv").open())}
rows, stage_counts, failure_counts = [], Counter(), Counter()
for packet_id, item in sorted(manifest.items()):
    annotation = json.loads((ANN / f"{packet_id}.json").read_text())
    metric = metrics[item["run_id"]]
    stages = [event["label"] for event in annotation["stage_events"]]
    stage_counts.update(stages); failure_counts.update(annotation["failure_modes"])
    rows.append({
        "packet_id": packet_id, "run_id": item["run_id"], "task": item["task_id"], "model": metric["model"],
        "outcome": metric["outcome"], "pass": metric["pass"], "partial_score": metric["partial_score"],
        "steps": metric["steps"], "stage_count": len(stages), "failure_modes": json.dumps(annotation["failure_modes"]),
        "activation_heuristic": metric["activation_heuristic"], "validated_after_last_edit": metric["validated_after_last_edit"],
    })
with (RESULTS / "s5_annotated_runs_private.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
with (RESULTS / "s5_stage_proportions.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["stage", "count", "proportion"]); writer.writeheader()
    for stage, count in sorted(stage_counts.items()): writer.writerow({"stage": stage, "count": count, "proportion": count / sum(stage_counts.values())})
with (RESULTS / "s5_failure_mode_rates.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["failure_mode", "run_count", "rate", "pass_rate_when_present"]); writer.writeheader()
    for mode, count in sorted(failure_counts.items()):
        matching = [r for r in rows if mode in json.loads(r["failure_modes"])]
        writer.writerow({"failure_mode": mode, "run_count": count, "rate": count / len(rows), "pass_rate_when_present": mean(r["pass"] == "True" for r in matching)})

by_model = defaultdict(list)
for row in rows: by_model[row["model"]].append(row)
summary = []
for model, values in sorted(by_model.items()):
    summary.append({
        "model": model, "runs": len(values), "passes": sum(x["pass"] == "True" for x in values),
        "mean_partial_score": mean(float(x["partial_score"]) for x in values if x["partial_score"]),
        "mean_steps": mean(float(x["steps"]) for x in values),
        "activation_heuristic_rate": mean(x["activation_heuristic"] != "not_observed" for x in values),
        "validated_after_last_edit_rate": mean(x["validated_after_last_edit"] == "True" for x in values),
    })
with (RESULTS / "s5_model_summary.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(summary[0])); writer.writeheader(); writer.writerows(summary)

# Fixed, stratified, blinded packets for the human reviewer.  The copied files
# intentionally omit the private model/outcome mapping.
random.seed(20261008)
sample = []
for model in sorted(by_model):
    population = by_model[model][:]
    random.shuffle(population)
    sample.extend(population[:12])
for row in sample:
    shutil.copyfile(PACKETS / f"{row['packet_id']}.json", REVIEW / f"{row['packet_id']}.json")
review_manifest = {"blinded": True, "packet_ids": [r["packet_id"] for r in sample], "human_annotation_path": "data/s5_manual_review/human_annotations.jsonl"}
(REVIEW / "review_manifest.json").write_text(json.dumps(review_manifest, indent=2) + "\n")
print(json.dumps({"runs": len(rows), "review_packets": len(sample), "stage_events": sum(stage_counts.values())}))
