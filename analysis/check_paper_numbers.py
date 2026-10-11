#!/usr/bin/env python3
"""Check key manuscript numbers against locked S7 tables and dev cross-tab."""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
TABS = ROOT / "results" / "tables" / "s7"

MODELS = {
    r"\QwenWeak": "qwen3.5:9b",
    r"\Gemma": "gemma4:26b",
    r"\QwenStrong": "qwen3.8:27b",
    r"\Coder": "qwen3-coder-next",
    r"\Llama": "llama3.1:8b",
    r"\GPT\tnote{a}": "gpt-5.6-sol",
}


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def section(text: str, label: str) -> str:
    found = re.search(
        rf"% PAPER_NUMBERS:{label}_BEGIN(.*?)% PAPER_NUMBERS:{label}_END",
        text,
        re.S,
    )
    if not found:
        raise AssertionError(f"missing PAPER_NUMBERS:{label} marker")
    return found.group(1)


def pct(x: float) -> str:
    return f"{100 * x:.1f}"


def main() -> int:
    tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    t1 = csv_rows(TABS / "S7_T1_model_condition_summary.csv")
    t2 = csv_rows(TABS / "S7_T2_core_paired_differences.csv")
    core_rows = section(tex, "CORE").splitlines()
    checked = 0

    for line in core_rows:
        if "&" not in line:
            continue
        cells = [c.strip() for c in line.strip().rstrip("\\\\").split("&")]
        model_cell = cells[0]
        model = next((name for macro, name in MODELS.items() if model_cell.startswith(macro)), None)
        if model is None:
            raise AssertionError(f"unknown model macro in core table: {model_cell}")
        for condition, cell in (("C0", cells[1]), ("C1", cells[2])):
            match = re.search(r"(\d+)/(\d+) \((\d+\.\d+)\\%(?:,\s*floor)?\)", cell)
            if not match:
                raise AssertionError(f"cannot parse {model}/{condition} cell: {cell}")
            source = next(r for r in t1 if r["model"] == model and r["condition"] == condition and r["split"] == "all")
            actual = (int(match.group(1)), int(match.group(2)), float(match.group(3)))
            expected = (int(source["verifier_pass"]), int(source["primary_n"]), round(100 * float(source["verifier_pass_rate"]), 1))
            if actual != expected:
                raise AssertionError(f"{model} {condition}: manuscript={actual}, source={expected}")
            checked += 3
        diff = re.search(r"([+-]?\d+\.\d+)(?:\^\\dagger)?\\;\[([+-]?\d+\.\d+),\s*([+-]?\d+\.\d+)\]", cells[3])
        if not diff:
            raise AssertionError(f"cannot parse paired interval: {cells[3]}")
        source = next(r for r in t2 if r["model"] == model and r["scope"] == "all")
        actual = tuple(float(v) for v in diff.groups())
        expected = tuple(round(100 * float(source[k]), 1) for k in ("mean_difference", "bootstrap_low", "bootstrap_high"))
        if actual != expected:
            raise AssertionError(f"{model} paired contrast: manuscript={actual}, source={expected}")
        checked += 3

    cross = csv_rows(ROOT / "results" / "tables" / "report" / "behavior_outcome_crosstab.csv")
    cross_text = section(tex, "CROSSTAB")
    for row in cross:
        for group in ("strong-pass", "strong-fail", "weak-pass", "weak-fail"):
            count, n, rate = row[f"{group}_count"], row[f"{group}_n"], float(row[f"{group}_rate"])
            token = f"{count}/{n} ({pct(rate)}\\%)"
            if token not in cross_text:
                raise AssertionError(f"cross-tab value missing or changed: {row['behavior']} {group}: {token}")
            checked += 1

    paired = csv_rows(TABS / "S7_T7_process_paired.csv")
    qwen_validation = next(r for r in paired if r["model"] == "qwen3.5:9b" and r["scope"] == "all"
                           and r["contrast"] == "C1-C0" and r["metric"] == "validated_after_last_edit_intent")
    v1 = csv_rows(TABS / "S7_T6_exploratory.csv")
    v1_row = next(r for r in v1 if r["comparison"] == "v1_vs_C1_test_in")
    required = [
        f"{100 * float(qwen_validation['mean_difference']):.1f}",
        f"{100 * float(v1_row['mean_difference']):.1f}",
        "50/105 (47.6\\%)",
        "39/75 (52.0\\%)",
        "9.0--11.6",
        "104",
    ]
    for token in required:
        if token not in tex:
            raise AssertionError(f"required reported value missing: {token}")
        checked += 1

    abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S).group(1)
    words = re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", re.sub(r"\\[A-Za-z]+\{?([^{}]*)\}?", r" \1 ", abstract))
    if not 150 <= len(words) <= 200:
        raise AssertionError(f"abstract word count {len(words)} is outside 150--200")
    if re.search(r"\bS[4-7]\b|\bL3b\b", tex):
        raise AssertionError("internal batch label remains in the manuscript")
    if "[repository URL to be added]" not in tex:
        raise AssertionError("repository URL placeholder missing")
    for fig in ("main_results.pdf", "decoupling.pdf", "behavior_outcome.pdf", "failure_flags.pdf", "legacy_vs_verifier.pdf", "kappa_pabak.pdf"):
        if not (PAPER / "figures" / fig).exists():
            raise AssertionError(f"missing figure asset: {fig}")
    print(f"PASS: {checked} numeric checks; abstract={len(words)} words; all required figure assets present.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, StopIteration, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
