#!/usr/bin/env python3
"""Qwen-only S7 monitoring/audit split; no formal outcome inference."""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

try:
    from .monitor_s7_metrics import row
    from .s7_protocol import ROOT, skill_id_for
except ImportError:
    from monitor_s7_metrics import row
    from s7_protocol import ROOT, skill_id_for


METRICS = ("steps", "first_edit_position", "validated_after_last_edit", "write_file_rewrite_count", "loop_count")


def quantile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    xs = sorted(values); position = (len(xs) - 1) * p; low = int(position); high = min(low + 1, len(xs) - 1)
    return xs[low] + (xs[high] - xs[low]) * (position - low)


def describe(values: list[float]) -> dict[str, float | int | None]:
    return {"n": len(values), "mean": sum(values) / len(values) if values else None, "median": quantile(values, .5), "q1": quantile(values, .25), "q3": quantile(values, .75)}


def event_tools(run_dir: Path, cap: int | None = None) -> list[dict]:
    events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()] if (run_dir / "events.jsonl").exists() else []
    tools = [event for event in events if event.get("event") == "tool_result"]
    return tools if cap is None else tools[:cap]


def pre32_metrics(run_dir: Path) -> dict[str, float] | None:
    tools = event_tools(run_dir, 32)
    if len(event_tools(run_dir)) < 32:
        return None
    writes = [i for i, event in enumerate(tools, 1) if event.get("tool_name") == "write_file"]
    validations = [i for i, event in enumerate(tools, 1) if event.get("tool_name") == "run_command" and any(token in str(event.get("arguments") or "").lower() for token in ("test", "pytest", "unittest", "py_compile"))]
    paths = set(); action_counts = Counter()
    for event in tools:
        action_counts[(event.get("tool_name"), event.get("arguments"))] += 1
        if event.get("tool_name") == "write_file":
            try: paths.add(json.loads(event.get("arguments") or "{}").get("path"))
            except json.JSONDecodeError: pass
    return {"first_edit_position": float(writes[0]) if writes else 0.0, "validated_after_last_edit": float(bool(writes and any(index > writes[-1] for index in validations))), "write_file_rewrite_count": float(max(0, len(writes) - len(paths))), "loop_count": float(sum(count - 1 for count in action_counts.values() if count >= 3))}


