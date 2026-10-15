#!/usr/bin/env python3
"""Refresh the checked-in batch progress ledger from artifact directories."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def count_metadata(root: Path) -> int:
    return len(list(root.glob("pilot_*/metadata.json"))) if root.exists() else 0

def count_s7(root: Path) -> int:
    return len(list(root.glob("s7-*/metadata.json"))) if root.exists() else 0

# B0/B2 preserve some historical payloads without per-run metadata.  The
# reviewed protocol ledger therefore remains the authoritative 246 total.
science_completed = 246
replacements = count_metadata(ROOT / "data/b5_provider_replacements")
judge = len(list((ROOT / "data/b5_r2_blinded_annotations").glob("packet_*.json")))
l3b = count_metadata(ROOT / "data/l3b_runs")
s7 = count_s7(ROOT / "data/s7_runs")
s8 = count_metadata(ROOT / "data/s8_runs")
if l3b == 0:
    l3b_state = "preregistered; awaiting user confirmation"
    current = "Current task: B5 is complete; awaiting explicit user authorization before the preregistered L3b batch."
    estimate = "Estimated remaining: 72 L3b runs only if explicitly authorized; otherwise the next stage is S7 planning, not execution."
elif l3b < 72:
    l3b_state = "running sequentially at worker_concurrency=1"
    current = "Current task: L3b dev-validate batch is running; no test split is runnable by these scripts."
    estimate = f"Estimated remaining: {72-l3b} L3b runs; S7 remains planning-only."
else:
    l3b_state = "complete; analysis pending"
    current = "Current task: L3b batch complete; prepare its descriptive analysis without running test splits."
    estimate = "Estimated remaining: no authorized model runs; S7 remains planning-only."
if s7 == 0:
    s7_state = "locked; not started"
    current = "Current task: S7 execution lock is complete; no scheduled test run has started."
    estimate = "Estimated remaining: 1086 locked S7 runs; resume only in the checked-in per-model schedule order."
elif s7 < 1086:
    s7_state = "running in locked schedule order"
    current = "Current task: S7 is running from immutable schedules; completed run IDs are resumable only with complete artifacts."
    estimate = f"Estimated remaining: {1086-s7} locked S7 runs."
else:
    if (ROOT / "results/s7/analysis_manifest.json").exists():
        s7_state = "complete; formal analysis complete"
        current = "Current task: S7 execution and gated formal analysis are complete; await the owner's S8 decision."
        estimate = "Estimated remaining: no authorized model calls; formal S7 tables and figures are available."
    else:
        s7_state = "complete; analysis pending"
        current = "Current task: S7 scheduled runs are complete; derive only the locked analyses."
        estimate = "Estimated remaining: no further model calls; analyze the immutable run artifacts."
if s8 == 0:
    s8_state = "locked; awaiting execution"
elif s8 < 192:
    s8_state = "running sequentially at worker_concurrency=1"
    current = "Current task: S8 dev-only mechanism study is running in its immutable schedule order."
    estimate = f"Estimated remaining: {192-s8} S8 runs; S7 remains complete and immutable."
else:
    s8_state = "complete; analysis pending"
    current = "Current task: S8 dev-only mechanism study is complete; derive the predeclared analysis."
    estimate = "Estimated remaining: no authorized model calls; analyze immutable S8 artifacts."
lines = [
    "# Batch status", "",
    "This ledger is refreshed by `harness/update_status.py` after each completed run or judge annotation.", "",
    "| batch | planned | completed | remaining | state |",
    "|---|---:|---:|---:|---|",
    f"| Historical/direct r2 science runs | 246 | {science_completed} | {max(0,246-science_completed)} | complete (legacy and B0--B4 evidence) |",
    f"| B5 provider-error replacements | 8 | {replacements} | {max(0,8-replacements)} | protocol committed; sequential concurrency=1 |",
    f"| B5 r2 blind LLM judge | 24 | {judge} | {max(0,24-judge)} | newly anonymized packets only |",
    f"| L3b dev-validate | 72 | {l3b} | {max(0,72-l3b)} | {l3b_state} |",
    f"| S7 locked formal benchmark | 1086 | {s7} | {max(0,1086-s7)} | {s7_state} |",
    f"| S8 dev-only mechanism study | 192 | {s8} | {max(0,192-s8)} | {s8_state} |",
    "", current, estimate, "",
]
(ROOT / "STATUS.md").write_text("\n".join(lines), encoding="utf-8")
