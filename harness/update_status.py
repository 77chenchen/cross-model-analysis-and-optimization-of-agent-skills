#!/usr/bin/env python3
"""Refresh the checked-in batch progress ledger from artifact directories."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def count_metadata(root: Path) -> int:
    return len(list(root.glob("pilot_*/metadata.json"))) if root.exists() else 0

# B0/B2 preserve some historical payloads without per-run metadata.  The
# reviewed protocol ledger therefore remains the authoritative 246 total.
science_completed = 246
replacements = count_metadata(ROOT / "data/b5_provider_replacements")
judge = len(list((ROOT / "data/b5_r2_blinded_annotations").glob("packet_*.json")))
l3b = count_metadata(ROOT / "data/l3b_runs")
lines = [
    "# Batch status", "",
    "This ledger is refreshed by `harness/update_status.py` after each completed run or judge annotation.", "",
    "| batch | planned | completed | remaining | state |",
    "|---|---:|---:|---:|---|",
    f"| Historical/direct r2 science runs | 246 | {science_completed} | {max(0,246-science_completed)} | complete (legacy and B0--B4 evidence) |",
    f"| B5 provider-error replacements | 8 | {replacements} | {max(0,8-replacements)} | protocol committed; sequential concurrency=1 |",
    f"| B5 r2 blind LLM judge | 24 | {judge} | {max(0,24-judge)} | newly anonymized packets only |",
    f"| L3b dev-validate (not authorized to run) | 72 | {l3b} | {max(0,72-l3b)} | preregistered; awaiting user confirmation |",
    "", "Current task: B5 protocol artifacts, provider replacements, and blind judge; no test split is runnable by these scripts.",
    "Estimated remaining after this commit: 8 sequential replacement runs and 24 judge calls; L3b remains excluded until explicit authorization.", "",
]
(ROOT / "STATUS.md").write_text("\n".join(lines), encoding="utf-8")