def paired(rows: list[dict], left: str, right: str, tasks: set[str] | None = None) -> dict:
    by = defaultdict(lambda: defaultdict(list))
    for value in rows:
        if value["condition"] in {left, right} and (tasks is None or value["task"] in tasks):
            by[value["task"]][value["condition"]].append(value)
    result = {}
    for metric in METRICS:
        differences = []
        for task, conditions in by.items():
            if not conditions[left] or not conditions[right]: continue
            a = [float(x[metric] or 0) for x in conditions[left]]; b = [float(x[metric] or 0) for x in conditions[right]]
            differences.append(sum(a) / len(a) - sum(b) / len(b))
        summary = describe(differences)
        summary.update({"positive_tasks": sum(x > 0 for x in differences), "negative_tasks": sum(x < 0 for x in differences), "zero_tasks": sum(x == 0 for x in differences)})
        result[metric] = summary
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=ROOT / "data" / "s7_runs")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "s7_monitoring" / "qwen_monitoring_revision.json")
    args = parser.parse_args()
    entries = []
    raw = []
    for metadata_path in sorted(args.runs.glob("*/metadata.json")):
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata.get("requested_model_id") != "qwen3.5:9b": continue
        run_dir = metadata_path.parent; value = row(run_dir); value["skill"] = skill_id_for(value["task"]); entries.append(value); raw.append((run_dir, metadata))
    conditions = ("C0", "C1", "v1", "l3b")
    outcomes = {}; activation = {}; process = {}; crosstab = {}
    for condition in conditions:
        selected = [pair for pair in raw if pair[1]["condition"] == condition]
        values = [value for value in entries if value["condition"] == condition]
        flags = Counter(); legacy = Counter(); cross = Counter()
        for run_dir, metadata in selected:
            verifier = json.loads((run_dir / "verifier.json").read_text(encoding="utf-8"))
            outcome_flags = metadata.get("outcome_flags") or {}
            flags["pass"] += verifier.get("passed") is True
            flags["verifier_fail"] += verifier.get("passed") is False
            for key in ("timeout", "max_steps_reached", "verifier_timeout", "provider_error", "final_empty"):
                flags[key] += bool(outcome_flags.get(key) or (key == "verifier_timeout" and metadata.get(key)))
            legacy[metadata.get("outcome_category")] += 1
            cross[(verifier.get("passed") is True, bool(outcome_flags.get("final_empty")))] += 1
        outcomes[condition] = {"n": len(selected), "nonexclusive_flags": dict(flags), "legacy_outcome": dict(legacy)}
        crosstab[condition] = {f"pass_{passed}_final_empty_{empty}": count for (passed, empty), count in sorted(cross.items())}
        labels = Counter(value["activation_heuristic"] for value in values)
        activation[condition] = {label: {"count": labels[label], "rate": labels[label] / len(values)} for label in ("explicit", "observable_inferred", "not_observed")}
        process[condition] = {metric: describe([float(value[metric] or 0) for value in values]) for metric in METRICS}
    skill_process = {}
    for condition in conditions:
        for skill in ("A", "B", "C"):
            values = [value for value in entries if value["condition"] == condition and value["skill"] == skill]
            if values: skill_process[f"{condition}::{skill}"] = {metric: describe([float(value[metric] or 0) for value in values]) for metric in METRICS}
    test_in = {value["task"] for value in entries if value["split"] == "test_in"}
    pre32 = defaultdict(lambda: defaultdict(list))
    pre32_audit = {"prompt_hash_equal_by_skill": True, "skill_hash_equal_by_skill": True, "tool_schema_versions": set(), "worker_concurrency": set()}
    for run_dir, metadata in raw:
        if metadata["condition"] not in {"C1", "l3b"}: continue
        metric = pre32_metrics(run_dir)
        if metric is not None: pre32[metadata["condition"]][metadata["task_id"]].append(metric)
        pre32_audit["tool_schema_versions"].add(metadata.get("tool_schema_version")); pre32_audit["worker_concurrency"].add(metadata.get("worker_concurrency"))
    for skill in ("A", "B", "C"):
        c1 = {metadata.get("prompt_hash") for _, metadata in raw if metadata["condition"] == "C1" and skill_id_for(metadata["task_id"]) == skill}
        l3 = {metadata.get("prompt_hash") for _, metadata in raw if metadata["condition"] == "l3b" and skill_id_for(metadata["task_id"]) == skill}
        pre32_audit["prompt_hash_equal_by_skill"] &= c1 == l3
        c1s = {metadata.get("skill_hash") for _, metadata in raw if metadata["condition"] == "C1" and skill_id_for(metadata["task_id"]) == skill}
        l3s = {metadata.get("skill_hash") for _, metadata in raw if metadata["condition"] == "l3b" and skill_id_for(metadata["task_id"]) == skill}
        pre32_audit["skill_hash_equal_by_skill"] &= c1s == l3s
    pre32_pairs = {}
    for metric in ("first_edit_position", "validated_after_last_edit", "write_file_rewrite_count", "loop_count"):
        diffs = []
        for task in set(pre32["C1"]) & set(pre32["l3b"]):
            c1 = [value[metric] for value in pre32["C1"][task]]; l3 = [value[metric] for value in pre32["l3b"][task]]
            diffs.append(sum(l3) / len(l3) - sum(c1) / len(c1))
        pre32_pairs[metric] = describe(diffs)
    output = {"scope": "qwen_only_monitoring_not_formal_analysis", "run_count": len(entries), "outcomes": outcomes, "pass_final_empty_crosstab": crosstab, "activation": activation, "process_distributions": process, "skill_process_distributions": skill_process, "task_paired_C1_minus_C0": paired(entries, "C1", "C0"), "task_paired_v1_minus_C1_test_in": paired(entries, "v1", "C1", test_in), "pre32_C1_l3b": {"A_layer_runs": {condition: sum(len(values) for values in tasks.values()) for condition, tasks in pre32.items()}, "pre32_invariants": {**pre32_audit, "tool_schema_versions": sorted(pre32_audit["tool_schema_versions"]), "worker_concurrency": sorted(pre32_audit["worker_concurrency"])}, "task_paired_L3b_minus_C1": pre32_pairs}, "notes": {"activation_stratification": "explicit only; observable_inferred is process-only", "legacy_empty_termination": "retained in outcomes.legacy_outcome", "formal_analysis": "deferred until all 870 scheduled runs complete"}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"runs": len(entries), "output": str(args.output)}))


if __name__ == "__main__":
    main()
