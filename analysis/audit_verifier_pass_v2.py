#!/usr/bin/env python3
"""Read-only old/new outcome audit for completed cohorts and interim S7."""
from __future__ import annotations

import json
from pathlib import Path

from analysis.verifier_pass_v2 import ROOT, VERSION, read_records, sensitivity_views


def main() -> None:
    roots = {
        "S4": ROOT / "data/b3_s4_r2_runs",
        "S5_original": ROOT / "data/b3_s5_r2_runs",
        "S5_replacements": ROOT / "data/b5_provider_replacements",
        "S6_L3b": ROOT / "data/l3b_runs",
    }
    cohorts = {name: read_records(path) for name, path in roots.items()}
    s5_effective = [row for row in cohorts["S5_original"] if not row["provider_error_protocol"]] + cohorts["S5_replacements"]
    completed = {name: sensitivity_views(rows) for name, rows in cohorts.items()}
    completed["S5_replacement_inclusive"] = sensitivity_views(s5_effective)
    output = ROOT / "data/verifier_pass_v2_cohort_audit.json"
    output.write_text(json.dumps({"analysis_version": VERSION, "cohorts": completed}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    interim_rows = read_records(ROOT / "data/s7_runs")
    interim = ROOT / "data/s7_monitoring/verifier_pass_v2_interim.json"
    interim.parent.mkdir(parents=True, exist_ok=True)
    interim.write_text(json.dumps({
        "watermark": "INTERIM MONITORING — NOT FORMAL S7 RESULTS",
        "analysis_version": VERSION,
        "completed_records_at_snapshot": len(interim_rows),
        "views": sensitivity_views(interim_rows),
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"completed_audit": str(output), "s7_interim": str(interim), "s7_records": len(interim_rows)}))


if __name__ == "__main__":
    main()
