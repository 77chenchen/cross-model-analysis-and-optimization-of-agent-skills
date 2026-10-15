#!/usr/bin/env python3
"""Predeclared task-paired analysis for the fresh-task S8-b study."""
from __future__ import annotations

import csv
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "data" / "s8b_runs"
OUT = ROOT / "results" / "tables" / "s8b"
CONDITIONS = ("C1", "externalized", "imitation", "generic_control")
BOOTSTRAP_SEED = 20261016
BOOTSTRAP_DRAWS = 10_000
VALIDATION = re.compile(r"pytest|unittest|\btest\b|py_compile|python[0-9.]*\s+.*\.py", re.I)
PHRASES = {
    "read": re.compile(r"\b(read|inspect|open|review)\b", re.I),
    "targeted": re.compile(r"\b(targeted|minimal|small|avoid(?:ing)?\s+(?:a\s+)?(?:whole|full)[ -]?file\s+rewrit)", re.I),
    "validate": re.compile(r"\b(validat|verif|test|check)\w*\b", re.I),
    "reread": re.compile(r"\b(re-?read|read\s+(?:the\s+)?final|inspect\s+(?:the\s+)?final)\b", re.I),
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def events(path: Path) -> list[dict]:
    output = []
    if path.is_file():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                output.append(value)
    return output


def response_text(run_dir: Path) -> dict[int, str]:
    output = {}
    for index, path in enumerate(sorted((run_dir / "raw_responses").glob("response_*.json")), 1):
        payload = load(path)
        message = ((payload.get("choices") or [{}])[0].get("message") or {})
        output[index] = "\n".join(str(message.get(key) or "") for key in ("content", "reasoning"))
    return output


def provider_error_protocol(metadata: dict, runtime: dict) -> bool:
    return bool(runtime.get("provider_error") or metadata.get("outcome_category") == "provider_error")


def read_run(run_dir: Path) -> dict:
    metadata = load(run_dir / "metadata.json")
    verifier = load(run_dir / "verifier.json")
    runtime = load(run_dir / "runtime_r2.json")
    stream = events(run_dir / "events.jsonl")
    calls = [event for event in stream if event.get("event") == "tool_result"]
    indexed = [(index, event) for index, event in enumerate(calls, 1)]
    writes = [(index, event) for index, event in indexed if event.get("tool_name") == "write_file"]
    reads = [(index, event) for index, event in indexed if event.get("tool_name") == "read_file"]
    commands = [(index, event) for index, event in indexed if event.get("tool_name") == "run_command"]
    first_write = writes[0][0] if writes else None
    last_write = writes[-1][0] if writes else None
    response_by_index = response_text(run_dir)

    def text_before_response(response_index: int) -> str:
        return "\n".join(response_by_index.get(index, "") for index in range(1, response_index + 1))

    explicit_actions = set()
    for _, event in indexed:
        response_index = int(event.get("response_index") or 0)
        preceding = text_before_response(response_index)
        tool = event.get("tool_name")
        if tool == "read_file" and PHRASES["read"].search(preceding):
            explicit_actions.add("read")
        if tool == "write_file" and PHRASES["targeted"].search(preceding):
            explicit_actions.add("targeted")
        if tool == "run_command" and VALIDATION.search(str(event.get("arguments") or "")) and PHRASES["validate"].search(preceding):
            explicit_actions.add("validate")
        if tool == "read_file" and last_write is not None:
            call_index = next((i for i, candidate in indexed if candidate is event), 0)
            if call_index > last_write and PHRASES["reread"].search(preceding):
                explicit_actions.add("reread")

    written_paths = []
    for _, event in writes:
        try:
            written_paths.append(json.loads(event.get("arguments") or "{}").get("path"))
        except json.JSONDecodeError:
            written_paths.append(None)
    identities = Counter((event.get("tool_name"), str(event.get("arguments") or "")) for _, event in indexed)
    validation_after = bool(last_write and any(
        index > last_write and VALIDATION.search(str(event.get("arguments") or ""))
        for index, event in commands
    ))
    read_before = bool(first_write and any(index < first_write for index, _ in reads))
    reread_after = bool(last_write and any(index > last_write for index, _ in reads))
    flags = metadata.get("outcome_flags") or {}
    return {
        "run_id": metadata.get("run_id", run_dir.name),
        "task": metadata.get("task_id"),
        "condition": metadata.get("condition"),
        "repetition": metadata.get("repetition"),
        "verifier_pass": verifier.get("passed") is True,
        "provider_error_protocol": provider_error_protocol(metadata, runtime),
        "partial_score": (verifier.get("summary") or {}).get("partial_score"),
        "steps": len(calls),
        "read_before_edit": read_before,
        "validated_after_last_edit": validation_after,
        "reread_after_edit": reread_after,
        "write_file_rewrite_count": max(0, len(written_paths) - len(set(written_paths))),
        "loop_count": sum(count - 1 for count in identities.values() if count >= 3),
        "explicit_activation": bool(explicit_actions),
        "explicit_actions": ";".join(sorted(explicit_actions)),
        "final_empty": bool(flags.get("final_empty")),
        "timeout": bool(flags.get("timeout")),
        "max_steps_reached": bool(flags.get("max_steps_reached")),
    }


def wilson(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float | None, float | None]:
    if not n:
        return None, None
    p = successes / n
    scale = 1 + z*z/n
    center = (p + z*z/(2*n)) / scale
    margin = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / scale
    return center - margin, center + margin


def bootstrap(values: list[float], seed: int) -> tuple[float | None, float | None, float | None]:
    if not values:
        return None, None, None
    rng = random.Random(seed)
    draws = sorted(sum(rng.choice(values) for _ in values) / len(values) for _ in range(BOOTSTRAP_DRAWS))
    return sum(values)/len(values), draws[249], draws[9749]


def emit(name: str, rows: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0]) if rows else []
    with (OUT / f"{name}.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    markdown = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    markdown += ["| " + " | ".join(str(row.get(column, "")) for column in columns) + " |" for row in rows]
    (OUT / f"{name}.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")


def main() -> None:
    rows = [read_run(path.parent) for path in sorted(RUNS.glob("*/metadata.json"))]
    if len(rows) != 192:
        raise SystemExit(f"S8-b analysis blocked: expected 192 complete records, found {len(rows)}")
    summary = []
    for condition in CONDITIONS:
        selected = [row for row in rows if row["condition"] == condition]
        primary = [row for row in selected if not row["provider_error_protocol"]]
        passed = sum(row["verifier_pass"] for row in primary)
        low, high = wilson(passed, len(primary))
        summary.append({
            "condition": condition, "scheduled": len(selected),
            "provider_error_protocol": len(selected)-len(primary), "primary_n": len(primary),
            "verifier_pass": passed, "pass_rate": passed/len(primary) if primary else None,
            "wilson_low": low, "wilson_high": high,
            "provider_as_failure_rate": sum(row["verifier_pass"] and not row["provider_error_protocol"] for row in selected)/len(selected),
            "explicit_activation_n": sum(row["explicit_activation"] for row in primary),
            "explicit_activation_rate": sum(row["explicit_activation"] for row in primary)/len(primary) if primary else None,
            "activation_tasks": len({row["task"] for row in primary if row["explicit_activation"]}),
            "final_empty": sum(row["final_empty"] for row in selected),
            "timeout": sum(row["timeout"] for row in selected),
            "max_steps_reached": sum(row["max_steps_reached"] for row in selected),
        })
    emit("S8B_T1_condition_summary", summary)

    by_cell = defaultdict(list)
    for row in rows:
        if not row["provider_error_protocol"]:
            by_cell[(row["task"], row["condition"])].append(float(row["verifier_pass"]))
    comparisons = []
    for treatment in ("C1", "externalized", "imitation"):
        differences = []
        for task in sorted({row["task"] for row in rows}):
            treated = by_cell.get((task, treatment), [])
            control = by_cell.get((task, "generic_control"), [])
            if treated and control:
                differences.append(sum(treated)/len(treated) - sum(control)/len(control))
        mean, low, high = bootstrap(differences, BOOTSTRAP_SEED + CONDITIONS.index(treatment))
        comparisons.append({
            "contrast": f"{treatment}-generic_control", "n_tasks": len(differences),
            "mean_difference": mean, "bootstrap_low": low, "bootstrap_high": high,
            "bootstrap_draws": BOOTSTRAP_DRAWS, "bootstrap_seed": BOOTSTRAP_SEED + CONDITIONS.index(treatment),
        })
    emit("S8B_T2_task_paired_differences", comparisons)

    process = []
    metrics = ("steps", "read_before_edit", "validated_after_last_edit", "reread_after_edit", "write_file_rewrite_count", "loop_count", "partial_score")
    for condition in CONDITIONS:
        selected = [row for row in rows if row["condition"] == condition and not row["provider_error_protocol"]]
        for metric in metrics:
            values = sorted(float(row[metric]) for row in selected if row.get(metric) is not None)
            def quantile(p: float):
                position=(len(values)-1)*p; lo=math.floor(position); hi=math.ceil(position)
                return values[lo] if lo==hi else values[lo]*(hi-position)+values[hi]*(position-lo)
            process.append({
                "condition": condition, "metric": metric, "n": len(values),
                "mean": sum(values)/len(values) if values else None,
                "median": quantile(.5) if values else None,
                "q1": quantile(.25) if values else None,
                "q3": quantile(.75) if values else None,
            })
    emit("S8B_T3_process_metrics", process)
    emit("S8B_run_metrics", rows)
    print(json.dumps({"runs": len(rows), "tables": 4, "output": str(OUT)}))


if __name__ == "__main__":
    main()
