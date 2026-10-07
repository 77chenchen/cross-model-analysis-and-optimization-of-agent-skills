#!/usr/bin/env python3
"""Run every positive/negative/shortcut admission case for the pilot pool."""
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
admission = json.loads((ROOT / "tasks/pilot/admission.json").read_text())
for entry in admission["tasks"]:
    task, prefix = entry["id"], entry["fixture_prefix"]
    verifier = ROOT / "verifiers" / f"{task}.py"
    cases = (("positive", ROOT / "verifiers/fixtures" / f"{prefix}_positive", 0),
             ("template", ROOT / "tasks/pilot" / task / "template", 1),
             ("shortcut", ROOT / "verifiers/fixtures" / f"{prefix}_shortcut", 1))
    for label, target, expected in cases:
        result = subprocess.run(["python3", str(verifier), str(target)], capture_output=True, text=True)
        if result.returncode != expected:
            raise SystemExit(f"{task}/{label}: expected {expected}, got {result.returncode}: {result.stdout}{result.stderr}")
    print(f"admitted: {task}")
print(f"validated {len(admission['tasks'])} pilot tasks")
