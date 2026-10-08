#!/usr/bin/env python3
"""Create a non-mutating overlay marking historical CLI artifacts as legacy."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEGACY_ROOTS = ("data/pilot_runs", "data/calibration_runs", "data/s5_runs", "data/s6_l3_runs")


def main() -> None:
    rows = []
    for relative_root in LEGACY_ROOTS:
        root = ROOT / relative_root
        for path in sorted(root.glob("**/metadata.json")):
            try:
                metadata = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            rows.append({
                "metadata_path": str(path.relative_to(ROOT)),
                "run_id": metadata.get("run_id", path.parent.name),
                "requested_model_id": metadata.get("requested_model_id"),
                "run_cohort": metadata.get("run_cohort"),
                "runner": "codex-cli",
                "analysis_cohort": "legacy_not_pooled_with_r2",
            })
    output = ROOT / "data/legacy_runner_registry.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metadata_path", "run_id", "requested_model_id", "run_cohort", "runner", "analysis_cohort"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} legacy run records -> {output}")


if __name__ == "__main__":
    main()
