#!/usr/bin/env python3
"""Produce the preregistered descriptive L3b summary; never infer efficacy."""
from __future__ import annotations

import csv
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def wilson(success: int, total: int) -> list[float | None]:
    if not total:
        return [None, None]
    z = 1.95996398454
    p = success / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [center - margin, center + margin]


def rate(success: int, total: int) -> dict:
    return {"successes": success, "denominator": total, "rate": success / total if total else None, "wilson_95": wilson(success, total)}


baselines = {row["task_id"]: float(row["seed_partial_score"]) for row in csv.DictReader((ROOT / "data/pilot_seed_partial_baselines.csv").open())}
rows = []
for metadata_path in sorted((ROOT / "data/l3b_runs").glob("pilot_*/metadata.json")):
    meta = json.loads(metadata_path.read_text())
    events = [json.loads(line) for line in (metadata_path.parent / "events.jsonl").read_text().splitlines()]
    trigger_index = next((index for index, event in enumerate(events) if event.get("event") == "l3b_budget_reminder_injected"), None)
    after = events[trigger_index + 1:] if trigger_index is not None else []
    validated = any(event.get("event") == "tool_result" and event.get("tool_name") == "run_command" and event.get("result", {}).get("ok") for event in after)
    score = meta.get("partial_score")
    provider_error = bool(meta["outcome_flags"].get("provider_error"))
    rows.append({
        "run_id": meta["run_id"], "task_id": meta["task_id"],
        "condition": "l3b" if meta.get("l3b_trigger_at") else "baseline",
        "split": "dev_validate", "outcome": meta["outcome_category"],
        "triggered": bool(meta.get("l3b_triggered")),
        "post_trigger_validation": validated,
        "partial_score": score, "seed_partial_score": baselines[meta["task_id"]],
        "partial_delta_seed": None if score is None else score - baselines[meta["task_id"]],
        "partial_increased": None if score is None else score > baselines[meta["task_id"]],
        "pass": meta["outcome_category"] == "pass",
        "max_steps_reached": bool(meta["outcome_flags"].get("max_steps_reached")),
        "provider_error": provider_error,
    })

csv_path = ROOT / "data/l3b_results.csv"
with csv_path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
    writer.writeheader(); writer.writerows(rows)

groups = defaultdict(list)
for row in rows:
    groups[(row["split"], row["condition"])].append(row)
summary = {"scope": "dev_validate only; descriptive, not an efficacy claim", "groups": {}, "mechanism": {}}
for (split, condition), group in sorted(groups.items()):
    usable = [row for row in group if not row["provider_error"]]
    scored = [row for row in usable if row["partial_score"] is not None]
    deltas = [row["partial_delta_seed"] for row in scored]
    increased = [row for row in scored if row["partial_increased"]]
    summary["groups"][f"{split}/{condition}"] = {
        "runs": len(group), "provider_error": len(group) - len(usable),
        "outcomes": dict(sorted(Counter(row["outcome"] for row in group).items())),
        "pass_excluding_provider_error": rate(sum(row["pass"] for row in usable), len(usable)),
        "max_steps_reached": rate(sum(row["max_steps_reached"] for row in usable), len(usable)),
        "partial_score": {"n": len(scored), "mean": statistics.mean(row["partial_score"] for row in scored) if scored else None, "median": statistics.median(row["partial_score"] for row in scored) if scored else None},
        "partial_delta_from_seed": {"n": len(deltas), "mean": statistics.mean(deltas) if deltas else None, "median": statistics.median(deltas) if deltas else None, "positive_delta": rate(len(increased), len(scored))},
    }

l3b = [row for row in rows if row["condition"] == "l3b"]
triggered = [row for row in l3b if row["triggered"]]
triggered_usable = [row for row in triggered if not row["provider_error"]]
triggered_scored = [row for row in triggered_usable if row["partial_score"] is not None]
summary["mechanism"] = {
    "l3b_assigned_runs": len(l3b), "trigger_count": rate(len(triggered), len(l3b)),
    "post_trigger_validation": rate(sum(row["post_trigger_validation"] for row in triggered_usable), len(triggered_usable)),
    "post_trigger_partial_increase": rate(sum(row["partial_increased"] for row in triggered_scored), len(triggered_scored)),
    "post_trigger_final_pass": rate(sum(row["pass"] for row in triggered_usable), len(triggered_usable)),
}

json_path = ROOT / "data/l3b_summary.json"
json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

lines = ["# L3b descriptive results", "", "This is a dev-validate-only, small-sample descriptive report. It does not claim that L3b is effective.", ""]
for name, value in summary["groups"].items():
    lines.extend([f"## {name}", "", f"Runs: {value['runs']}; provider errors: {value['provider_error']}; outcomes: {value['outcomes']}.", "", f"Pass excluding provider errors: {value['pass_excluding_provider_error']['rate']:.3f} (Wilson 95% {value['pass_excluding_provider_error']['wilson_95']}).", f"Max-step reached: {value['max_steps_reached']['rate']:.3f} (Wilson 95% {value['max_steps_reached']['wilson_95']}).", f"Mean partial score: {value['partial_score']['mean']}; mean seed-relative partial delta: {value['partial_delta_from_seed']['mean']}; positive-delta frequency: {value['partial_delta_from_seed']['positive_delta']['rate']} (Wilson 95% {value['partial_delta_from_seed']['positive_delta']['wilson_95']}).", ""])
mechanism = summary["mechanism"]
lines.extend(["## Mechanism activation", "", f"L3b reminders triggered in {mechanism['trigger_count']['successes']}/{mechanism['trigger_count']['denominator']} assigned runs (Wilson 95% {mechanism['trigger_count']['wilson_95']}). Among triggered runs, post-trigger validation was {mechanism['post_trigger_validation']['rate']}, partial increase was {mechanism['post_trigger_partial_increase']['rate']}, and final pass was {mechanism['post_trigger_final_pass']['rate']}. The mechanism is observable only where triggered; samples are small.", ""])
(ROOT / "docs/l3b_results.md").write_text("\n".join(lines), encoding="utf-8")
print(json.dumps(summary, indent=2))
