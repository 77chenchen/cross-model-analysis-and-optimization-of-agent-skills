#!/usr/bin/env python3
"""Build report-only supplements from frozen S4 and formal S7 artifacts.

This module does not run models or verifiers.  It treats
``verifier.json.passed`` as the outcome and excludes retry-exhausted transport
errors from primary denominators.  S7 task-paired bootstrap values already
published by the locked formal analysis are not regenerated here.
"""
from __future__ import annotations

import csv
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

from analysis.verifier_pass_v2 import ROOT, provider_error_protocol

VERSION = "report-supplements-v1.0.0"
SEED = 20261011
BOOTSTRAP_DRAWS = 10_000

S7_METRICS = ROOT / "results" / "s7" / "run_metrics.csv"
S4_RUNS = ROOT / "data" / "b3_s4_r2_runs"
TABLES = ROOT / "results" / "tables" / "report"
DOC = ROOT / "docs" / "behavior_outcome_crosstab.md"
TAXONOMY_DOC = ROOT / "docs" / "weak_failure_taxonomy.md"
JUDGE_MANIFEST = ROOT / "data" / "b5_r2_blinded_packets" / "b5_r2_private_manifest.json"
JUDGE_ANNOTATIONS = ROOT / "data" / "b5_r2_blinded_annotations"

STRONG = {"gemma4:26b", "qwen3.8:27b", "qwen3-coder-next"}
WEAK = "qwen3.5:9b"
DEV_DIAGNOSE = {
    "pilot_a01_label_parser",
    "pilot_a03_record_deduplication",
    "pilot_a05_version_parser",
    "pilot_b01_csv_cleaning",
    "pilot_b03_duplicate_audit",
    "pilot_b05_date_validation",
}
VALIDATION_INTENT = re.compile(r"pytest|unittest|\btest\b|py_compile|python[0-9.]*\s+.*\.py", re.I)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_bool(value: object) -> bool:
    return str(value).strip().lower() == "true"


def quantile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * p
    lo, hi = math.floor(position), math.ceil(position)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] * (hi - position) + ordered[hi] * (position - lo)


def summary(values: list[float]) -> dict[str, float | int]:
    return {
        "n": len(values),
        "median": median(values),
        "q1": quantile(values, 0.25),
        "q3": quantile(values, 0.75),
    }


