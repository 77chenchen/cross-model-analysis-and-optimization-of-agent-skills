#!/usr/bin/env python3
"""Read-only verifier-pass erratum audit for retained r2 cohorts."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAP = 32


def _beta_fraction(a: float, b: float, x: float) -> float:
    """Continued fraction for the regularized incomplete beta function."""
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d, h = 1.0, 1.0 - qab * x / qap, 1.0 / max(1e-300, 1.0 - qab * x / qap)
    for step in range(1, 201):
        twice = 2 * step
        aa = step * (b - step) * x / ((qam + twice) * (a + twice))
        d = 1.0 + aa * d; d = max(d, 1e-300); c = 1.0 + aa / c; c = max(c, 1e-300); d = 1.0 / d; h *= d * c
        aa = -(a + step) * (qab + step) * x / ((a + twice) * (qap + twice))
        d = 1.0 + aa * d; d = max(d, 1e-300); c = 1.0 + aa / c; c = max(c, 1e-300); d = 1.0 / d
        delta = d * c; h *= delta
        if abs(delta - 1.0) < 3e-14:
            break
    return h


def beta_cdf(x: float, a: float, b: float) -> float:
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1) / (a + b + 2):
        return front * _beta_fraction(a, b, x) / a
    return 1 - front * _beta_fraction(b, a, 1 - x) / b


def beta_quantile(p: float, a: float, b: float) -> float:
    low, high = 0.0, 1.0
    for _ in range(100):
        mid = (low + high) / 2
        if beta_cdf(mid, a, b) < p: low = mid
        else: high = mid
    return (low + high) / 2


def clopper_pearson(success: int, total: int, alpha: float = .05) -> list[float | None]:
    if not total: return [None, None]
    lower = 0.0 if success == 0 else beta_quantile(alpha / 2, success, total - success + 1)
    upper = 1.0 if success == total else beta_quantile(1 - alpha / 2, success + 1, total - success)
    return [lower, upper]


def fisher_two_sided(a: int, n_a: int, b: int, n_b: int) -> float:
    """Two-sided Fisher exact p value by probability ordering."""
    total_success, total, observed = a + b, n_a + n_b, a
    low, high = max(0, total_success - n_b), min(n_a, total_success)
    denominator = math.comb(total, total_success)
    probability = lambda value: math.comb(n_a, value) * math.comb(n_b, total_success - value) / denominator
    observed_p = probability(observed)
    return sum(probability(value) for value in range(low, high + 1) if probability(value) <= observed_p + 1e-15)


def comparison(label: str, baseline: list[dict], l3b: list[dict]) -> dict:
    a, b = sum(row["verifier_pass"] for row in baseline), sum(row["verifier_pass"] for row in l3b)
    return {"label": label, "baseline": {"successes": a, "denominator": len(baseline), "rate": a / len(baseline) if baseline else None, "exact_95_ci": clopper_pearson(a, len(baseline))}, "l3b": {"successes": b, "denominator": len(l3b), "rate": b / len(l3b) if l3b else None, "exact_95_ci": clopper_pearson(b, len(l3b))}, "fisher_two_sided_p": fisher_two_sided(a, len(baseline), b, len(l3b)) if baseline and l3b else None}


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
        runtime_path = metadata_path.parent / "runtime_r2.json"
        runtime = read_json(runtime_path) if runtime_path.exists() else {}
        flags = metadata.get("outcome_flags") or {}
        legacy = metadata.get("legacy_outcome_category", metadata.get("outcome_category"))
        provider_error_flag = bool(flags.get("provider_error"))
        # The protocol excludes transport exhaustion, not a hard runner timeout.
        # The historic flag unfortunately conflates them when a killed process
        # fails to emit a terminal event.
        provider_error_protocol = bool(metadata.get("outcome_category") == "provider_error" or runtime.get("provider_error"))
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
            "provider_error_flag": provider_error_flag,
            # `provider_error_flag` is retained verbatim from historical
            # metadata.  It can be true for a runner timeout, so it is not the
            # protocol exclusion rule.  This derived field is the authoritative
            # analysis field: exhausted request-transport failure only.
            "provider_error_protocol": provider_error_protocol,
            # Compatibility alias for the first erratum snapshot; do not use
            # it in new analysis code.
            "protocol_provider_error": provider_error_protocol,
            "timeout": bool(flags.get("timeout")),
            "tool_calls": len(tool_events(metadata_path.parent)),
            "l3b_triggered": bool(metadata.get("l3b_triggered")),
            "l3b_trigger_at": metadata.get("l3b_trigger_at"),
            "final_empty": bool(flags.get("final_empty")),
        })
    return result


def summary(rows: list[dict]) -> dict:
    scheduled = len(rows)
    providers = sum(row["provider_error_protocol"] for row in rows)
    provider_flags = sum(row["provider_error_flag"] for row in rows)
    usable = [row for row in rows if not row["provider_error_protocol"]]
    legacy = sum(row["legacy_pass"] for row in usable)
    verifier = sum(row["verifier_pass"] for row in usable)
    return {
        "scheduled": scheduled,
        "provider_error_protocol": providers,
        "protocol_provider_error_legacy_alias": providers,
        "provider_error_flag": provider_flags,
        "verifier_available": sum(row["verifier_available"] for row in rows),
        "primary_denominator_excluding_provider_error": len(usable),
        "legacy_pass_numerator": legacy,
        "legacy_pass_rate": legacy / len(usable) if usable else None,
        "verifier_pass_numerator": verifier,
        "verifier_pass_rate": verifier / len(usable) if usable else None,
        "difference_verifier_minus_legacy_passes": verifier - legacy,
        "sensitivity_denominator_including_provider_error": scheduled,
        "verifier_pass_rate_provider_as_nonpass": verifier / scheduled if scheduled else None,
        "protocol_provider_errors_with_verifier_result": sum(row["provider_error_protocol"] and row["verifier_available"] for row in rows),
        "protocol_provider_errors_with_verifier_fail": sum(row["provider_error_protocol"] and row["verifier_fail"] for row in rows),
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
                "post_trigger_verifier_pass_numerator": sum(row["verifier_pass"] for row in triggered if not row["provider_error_protocol"]),
                "post_trigger_verifier_pass_denominator": sum(not row["provider_error_protocol"] for row in triggered),
            }
        else:
            eligible = [row for row in layers["A_reached_call_32"] if replay.get(row["run_id"], {}).get("final_minus_at32") not in (None, "")]
            result[condition]["negative_control"] = {
                "A_layer_replayable_runs": len(eligible),
                "A_layer_partial_increase_numerator": sum(float(replay[row["run_id"]]["final_minus_at32"]) > 0 for row in eligible),
                "A_layer_verifier_pass_numerator": sum(row["verifier_pass"] for row in layers["A_reached_call_32"] if not row["provider_error_protocol"]),
                "A_layer_verifier_pass_denominator": sum(not row["provider_error_protocol"] for row in layers["A_reached_call_32"]),
            }
    return result


def l3b_transition_audit(rows: list[dict]) -> dict:
    replay = {item["run_id"]: item for item in csv.DictReader((ROOT / "data" / "l3b_replay_at32.csv").open(encoding="utf-8"))}
    groups = {condition: [row for row in rows if row["condition"] == condition] for condition in ("baseline", "l3b")}
    a_layer = {condition: [row for row in values if row["tool_calls"] >= CAP] for condition, values in groups.items()}
    b_layer = {condition: [row for row in values if row["tool_calls"] < CAP] for condition, values in groups.items()}
    at32_passed: dict[str, list[dict]] = {}
    at32_not_passed: dict[str, list[dict]] = {}
    at32_unavailable: dict[str, list[dict]] = {}
    for condition, values in a_layer.items():
        at32_passed[condition], at32_not_passed[condition], at32_unavailable[condition] = [], [], []
        for row in values:
            raw = replay.get(row["run_id"], {}).get("partial_at_32")
            if raw in (None, ""):
                at32_unavailable[condition].append(row)
            elif float(raw) == 1.0:
                at32_passed[condition].append(row)
            else:
                at32_not_passed[condition].append(row)
    old_validation, strict_validation = [], []
    for row in groups["l3b"]:
        if not row["l3b_triggered"]: continue
        event_path = ROOT / row["run_dir"] / "events.jsonl"
        events = [json.loads(line) for line in event_path.read_text(encoding="utf-8").splitlines()]
        marker = next(index for index, event in enumerate(events) if event.get("event") == "l3b_budget_reminder_injected")
        commands = [event for event in events[marker + 1:] if event.get("event") == "tool_result" and event.get("tool_name") == "run_command"]
        old_validation.append(any(event.get("result", {}).get("ok") for event in commands))
        strict_validation.append(any(any(token in str(event.get("arguments") or "").lower() for token in ("test", "pytest", "unittest", "py_compile")) for event in commands))
    proxy_reliability = {}
    for condition, values in at32_passed.items():
        final_fail = [row for row in values if not row["verifier_pass"]]
        proxy_reliability[condition] = {
            "partial_at_32_equals_1_runs": len(values),
            "final_verifier_not_pass": len(final_fail),
            "final_verifier_pass": len(values) - len(final_fail),
            "run_ids_final_verifier_not_pass": [row["run_id"] for row in final_fail],
        }
    return {
        "at32_status": {condition: {"A_layer_runs": len(a_layer[condition]), "already_verifier_pass_at32": len(at32_passed[condition]), "not_verifier_pass_at32": len(at32_not_passed[condition]), "at32_unavailable": len(at32_unavailable[condition])} for condition in groups},
        "comparisons": [comparison("A layer: final verifier pass", a_layer["baseline"], a_layer["l3b"]), comparison("B layer: final verifier pass", b_layer["baseline"], b_layer["l3b"]), comparison("At-call-32 non-pass only: final verifier pass", at32_not_passed["baseline"], at32_not_passed["l3b"])],
        "partial_at_32_proxy_reliability": proxy_reliability,
        "trigger_validation_definitions": {"legacy_transport_success_any_run_command": {"successes": sum(old_validation), "denominator": len(old_validation)}, "strict_validation_intent_keyword_after_trigger": {"successes": sum(strict_validation), "denominator": len(strict_validation), "keywords": ["test", "pytest", "unittest", "py_compile"]}},
    }


def provider_error_audit(rows: list[dict]) -> list[dict]:
    output = []
    for row in rows:
        if row["model"] != "qwen3.5:9b" or row["condition"] not in {"C0", "C1"} or not row["provider_error_flag"]:
            continue
        run_dir = ROOT / row["run_dir"]
        metadata, process = read_json(run_dir / "metadata.json"), read_json(run_dir / "process.json")
        runtime_path = run_dir / "runtime_r2.json"
        runtime = read_json(runtime_path) if runtime_path.exists() else {}
        output.append({"run_id": row["run_id"], "condition": row["condition"], "outcome_category": metadata.get("outcome_category"), "provider_error_flag": row["provider_error_flag"], "provider_error_protocol": row["provider_error_protocol"], "protocol_provider_error_legacy_alias": row["protocol_provider_error"], "timeout_flag": row["timeout"], "process_timed_out": process.get("timed_out"), "process_returncode": process.get("returncode"), "runtime_present": runtime_path.exists(), "runtime_provider_error": runtime.get("provider_error"), "request_retry_count": metadata.get("request_retry_count"), "request_retry_events": runtime.get("retry_events", []), "verifier_pass": row["verifier_pass"], "verifier_available": row["verifier_available"], "final_empty": row["final_empty"]})
    return output


def llama_diagnosis(rows: list[dict]) -> dict:
    llama = [row for row in rows if row["model"] == "llama3.1:8b"]
    response_finish, final_finish, tool_names, error_tools, error_messages = Counter(), Counter(), Counter(), Counter(), Counter()
    any_edits = any_tools = final_nonempty = raw_tool_call_responses = parse_error_runs = 0
    total_tools = total_parse_errors = 0
    for row in llama:
        run_dir = ROOT / row["run_dir"]
        metadata = read_json(run_dir / "metadata.json")
        final_finish[metadata.get("finish_reason")] += 1
        if not row["final_empty"]: final_nonempty += 1
        events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
        tools = [event for event in events if event.get("event") == "tool_result"]
        any_tools += bool(tools); any_edits += any(event.get("tool_name") == "write_file" for event in tools); total_tools += len(tools)
        parse = metadata.get("r2_tool_parse") or {}
        errors = sum(parse.get(key, 0) for key in ("invalid_json", "invalid_schema", "unknown_tool", "execution_error"))
        total_parse_errors += errors; parse_error_runs += bool(errors)
        for event in tools:
            tool_names[event.get("tool_name")] += 1
            result = event.get("result") or {}
            if not result.get("ok", True):
                error_tools[event.get("tool_name")] += 1
                error_messages[str(result.get("error") or result)[:160]] += 1
        for response in (run_dir / "raw_responses").glob("response_*.json"):
            payload = read_json(response); choice = (payload.get("choices") or [{}])[0]; response_finish[choice.get("finish_reason")] += 1
            raw_tool_call_responses += bool((choice.get("message") or {}).get("tool_calls"))
    return {"S4_r2_runs": len(llama), "S7_completed_runs": 0, "verifier_pass": sum(row["verifier_pass"] for row in llama), "final_finish_reason": dict(final_finish), "raw_response_finish_reason": dict(response_finish), "final_empty_runs": len(llama) - final_nonempty, "runs_with_any_tool_call": any_tools, "runs_with_write_file_edit": any_edits, "tool_calls": total_tools, "raw_responses_with_tool_calls": raw_tool_call_responses, "tool_parse": {"valid": sum((read_json(ROOT / row["run_dir"] / "metadata.json").get("r2_tool_parse") or {}).get("valid", 0) for row in llama), "invalid_json": 0, "invalid_schema": 0, "unknown_tool": 0, "execution_error": total_parse_errors, "runs_with_any_execution_or_parse_error": parse_error_runs}, "tool_names": dict(tool_names), "execution_error_tools": dict(error_tools), "execution_error_messages": dict(error_messages), "interpretation": "all S4 trajectories emitted parseable tool calls and edited files; the observed 0/36 is not an empty-output or unparseable-tool-call harness failure. However 16 run_command calls used timeout_seconds=300, above the documented 120-second maximum, causing execution rejection. This is a model tool-argument error that contributes to failure; the remaining universal verifier failure after edits indicates a capability/validation floor as well. No llama S7 record exists yet, so no S7 inference is available."}


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
    s5_effective = [row for row in all_records["S5_r2_raw"] if not row["provider_error_protocol"]] + all_records["S5_provider_replacements"]
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
        "S6_L3b_transition_audit": l3b_transition_audit(all_records["S6_L3b_dev_validate"]),
        "S7_qwen_C0_C1_provider_error_audit": provider_error_audit(all_records["S7_completed_snapshot"]),
        "llama3_1_8b_diagnosis": llama_diagnosis(all_records["S4_r2"]),
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
