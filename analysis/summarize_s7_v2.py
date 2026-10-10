#!/usr/bin/env python3
"""Formal S7 summary entry; hard-gated until all 870 locked runs complete."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from analysis.verifier_pass_v2 import ROOT, VERSION, enforce_formal_s7_gate, read_records, sensitivity_views


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=ROOT / "data/s7_runs")
    parser.add_argument("--output", type=Path, default=ROOT / "results/s7_verifier_pass_v2.json")
    args = parser.parse_args()
    manifest = enforce_formal_s7_gate(ROOT / "STATUS.md", ROOT / "analysis/analysis_patch_manifest.json")
    rows = read_records(args.runs)
    payload = {"analysis_version": VERSION, "patch_manifest": manifest, "views": sensitivity_views(rows)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"runs": len(rows), "output": str(args.output)}))


if __name__ == "__main__":
    main()
