#!/usr/bin/env python3
"""Remove model/result identifiers before an S5 judge sees trajectories."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data/s5_runs"
DEST = ROOT / "data/s5_blinded_packets"
DEST.mkdir(exist_ok=True)
manifest = []
for index, run_dir in enumerate(sorted(SOURCE.glob("pilot_*")), start=1):
    actions = run_dir / "actions.jsonl"
    if not actions.exists():
        continue
    cleaned = []
    for line in actions.read_text().splitlines():
        event = json.loads(line)
        text = str(event.get("text") or "")
        command = str(event.get("command") or "")
        # Absolute workspace and run-directory names can encode the model ID.
        text = text.replace(str(run_dir), "<RUN_WORKSPACE>")
        command = command.replace(str(run_dir), "<RUN_WORKSPACE>")
        path_pattern = r"/Users/[^\s'\"]+/data/s5_runs/pilot_[^\s'\"]+"
        text = re.sub(path_pattern, "<RUN_WORKSPACE>", text)
        command = re.sub(path_pattern, "<RUN_WORKSPACE>", command)
        cleaned.append({
            "sequence": event.get("sequence"), "event_type": event.get("event_type"),
            "phase": event.get("phase"), "tool_name": event.get("tool_name"),
            "status": event.get("status"), "command": command, "text": text,
        })
    packet_id = f"packet_{index:03d}"
    task_id = json.loads((run_dir / "metadata.json").read_text())["task_id"]
    (DEST / f"{packet_id}.json").write_text(json.dumps({"packet_id": packet_id, "task_id": task_id, "actions": cleaned}, ensure_ascii=False, indent=2) + "\n")
    manifest.append({"packet_id": packet_id, "run_id": run_dir.name, "task_id": task_id, "blinded": True})
(DEST / "manifest_private.json").write_text(json.dumps({"packets": manifest}, indent=2) + "\n")
print(json.dumps({"packet_count": len(manifest), "blinded": True}))
