#!/usr/bin/env python3
"""Monitoring-only S7 trajectory metrics; not a formal effect analysis."""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

try:
    from .s7_protocol import ROOT
except ImportError:
    from s7_protocol import ROOT


VALIDATION = re.compile(r"pytest|unittest|\btest\b|py_compile|python[0-9.]*\s+.*\.py", re.I)


def trajectory_text(run_dir: Path, events: list[dict]) -> str:
    fragments = [str(event.get("arguments") or "") for event in events]
    for response in sorted((run_dir / "raw_responses").glob("response_*.json")):
        payload = json.loads(response.read_text(encoding="utf-8"))
        message = ((payload.get("choices") or [{}])[0].get("message") or {})
        fragments.extend([str(message.get("content") or ""), str(message.get("reasoning") or "")])
    return "\n".join(fragments).lower()


def row(run_dir: Path) -> dict[str, object]:
    meta = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
    events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()] if (run_dir / "events.jsonl").exists() else []
    tools = [event for event in events if event.get("event") == "tool_result"]
    writes = [index for index, event in enumerate(tools, 1) if event.get("tool_name") == "write_file"]
    validation = [index for index, event in enumerate(tools, 1) if event.get("tool_name") == "run_command" and VALIDATION.search(str(event.get("arguments") or ""))]
    repetitions = Counter((str(event.get("tool_name")), str(event.get("arguments"))) for event in tools)
    loops = sum(count - 1 for count in repetitions.values() if count >= 3)
    written_paths = set()
    for event in tools:
        if event.get("tool_name") == "write_file":
            try:
                written_paths.add(json.loads(event.get("arguments") or "{}").get("path"))
            except json.JSONDecodeError:
                pass
    text = trajectory_text(run_dir, events)
    if "skill protocol" in text or "skill a" in text or "skill b" in text or "skill c" in text:
        activation = "explicit"
    elif writes and validation:
        activation = "observable_inferred"
    else:
        activation = "not_observed"
    return {
        "run_id": meta["run_id"], "model": meta.get("requested_model_id"), "condition": meta.get("condition"), "split": meta.get("split"), "task": meta.get("task_id"), "outcome": meta.get("outcome_category"), "steps": len(tools), "first_edit_position": writes[0] if writes else None, "validated_after_last_edit": bool(writes and any(position > writes[-1] for position in validation)), "write_file_count": len(writes), "write_file_rewrite_count": max(0, len(writes) - len(written_paths)), "loop_count": loops, "activation_heuristic": activation, "final_empty": (meta.get("outcome_flags") or {}).get("final_empty"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=ROOT / "data" / "s7_runs")
    parser.add_argument("--csv", type=Path, default=ROOT / "data" / "s7_monitoring" / "run_metrics.csv")
    parser.add_argument("--summary", type=Path, default=ROOT / "data" / "s7_monitoring" / "condition_monitoring.json")
    args = parser.parse_args()
    rows = [row(path.parent) for path in sorted(args.runs.glob("*/metadata.json"))]
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["run_id"])
        writer.writeheader(); writer.writerows(rows)
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for value in rows:
        groups[(str(value["model"]), str(value["condition"]))].append(value)
    summary = {}
    for (model, condition), values in sorted(groups.items()):
        number = len(values)
        mean = lambda field: sum(float(value[field] or 0) for value in values) / number
        summary[f"{model}::{condition}"] = {"runs": number, "mean_steps": mean("steps"), "mean_first_edit_position": mean("first_edit_position"), "validation_after_last_edit_rate": sum(bool(value["validated_after_last_edit"]) for value in values) / number, "mean_write_file_rewrite_count": mean("write_file_rewrite_count"), "mean_loop_count": mean("loop_count"), "activation_rate": sum(value["activation_heuristic"] != "not_observed" for value in values) / number, "final_empty_rate": sum(bool(value["final_empty"]) for value in values) / number, "activation_labels": dict(Counter(value["activation_heuristic"] for value in values))}
    args.summary.write_text(json.dumps({"scope": "monitoring_only_not_formal_inference", "metric_definitions": {"write_file_rewrite_count": "write_file calls minus unique written paths", "loop_count": "sum(count-1) for identical tool-name/arguments pairs with count >= 3", "activation_heuristic": "skill-activation-heuristic-v1"}, "by_model_condition": summary}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"runs": len(rows), "csv": str(args.csv), "summary": str(args.summary)}))


if __name__ == "__main__":
    main()
