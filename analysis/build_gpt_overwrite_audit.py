#!/usr/bin/env python3
"""Write the retained manifest for the owner-directed GPT overwrite event."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from analysis.verifier_pass_v2 import ROOT

SCHEDULE = ROOT / "config" / "s7_schedules" / "gpt_5_6_sol.tsv"
OUT = ROOT / "data" / "s7_gpt_overwrite_audit_20261011.json"
INITIAL_USABLE = {
    "s7-gpt-5-6-sol-test_in_a11_duration-C0-r1",
    "s7-gpt-5-6-sol-test_out_c04_policy-C1-r3",
    "s7-gpt-5-6-sol-test_in_b08_total-C0-r2",
    "s7-gpt-5-6-sol-test_in_a12_enum-C1-r1",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    with SCHEDULE.open(encoding="utf-8", newline="") as handle:
        schedule = list(csv.DictReader(handle, delimiter="\t"))
    run_ids = [row["run_id"] for row in schedule]
    overwritten = [run_id for run_id in run_ids if run_id not in INITIAL_USABLE]
    assert len(run_ids) == 108 and len(overwritten) == 104
    payload = {
        "schema_version": "s7-gpt-overwrite-audit-v2",
        "date": "2026-10-11",
        "archive_status": "archives deleted; manifest retained",
        "schedule": {"path": str(SCHEDULE.relative_to(ROOT)), "sha256": sha256(SCHEDULE), "scheduled_runs": 108},
        "initial_cohort": {
            "record_count": 108,
            "overwritten_record_count": 104,
            "retained_initial_usable_record_count": 4,
            "retained_initial_usable_run_ids": sorted(INITIAL_USABLE),
            "overwritten_run_ids": overwritten,
            "failure_reason_classification": {"codex_usage_limit_rejection": 104},
        },
        "deleted_archives": [
            {"former_path": "/tmp/s7-gpt-overwrite.qlslty", "record_count": 104, "failure_reason_classification": {"codex_usage_limit_rejection": 104}, "sha256": None, "sha256_status": "not computed before deletion"},
            {"former_path": "/tmp/s7-gpt-overwrite-round2.lAppQs", "record_count": 42, "failure_reason_classification": {"codex_usage_limit_rejection": 42}, "sha256": None, "sha256_status": "not computed before deletion"},
        ],
        "final_active_cohort": {"record_count": 108, "provider_error_protocol": 0, "note": "Active artifacts are the post-overwrite cohort; this manifest is not an archived-response substitute."},
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"overwritten": len(overwritten), "schedule_sha256": payload["schedule"]["sha256"]}))


if __name__ == "__main__":
    main()
