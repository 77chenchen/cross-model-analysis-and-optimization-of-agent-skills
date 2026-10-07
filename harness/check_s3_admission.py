#!/usr/bin/env python3
"""Validate all S3 task contracts without invoking a model."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((ROOT / "tasks/formal_manifest.json").read_text())
results = []

for task in MANIFEST["tasks"]:
    task_id = task["id"]
    split = task["split"]
    candidates = {
        "positive": ROOT / "verifiers/fixtures" / f"{task_id}_positive",
        "negative_template": ROOT / "tasks" / split / task_id / "template",
        "shortcut": ROOT / "verifiers/fixtures" / f"{task_id}_shortcut",
    }
    observations = {}
    for label, workspace in candidates.items():
        run = subprocess.run(
            [sys.executable, str(ROOT / "verifiers/contract_verifier.py"), task_id, str(workspace)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        try:
            payload = json.loads(run.stdout)
        except json.JSONDecodeError:
            payload = {"passed": False, "error": "non_json_verifier_output"}
        observations[label] = {"exit_code": run.returncode, **payload}
    accepted = (
        observations["positive"].get("passed") is True
        and observations["negative_template"].get("passed") is False
        and observations["shortcut"].get("passed") is False
    )
    results.append({"id": task_id, "split": split, "accepted": accepted, "checks": observations})

report = {"stage": "S3", "task_count": len(results), "all_accepted": all(x["accepted"] for x in results), "tasks": results}
(ROOT / "tasks/s3_admission.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"task_count": report["task_count"], "all_accepted": report["all_accepted"]}))
raise SystemExit(0 if report["all_accepted"] else 1)
