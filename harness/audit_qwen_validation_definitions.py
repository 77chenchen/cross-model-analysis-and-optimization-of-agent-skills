#!/usr/bin/env python3
"""Read-only qwen C0/C1 check of pre-declared validation definitions."""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYWORDS = ("test", "pytest", "unittest", "py_compile")


def q(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"q25": None, "median": None, "q75": None}
    values = sorted(values)
    return {"q25": statistics.quantiles(values, n=4, method="inclusive")[0], "median": statistics.median(values), "q75": statistics.quantiles(values, n=4, method="inclusive")[2]}


def row(metadata_path: Path) -> dict | None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("requested_model_id") != "qwen3.5:9b" or metadata.get("condition") not in {"C0", "C1"}:
        return None
    events = [json.loads(line) for line in (metadata_path.parent / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    calls = [event for event in events if event.get("event") == "tool_result"]
    last_write = max((index for index, event in enumerate(calls) if event.get("tool_name") == "write_file"), default=None)
    after = calls[last_write + 1:] if last_write is not None else []
    commands = [event for event in after if event.get("tool_name") == "run_command"]
    return {
        "run_id": metadata["run_id"], "task": metadata["task_id"], "condition": metadata["condition"],
        "edited": last_write is not None,
        "primary_validation_intent": any(any(word in str(event.get("arguments") or "").lower() for word in KEYWORDS) for event in commands),
        "sensitivity_transport_success": any((event.get("result") or {}).get("ok") is True for event in commands),
    }


def rate(rows: list[dict], key: str) -> dict:
    edited = [row for row in rows if row["edited"]]
    return {"edited_runs": len(edited), "validated": sum(row[key] for row in edited), "rate": sum(row[key] for row in edited) / len(edited) if edited else None}


def directions(rows: list[dict], key: str) -> dict:
    by = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if row["edited"]:
            by[row["task"]][row["condition"]].append(float(row[key]))
    diffs = []
    per_task = []
    for task, values in sorted(by.items()):
        if not values["C0"] or not values["C1"]:
            continue
        diff = sum(values["C1"]) / len(values["C1"]) - sum(values["C0"]) / len(values["C0"])
        diffs.append(diff); per_task.append({"task": task, "C1_minus_C0": diff})
    return {"task_count": len(diffs), "negative": sum(value < 0 for value in diffs), "positive": sum(value > 0 for value in diffs), "zero": sum(value == 0 for value in diffs), "C1_minus_C0_quantiles": q(diffs), "per_task": per_task}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=ROOT / "data" / "s7_runs")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "s7_monitoring" / "qwen_validation_definition_audit_20261010.json")
    args = parser.parse_args()
    rows = [value for path in args.runs.glob("*/metadata.json") if (value := row(path))]
    c0 = [row for row in rows if row["condition"] == "C0"]
    c1 = [row for row in rows if row["condition"] == "C1"]
    payload = {
        "scope": "qwen3.5:9b C0/C1 only; read-only monitoring; no other model process snapshot",
        "definitions": {
            "primary_validation_intent": "after final write_file, run_command arguments contain test, pytest, unittest, or py_compile",
            "sensitivity_transport_success": "after final write_file, run_command result.ok is true regardless of command text",
            "denominator": "runs with at least one write_file; no-edit runs are not falsely called unvalidated",
        },
        "by_condition": {"C0": {"primary": rate(c0, "primary_validation_intent"), "sensitivity": rate(c0, "sensitivity_transport_success")}, "C1": {"primary": rate(c1, "primary_validation_intent"), "sensitivity": rate(c1, "sensitivity_transport_success")}},
        "task_paired_direction": {"primary": directions(rows, "primary_validation_intent"), "sensitivity": directions(rows, "sensitivity_transport_success")},
        "records": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"runs": len(rows), "output": str(args.output)}))


if __name__ == "__main__":
    main()
