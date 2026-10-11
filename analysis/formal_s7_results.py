#!/usr/bin/env python3
"""Generate the gated S7 formal-analysis tables from immutable run artifacts.

The primary outcome is always ``verifier.json.passed``.  Retry-exhausted
transport failures are excluded from the primary denominator and counted as
failures in the scheduled-run sensitivity view.  Repetitions are aggregated
inside task-condition cells before paired task bootstrap resampling.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Sequence

from analysis.verifier_pass_v2 import ROOT, enforce_formal_s7_gate, provider_error_protocol

VERSION = "s7-formal-v1.0.0"
BOOTSTRAP_SEED = 701009
BOOTSTRAP_DRAWS = 10_000
RUNS = ROOT / "data" / "s7_runs"
OUT = ROOT / "results" / "s7"
TABLES = ROOT / "results" / "tables" / "s7"

MODELS = [
    "qwen3.5:9b",
    "gemma4:26b",
    "qwen3.8:27b",
    "qwen3-coder-next",
    "llama3.1:8b",
    "gpt-5.6-sol",
]
CONDITIONS = ["C0", "C1", "v1", "l3b"]
FLAGS = [
    "final_empty",
    "no_edit",
    "compile_error",
    "verifier_fail",
    "timeout",
    "context_overflow",
    "provider_error",
    "max_steps_reached",
    "verifier_timeout",
]
VALIDATION_INTENT = re.compile(r"pytest|unittest|\btest\b|py_compile|python[0-9.]*\s+.*\.py", re.I)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_events(path: Path) -> tuple[list[dict], list[dict]]:
    events: list[dict] = []
    errors: list[dict] = []
    if not path.exists():
        return events, errors
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append({"path": str(path.relative_to(ROOT)), "line": line_number, "error": str(error)})
            continue
        if isinstance(event, dict):
            events.append(event)
    return events, errors


def seed_partial_baselines() -> dict[str, float]:
    admission = load_json(ROOT / "tasks" / "s3_admission.json")
    output: dict[str, float] = {}
    for item in admission.get("tasks", []):
        checks = ((item.get("checks") or {}).get("negative_template") or {}).get("checks") or {}
        output[item["id"]] = sum(value is True for value in checks.values()) / len(checks) if checks else 0.0
    return output


def trajectory_text(run_dir: Path, events: Sequence[dict]) -> str:
    fragments = [str(event.get("arguments") or "") for event in events]
    for response in sorted((run_dir / "raw_responses").glob("response_*.json")):
        payload = load_json(response)
        message = ((payload.get("choices") or [{}])[0].get("message") or {})
        fragments.extend([str(message.get("content") or ""), str(message.get("reasoning") or "")])
    return "\n".join(fragments).lower()


def read_run(run_dir: Path, baselines: dict[str, float]) -> tuple[dict, list[dict]]:
    metadata = load_json(run_dir / "metadata.json")
    verifier = load_json(run_dir / "verifier.json")
    runtime = load_json(run_dir / "runtime_r2.json") or load_json(run_dir / "runtime.json")
    process = load_json(run_dir / "process.json")
    events, event_errors = safe_events(run_dir / "events.jsonl")
    calls = [event for event in events if event.get("event") == "tool_result"]
    writes = [index for index, event in enumerate(calls, 1) if event.get("tool_name") == "write_file"]
    runs = [
        (index, event)
        for index, event in enumerate(calls, 1)
        if event.get("tool_name") == "run_command"
    ]
    validation_intent = [
        index for index, event in runs if VALIDATION_INTENT.search(str(event.get("arguments") or ""))
    ]
    validation_success = [
        index
        for index, event in runs
        if bool((event.get("result") or {}).get("ok"))
        and (event.get("result") or {}).get("returncode") in (None, 0)
    ]
    identities = [(str(event.get("tool_name")), str(event.get("arguments") or "")) for event in calls]
    counts = Counter(identities)
    written_paths: set[str] = set()
    for event in calls:
        if event.get("tool_name") != "write_file":
            continue
        try:
            written_paths.add(str(json.loads(event.get("arguments") or "{}").get("path")))
        except json.JSONDecodeError:
            pass
    text = trajectory_text(run_dir, events)
    if "skill protocol" in text or "skill a" in text or "skill b" in text or "skill c" in text:
        activation = "explicit"
    elif writes and validation_intent:
        activation = "observable_inferred"
    else:
        activation = "not_observed"
    flags = metadata.get("outcome_flags") or {}
    usage = metadata.get("r2_usage") or {}
    partial = ((verifier.get("summary") or {}).get("partial_score"))
    task = str(metadata.get("task_id"))
    provider_protocol = provider_error_protocol(metadata, runtime)
    aligned_process_surface = metadata.get("runner") != "codex-cli"
    row = {
        "run_id": metadata.get("run_id", run_dir.name),
        "model": metadata.get("requested_model_id"),
        "condition": metadata.get("condition", metadata.get("skill_version")),
        "split": metadata.get("split"),
        "task": task,
        "skill": metadata.get("skill_id"),
        "repetition": metadata.get("repetition"),
        "runner": metadata.get("runner"),
        "verifier_pass": verifier.get("passed") is True,
        "verifier_available": isinstance(verifier.get("passed"), bool),
        "provider_error_protocol": provider_protocol,
        "legacy_pass": metadata.get("legacy_outcome_category", metadata.get("outcome_category")) == "pass",
        "partial_score": partial,
        "seed_partial": baselines.get(task, 0.0),
        "partial_delta_seed": (float(partial) - baselines.get(task, 0.0)) if isinstance(partial, (int, float)) else None,
        "steps": len(calls) if aligned_process_surface else None,
        "assistant_turns": sum(event.get("event") == "provider_response" for event in events) if aligned_process_surface else None,
        "first_edit_position": (writes[0] if writes else None) if aligned_process_surface else None,
        "validated_after_last_edit_intent": bool(writes and any(index > writes[-1] for index in validation_intent)) if aligned_process_surface else None,
        "validated_after_last_edit_success": bool(writes and any(index > writes[-1] for index in validation_success)) if aligned_process_surface else None,
        "write_file_count": len(writes) if aligned_process_surface else None,
        "write_file_rewrite_count": max(0, len(writes) - len(written_paths)) if aligned_process_surface else None,
        "repeated_action_count": sum(count - 1 for count in counts.values() if count > 1) if aligned_process_surface else None,
        "loop_count": sum(count - 1 for count in counts.values() if count >= 3) if aligned_process_surface else None,
        "activation": activation if aligned_process_surface else None,
        "l3b_triggered": bool(metadata.get("l3b_triggered")),
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "reasoning_tokens": usage.get("reasoning_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "event_parse_error_count": len(event_errors),
    }
    for flag in FLAGS:
        row[flag] = bool(flags.get(flag))
    row["timeout"] = bool(row["timeout"] or process.get("timed_out"))
    row["verifier_fail"] = not row["verifier_pass"]
    row["provider_error"] = provider_protocol
    return row, event_errors


def wilson(successes: int, denominator: int, z: float = 1.959963984540054) -> tuple[float | None, float | None]:
    if denominator == 0:
        return None, None
    p = successes / denominator
    scale = 1 + z * z / denominator
    center = (p + z * z / (2 * denominator)) / scale
    margin = z * math.sqrt(p * (1 - p) / denominator + z * z / (4 * denominator * denominator)) / scale
    return center - margin, center + margin


def quantile(values: Sequence[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    position = (len(ordered) - 1) * probability
    low, high = math.floor(position), math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] * (high - position) + ordered[high] * (position - low)


def bootstrap(values: Sequence[float], seed: int = BOOTSTRAP_SEED) -> dict:
    if not values:
        return {"n_tasks": 0, "mean_difference": None, "bootstrap_low": None, "bootstrap_high": None}
    rng = random.Random(seed)
    draws = sorted(sum(rng.choice(values) for _ in values) / len(values) for _ in range(BOOTSTRAP_DRAWS))
    return {
        "n_tasks": len(values),
        "mean_difference": sum(values) / len(values),
        "bootstrap_low": draws[int(0.025 * (BOOTSTRAP_DRAWS - 1))],
        "bootstrap_high": draws[int(0.975 * (BOOTSTRAP_DRAWS - 1))],
    }


def summarize_runs(rows: Sequence[dict]) -> dict:
    primary = [row for row in rows if not row["provider_error_protocol"]]
    passed = sum(row["verifier_pass"] for row in primary)
    low, high = wilson(passed, len(primary))
    scheduled_pass = sum(row["verifier_pass"] and not row["provider_error_protocol"] for row in rows)
    sensitivity_low, sensitivity_high = wilson(scheduled_pass, len(rows))
    output = {
        "scheduled": len(rows),
        "provider_error_protocol": len(rows) - len(primary),
        "primary_n": len(primary),
        "verifier_pass": passed,
        "verifier_pass_rate": passed / len(primary) if primary else None,
        "wilson_low": low,
        "wilson_high": high,
        "sensitivity_n": len(rows),
        "sensitivity_pass": scheduled_pass,
        "sensitivity_pass_rate": scheduled_pass / len(rows) if rows else None,
        "sensitivity_wilson_low": sensitivity_low,
        "sensitivity_wilson_high": sensitivity_high,
        "legacy_pass": sum(row["legacy_pass"] for row in primary),
    }
    for flag in FLAGS:
        output[flag] = sum(bool(row[flag]) for row in rows)
    return output


def emit_csv(name: str, rows: list[dict]) -> Path:
    TABLES.mkdir(parents=True, exist_ok=True)
    path = TABLES / f"{name}.csv"
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    markdown = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        markdown.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    (TABLES / f"{name}.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    return path


def grouped_summary(rows: list[dict]) -> list[dict]:
    output: list[dict] = []
    keys = sorted({(row["model"], row["condition"]) for row in rows}, key=lambda x: (MODELS.index(x[0]), CONDITIONS.index(x[1])))
    for model, condition in keys:
        selected = [row for row in rows if row["model"] == model and row["condition"] == condition]
        for split in ("all", "test_in", "test_out"):
            subset = selected if split == "all" else [row for row in selected if row["split"] == split]
            if subset:
                output.append({"model": model, "condition": condition, "split": split, **summarize_runs(subset)})
    return output


def task_cells(rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row["model"], row["task"], row["condition"])].append(row)
    output: list[dict] = []
    for (model, task, condition), values in sorted(groups.items()):
        summary = summarize_runs(values)
        output.append({"model": model, "task": task, "split": values[0]["split"], "skill": values[0]["skill"], "condition": condition, **summary})
    return output


def paired_comparisons(cells: list[dict]) -> list[dict]:
    lookup = {(row["model"], row["task"], row["condition"]): row for row in cells}
    scopes = [
        ("all", lambda row: True),
        ("test_in", lambda row: row["split"] == "test_in"),
        ("test_out", lambda row: row["split"] == "test_out"),
        ("all_excluding_b09_phone", lambda row: row["task"] != "test_in_b09_phone"),
        ("test_in_excluding_b09_phone", lambda row: row["split"] == "test_in" and row["task"] != "test_in_b09_phone"),
    ]
    output: list[dict] = []
    for model in MODELS:
        for scope, predicate in scopes:
            differences: list[float] = []
            sensitivity: list[float] = []
            for (cell_model, task, condition), c0 in lookup.items():
                if cell_model != model or condition != "C0" or not predicate(c0):
                    continue
                c1 = lookup.get((model, task, "C1"))
                if not c1:
                    continue
                if c0["verifier_pass_rate"] is not None and c1["verifier_pass_rate"] is not None:
                    differences.append(c1["verifier_pass_rate"] - c0["verifier_pass_rate"])
                sensitivity.append(c1["sensitivity_pass_rate"] - c0["sensitivity_pass_rate"])
            primary = bootstrap(differences, BOOTSTRAP_SEED)
            scheduled = bootstrap(sensitivity, BOOTSTRAP_SEED + 1)
            output.append({
                "model": model,
                "scope": scope,
                "contrast": "C1-C0",
                **primary,
                "sensitivity_n_tasks": scheduled["n_tasks"],
                "sensitivity_mean_difference": scheduled["mean_difference"],
                "sensitivity_bootstrap_low": scheduled["bootstrap_low"],
                "sensitivity_bootstrap_high": scheduled["bootstrap_high"],
                "reference_anchor": model == "gpt-5.6-sol",
            })
    return output


def task_distribution(cells: list[dict]) -> list[dict]:
    lookup = {(row["model"], row["task"], row["condition"]): row for row in cells}
    tasks = sorted({row["task"] for row in cells})
    output: list[dict] = []
    controlled = [model for model in MODELS if model != "gpt-5.6-sol"]
    for task in tasks:
        first = next(row for row in cells if row["task"] == task)
        row: dict[str, object] = {"task": task, "split": first["split"], "skill": first["skill"]}
        observed: list[float] = []
        for model in MODELS:
            for condition in ("C0", "C1"):
                cell = lookup.get((model, task, condition))
                rate = cell["verifier_pass_rate"] if cell else None
                row[f"{model}_{condition}"] = rate
                if model in controlled and rate is not None:
                    observed.append(float(rate))
        row["controlled_all_zero"] = bool(observed and all(value == 0 for value in observed))
        row["controlled_all_one"] = bool(observed and all(value == 1 for value in observed))
        output.append(row)
    return output


def process_summary(rows: list[dict]) -> list[dict]:
    metrics = [
        "steps",
        "assistant_turns",
        "first_edit_position",
        "validated_after_last_edit_intent",
        "validated_after_last_edit_success",
        "write_file_rewrite_count",
        "loop_count",
        "partial_delta_seed",
        "total_tokens",
    ]
    output: list[dict] = []
    for model, condition in sorted({(row["model"], row["condition"]) for row in rows}, key=lambda x: (MODELS.index(x[0]), CONDITIONS.index(x[1]))):
        selected = [row for row in rows if row["model"] == model and row["condition"] == condition and not row["provider_error_protocol"] and row.get("activation") is not None]
        for metric in metrics:
            values = [float(row[metric]) for row in selected if row.get(metric) is not None]
            output.append({
                "model": model,
                "condition": condition,
                "metric": metric,
                "n": len(values),
                "mean": sum(values) / len(values) if values else None,
                "median": quantile(values, 0.5),
                "q1": quantile(values, 0.25),
                "q3": quantile(values, 0.75),
            })
    return output


def activation_summary(rows: list[dict]) -> list[dict]:
    output: list[dict] = []
    for model, condition in sorted({(row["model"], row["condition"]) for row in rows}, key=lambda x: (MODELS.index(x[0]), CONDITIONS.index(x[1]))):
        selected = [row for row in rows if row["model"] == model and row["condition"] == condition and not row["provider_error_protocol"]]
        labels = Counter(row["activation"] for row in selected)
        for label in ("explicit", "observable_inferred", "not_observed"):
            output.append({"model": model, "condition": condition, "activation": label, "count": labels[label], "n": len(selected), "rate": labels[label] / len(selected) if selected else None})
    return output


def process_paired(rows: list[dict]) -> list[dict]:
    """Task-paired process contrasts; qwen generated the C1/C0 hypothesis."""
    metrics = [
        "validated_after_last_edit_intent",
        "validated_after_last_edit_success",
        "steps",
        "write_file_rewrite_count",
        "loop_count",
    ]
    scopes = [
        ("all", lambda row: True),
        ("test_in", lambda row: row["split"] == "test_in"),
        ("test_out", lambda row: row["split"] == "test_out"),
    ]
    contrasts = [(model, "C1", "C0", "C1-C0") for model in MODELS if model != "gpt-5.6-sol"]
    contrasts.append(("qwen3.5:9b", "v1", "C1", "v1-C1"))
    output: list[dict] = []
    for model, treatment, control, label in contrasts:
        for scope, predicate in scopes:
            if label == "v1-C1" and scope != "test_in":
                continue
            selected = [row for row in rows if row["model"] == model and predicate(row) and not row["provider_error_protocol"]]
            for metric in metrics:
                by_cell: dict[tuple[str, str], list[float]] = defaultdict(list)
                for row in selected:
                    if row["condition"] not in (treatment, control) or row.get(metric) is None:
                        continue
                    by_cell[(row["task"], row["condition"])].append(float(row[metric]))
                differences: list[float] = []
                for task in sorted({task for task, _ in by_cell}):
                    treated = by_cell.get((task, treatment), [])
                    reference = by_cell.get((task, control), [])
                    if treated and reference:
                        differences.append(sum(treated) / len(treated) - sum(reference) / len(reference))
                summary = bootstrap(differences, BOOTSTRAP_SEED + 20)
                output.append({"model": model, "scope": scope, "contrast": label, "metric": metric, **summary, "hypothesis_source": "qwen monitoring" if model == "qwen3.5:9b" and label == "C1-C0" else "independent S7 test"})
    return output


def exploratory(cells: list[dict], rows: list[dict]) -> list[dict]:
    lookup = {(row["model"], row["task"], row["condition"]): row for row in cells}
    output: list[dict] = []
    for label, treatment, control, split in (
        ("v1_vs_C1_test_in", "v1", "C1", "test_in"),
        ("L3b_vs_C1_all", "l3b", "C1", "all"),
        ("L3b_vs_C1_test_in", "l3b", "C1", "test_in"),
        ("L3b_vs_C1_test_out", "l3b", "C1", "test_out"),
    ):
        differences: list[float] = []
        sensitivity: list[float] = []
        for (model, task, condition), treated in lookup.items():
            if model != "qwen3.5:9b" or condition != treatment or (split != "all" and treated["split"] != split):
                continue
            reference = lookup.get((model, task, control))
            if not reference:
                continue
            if treated["verifier_pass_rate"] is not None and reference["verifier_pass_rate"] is not None:
                differences.append(treated["verifier_pass_rate"] - reference["verifier_pass_rate"])
            sensitivity.append(treated["sensitivity_pass_rate"] - reference["sensitivity_pass_rate"])
        primary = bootstrap(differences, BOOTSTRAP_SEED + 2)
        scheduled = bootstrap(sensitivity, BOOTSTRAP_SEED + 3)
        output.append({"comparison": label, "layer": "unconditional_descriptive", **primary, "sensitivity_mean_difference": scheduled["mean_difference"], "sensitivity_low": scheduled["bootstrap_low"], "sensitivity_high": scheduled["bootstrap_high"]})

    for condition in ("C1", "l3b"):
        selected = [row for row in rows if row["model"] == "qwen3.5:9b" and row["condition"] == condition and not row["provider_error_protocol"]]
        for layer, predicate in (("A_reached_call_32", lambda row: row["steps"] >= 32), ("B_ended_before_32", lambda row: row["steps"] < 32)):
            subset = [row for row in selected if predicate(row)]
            output.append({
                "comparison": f"{condition}_call32_stratum",
                "layer": layer,
                "n_tasks": len({row["task"] for row in subset}),
                "runs": len(subset),
                "verifier_pass": sum(row["verifier_pass"] for row in subset),
                "verifier_pass_rate": sum(row["verifier_pass"] for row in subset) / len(subset) if subset else None,
                "validation_after_edit": sum(row["validated_after_last_edit_intent"] for row in subset),
                "explicit_activation": sum(row["activation"] == "explicit" for row in subset),
                "mechanism_note": "post-assignment descriptive stratum; not an effect estimate",
            })
    return output


def main() -> None:
    manifest = enforce_formal_s7_gate(ROOT / "STATUS.md", ROOT / "analysis" / "analysis_patch_manifest.json")
    baselines = seed_partial_baselines()
    rows: list[dict] = []
    event_errors: list[dict] = []
    for metadata_path in sorted(RUNS.glob("s7-*/metadata.json")):
        row, errors = read_run(metadata_path.parent, baselines)
        rows.append(row)
        event_errors.extend(errors)
    if len(rows) != 870:
        raise RuntimeError(f"expected 870 S7 records, found {len(rows)}")
    if sum(row["verifier_available"] for row in rows) != 870:
        raise RuntimeError("every S7 run must expose verifier.json.passed")

    grouped = grouped_summary(rows)
    cells = task_cells(rows)
    paired = paired_comparisons(cells)
    tasks = task_distribution(cells)
    process = process_summary(rows)
    activation = activation_summary(rows)
    exploratory_rows = exploratory(cells, rows)
    process_pairs = process_paired(rows)

    OUT.mkdir(parents=True, exist_ok=True)
    run_csv = OUT / "run_metrics.csv"
    with run_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    table_paths = [
        emit_csv("S7_T1_model_condition_summary", grouped),
        emit_csv("S7_T2_core_paired_differences", paired),
        emit_csv("S7_T3_task_distribution", tasks),
        emit_csv("S7_T4_process_metrics", process),
        emit_csv("S7_T5_activation", activation),
        emit_csv("S7_T6_exploratory", exploratory_rows),
        emit_csv("S7_T7_process_paired", process_pairs),
    ]
    audit = {
        "analysis_version": VERSION,
        "analysis_source_sha256": sha256(Path(__file__)),
        "verifier_pass_patch": manifest,
        "bootstrap": {"draws": BOOTSTRAP_DRAWS, "seed": BOOTSTRAP_SEED, "unit": "task"},
        "run_count": len(rows),
        "verifier_available": sum(row["verifier_available"] for row in rows),
        "provider_error_protocol": sum(row["provider_error_protocol"] for row in rows),
        "event_parse_errors": event_errors,
        "raw_event_files_missing": sum(not (RUNS / row["run_id"] / "events.jsonl").exists() for row in rows),
        "tables": {path.name: sha256(path) for path in table_paths},
        "run_metrics_sha256": sha256(run_csv),
        "notes": [
            "GPT is an uncontrolled Codex reference anchor and is never pooled with r2 comparisons.",
            "v1 and L3b are exploratory; call-32 strata are post-assignment descriptive strata.",
            "Malformed event lines are skipped only for process metrics and listed above; verifier outcomes are unaffected.",
        ],
    }
    (OUT / "analysis_manifest.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"runs": len(rows), "tables": len(table_paths), "provider_error_protocol": audit["provider_error_protocol"], "event_parse_errors": len(event_errors), "output": str(OUT)}))


if __name__ == "__main__":
    main()