def emit(name: str, rows: list[dict]) -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    with (TABLES / f"{name}.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    lines.extend("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |" for row in rows)
    (TABLES / f"{name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def fmt_iqr(values: list[float], percentage: bool = False) -> str:
    item = summary(values)
    factor = 100 if percentage else 1
    suffix = "%" if percentage else ""
    return f"{item['median'] * factor:.1f} [{item['q1'] * factor:.1f}, {item['q3'] * factor:.1f}]{suffix}"


def strong_weak_process(rows: list[dict[str, str]]) -> list[dict]:
    output: list[dict] = []
    for cohort, models, repeats in (("strong", STRONG, 3), ("weak", {WEAK}, 5)):
        for condition in ("C0", "C1"):
            selected = [
                row for row in rows
                if row["model"] in models
                and row["condition"] == condition
                and not as_bool(row["provider_error_protocol"])
            ]
            numeric = lambda key: [float(row[key]) for row in selected if row.get(key, "") != ""]
            binary = lambda key: [float(as_bool(row[key])) for row in selected if row.get(key, "") != ""]
            timeout = binary("timeout")
            rewrite = [float(float(row["write_file_rewrite_count"]) > 0) for row in selected if row.get("write_file_rewrite_count", "") != ""]
            validation_intent = binary("validated_after_last_edit_intent")
            validation_success = binary("validated_after_last_edit_success")
            output.append({
                "cohort": cohort,
                "condition": condition,
                "models": 3 if cohort == "strong" else 1,
                "tasks": 18,
                "repetitions": repeats,
                "scheduled_n": 18 * repeats * len(models),
                "usable_n": len(selected),
                "steps_median_iqr": fmt_iqr(numeric("steps")),
                # r2 defines a step as a parsed tool result, so this equals tool calls.
                "tool_calls_median_iqr": fmt_iqr(numeric("steps")),
                "assistant_turns_median_iqr": fmt_iqr(numeric("assistant_turns")),
                "validation_intent_median_iqr": fmt_iqr(validation_intent, True),
                "validation_intent_rate": sum(validation_intent) / len(validation_intent),
                "validation_success_median_iqr": fmt_iqr(validation_success, True),
                "validation_success_rate": sum(validation_success) / len(validation_success),
                "rewrite_any_median_iqr": fmt_iqr(rewrite, True),
                "rewrite_any_rate": sum(rewrite) / len(rewrite),
                "timeout_median_iqr": fmt_iqr(timeout, True),
                "timeout_rate": sum(timeout) / len(timeout),
            })
    return output


def safe_events(path: Path) -> list[dict]:
    events: list[dict] = []
    if not path.exists():
        return events
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)
    return events


def tool_path(event: dict) -> str:
    try:
        return str(json.loads(event.get("arguments") or "{}").get("path") or "")
    except json.JSONDecodeError:
        return ""


def behavior_flags(events: list[dict]) -> dict[str, bool]:
    tools = [event for event in events if event.get("event") == "tool_result"]
    writes = [
        (index, event) for index, event in enumerate(tools, 1)
        if event.get("tool_name") == "write_file" and (event.get("result") or {}).get("ok") is True
    ]
    reads = [
        index for index, event in enumerate(tools, 1)
        if event.get("tool_name") == "read_file" and (event.get("result") or {}).get("ok") is True
    ]
    validation_intent = [
        index for index, event in enumerate(tools, 1)
        if event.get("tool_name") == "run_command"
        and VALIDATION_INTENT.search(str(event.get("arguments") or ""))
    ]
    paths = Counter(tool_path(event) for _, event in writes)
    first_write = writes[0][0] if writes else None
    last_write = writes[-1][0] if writes else None
    return {
        "read_before_edit": bool(writes and any(index < first_write for index in reads)),
        "validation_after_edit": bool(writes and any(index > last_write for index in validation_intent)),
        # No edit is not credited as avoiding a rewrite.
        "avoids_rewrite": bool(writes and all(count == 1 for count in paths.values())),
        "reread_after_edit": bool(writes and any(index > last_write for index in reads)),
    }


def s4_behavior_rows() -> tuple[list[dict], list[dict]]:
    runs: list[dict] = []
    excluded: list[dict] = []
    for metadata_path in sorted(S4_RUNS.glob("*/metadata.json")):
        run_dir = metadata_path.parent
        metadata = load(metadata_path)
        task = metadata.get("task_id")
        model = metadata.get("requested_model_id")
        if task not in DEV_DIAGNOSE or model not in STRONG | {WEAK}:
            continue
        runtime = load(run_dir / "runtime_r2.json") or load(run_dir / "runtime.json")
        if provider_error_protocol(metadata, runtime):
            excluded.append({"run_id": metadata.get("run_id", run_dir.name), "reason": "provider_error_protocol"})
            continue
        verifier = load(run_dir / "verifier.json")
        cohort = "strong" if model in STRONG else "weak"
        outcome = "pass" if verifier.get("passed") is True else "fail"
        runs.append({
            "run_id": metadata.get("run_id", run_dir.name),
            "task": task,
            "model": model,
            "cell": f"{cohort}-{outcome}",
            **behavior_flags(safe_events(run_dir / "events.jsonl")),
        })
    return runs, excluded


def behavior_crosstab() -> tuple[list[dict], list[dict], list[dict]]:
    runs, excluded = s4_behavior_rows()
    behaviors = ["read_before_edit", "validation_after_edit", "avoids_rewrite", "reread_after_edit"]
    cells = ["strong-pass", "strong-fail", "weak-pass", "weak-fail"]
    output: list[dict] = []
    for behavior in behaviors:
        row: dict[str, object] = {"behavior": behavior}
        for cell in cells:
            selected = [run for run in runs if run["cell"] == cell]
            count = sum(bool(run[behavior]) for run in selected)
            row[f"{cell}_count"] = count
            row[f"{cell}_n"] = len(selected)
            row[f"{cell}_rate"] = count / len(selected) if selected else None
        output.append(row)
    return output, runs, excluded


def write_behavior_doc(rows: list[dict], runs: list[dict], excluded: list[dict]) -> None:
    labels = {
        "read_before_edit": "Read before edit",
        "validation_after_edit": "Validation after last edit (intent)",
        "avoids_rewrite": "Avoid repeated full-file write",
        "reread_after_edit": "Reread after last edit",
    }
    lines = [
        "# Behavior--outcome cross-tab",
        "",
        "> Scope: S4 `dev_diagnose`, v0 only; descriptive and post hoc. Strong is",
        "> gemma4:26b, qwen3.8:27b, and qwen3-coder-next; weak is qwen3.5:9b.",
        "> The outcome is `verifier.json.passed`. Retry-exhausted provider errors",
        "> are excluded from the primary cells.",
        "",
        "| Mechanical behavior | Strong pass | Strong fail | Weak pass | Weak fail |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        cells = []
        for cell in ("strong-pass", "strong-fail", "weak-pass", "weak-fail"):
            count, n = row[f"{cell}_count"], row[f"{cell}_n"]
            cells.append(f"{count}/{n} ({100 * row[f'{cell}_rate']:.1f}%)")
        lines.append(f"| {labels[row['behavior']]} | " + " | ".join(cells) + " |")
    lines.extend([
        "",
        "## Mechanical definitions",
        "",
        "- **Read before edit:** a successful `read_file` occurs before the first successful `write_file`.",
        "- **Validation after last edit (intent):** after the last successful `write_file`, a `run_command` argument matches the frozen validation-intent rule (`test`, `pytest`, `unittest`, `py_compile`, or a Python invocation of a `.py` file). Command success is not required by this intent indicator.",
        "- **Avoid repeated full-file write:** the run edits at least once and no path receives more than one successful `write_file`. A no-edit run is not credited.",
        "- **Reread after last edit:** a successful `read_file` occurs after the last successful `write_file`.",
        "",
        f"The table contains {len(runs)} usable runs; {len(excluded)} retry-exhausted provider-error run(s) were excluded.",
        "The four cells are observational strata, not randomized conditions, so their differences are mechanism descriptions rather than effect estimates.",
    ])
    DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def task_cells(rows: list[dict[str, str]], model: str) -> dict[tuple[str, str], list[int]]:
    cells: dict[tuple[str, str], list[int]] = defaultdict(list)
    for row in rows:
        if row["model"] != model or row["condition"] not in {"C0", "C1"}:
            continue
        if as_bool(row["provider_error_protocol"]):
            continue
        cells[(row["task"], row["condition"])].append(int(as_bool(row["verifier_pass"])))
    return cells


def paired_bootstrap(values: list[float], seed: int) -> tuple[float | None, float | None, float | None]:
    if not values:
        return None, None, None
    rng = random.Random(seed)
    draws = sorted(sum(rng.choice(values) for _ in values) / len(values) for _ in range(BOOTSTRAP_DRAWS))
    return sum(values) / len(values), draws[int(0.025 * (BOOTSTRAP_DRAWS - 1))], draws[int(0.975 * (BOOTSTRAP_DRAWS - 1))]


def informative_task_sensitivity(rows: list[dict[str, str]]) -> list[dict]:
    output: list[dict] = []
    models = [WEAK, *sorted(STRONG), "llama3.1:8b", "gpt-5.6-sol"]
    for offset, model in enumerate(models):
        cells = task_cells(rows, model)
        values: list[float] = []
        excluded_zero = excluded_one = 0
        tasks = sorted({task for task, _ in cells})
        for task in tasks:
            c0, c1 = cells.get((task, "C0"), []), cells.get((task, "C1"), [])
            if not c0 or not c1:
                continue
            p0, p1 = sum(c0) / len(c0), sum(c1) / len(c1)
            if p0 == p1 == 0:
                excluded_zero += 1
                continue
            if p0 == p1 == 1:
                excluded_one += 1
                continue
            values.append(p1 - p0)
        mean, low, high = paired_bootstrap(values, SEED + offset)
        output.append({
            "model": model,
            "rule": "post-hoc: exclude task pairs with C0=C1=0 or C0=C1=1",
            "retained_tasks": len(values),
            "excluded_all_zero": excluded_zero,
            "excluded_all_one": excluded_one,
            "C1_minus_C0_pp": None if mean is None else 100 * mean,
            "bootstrap_low_pp": None if low is None else 100 * low,
            "bootstrap_high_pp": None if high is None else 100 * high,
            "reference_anchor": model == "gpt-5.6-sol",
        })
    return output


def minimum_detectable_effect(rows: list[dict[str, str]]) -> list[dict]:
    """Within-task repeated-Bernoulli planning approximation.

    For each task/condition cell with three repeats, estimate the unbiased
    Bernoulli sample variance.  Treat C0/C1 repetitions as independent within
    task, divide by three for each cell mean, then divide the average paired
    within-task variance by 18 tasks.  The 80%-power, two-sided 5% MDE is
    (1.96 + 0.8416) * SE.  This is descriptive, not a power guarantee.
    """
    output: list[dict] = []
    for model in [*sorted(STRONG), "llama3.1:8b"]:
        cells = task_cells(rows, model)
        pair_variances: list[float] = []
        for task in sorted({task for task, _ in cells}):
            c0, c1 = cells.get((task, "C0"), []), cells.get((task, "C1"), [])
            if len(c0) != 3 or len(c1) != 3:
                continue
            def sample_variance(values: list[int]) -> float:
                center = sum(values) / len(values)
                return sum((value - center) ** 2 for value in values) / (len(values) - 1)
            pair_variances.append(sample_variance(c0) / 3 + sample_variance(c1) / 3)
        average = sum(pair_variances) / len(pair_variances)
        se = math.sqrt(average / len(pair_variances))
        output.append({
            "model": model,
            "tasks": len(pair_variances),
            "repetitions_per_condition": 3,
            "mean_within_task_variance_of_paired_rate": average,
            "standard_error_within_only": se,
            "approx_mde_pp_80pct_power": 100 * (1.959964 + 0.841621) * se,
            "degenerate_floor_warning": average == 0,
        })
    return output


def retry_distribution(rows: list[dict[str, str]]) -> list[dict]:
    counts: Counter[tuple[str, str, str]] = Counter()
    for row in rows:
        if row["model"] == WEAK and as_bool(row["provider_error_protocol"]):
            counts[(row["condition"], row["split"], row["task"])] += 1
    return [
        {"condition": condition, "split": split, "task": task, "retry_exhausted": count}
        for (condition, split, task), count in sorted(counts.items())
    ]


def weak_failure_taxonomy(rows: list[dict[str, str]]) -> list[dict]:
    """Summarize only the three judge labels permitted as conclusion evidence.

    Labels are non-exclusive.  A failure with none of the three permitted
    labels, including a run never sent to the frozen judge, is counted once in
    ``other_or_unlabeled``.
    """
    reliable = ("file_corruption", "tool_misuse", "missed_constraint")
    packet_for_run = {item["run_id"]: item["packet_id"] for item in load(JUDGE_MANIFEST)}
    judge_for_run: dict[str, set[str]] = {}
    for run_id, packet_id in packet_for_run.items():
        annotation = load(JUDGE_ANNOTATIONS / f"{packet_id}.json")
        judge_for_run[run_id] = set(annotation.get("failure_modes") or [])

    s4_runs, _ = s4_behavior_rows()
    cohorts: dict[str, list[str]] = {
        "S4 dev_diagnose": [run["run_id"] for run in s4_runs if run["cell"] == "weak-fail"],
        "S7 C0": [
            row["run_id"] for row in rows
            if row["model"] == WEAK and row["condition"] == "C0"
            and not as_bool(row["provider_error_protocol"])
            and not as_bool(row["verifier_pass"])
        ],
        "S7 C1": [
            row["run_id"] for row in rows
            if row["model"] == WEAK and row["condition"] == "C1"
            and not as_bool(row["provider_error_protocol"])
            and not as_bool(row["verifier_pass"])
        ],
    }
    cohorts["Combined"] = [run_id for name, run_ids in cohorts.items() if name != "Combined" for run_id in run_ids]

    output: list[dict] = []
    for cohort, run_ids in cohorts.items():
        label_sets = [judge_for_run.get(run_id, set()) for run_id in run_ids]
        output.append({
            "cohort": cohort,
            "failed_runs_n": len(run_ids),
            "judge_covered_n": sum(run_id in judge_for_run for run_id in run_ids),
            **{label: sum(label in labels for labels in label_sets) for label in reliable},
            "other_or_unlabeled": sum(not (set(reliable) & labels) for labels in label_sets),
        })
    return output


def write_taxonomy_doc(rows: list[dict]) -> None:
    lines = [
        "# Weak-model failure taxonomy",
        "",
        "> Scope: verifier-failing qwen3.5:9b runs in S4 `dev_diagnose` and",
        "> formal S7 C0/C1. Retry-exhausted transport errors are excluded.",
        "> The only judge labels used are `file_corruption`, `tool_misuse`, and",
        "> `missed_constraint`, the three labels permitted as conclusion evidence",
        "> by the human--judge agreement audit.",
        "",
        "| Cohort | Failed runs n | Judge-covered n | File corruption | Tool misuse | Missed constraint | Other / unlabeled |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['cohort']} | {row['failed_runs_n']} | {row['judge_covered_n']} | "
            f"{row['file_corruption']} | {row['tool_misuse']} | {row['missed_constraint']} | "
            f"{row['other_or_unlabeled']} |"
        )
    lines.extend([
        "",
        "Labels are non-exclusive, so the three named columns can overlap. `Other / unlabeled` means that none of the three reliable labels was present; it includes failures outside the existing blinded judge sample. No new judge request was made. Consequently, the S7 rows primarily document missing taxonomy coverage and must not be read as evidence that the three failure modes were absent.",
    ])
    TAXONOMY_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = read_csv(S7_METRICS)
    process = strong_weak_process(rows)
    behavior, behavior_runs, behavior_excluded = behavior_crosstab()
    mde = minimum_detectable_effect(rows)
    informative = informative_task_sensitivity(rows)
    retries = retry_distribution(rows)
    taxonomy = weak_failure_taxonomy(rows)

    emit("strong_weak_process", process)
    emit("behavior_outcome_crosstab", behavior)
    emit("minimum_detectable_effect", mde)
    emit("posthoc_informative_task_sensitivity", informative)
    emit("qwen_retry_exhausted_distribution", retries)
    emit("weak_failure_taxonomy", taxonomy)
    write_behavior_doc(behavior, behavior_runs, behavior_excluded)
    write_taxonomy_doc(taxonomy)
    print(json.dumps({
        "version": VERSION,
        "tables": 6,
        "behavior_runs": len(behavior_runs),
        "behavior_excluded": len(behavior_excluded),
        "weak_failures": taxonomy[-1]["failed_runs_n"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
