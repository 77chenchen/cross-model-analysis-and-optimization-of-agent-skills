#!/usr/bin/env python3
"""Compute verifier partial score for each unmodified pilot seed, without a model."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = []
for task in sorted((ROOT / "tasks/pilot").iterdir()):
    if not task.is_dir():
        continue
    verifier = ROOT / "verifiers" / f"{task.name}.py"
    run = subprocess.run([sys.executable, str(verifier), str(task / "template")], capture_output=True, text=True, check=False)
    try:
        result = json.loads(run.stdout)
        checks = result.get("checks", {})
        passed = sum(value is True for value in checks.values())
        score = passed / len(checks) if checks else 0.0
    except json.JSONDecodeError:
        score, passed, checks = None, None, {}
    rows.append({"task_id": task.name, "seed_partial_score": score, "checks_passed": passed, "check_count": len(checks)})
output = ROOT / "data/pilot_seed_partial_baselines.csv"
output.parent.mkdir(exist_ok=True)
with output.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
    writer.writeheader(); writer.writerows(rows)
print(output)
