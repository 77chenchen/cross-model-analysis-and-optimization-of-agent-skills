#!/usr/bin/env python3
"""Formal S7 pass summary from frozen verifier.json, never legacy outcomes.

This is a post-run analysis replacement for the legacy CSV outcome summarizer.
It neither imports nor is called by the locked S7 execution machinery.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

try:
    from .s7_protocol import ROOT
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from s7_protocol import ROOT


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provider_error_protocol(metadata: dict, runtime: dict) -> bool:
    """True only for retry-exhausted request transport, not a hard timeout."""
    return bool(metadata.get("outcome_category") == "provider_error" or runtime.get("provider_error"))


def read_records(root: Path) -> list[dict]:
    rows: list[dict] = []
    for metadata_path in sorted(root.glob("*/metadata.json")):
        run_dir = metadata_path.parent
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        verifier_path = run_dir / "verifier.json"
        # An absent verifier result is not quietly converted into a legacy pass.
        verifier = json.loads(verifier_path.read_text(encoding="utf-8")) if verifier_path.exists() else {}
        runtime_path = run_dir / "runtime_r2.json"
        runtime = json.loads(runtime_path.read_text(encoding="utf-8")) if runtime_path.exists() else {}
        flags = metadata.get("outcome_flags") or {}
        rows.append({
            "run_id": metadata["run_id"],
            "model": metadata.get("requested_model_id"),
            "task": metadata.get("task_id"),
            "split": metadata.get("split"),
            "condition": metadata.get("condition"),
            "verifier_pass": verifier.get("passed") is True,
            "verifier_available": "passed" in verifier,
            "final_empty": bool(flags.get("final_empty")),
            "provider_error_protocol": provider_error_protocol(metadata, runtime),
            "provider_error_flag_legacy": bool(flags.get("provider_error")),
            "legacy_pass": metadata.get("legacy_outcome_category", metadata.get("outcome_category")) == "pass",
        })
    return rows


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def bootstrap(values: list[float], seed: int, draws: int = 10_000) -> dict:
    if not values:
        return {"n_tasks": 0, "mean": None, "bootstrap_95": None}
    rng = random.Random(seed)
    samples = sorted(sum(rng.choice(values) for _ in values) / len(values) for _ in range(draws))
    return {"n_tasks": len(values), "mean": mean(values), "bootstrap_95": [samples[int(.025 * (draws - 1))], samples[int(.975 * (draws - 1))]]}


def summarize(rows: list[dict]) -> dict:
    primary = [row for row in rows if not row["provider_error_protocol"]]
    return {
        "scheduled": len(rows),
        "provider_error_protocol": len(rows) - len(primary),
        "primary_n": len(primary),
        "verifier_pass": sum(row["verifier_pass"] for row in primary),
        "verifier_pass_rate": mean([float(row["verifier_pass"]) for row in primary]),
        "legacy_pass": sum(row["legacy_pass"] for row in primary),
        "final_empty": sum(row["final_empty"] for row in rows),
        "sensitivity_n_provider_as_nonpass": len(rows),
        "verifier_pass_rate_provider_as_nonpass": mean([float(row["verifier_pass"]) for row in rows]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=ROOT / "data" / "s7_runs")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "s7_verifier_pass_summary.json")
    args = parser.parse_args()
    rows = read_records(args.runs)
    by_cell: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        by_cell[(str(row["model"]), str(row["task"]), str(row["condition"]))].append(row)
    cells = [{"model": model, "task": task, "condition": condition, **summarize(value)} for (model, task, condition), value in sorted(by_cell.items())]
    lookup = {(row["model"], row["task"], row["condition"]): row for row in cells}
    def paired_summary(exclude_b09: bool) -> dict[str, dict]:
        paired: dict[tuple[str, str], list[float]] = defaultdict(list)
        for model, task, condition in lookup:
            if condition != "C0" or (exclude_b09 and task == "test_in_b09_phone") or (model, task, "C1") not in lookup:
                continue
            c0, c1 = lookup[(model, task, "C0")], lookup[(model, task, "C1")]
            if c0["verifier_pass_rate"] is not None and c1["verifier_pass_rate"] is not None:
                split = next(row["split"] for row in rows if row["model"] == model and row["task"] == task)
                paired[(model, str(split))].append(c1["verifier_pass_rate"] - c0["verifier_pass_rate"])
        return {f"{model}::{split}": bootstrap(values, seed=701009) for (model, split), values in sorted(paired.items())}
    output = {
        "analysis_code_sha256": sha256(Path(__file__)),
        "input": {"runs_root": str(args.runs), "run_metadata_and_verifier_file_count": sum(1 for _ in args.runs.glob("*/metadata.json"))},
        "definitions": {"primary_pass": "verifier.json.passed is true", "primary_denominator": "all records except provider_error_protocol (retry-exhausted transport); hard timeouts remain failures", "legacy_pass": "retained comparison only"},
        "task_condition_distribution": cells,
        "paired_C1_minus_C0_by_model_split": {
            "all_admitted_tasks": paired_summary(exclude_b09=False),
            "leave_out_test_in_b09_phone": paired_summary(exclude_b09=True),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"runs": len(rows), "output": str(args.output), "analysis_code_sha256": output["analysis_code_sha256"]}))


if __name__ == "__main__":
    main()
