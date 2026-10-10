#!/usr/bin/env python3
"""Compare confirmed human failure labels with local mechanical signals."""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data/b5_r2_blinded_packets/b5_r2_private_manifest.json"
HUMAN = ROOT / "data/b5_r2_human_review/human_annotations.jsonl"
RUNS = ROOT / "data/b3_s5_r2_runs"
OUTPUT = ROOT / "data/b5_r2_human_mechanical_audit_20261010.json"
KEYWORDS = ("test", "pytest", "unittest", "py_compile")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def binom_cdf(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k + 1))


def clopper_pearson(x: int, n: int, alpha: float = 0.05) -> list[float]:
    if n == 0:
        return [0.0, 1.0]
    if x == 0:
        lower = 0.0
    else:
        lo, hi = 0.0, x / n
        for _ in range(80):
            mid = (lo + hi) / 2
            # P_p(X >= x) increases with p.
            tail = 1 - binom_cdf(x - 1, n, mid)
            if tail < alpha / 2:
                lo = mid
            else:
                hi = mid
        lower = (lo + hi) / 2
    if x == n:
        upper = 1.0
    else:
        lo, hi = x / n, 1.0
        for _ in range(80):
            mid = (lo + hi) / 2
            # P_p(X <= x) decreases with p.
            if binom_cdf(x, n, mid) > alpha / 2:
                lo = mid
            else:
                hi = mid
        upper = (lo + hi) / 2
    return [lower, upper]


def inspect(run_dir: Path) -> dict[str, bool]:
    events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    tools = [event for event in events if event.get("event") == "tool_result"]
    writes = [index for index, event in enumerate(tools) if event.get("tool_name") == "write_file"]
    validations = [index for index, event in enumerate(tools)
                   if event.get("tool_name") == "run_command"
                   and any(word in str(event.get("arguments") or "").lower() for word in KEYWORDS)]
    repeated = Counter((str(event.get("tool_name")), str(event.get("arguments"))) for event in tools)
    tool_error = False
    for event in tools:
        result = event.get("result") or {}
        if result.get("ok") is False:
            tool_error = True
        if event.get("tool_name") == "run_command" and (result.get("timed_out") or result.get("returncode") not in (None, 0)):
            tool_error = True
    corrupt = False
    workspace = run_dir / "workspace"
    for source in workspace.rglob("*.py") if workspace.exists() else []:
        try:
            compile(source.read_text(encoding="utf-8"), str(source), "exec")
        except (SyntaxError, UnicodeError):
            corrupt = True
            break
    return {
        "insufficient_validation": bool(writes and not any(index > writes[-1] for index in validations)),
        "ineffective_debugging_loop": any(count >= 3 for count in repeated.values()),
        "tool_misuse": tool_error,
        "file_corruption": corrupt,
    }


def comparison(records: list[dict], label: str) -> dict:
    agree = sum(row["human"][label] == row["mechanical"][label] for row in records)
    table = {
        "human_positive_mechanical_positive": sum(row["human"][label] and row["mechanical"][label] for row in records),
        "human_positive_mechanical_negative": sum(row["human"][label] and not row["mechanical"][label] for row in records),
        "human_negative_mechanical_positive": sum(not row["human"][label] and row["mechanical"][label] for row in records),
        "human_negative_mechanical_negative": sum(not row["human"][label] and not row["mechanical"][label] for row in records),
    }
    return {"n": len(records), "agreement_n": agree, "agreement_rate": agree / len(records),
            "clopper_pearson_95": clopper_pearson(agree, len(records)), "contingency_2x2": table}


def main() -> None:
    manifest = load(MANIFEST)
    human_rows = [json.loads(line) for line in HUMAN.read_text(encoding="utf-8").splitlines() if line.strip()]
    if {row.get("annotator_id") for row in human_rows} != {"wangqichen"}:
        raise SystemExit("mechanical audit requires 24 confirmed wangqichen annotations")
    human = {row["run_id"]: set(row["failure_modes"]) for row in human_rows}
    records = []
    labels = ("insufficient_validation", "ineffective_debugging_loop", "tool_misuse", "file_corruption")
    for item in manifest:
        packet, run_id = item["packet_id"], item["run_id"]
        machine = inspect(RUNS / run_id)
        records.append({"packet_id": packet, "human": {label: label in human[packet] for label in labels}, "mechanical": machine})
    payload = {
        "scope": "24 confirmed human labels; local historical B5 trajectories only; post hoc mechanical convergent audit",
        "definitions": {
            "insufficient_validation": "edited run has no later run_command containing test, pytest, unittest, or py_compile",
            "ineffective_debugging_loop": "an identical tool-name/arguments pair occurs at least three times",
            "tool_misuse": "a tool reports ok=false, or run_command times out/returns nonzero",
            "file_corruption": "at least one final workspace Python file fails compile(source, ..., 'exec')",
            "interval": "two-sided Clopper-Pearson 95% interval for raw agreement",
        },
        "by_label": {label: comparison(records, label) for label in labels},
        "records": records,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "packets": len(records)}))


if __name__ == "__main__":
    main()
