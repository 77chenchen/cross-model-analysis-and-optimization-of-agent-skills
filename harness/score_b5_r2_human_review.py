#!/usr/bin/env python3
"""Validate completed B5-r2 human labels and then calculate Cohen's kappa.

This utility is intentionally inert until all 24 independent human labels are
present. It writes no report and never exposes judge labels to the reviewer.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKETS = ROOT / "data" / "b5_r2_human_review"
HUMAN_PATH = PACKETS / "human_annotations.jsonl"
JUDGE_DIR = ROOT / "data" / "b5_r2_blinded_annotations"
LABELS = [
    "premature_implementation", "repeated_exploration", "ineffective_debugging_loop",
    "insufficient_validation", "missed_constraint", "premature_completion",
    "tool_misuse", "empty_termination", "file_corruption",
]


def main() -> None:
    packet_ids = {path.stem for path in PACKETS.glob("packet_*.json")}
    if len(packet_ids) != 24:
        raise SystemExit(f"expected 24 public packets, found {len(packet_ids)}")
    if not HUMAN_PATH.exists():
        raise SystemExit(f"human labels not found: {HUMAN_PATH}")
    human_rows = [json.loads(line) for line in HUMAN_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    human = {row.get("run_id"): row for row in human_rows}
    if len(human_rows) != len(human) or set(human) != packet_ids:
        raise SystemExit("need exactly one human JSON object for every packet_001 through packet_024")
    if any(row.get("blinded") is not True for row in human.values()):
        raise SystemExit("all human labels must retain blinded: true")
    if any("unscorable" in row.get("failure_modes", []) for row in human.values()):
        raise SystemExit("at least one human packet is unscorable; retain raw labels and resolve protocol treatment before kappa")
    pairs = []
    for packet_id in sorted(packet_ids):
        judge = json.loads((JUDGE_DIR / f"{packet_id}.json").read_text(encoding="utf-8"))
        for label in LABELS:
            pairs.append((label in judge["failure_modes"], label in human[packet_id].get("failure_modes", [])))
    observed = sum(a == b for a, b in pairs) / len(pairs)
    judge_rate = sum(a for a, _ in pairs) / len(pairs)
    human_rate = sum(b for _, b in pairs) / len(pairs)
    expected = judge_rate * human_rate + (1 - judge_rate) * (1 - human_rate)
    kappa = (observed - expected) / (1 - expected) if expected != 1 else None
    print(json.dumps({"unit": "packet_failure_mode", "packets": len(packet_ids), "pairs": len(pairs), "observed_agreement": observed, "expected_agreement": expected, "cohens_kappa": kappa}, indent=2))


if __name__ == "__main__":
    main()
