#!/usr/bin/env python3
"""Mechanical B5-r2 terminal-empty flag; outside human kappa."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRIVATE = ROOT / "data" / "b5_r2_blinded_packets" / "b5_r2_private_manifest.json"
SOURCE = ROOT / "data" / "b3_s5_r2_runs"
def main() -> None:
    rows = []
    for item in json.loads(PRIVATE.read_text(encoding="utf-8")):
        events = [json.loads(line) for line in (SOURCE / item["run_id"] / "events.jsonl").read_text(encoding="utf-8").splitlines()]
        terminal = [event for event in events if event.get("event") == "provider_response"][-1]
        rows.append({"packet_id": item["packet_id"], "empty_termination_mechanical": terminal.get("finish_reason") == "stop" and terminal.get("visible_content_chars") == 0})
    print(json.dumps({"definition": "last provider_response has finish_reason stop and visible_content_chars == 0", "not_in_human_labels_or_kappa": True, "records": rows}, indent=2))
if __name__ == "__main__": main()
