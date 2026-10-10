#!/usr/bin/env python3
"""Read-only verifier-pass erratum audit for retained r2 cohorts."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAP = 32


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def tool_events(run_dir: Path) -> list[dict]:
    path = run_dir / "events.jsonl"
    if not path.exists():
        return []
    events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    return [event for event in events if event.get("event") == "tool_result"]


def records(root: Path, cohort: str) -> list[dict]:
    result = []
    for metadata_path in sorted(root.glob("*/metadata.json")):
        metadata = read_json(metadata_path)
        verifier_path = metadata_path.parent / "verifier.json"
        verifier = read_json(verifier_path) if verifier_path.exists() else {}
        flags = metadata.get("outcome_flags") or {}
        legacy = metadata.get("legacy_outcome_category", metadata.get("outcome_category"))
        provider_error = bool(flags.get("provider_error") or metadata.get("outcome_category") == "provider_error")
        result.append({
            "cohort": cohort,
            "run_dir": str(metadata_path.parent.relative_to(ROOT)),
            "run_id": metadata["run_id"],
            "model": metadata.get("requested_model_id"),
            "task": metadata.get("task_id"),
            "condition": metadata.get("condition") or ("l3b" if metadata.get("l3b_trigger_at") is not None else "baseline"),
            "legacy_outcome": legacy,
            "legacy_pass": legacy == "pass",
            "verifier_available": "passed" in verifier,
            "verifier_pass": verifier.get("passed") is True,
            "verifier_fail": verifier.get("passed") is False,
            "provider_error": provider_error,
            "tool_calls": len(tool_events(metadata_path.parent)),
            "l3b_triggered": bool(metadata.get("l3b_triggered")),
            "l3b_trigger_at": metadata.get("l3b_trigger_at"),
            "final_empty": bool(flags.get("final_empty")),
        })
    return result


def summary(rows: list[dict]) -> dict:
    scheduled = len(rows)
    providers = sum(row["provider_error"] for row in rows)
    usable = [row for row in rows if not row["provider_error"]]
    legacy = sum(row["legacy_pass"] for row in usable)
    verifier = sum(row["verifier_pass"] for row in usable)
    return {
        "scheduled": scheduled,
        "provider_error": providers,
        "verifier_available": sum(row["verifier_available"] for row in rows),
        "primary_denominator_excluding_provider_error": len(usable),
        "legacy_pass_numerator": legacy,
        "legacy_pass_rate": legacy / len(usable) if usable else None,
        "verifier_pass_numerator": verifier,
        "verifier_pass_rate": verifier / len(usable) if usable else None,
        "difference_verifier_minus_legacy_passes": verifier - legacy,
        "sensitivity_denominator_including_provider_error": scheduled,
        "verifier_pass_rate_provider_as_nonpass": verifier / scheduled if scheduled else None,
        "provider_errors_with_verifier_result": sum(row["provider_error"] and row["verifier_available"] for row in rows),
        "provider_errors_with_verifier_fail": sum(row["provider_error"] and row["verifier_fail"] for row in rows),
    }


def by_field(rows: list[dict], field: str) -> dict[str, dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(field))].append(row)
    return {key: summary(value) for key, value in sorted(grouped.items())}


def l3b_detail(rows: list[dict]) -> dict:
    replay: dict[str, dict] = {}
    replay_path = ROOT / "data" / "l3b_replay_at32.csv"
    with replay_path.open(newline="", encoding="utf-8") as handle:
        for item in csv.DictReader(handle):
            replay[item["run_id"]] = item
    result: dict[str, dict] = {}
    for condition in ("baseline", "l3b"):
        selected = [row for row in rows if row["condition"] == condition]
        layers = {"A_reached_call_32": [row for row in selected if row["tool_calls"] >= CAP], "B_ended_before_32": [row for row in selected if row["tool_calls"] < CAP]}
        result[condition] = {name: summary(values) for name, values in layers.items()}
        if condition == "l3b":
            triggered = [row for row in selected if row["l3b_triggered"]]
            validations = []
            for row in triggered:
                path = ROOT / row["run_dir"] / "events.jsonl"
                events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
                marker = next((index for index, event in enumerate(events) if event.get("event") == "l3b_budget_reminder_injected"), None)
                after = events[marker + 1:] if marker is not None else []
                validations.append(any(event.get("event") == "tool_result" and event.get("tool_name") == "run_command" and any(token in str(event.get("arguments") or "").lower() for token in ("test", "pytest", "unittest", "py_compile")) for event in after))
            replayable = [replay[row["run_id"]] for row in triggered if replay.get(row["run_id"], {}).get("final_minus_at32") not in (None, "")]
            result[condition]["trigger_conversion"] = {
                "triggered_runs": len(triggered),
                "post_trigger_validation_numerator": sum(validations),
                "post_trigger_validation_denominator": len(validations),
                "post_trigger_partial_increase_numerator": sum(float(item["final_minus_at32"]) > 0 for item in replayable),
                "post_trigger_partial_increase_denominator": len(replayable),
                "post_trigger_verifier_pass_numerator": sum(row["verifier_pass"] for row in triggered if not row["provider_error"]),
                "post_trigger_verifier_pass_denominator": sum(not row["provider_error"] for row in triggered),
            }
        else:
            eligible = [row for row in layers["A_reached_call_32"] if replay.get(row["run_id"], {}).get("final_minus_at32") not in (None, "")]
            result[condition]["negative_control"] = {
                "A_layer_replayable_runs": len(eligible),
                "A_layer_partial_increase_numerator": sum(float(replay[row["run_id"]]["final_minus_at32"]) > 0 for row in eligible),
                "A_layer_verifier_pass_numerator": sum(row["verifier_pass"] for row in layers["A_reached_call_32"] if not row["provider_error"]),
                "A_layer_verifier_pass_denominator": sum(not row["provider_error"] for row in layers["A_reached_call_32"]),
            }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "verifier_pass_erratum_20261010.json")
    args = parser.parse_args()
    cohorts = {
        "S4_r2": ROOT / "data" / "b3_s4_r2_runs",
        "S5_r2_raw": ROOT / "data" / "b3_s5_r2_runs",
        "S5_provider_replacements": ROOT / "data" / "b5_provider_replacements",
        "S6_L3b_dev_validate": ROOT / "data" / "l3b_runs",
        "S7_completed_snapshot": ROOT / "data" / "s7_runs",
    }
    all_records = {name: records(path, name) for name, path in cohorts.items()}
    s5_effective = [row for row in all_records["S5_r2_raw"] if not row["provider_error"]] + all_records["S5_provider_replacements"]
    s4_by_model = by_field(all_records["S4_r2"], "model")
    calibration = {model: {**value, "eligible_20_to_80_percent": value["verifier_pass_rate"] is not None and .2 <= value["verifier_pass_rate"] <= .8} for model, value in s4_by_model.items()}
    payload = {
        "scope": "read_only_verifier_pass_erratum; legacy outcomes retained and not overwritten",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "cohort_summary": {name: summary(rows) for name, rows in all_records.items()},
        "S5_replacement_inclusive_effective_36": summary(s5_effective),
        "S4_calibration_by_model": calibration,
        "S4_selection_rule": "primary verifier-pass rate, provider errors excluded; eligible if 0.20 <= rate <= 0.80",
        "S6_L3b_verifier_pass_stratification": l3b_detail(all_records["S6_L3b_dev_validate"]),
        "S7_by_model_condition": {},
        "records": {name: rows for name, rows in all_records.items()},
    }
    # Construct S7 groups after the serializable payload skeleton above.
    s7_groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for item in all_records["S7_completed_snapshot"]:
        s7_groups[(str(item["model"]), str(item["condition"]))].append(item)
    payload["S7_by_model_condition"] = {f"{model}::{condition}": summary(values) for (model, condition), values in sorted(s7_groups.items())}
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "s7_runs": len(all_records["S7_completed_snapshot"])}))


if __name__ == "__main__":
    main()
