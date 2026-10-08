#!/usr/bin/env python3
"""Create a fresh blinded 24-packet sample from B3/S5 r2 baselines.

The public packet directory contains no task, model, outcome, or run identifier.
The private mapping remains ignored so it cannot leak to annotators or reports.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
source = ROOT / "data/b3_s5_r2_runs"
public = ROOT / "data/b5_r2_human_review"
private = ROOT / "data/b5_r2_blinded_packets"
public.mkdir(exist_ok=True); private.mkdir(exist_ok=True)
runs = sorted(source.glob("pilot_*/metadata.json"))
if len(runs) != 36:
    raise SystemExit(f"expected 36 r2 baseline runs, found {len(runs)}")
selected = sorted(random.Random(20261008).sample(runs, 24), key=lambda path: path.parent.name)
manifest = []
for index, metadata_path in enumerate(selected, 1):
    run = metadata_path.parent
    packet_id = f"packet_{index:03d}"
    trajectory = []
    for line in (run / "events.jsonl").read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        kind = event.get("event")
        if kind == "provider_response":
            trajectory.append({"event": kind, "finish_reason": event.get("finish_reason"), "visible_content_chars": event.get("visible_content_chars"), "reasoning_chars": event.get("reasoning_chars"), "tool_call_count": event.get("tool_call_count")})
        elif kind == "tool_result":
            trajectory.append({"event": kind, "tool_name": event.get("tool_name"), "arguments": event.get("arguments"), "result": event.get("result")})
        elif kind in {"provider_error", "max_steps_reached", "runner_deadline_exceeded", "context_budget_exceeded", "request_failure"}:
            trajectory.append({key: value for key, value in event.items() if key not in {"timestamp", "response_index"}})
    packet = {"packet_id": packet_id, "protocol": "b5-r2-blind-v1", "trajectory": trajectory}
    (public / f"{packet_id}.json").write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    metadata = json.loads(metadata_path.read_text())
    manifest.append({"packet_id": packet_id, "run_id": metadata["run_id"], "task_id": metadata["task_id"], "repetition": metadata["repetition"]})
(private / "b5_r2_private_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
(ROOT / "data/b5_r2_human_review_manifest.json").write_text(json.dumps({"protocol": "b5-r2-blind-v1", "packet_count": 24, "selection_seed": 20261008, "old_packets_use": "method validation only; excluded from report kappa"}, indent=2) + "\n", encoding="utf-8")
print(f"wrote {len(manifest)} packets")
