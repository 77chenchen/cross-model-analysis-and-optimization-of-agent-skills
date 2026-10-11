"""Create the dashboard's public, aggregate-only data payload."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dashboard" / "dist" / "data.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(value: str) -> float | int | None:
    if value == "":
        return None
    result = float(value)
    return int(result) if result.is_integer() else result


summary = read_csv(ROOT / "results/tables/s7/S7_T1_model_condition_summary.csv")
metrics = read_csv(ROOT / "results/tables/s7/S7_T4_process_metrics.csv")
paired = read_csv(ROOT / "results/tables/s7/S7_T7_process_paired.csv")

payload = {
    "provenance": {
        "release": "S7 formal results",
        "primary_outcome": "verifier.json.passed",
        "unit": "run for rates; task for paired contrasts",
        "gpt_note": "GPT-5.6 Sol is a sampling-uncontrolled reference anchor.",
    },
    "summary": [
        {key: number(value) if key not in {"model", "condition", "split"} else value
         for key, value in row.items()}
        for row in summary
    ],
    "metrics": [
        {key: number(value) if key not in {"model", "condition", "metric"} else value
         for key, value in row.items()}
        for row in metrics
    ],
    "paired": [
        {key: number(value) if key not in {"model", "scope", "contrast", "metric", "hypothesis_source"} else value
         for key, value in row.items()}
        for row in paired
    ],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
