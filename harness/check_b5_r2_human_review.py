#!/usr/bin/env python3
"""Validate B5-r2 human failure labels without reading judge labels."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "b5_r2_human_review" / "human_annotations.jsonl"
ALLOWED = {"premature_implementation", "repeated_exploration", "ineffective_debugging_loop", "insufficient_validation", "missed_constraint", "premature_completion", "tool_misuse", "file_corruption", "none_observed", "unscorable"}
EXCLUSIVE = {"none_observed", "unscorable"}
EXPECTED = {f"packet_{i:03d}" for i in range(1, 25)}
REQUIRED = {"run_id", "annotator_id", "blinded", "stage_events", "failure_modes"}

def main() -> None:
    errors, rows = [], []
    if not PATH.exists():
        print(json.dumps({"valid": False, "errors": [f"missing {PATH}"], "expected_lines": 24}, indent=2)); raise SystemExit(1)
    for number, text in enumerate(PATH.read_text(encoding="utf-8").splitlines(), 1):
        if not text.strip(): errors.append(f"line {number}: blank lines are not allowed"); continue
        try: value = json.loads(text)
        except json.JSONDecodeError as exc: errors.append(f"line {number}: invalid JSON: {exc.msg}"); continue
        if not isinstance(value, dict): errors.append(f"line {number}: must be a JSON object"); continue
        rows.append((number, value))
    if len(rows) != 24: errors.append(f"expected 24 JSON lines, found {len(rows)}")
    ids = [row.get("run_id") for _, row in rows]
    if len(ids) != len(set(ids)): errors.append("run_id values must be unique")
    if set(ids) != EXPECTED: errors.append("run_id values must be exactly packet_001 through packet_024")
    for number, row in rows:
        if set(row) != REQUIRED: errors.append(f"line {number}: fields must be exactly {sorted(REQUIRED)}")
        if not isinstance(row.get("annotator_id"), str) or not row.get("annotator_id"): errors.append(f"line {number}: annotator_id must be non-empty string")
        if row.get("blinded") is not True: errors.append(f"line {number}: blinded must be true")
        if row.get("stage_events") != []: errors.append(f"line {number}: stage_events must be []")
        labels = row.get("failure_modes")
        if not isinstance(labels, list) or not labels: errors.append(f"line {number}: failure_modes must be non-empty array"); continue
        if len(labels) != len(set(labels)): errors.append(f"line {number}: duplicate failure mode")
        if set(labels) - ALLOWED: errors.append(f"line {number}: unsupported labels {sorted(set(labels) - ALLOWED)}")
        if set(labels) & EXCLUSIVE and len(labels) != 1: errors.append(f"line {number}: exclusive label must be alone")
    print(json.dumps({"valid": not errors, "line_count": len(rows), "expected_packet_ids": sorted(EXPECTED), "errors": errors}, indent=2))
    if errors: raise SystemExit(1)
if __name__ == "__main__": main()
