#!/usr/bin/env python3
"""Draw deterministic model-by-outcome strata for blinded S7 trajectory review."""
from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

try:
    from .s7_protocol import ROOT
except ImportError:
    from s7_protocol import ROOT


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=ROOT / "data" / "s7_runs")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "s7_blinded_packets.jsonl")
    parser.add_argument("--per-stratum", type=int, default=2)
    parser.add_argument("--seed", type=int, default=719009)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    strata: dict[tuple[str, str], list[Path]] = defaultdict(list)
    for meta in sorted(args.runs.glob("*/metadata.json")):
        value = json.loads(meta.read_text(encoding="utf-8"))
        strata[(str(value.get("requested_model_id")), str(value.get("outcome_category")))].append(meta.parent)
    selected = []
    for key, directories in sorted(strata.items()):
        rng.shuffle(directories)
        selected.extend((key, directory) for directory in directories[:args.per_stratum])
    with args.output.open("w", encoding="utf-8") as handle:
        for index, (_, directory) in enumerate(selected, start=1):
            metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
            events = (directory / "events.jsonl").read_text(encoding="utf-8") if (directory / "events.jsonl").exists() else ""
            handle.write(json.dumps({"packet_id": f"s7-blind-{index:04d}", "task_id": metadata.get("task_id"), "condition": metadata.get("condition"), "trajectory": events, "final_message": (directory / "final.md").read_text(encoding="utf-8") if (directory / "final.md").exists() else ""}, ensure_ascii=False) + "\n")
    print(json.dumps({"packets": len(selected), "strata": len(strata), "seed": args.seed, "output": str(args.output)}))


if __name__ == "__main__":
    main()
