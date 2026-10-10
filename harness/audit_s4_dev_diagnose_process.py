#!/usr/bin/env python3
"""Read-only, post-hoc process audit for the frozen S4 dev_diagnose runs.

This script deliberately consumes only historical S4 records.  It is not used
by the S7 runner, scheduler, prompt builder, or any locked execution asset.
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEV_DIAGNOSE = {
    "pilot_a01_label_parser", "pilot_a03_record_deduplication",
    "pilot_a05_version_parser", "pilot_b01_csv_cleaning",
    "pilot_b03_duplicate_audit", "pilot_b05_date_validation",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def quantiles(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"mean": None, "median": None, "q25": None, "q75": None}
    ordered = sorted(values)
    return {
        "mean": sum(values) / len(values),
        "median": statistics.median(ordered),
        "q25": statistics.quantiles(ordered, n=4, method="inclusive")[0],
        "q75": statistics.quantiles(ordered, n=4, method="inclusive")[2],
    }


def inspect_run(metadata_path: Path) -> dict | None:
    metadata = load(metadata_path)
    if metadata.get("task_id") not in DEV_DIAGNOSE:
        return None
    run_dir = metadata_path.parent
    events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    tools = [event for event in events if event.get("event") == "tool_result"]
    responses = [load(path) for path in sorted((run_dir / "raw_responses").glob("response_*.json"))]
    first_write = next((index for index, event in enumerate(tools) if event.get("tool_name") == "write_file"), None)
    # A successful read is required: a failed or absent read must not be
    # mistaken for informed inspection.
    first_read = next((index for index, event in enumerate(tools)
                       if event.get("tool_name") == "read_file" and (event.get("result") or {}).get("ok") is True), None)
    tool_call_responses = sum(bool(((item.get("choices") or [{}])[0].get("message") or {}).get("tool_calls")) for item in responses)
    finishes = [((item.get("choices") or [{}])[0]).get("finish_reason") for item in responses]
    return {
        "run_id": metadata["run_id"], "model": metadata.get("requested_model_id"),
        "task": metadata.get("task_id"), "assistant_turns": len(responses),
        "tool_calls": len(tools),
        "tool_calls_per_assistant_turn": len(tools) / len(responses) if responses else None,
        "write_before_first_successful_read": first_write is not None and (first_read is None or first_write < first_read),
        "no_successful_read": first_read is None,
        "one_tool_call_response_then_stop": tool_call_responses == 1 and len(responses) == 2 and finishes[-1] == "stop",
        "tool_call_responses": tool_call_responses,
        "finish_reasons": finishes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=ROOT / "data" / "b3_s4_r2_runs")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "s4_dev_diagnose_process_audit_20261010.json")
    args = parser.parse_args()
    rows = [row for path in args.runs.glob("*/metadata.json") if (row := inspect_run(path))]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["model"]].append(row)
    by_model = {}
    for model, values in sorted(grouped.items()):
        turns = [float(row["assistant_turns"]) for row in values]
        calls = [row["tool_calls_per_assistant_turn"] for row in values if row["tool_calls_per_assistant_turn"] is not None]
        by_model[model] = {
            "runs": len(values),
            "assistant_turns": quantiles(turns),
            "tool_calls_per_assistant_turn": quantiles(calls),
            "write_before_first_successful_read": {"numerator": sum(row["write_before_first_successful_read"] for row in values), "denominator": len(values)},
            "no_successful_read": {"numerator": sum(row["no_successful_read"] for row in values), "denominator": len(values)},
            "one_tool_call_response_then_stop": {"numerator": sum(row["one_tool_call_response_then_stop"] for row in values), "denominator": len(values)},
        }
    payload = {
        "scope": "post_hoc_exploratory; historical S4 dev_diagnose only; no new model calls",
        "definitions": {
            "assistant_turns": "number of stored raw assistant responses",
            "tool_calls_per_assistant_turn": "tool_result events divided by stored raw assistant responses",
            "write_before_first_successful_read": "a write_file tool result precedes the first successful read_file tool result; no successful read counts as early write when a write exists",
            "one_tool_call_response_then_stop": "exactly one response with tool_calls, exactly two responses total, and final finish_reason stop",
        },
        "by_model": by_model,
        "records": rows,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "runs": len(rows)}))


if __name__ == "__main__":
    main()
