#!/usr/bin/env python3
"""Derive locked run-level S7 trajectory metrics without making model calls."""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

try:
    from .s7_protocol import ROOT
except ImportError:
    from s7_protocol import ROOT


EDIT = re.compile(r"write_file|apply_patch|\btee\b|>\s*[^&]|sed\s+-i|perl\s+-pi")
VALIDATE = re.compile(r"pytest|unittest|\btest\b|py_compile|python[0-9.]*\s+.*\.py", re.I)


def metrics(run_dir: Path) -> dict[str, object]:
    meta = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
    events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()] if (run_dir / "events.jsonl").exists() else []
    calls = [event for event in events if event.get("event") == "tool_result"]
    text = [str(event.get("arguments") or "") for event in calls]
    edits = [index + 1 for index, command in enumerate(text) if EDIT.search(command)]
    validations = [index + 1 for index, command in enumerate(text) if VALIDATE.search(command)]
    repeats = sum(count - 1 for count in Counter(text).values() if count > 1)
    usage = meta.get("r2_usage") or {}
    return {
        "run_id": meta["run_id"], "model": meta.get("requested_model_id"), "split": meta.get("split"), "task": meta.get("task_id"), "condition": meta.get("condition"), "repetition": meta.get("repetition"), "outcome": meta.get("outcome_category"), "partial_score": meta.get("partial_score"), "steps": meta.get("r2_tool_call_count", len(calls)), "input_tokens": usage.get("prompt_tokens"), "output_tokens": usage.get("completion_tokens"), "total_tokens": usage.get("total_tokens"), "reasoning_tokens": usage.get("reasoning_tokens"), "first_edit_position": edits[0] if edits else None, "validated_after_last_edit": bool(edits and any(step > edits[-1] for step in validations)), "repeated_action_count": repeats, "no_progress_loop_count": sum(count - 1 for count in Counter(text).values() if count >= 3), "final_empty": (meta.get("outcome_flags") or {}).get("final_empty"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=ROOT / "data" / "s7_runs")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "s7_metrics.csv")
    args = parser.parse_args()
    rows = [metrics(path.parent) for path in sorted(args.runs.glob("*/metadata.json"))]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["run_id"])
        writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"runs": len(rows), "output": str(args.output)}))


if __name__ == "__main__":
    main()
