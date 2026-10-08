#!/usr/bin/env python3
"""Analyze S4 qwen3.5:9b artifacts without modifying any run directory."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "data/calibration_runs"
OUT = ROOT / "data/diagnostics/s4_qwen35_20261008"
OUT.mkdir(parents=True, exist_ok=True)

def command_text(action): return str(action.get("command") or "").lower()
def is_compile(text): return "py_compile" in text or "compileall" in text
def is_validate(text): return any(x in text for x in ("pytest", "unittest", "assert ", "python3 ", "python -"))

rows = []
for run in sorted(RUNS.glob("pilot_*qwen3.5_9b*v0*r*")):
    meta_path = run / "metadata.json"
    if not meta_path.exists(): continue
    meta = json.loads(meta_path.read_text())
    actions = [json.loads(x) for x in (run / "actions.jsonl").read_text().splitlines()]
    edits = [a["sequence"] for a in actions if a.get("tool_name") == "file_change" and a.get("status") == "completed"]
    commands = [a for a in actions if a.get("event_type") == "command" and a.get("status") == "completed"]
    final = (run / "final.md").read_text() if (run / "final.md").exists() else ""
    runtime = json.loads((run / "runtime.json").read_text()) if (run / "runtime.json").exists() else {}
    raw = (run / "trajectory.jsonl").read_text().lower()
    after = [command_text(a) for a in commands if edits and a["sequence"] > edits[-1]]
    rows.append({
        "run_id": run.name, "task": meta["task_id"], "final_empty": not final.strip(), "edited": bool(edits),
        "compile_after_edit": any(is_compile(x) for x in after), "validation_after_edit": any(is_validate(x) for x in after),
        "partial_score": meta.get("partial_score"), "legacy_outcome": meta.get("outcome_category"),
        "finish_reason": runtime.get("finish_reason"), "reasoning_tokens": runtime.get("usage", {}).get("reasoning_output_tokens"),
        "turn_completed": runtime.get("turn_completed"), "malformed_tool_calls": runtime.get("malformed_tool_calls"),
        "length_signal": any(x in raw for x in ("context length", "context window", "maximum context", "length")),
    })
with (OUT / "run_flags.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)

cross = Counter((r["final_empty"], r["edited"], r["compile_after_edit"] or r["validation_after_edit"], r["partial_score"]) for r in rows)
with (OUT / "cross_table.csv").open("w", newline="") as f:
    fields=["final_empty","edited","post_edit_compile_or_validation","partial_score","runs"]
    writer=csv.DictWriter(f,fieldnames=fields); writer.writeheader()
    for (empty, edited, validated, score), count in sorted(cross.items(), key=str): writer.writerow({"final_empty":empty,"edited":edited,"post_edit_compile_or_validation":validated,"partial_score":score,"runs":count})

empty = [r for r in rows if r["final_empty"]]
sample = empty[:8]
(OUT / "sampled_empty_runs.json").write_text(json.dumps(sample, indent=2) + "\n")
summary = {
    "run_count": len(rows), "empty_count": len(empty), "legacy_outcomes": dict(Counter(r["legacy_outcome"] for r in rows)),
    "empty_with_partial_score": sum(r["partial_score"] is not None for r in empty),
    "empty_with_verifier_partial_positive": sum((r["partial_score"] or 0) > 0 for r in empty),
    "sample_size": len(sample),
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary))
