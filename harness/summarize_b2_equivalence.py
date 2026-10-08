#!/usr/bin/env python3
"""Produce a descriptive, non-pooled B2 runner comparison table."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/b2_runner_equivalence"


def read(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def main() -> None:
    rows = []
    for directory, runner in ((OUT / "codex_cli", "codex-cli"), (OUT / "r2", "r2-direct-chat-completions")):
        for metadata_path in sorted(directory.glob("pilot_*/metadata.json")):
            metadata = read(metadata_path)
            runtime = read(metadata_path.parent / ("runtime_r2.json" if runner.startswith("r2") else "runtime.json"))
            rows.append({
                "runner": runner, "task_id": metadata.get("task_id"), "run_id": metadata.get("run_id"),
                "outcome_category": metadata.get("outcome_category"), "partial_score": metadata.get("partial_score"),
                "verifier_checks_passed": metadata.get("verifier_checks_passed"), "verifier_check_count": metadata.get("verifier_check_count"),
                "final_empty": (metadata.get("outcome_flags") or {}).get("final_empty"),
                "no_edit": (metadata.get("outcome_flags") or {}).get("no_edit"),
                "provider_error": (metadata.get("outcome_flags") or {}).get("provider_error"),
                "timeout": (metadata.get("outcome_flags") or {}).get("timeout"),
                "finish_reason": metadata.get("finish_reason"), "response_count": runtime.get("response_count"),
                "tool_call_count": runtime.get("tool_call_count"), "temperature_effective": metadata.get("temperature_effective"),
                "seed_effective": metadata.get("seed_effective"),
            })
    rows.sort(key=lambda row: (row["task_id"] or "", row["runner"]))
    fields = ["runner", "task_id", "run_id", "outcome_category", "partial_score", "verifier_checks_passed", "verifier_check_count", "final_empty", "no_edit", "provider_error", "timeout", "finish_reason", "response_count", "tool_call_count", "temperature_effective", "seed_effective"]
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    print(f"{len(rows)} rows")


if __name__ == "__main__":
    main()
