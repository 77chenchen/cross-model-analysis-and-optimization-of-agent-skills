#!/usr/bin/env python3
"""Extract r2 terminal-path and behavior signals from the completed B3 S5 runs."""
from __future__ import annotations
import csv, json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = []
for metadata_path in sorted((ROOT / "data/b3_s5_r2_runs").glob("pilot_*/metadata.json")):
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    runtime = json.loads((metadata_path.parent / "runtime_r2.json").read_text(encoding="utf-8"))
    events = [json.loads(line) for line in (metadata_path.parent / "events.jsonl").read_text(encoding="utf-8").splitlines() if line]
    event_names = [event.get("event") for event in events]
    tool_events = [event for event in events if event.get("event") == "tool_result"]
    first_write = next((index for index, event in enumerate(tool_events) if event.get("tool_name") == "write_file" and (event.get("result") or {}).get("ok")), None)
    validation_after_write = False
    if first_write is not None:
        for event in tool_events[first_write + 1:]:
            if event.get("tool_name") == "run_command" and any(term in str(event.get("arguments", "")).lower() for term in ("test", "pytest", "unittest", "compile")):
                validation_after_write = True
    terminal_path = "provider_error" if "provider_error" in event_names else "max_steps" if "max_steps_reached" in event_names else "final_response"
    flags = metadata.get("outcome_flags") or {}
    rows.append({
        "run_id": metadata["run_id"], "task_id": metadata["task_id"], "repetition": metadata["repetition"], "legacy_outcome": metadata["outcome_category"], "partial_score": metadata.get("partial_score"),
        "terminal_path": terminal_path, "final_empty": flags.get("final_empty"), "no_edit": flags.get("no_edit"), "compile_error": flags.get("compile_error"), "verifier_fail": flags.get("verifier_fail"), "provider_error": flags.get("provider_error"),
        "response_count": runtime.get("response_count"), "tool_call_count": runtime.get("tool_call_count"), "valid_tool_calls": (runtime.get("tool_parse") or {}).get("valid"), "tool_parse_errors": sum(value for key, value in (runtime.get("tool_parse") or {}).items() if key != "valid"),
        "post_edit_validation": validation_after_write, "provider_error_text": runtime.get("provider_error"),
    })
out = ROOT / "data/diagnostics/b4_b3_s5_r2"; out.mkdir(parents=True, exist_ok=True)
with (out / "run_signals.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
cross = Counter((str(row["final_empty"]), str(not row["no_edit"]), row["terminal_path"], str(row["partial_score"])) for row in rows)
with (out / "cross_table.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle, lineterminator="\n"); writer.writerow(["final_empty", "edited", "terminal_path", "partial_score", "runs"])
    writer.writerows([(*key, value) for key, value in sorted(cross.items())])
summary = {"runs": len(rows), "terminal_paths": dict(Counter(row["terminal_path"] for row in rows)), "legacy_outcomes": dict(Counter(row["legacy_outcome"] for row in rows)), "all_tool_calls_parseable": all(row["tool_parse_errors"] == 0 for row in rows), "max_step_empty_runs": sum(row["final_empty"] and row["terminal_path"] == "max_steps" for row in rows), "provider_502_runs": sum("502" in str(row["provider_error_text"]) for row in rows), "post_edit_validation_runs": sum(row["post_edit_validation"] for row in rows)}
(out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary))
