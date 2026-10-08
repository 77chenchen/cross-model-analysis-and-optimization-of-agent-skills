#!/usr/bin/env python3
"""Derive run-level S5 metrics without inferring missing provider fields."""
import csv
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data/s5_runs"
OUT = SOURCE / "s5_run_metrics.csv"

def command_is_edit(command: str) -> bool:
    return bool(re.search(r"apply_patch|\btee\b|>\s*[^&]|sed\s+-i|perl\s+-pi|cat\s+<<", command))

def command_is_validation(command: str) -> bool:
    return bool(re.search(r"pytest|unittest|\btest\b|py_compile|python[0-9.]*\s+.*\.py", command, re.I))

rows = []
for meta_path in sorted(SOURCE.glob("*/metadata.json")):
    run_dir = meta_path.parent
    meta = json.loads(meta_path.read_text())
    runtime = json.loads((run_dir / "runtime.json").read_text())
    process = json.loads((run_dir / "process.json").read_text())
    actions = [json.loads(line) for line in (run_dir / "actions.jsonl").read_text().splitlines()]
    # The normalizer records both command start and completion events.  Count
    # completed calls only so each agent action contributes at most once.
    commands = [a for a in actions if a.get("event_type") == "command" and a.get("status") == "completed"]
    command_texts = [str(a.get("command") or "") for a in commands]
    failed_calls = sum(a.get("status") == "failed" for a in commands)
    repeats = sum(count - 1 for count in Counter(command_texts).values() if count > 1)
    edits = [a["sequence"] for a in commands if command_is_edit(str(a.get("command") or ""))]
    validations = [a["sequence"] for a in commands if command_is_validation(str(a.get("command") or ""))]
    full_text = "\n".join((str(a.get("text") or "") + " " + str(a.get("command") or "")) for a in actions).lower()
    if "skill protocol" in full_text or "skill a" in full_text or "skill b" in full_text:
        activation = "explicit"
    elif edits and validations:
        activation = "observable_inferred"
    else:
        activation = "not_observed"
    duration = None
    if process.get("started_at") and process.get("finished_at"):
        duration = (datetime.fromisoformat(process["finished_at"]) - datetime.fromisoformat(process["started_at"])).total_seconds()
    usage = runtime.get("usage", {})
    rows.append({
        "run_id": meta["run_id"], "model": meta["requested_model_id"], "task": meta["task_id"],
        "repetition": meta.get("repetition"), "outcome": meta.get("outcome_category"),
        "pass": meta.get("outcome_category") == "pass", "partial_score": meta.get("partial_score"),
        "steps": len(actions), "command_count": len(commands), "duration_seconds": duration,
        "input_tokens": usage.get("input_tokens"), "cached_input_tokens": usage.get("cached_input_tokens"),
        "output_tokens": usage.get("output_tokens"), "reasoning_output_tokens": usage.get("reasoning_output_tokens"),
        "repeated_action_rate": repeats / len(commands) if commands else None,
        "failed_call_rate": failed_calls / len(commands) if commands else None,
        "no_progress_loop_count": sum(count - 1 for count in Counter(command_texts).values() if count >= 3),
        "first_edit_sequence": edits[0] if edits else None,
        "validated_after_last_edit": any(v > edits[-1] for v in validations) if edits else False,
        "activation_heuristic": activation,
    })
with OUT.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["run_id"])
    writer.writeheader(); writer.writerows(rows)
print(json.dumps({"run_count": len(rows), "output": str(OUT)}))
