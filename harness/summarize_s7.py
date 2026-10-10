#!/usr/bin/env python3
"""Legacy S7 summarizer retained only to reject the obsolete pass source."""
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

try:
    from .s7_protocol import ROOT
except ImportError:
    from s7_protocol import ROOT


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def bootstrap(differences: list[float], seed: int = 701009, draws: int = 10_000) -> dict[str, object]:
    if not differences:
        return {"n_tasks": 0, "mean": None, "bootstrap_95": None}
    rng = random.Random(seed)
    samples = sorted(sum(rng.choice(differences) for _ in differences) / len(differences) for _ in range(draws))
    return {"n_tasks": len(differences), "mean": mean(differences), "bootstrap_95": [samples[int(.025 * (draws - 1))], samples[int(.975 * (draws - 1))]]}


def main() -> None:
    raise SystemExit(
        "ERROR: harness/summarize_s7.py is a legacy entry that derives pass "
        "from outcome_category. After S7 reaches 870/870, use "
        "python3 -m analysis.summarize_s7_v2; verifier.json.passed is the "
        "only valid primary outcome."
    )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metrics", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "s7_summary.json")
    args = parser.parse_args()
    with args.metrics.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["model"], row["task"], row["condition"])].append(row)
    differences: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    distributions = []
    for (model, task, condition), values in sorted(grouped.items()):
        usable = [value for value in values if value["outcome"] != "provider_error"]
        passes = [value["outcome"] == "pass" for value in usable]
        distributions.append({"model": model, "task": task, "condition": condition, "scheduled": len(values), "provider_errors": len(values) - len(usable), "pass_count": sum(passes), "pass_rate_primary": mean([float(value) for value in passes])})
    for model in sorted({row["model"] for row in rows}):
        for task in sorted({row["task"] for row in rows if row["model"] == model}):
            c0 = next((item for item in distributions if item["model"] == model and item["task"] == task and item["condition"] == "C0"), None)
            c1 = next((item for item in distributions if item["model"] == model and item["task"] == task and item["condition"] == "C1"), None)
            if c0 and c1 and c0["pass_rate_primary"] is not None and c1["pass_rate_primary"] is not None:
                split = next(row["split"] for row in rows if row["model"] == model and row["task"] == task)
                differences[model][split].append(c1["pass_rate_primary"] - c0["pass_rate_primary"])
    result = {"by_model_split": {model: {split: bootstrap(values) for split, values in splits.items()} for model, splits in differences.items()}, "task_pass_distribution": distributions, "notes": {"statistical_unit": "task", "provider_error_primary": "excluded from denominator", "provider_error_sensitivity": "include as non-pass", "comparison": "C1 minus C0 paired bootstrap", "exploratory_conditions": ["v1", "l3b"]}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "output": str(args.output)}))


if __name__ == "__main__":
    main()
