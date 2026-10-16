#!/usr/bin/env python3
"""Create paper-facing S8-b task-paired summaries from existing run metrics.

This module is analysis-only. It does not invoke a model or modify locked S8-b
assets. Retry-exhausted provider errors are excluded before task aggregation,
matching the locked primary-outcome denominator.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results" / "tables" / "s8b" / "S8B_run_metrics.csv"
OUT = ROOT / "results" / "tables" / "s8b"
CONDITIONS = ("C1", "externalized", "imitation", "generic_control")
TREATMENTS = CONDITIONS[:-1]
METRICS = (
    "validated_after_last_edit",
    "reread_after_edit",
    "write_file_rewrite_count",
    "loop_count",
    "steps",
)
BINARY_METRICS = {
    "validated_after_last_edit",
    "reread_after_edit",
}
SEED = 20261016
BOOTSTRAP_DRAWS = 10_000


def read_rows() -> list[dict[str, str]]:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def paired_bootstrap(values: np.ndarray, seed: int) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    n = len(values)
    draws = values[rng.integers(0, n, size=(BOOTSTRAP_DRAWS, n))].mean(axis=1)
    return float(values.mean()), float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = read_rows()
    usable = [row for row in rows if row["provider_error_protocol"].lower() == "false"]
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in usable:
        grouped[(row["task"], row["condition"])].append(row)

    tasks = sorted({row["task"] for row in usable})
    missing = [(task, condition) for task in tasks for condition in CONDITIONS if not grouped[(task, condition)]]
    if missing:
        raise RuntimeError(f"missing usable task-condition cells: {missing}")

    task_rows: list[dict[str, object]] = []
    cell_means: dict[tuple[str, str, str], float] = {}
    for task in tasks:
        for condition in CONDITIONS:
            cell = grouped[(task, condition)]
            out: dict[str, object] = {
                "task": task,
                "condition": condition,
                "usable_runs": len(cell),
                "verifier_pass_rate": np.mean([row["verifier_pass"].lower() == "true" for row in cell]),
            }
            for metric in METRICS:
                values = [
                    float(row[metric].lower() == "true") if metric in BINARY_METRICS else float(row[metric])
                    for row in cell if row[metric] != ""
                ]
                out[metric] = float(np.mean(values)) if values else ""
                if values:
                    cell_means[(task, condition, metric)] = float(np.mean(values))
            task_rows.append(out)

    task_fields = ["task", "condition", "usable_runs", "verifier_pass_rate", *METRICS]
    write_csv(OUT / "S8B_T4_task_condition_metrics.csv", task_rows, task_fields)

    contrast_rows: list[dict[str, object]] = []
    for treatment_index, treatment in enumerate(TREATMENTS):
        for metric_index, metric in enumerate(METRICS):
            paired_tasks = [
                task for task in tasks
                if (task, treatment, metric) in cell_means and (task, "generic_control", metric) in cell_means
            ]
            differences = np.asarray([
                cell_means[(task, treatment, metric)] - cell_means[(task, "generic_control", metric)]
                for task in paired_tasks
            ], dtype=float)
            estimate, low, high = paired_bootstrap(
                differences,
                SEED + 100 * treatment_index + metric_index,
            )
            contrast_rows.append({
                "contrast": f"{treatment}-generic_control",
                "metric": metric,
                "n_tasks": len(paired_tasks),
                "mean_difference": estimate,
                "bootstrap_low": low,
                "bootstrap_high": high,
                "bootstrap_draws": BOOTSTRAP_DRAWS,
                "bootstrap_seed": SEED + 100 * treatment_index + metric_index,
            })

    contrast_fields = [
        "contrast", "metric", "n_tasks", "mean_difference", "bootstrap_low",
        "bootstrap_high", "bootstrap_draws", "bootstrap_seed",
    ]
    write_csv(OUT / "S8B_T5_process_paired_differences.csv", contrast_rows, contrast_fields)
    write_markdown(
        OUT / "S8B_T5_process_paired_differences.md",
        ["Contrast", "Metric", "Tasks", "Mean difference", "95% paired bootstrap"],
        [[
            str(row["contrast"]), str(row["metric"]), str(row["n_tasks"]),
            f"{float(row['mean_difference']):.4f}",
            f"[{float(row['bootstrap_low']):.4f}, {float(row['bootstrap_high']):.4f}]",
        ] for row in contrast_rows],
    )

    provider_rows: list[dict[str, object]] = []
    for condition in CONDITIONS:
        all_condition = [row for row in rows if row["condition"] == condition]
        provider_rows.append({
            "condition": condition,
            "scheduled": len(all_condition),
            "provider_error_protocol": sum(row["provider_error_protocol"].lower() == "true" for row in all_condition),
            "usable": sum(row["provider_error_protocol"].lower() == "false" for row in all_condition),
        })
    write_csv(
        OUT / "S8B_T6_provider_error_accounting.csv",
        provider_rows,
        ["condition", "scheduled", "provider_error_protocol", "usable"],
    )

    products = [
        OUT / "S8B_T4_task_condition_metrics.csv",
        OUT / "S8B_T5_process_paired_differences.csv",
        OUT / "S8B_T5_process_paired_differences.md",
        OUT / "S8B_T6_provider_error_accounting.csv",
    ]
    manifest = {
        "version": "s8b-paper-analysis-v1.0.0",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "primary_denominator": "exclude provider_error_protocol; include timeout and max_steps_reached",
        "sampling_unit": "task after averaging repetitions within task-condition cells",
        "bootstrap_draws": BOOTSTRAP_DRAWS,
        "products": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in products
        },
    }
    (OUT / "S8B_paper_analysis_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(task_rows)} task-condition rows and {len(contrast_rows)} paired process rows")


if __name__ == "__main__":
    main()
