#!/usr/bin/env python3
"""Validate the blind judge output and prevent accidental model/result fields."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
annotations = ROOT / "data/s5_blinded_annotations"
packets = {p.stem for p in (ROOT / "data/s5_blinded_packets").glob("packet_*.json")}
forbidden = {"model", "provider", "outcome", "pass", "verifier", "cost"}
accepted, rejected = [], []
for path in sorted(annotations.glob("packet_*.json")):
    try:
        data = json.loads(path.read_text())
        keys = set(data)
        valid = path.stem in packets and data.get("run_id") == path.stem and data.get("blinded") is True and not keys & forbidden
    except json.JSONDecodeError:
        valid = False
    (accepted if valid else rejected).append(path.name)
report = {"expected": len(packets), "accepted": len(accepted), "rejected": rejected, "blinded": True}
(annotations / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
raise SystemExit(0 if len(accepted) == len(packets) else 1)
