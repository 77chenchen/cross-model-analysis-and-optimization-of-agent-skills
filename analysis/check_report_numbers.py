#!/usr/bin/env python3
"""Fail when report S7 counts or percentage-point estimates drift from tables."""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "report.md"
TABLES = ROOT / "results" / "tables" / "s7"


def rows(name: str) -> list[dict[str, str]]:
    with (TABLES / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def block(text: str, name: str) -> str:
    match = re.search(
        rf"<!-- S7_CHECK:{name}_BEGIN -->(.*?)<!-- S7_CHECK:{name}_END -->",
        text,
        re.S,
    )
    if not match:
        raise AssertionError(f"missing S7_CHECK block: {name}")
    return match.group(1)


def table_lines(text: str) -> list[list[str]]:
    output = []
    for line in text.splitlines():
        if not line.startswith("|") or set(line.replace("|", "").replace(":", "").replace("-", "").strip()) == set():
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] != "Model" and not all(set(cell) <= {"-", ":"} for cell in cells):
            output.append(cells)
    return output


def canonical_model(value: str) -> str:
    return value.replace(" (reference anchor)", "")


def rounded(value: str | float, digits: int = 1) -> float:
    return round(float(value), digits)


def parse_rate(cell: str) -> tuple[int, int, float]:
    match = re.fullmatch(r"(\d+)/(\d+) \(([-+]?\d+(?:\.\d+)?)%\)", cell)
    if not match:
        raise AssertionError(f"cannot parse pass cell: {cell!r}")
    return int(match.group(1)), int(match.group(2)), float(match.group(3))


def parse_difference(cell: str) -> tuple[float, float, float]:
    match = re.fullmatch(r"([-+]?\d+(?:\.\d+)?) \[([-+]?\d+(?:\.\d+)?), ([-+]?\d+(?:\.\d+)?)\]", cell)
    if not match:
        raise AssertionError(f"cannot parse difference cell: {cell!r}")
    return tuple(float(match.group(index)) for index in (1, 2, 3))


def assert_close(actual: float, expected: float, label: str, tolerance: float = 0.051) -> None:
    if abs(actual - expected) > tolerance:
        raise AssertionError(f"{label}: report={actual}, table={expected}")


def main() -> int:
    text = REPORT.read_text(encoding="utf-8")
    t1 = rows("S7_T1_model_condition_summary.csv")
    t2 = rows("S7_T2_core_paired_differences.csv")
    t5 = rows("S7_T5_activation.csv")
    t6 = rows("S7_T6_exploratory.csv")
    t7 = rows("S7_T7_process_paired.csv")
    index_t1 = {(row["model"], row["condition"], row["split"]): row for row in t1}
    index_t2 = {(row["model"], row["scope"]): row for row in t2 if row["contrast"] == "C1-C0"}
    checked = 0

    core = table_lines(block(text, "CORE"))
    if len(core) != 6:
        raise AssertionError(f"CORE block has {len(core)} model rows, expected 6")
    for cells in core:
        model = canonical_model(cells[0])
        for condition, cell in (("C0", cells[1]), ("C1", cells[2])):
            passed, denominator, rate = parse_rate(cell)
            source = index_t1[(model, condition, "all")]
            if (passed, denominator) != (int(source["verifier_pass"]), int(source["primary_n"])):
                raise AssertionError(f"{model} {condition}: report={passed}/{denominator}, table={source['verifier_pass']}/{source['primary_n']}")
            assert_close(rate, 100 * float(source["verifier_pass_rate"]), f"{model} {condition} rate")
            checked += 3
        estimate, low, high = parse_difference(cells[3])
        source = index_t2[(model, "all")]
        for label, actual, key in (("estimate", estimate, "mean_difference"), ("low", low, "bootstrap_low"), ("high", high, "bootstrap_high")):
            assert_close(actual, 100 * float(source[key]), f"{model} all {label}")
            checked += 1

    split = table_lines(block(text, "SPLIT"))
    if len(split) != 6:
        raise AssertionError(f"SPLIT block has {len(split)} model rows, expected 6")
    for cells in split:
        model = canonical_model(cells[0])
        for scope, cell in (("test_in", cells[1]), ("test_out", cells[2])):
            parsed = parse_difference(cell)
            source = index_t2[(model, scope)]
            for label, actual, key in zip(("estimate", "low", "high"), parsed, ("mean_difference", "bootstrap_low", "bootstrap_high")):
                assert_close(actual, 100 * float(source[key]), f"{model} {scope} {label}")
                checked += 1

    activation = next(row for row in t5 if row["model"] == "qwen3.5:9b" and row["condition"] == "v1" and row["activation"] == "explicit")
    activation_text = re.search(r"explicit reference occurs in (\d+)/(\d+) runs", text)
    if not activation_text:
        raise AssertionError("v1 explicit activation a/b count not found")
    if tuple(map(int, activation_text.groups())) != (int(activation["count"]), int(activation["n"])):
        raise AssertionError("v1 explicit activation count differs from S7_T5")
    checked += 2

    metrics = rows("S7_T4_process_metrics.csv")
    l3b_n = next(int(row["n"]) for row in metrics if row["model"] == "qwen3.5:9b" and row["condition"] == "l3b" and row["metric"] == "steps")
    l3b_triggers = int(next(row["runs"] for row in t6 if row["comparison"] == "l3b_call32_stratum" and row["layer"] == "A_reached_call_32"))
    trigger_text = re.search(r"L3b triggers in only (\d+)/(\d+) usable runs", text)
    if not trigger_text or tuple(map(int, trigger_text.groups())) != (l3b_triggers, l3b_n):
        raise AssertionError("L3b trigger a/b count differs from run_metrics/T4")
    checked += 2

    v1 = next(row for row in t6 if row["comparison"] == "v1_vs_C1_test_in")
    v1_text = re.search(r"paired verifier-pass difference is ([-+]?\d+\.\d+) points\s+with a \[([-+]?\d+\.\d+), ([-+]?\d+\.\d+)\] bootstrap interval", text)
    if not v1_text:
        raise AssertionError("v1 verifier-pass percentage-point sentence not found")
    for label, actual, key in zip(("estimate", "low", "high"), map(float, v1_text.groups()), ("mean_difference", "bootstrap_low", "bootstrap_high")):
        assert_close(actual, 100 * float(v1[key]), f"v1-C1 {label}")
        checked += 1

    validation_expected = {
        row["model"]: 100 * float(row["mean_difference"])
        for row in t7
        if row["scope"] == "all" and row["contrast"] == "C1-C0" and row["metric"] == "validated_after_last_edit_intent"
    }
    validation_match = re.search(
        r"qwen\s+\(task-level\s+C1-minus-C0 validation after final edit: ([-+]?\d+\.\d+) points\).*?gemma is ([-+]?\d+\.\d+), qwen3\.8 is ([-+]?\d+\.\d+), qwen-coder\s+is ([-+]?\d+\.\d+), and llama is ([-+]?\d+\.\d+) points",
        text,
        re.S,
    )
    if not validation_match:
        raise AssertionError("validation-direction percentage-point sentence not found")
    for model, actual in zip(("qwen3.5:9b", "gemma4:26b", "qwen3.8:27b", "qwen3-coder-next", "llama3.1:8b"), map(float, validation_match.groups())):
        assert_close(actual, validation_expected[model], f"{model} validation direction")
        checked += 1

    print(f"PASS: {checked} report values match results/tables/s7 (counts, denominators, rates, and percentage points).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
