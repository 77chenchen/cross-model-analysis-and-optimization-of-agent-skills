#!/usr/bin/env python3
"""Report raw B3/S5 and replacement-inclusive denominators separately."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def metadata(directory: str):
    return [json.loads(path.read_text()) for path in sorted((ROOT / directory).glob("pilot_*/metadata.json"))]

original = metadata("data/b3_s5_r2_runs")
replacement = metadata("data/b5_provider_replacements")
replaced_ids = {row.get("replacement_of") for row in replacement}

def summary(rows):
    counts = Counter(row["outcome_category"] for row in rows)
    denominator = len(rows) - counts["provider_error"]
    return {"runs": len(rows), "outcomes": dict(sorted(counts.items())), "pass_denominator_excluding_provider_error": denominator, "passes": counts["pass"], "pass_rate": counts["pass"] / denominator if denominator else None}

raw = summary(original)
replacement_inclusive = summary([row for row in original if row["run_id"] not in replaced_ids] + replacement)
report = {"raw_original_36": raw, "replacement_inclusive": replacement_inclusive, "replacement_runs_completed": len(replacement), "replacement_ids_expected": 8, "note": "Provider errors are excluded from every pass denominator; old records remain unchanged."}
output = ROOT / "data/b5_provider_replacement_summary.json"
output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
