#!/usr/bin/env python3
"""Local-only descriptive checks for final-empty and verifier-error denominators.

This module reads completed S7 artifacts; it never runs a verifier, model, or
judge and does not modify frozen assets or formal primary-result tables.
"""
from __future__ import annotations

import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from analysis.verifier_pass_v2 import ROOT

METRICS = ROOT / "results" / "s7" / "run_metrics.csv"
RUNS = ROOT / "data" / "s7_runs"
OUT = ROOT / "results" / "tables" / "report"
DOC_TAXONOMY = ROOT / "docs" / "weak_failure_taxonomy.md"
DOC_SENSITIVITY = ROOT / "docs" / "verifier_error_sensitivity.md"
MODELS = ["qwen3.5:9b", "gemma4:26b", "qwen3.8:27b", "qwen3-coder-next", "llama3.1:8b", "gpt-5.6-sol"]
FOCUS = MODELS[:4]
SEED = 20261011
DRAWS = 10_000


def truth(value: object) -> bool:
    return str(value).strip().lower() == "true"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_rows() -> list[dict[str, str]]:
    with METRICS.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_table(name: str, rows: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0]) if rows else []
    with (OUT / f"{name}.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    lines += ["| " + " | ".join(str(row[column]) for column in columns) + " |" for row in rows]
    (OUT / f"{name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def pct(num: int, den: int) -> str:
    return "NA" if den == 0 else f"{100 * num / den:.1f}%"


def final_empty_table(rows: list[dict[str, str]]) -> list[dict]:
    output = []
    for model in FOCUS:
        selected = [row for row in rows if row["model"] == model and row["condition"] in {"C0", "C1"}]
        empty = [row for row in selected if truth(row["final_empty"])]
        nonempty = [row for row in selected if not truth(row["final_empty"])]
        empty_pass = sum(truth(row["verifier_pass"]) for row in empty)
        nonempty_pass = sum(truth(row["verifier_pass"]) for row in nonempty)
        output.append({"model": model, "all_runs_n": len(selected), "final_empty_n": len(empty),
                       "final_empty_rate": pct(len(empty), len(selected)), "final_empty_pass_n": empty_pass,
                       "final_empty_pass_rate": pct(empty_pass, len(empty)), "non_final_empty_n": len(nonempty),
                       "non_final_empty_pass_n": nonempty_pass, "non_final_empty_pass_rate": pct(nonempty_pass, len(nonempty)),
                       "provider_error_protocol_n": sum(truth(row["provider_error_protocol"]) for row in selected)})
    return output


def error_kind(row: dict[str, str]) -> str | None:
    if truth(row["verifier_pass"]) or truth(row["provider_error_protocol"]):
        return None
    verifier = load(RUNS / row["run_id"] / "verifier.json")
    checks = verifier.get("checks") if isinstance(verifier.get("checks"), dict) else {}
    if checks:
        return None
    error = verifier.get("error")
    if truth(row.get("verifier_timeout", "False")) or "timeout" in str(error).lower():
        return "verifier_timeout"
    if error:
        message = str(error).lower()
        if "jsondecode" in message or "parse" in message or "decode" in message:
            return "output_unparseable"
        return "verifier_exception_or_abnormal_exit"
    return "no_named_check_passed_false"


def error_table(rows: list[dict[str, str]]) -> list[dict]:
    output = []
    for model in MODELS:
        for condition in ("C0", "C1"):
            selected = [row for row in rows if row["model"] == model and row["condition"] == condition and not truth(row["provider_error_protocol"])]
            kinds = Counter(kind for row in selected if (kind := error_kind(row)))
            output.append({"model": model, "condition": condition, "eligible_n": len(selected),
                           "verifier_timeout": kinds["verifier_timeout"],
                           "verifier_exception_or_abnormal_exit": kinds["verifier_exception_or_abnormal_exit"],
                           "output_unparseable": kinds["output_unparseable"],
                           "no_named_check_passed_false": kinds["no_named_check_passed_false"],
                           "total_no_named_check": sum(kinds.values())})
    return output


def bootstrap(values: list[float], seed: int) -> tuple[float | None, float | None, float | None]:
    if not values: return None, None, None
    rng = random.Random(seed)
    draws = sorted(sum(rng.choice(values) for _ in values) / len(values) for _ in range(DRAWS))
    return sum(values) / len(values), draws[int(.025 * (DRAWS - 1))], draws[int(.975 * (DRAWS - 1))]


def sensitivity_table(rows: list[dict[str, str]]) -> list[dict]:
    output = []
    for offset, model in enumerate(MODELS):
        condition_data = {}
        for condition in ("C0", "C1"):
            eligible = [row for row in rows if row["model"] == model and row["condition"] == condition and not truth(row["provider_error_protocol"])]
            retained = [row for row in eligible if error_kind(row) is None]
            condition_data[condition] = retained
            output.append({"model": model, "row_type": "condition", "condition": condition,
                           "primary_n": len(eligible), "excluded_no_named_check": len(eligible) - len(retained),
                           "sensitivity_n": len(retained), "verifier_pass_n": sum(truth(row["verifier_pass"]) for row in retained),
                           "verifier_pass_rate": pct(sum(truth(row["verifier_pass"]) for row in retained), len(retained)),
                           "C1_minus_C0_task_pp": "", "bootstrap_95pct_pp": ""})
        cells = defaultdict(lambda: defaultdict(list))
        for condition, subset in condition_data.items():
            for row in subset: cells[row["task"]][condition].append(int(truth(row["verifier_pass"])))
        differences = [sum(item["C1"]) / len(item["C1"]) - sum(item["C0"]) / len(item["C0"])
                       for item in cells.values() if item["C0"] and item["C1"]]
        estimate, low, high = bootstrap(differences, SEED + offset)
        output.append({"model": model, "row_type": "paired_task_difference", "condition": "C1-C0",
                       "primary_n": "", "excluded_no_named_check": "", "sensitivity_n": len(differences), "verifier_pass_n": "", "verifier_pass_rate": "",
                       "C1_minus_C0_task_pp": "NA" if estimate is None else f"{100 * estimate:+.1f}",
                       "bootstrap_95pct_pp": "NA" if low is None else f"[{100 * low:+.1f}, {100 * high:+.1f}]"})
    return output


def write_docs(final_rows: list[dict], errors: list[dict], sensitivity: list[dict]) -> None:
    # Regeneration is idempotent: replace, rather than append, this derived section.
    tax = DOC_TAXONOMY.read_text(encoding="utf-8").split("## `final_empty` conditional denominators", 1)[0].rstrip()
    section = ["", "## `final_empty` conditional denominators", "", "Scope is all completed S7 C0+C1 records for qwen3.5:9b and the three strong comparison models, including any protocol provider-error records because this is a descriptive behavior rate. `verifier_pass` remains the frozen verifier field; these conditional rates are not causal estimates.", "", "| Model | All runs n | Final empty n (%) | Pass among final-empty | Non-final-empty n | Pass among non-final-empty | Provider-error records |", "|---|---:|---:|---:|---:|---:|---:|"]
    for row in final_rows:
        section.append(f"| {row['model']} | {row['all_runs_n']} | {row['final_empty_n']} ({row['final_empty_rate']}) | {row['final_empty_pass_n']}/{row['final_empty_n']} ({row['final_empty_pass_rate']}) | {row['non_final_empty_n']} | {row['non_final_empty_pass_n']}/{row['non_final_empty_n']} ({row['non_final_empty_pass_rate']}) | {row['provider_error_protocol_n']} |")
    DOC_TAXONOMY.write_text(tax.rstrip() + "\n" + "\n".join(section) + "\n", encoding="utf-8")
    lines = ["# Verifier no-named-check sensitivity", "", "This local-only sensitivity excludes eligible runs where `verifier.json` has no named checks and `passed` is false. It does not replace the preregistered primary outcome, which retains such runs as failures.", "", "## Composition", "", "Categories are mutually exclusive within the no-named-check subset. `verifier_exception_or_abnormal_exit` is a nonempty verifier error not matching timeout or parsing patterns; no non-zero agent-process exits were observed in this subset, so the non-zero entries are verifier exceptions. `output_unparseable` uses a literal parse/decode marker in that error. Zero values are retained for clarity.", "", "| Model | Condition | Eligible n | Verifier timeout | Verifier exception / abnormal exit | Output unparseable | No named check, passed=false | Total excluded |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    for row in errors:
        lines.append(f"| {row['model']} | {row['condition']} | {row['eligible_n']} | {row['verifier_timeout']} | {row['verifier_exception_or_abnormal_exit']} | {row['output_unparseable']} | {row['no_named_check_passed_false']} | {row['total_no_named_check']} |")
    lines += ["", "## Sensitivity pass rates and task-paired difference", "", "The condition rows give verifier-pass rates after the exclusion. The difference row averages within-task C1-minus-C0 repeat pass rates over tasks with at least one retained run in both conditions; its interval is a fixed-seed 10,000-draw paired bootstrap and is descriptive.", "", "| Model | Row | Primary n | Excluded | Sensitivity n | Pass n | Pass rate | C1-C0 task pp [95% bootstrap] |", "|---|---|---:|---:|---:|---:|---:|---|"]
    for row in sensitivity:
        if row['row_type'] == 'condition':
            lines.append(f"| {row['model']} | {row['condition']} | {row['primary_n']} | {row['excluded_no_named_check']} | {row['sensitivity_n']} | {row['verifier_pass_n']} | {row['verifier_pass_rate']} | |")
        else:
            lines.append(f"| {row['model']} | C1-C0 paired tasks (n={row['sensitivity_n']}) | | | | | | {row['C1_minus_C0_task_pp']} {row['bootstrap_95pct_pp']} |")
    DOC_SENSITIVITY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = read_rows()
    final_rows, errors, sensitivity = final_empty_table(rows), error_table(rows), sensitivity_table(rows)
    write_table("final_empty_conditional", final_rows)
    write_table("verifier_error_composition", errors)
    write_table("verifier_error_sensitivity", sensitivity)
    write_docs(final_rows, errors, sensitivity)
    print(json.dumps({"final_empty_models": len(final_rows), "error_cells": len(errors), "sensitivity_rows": len(sensitivity)}))


if __name__ == "__main__": main()
