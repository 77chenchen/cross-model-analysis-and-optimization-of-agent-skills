#!/usr/bin/env python3
"""Render the gated S7 formal figures from formal-analysis CSV tables."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from analysis.figure_templates import annotated_heatmap, direct_label, interval_point, make_contact_sheet, panel_label
from analysis.formal_s7_results import MODELS, OUT, TABLES, wilson
from analysis.style import CONDITION_COLORS, DOUBLE_COLUMN_IN, INK, MUTED, configure_matplotlib, despine, model_label, model_style, save_figure
from analysis.verifier_pass_v2 import ROOT, enforce_formal_s7_gate

FIG = ROOT / "figures" / "s7"
DATA = FIG / "data"
STEMS = [
    "S7_F1_main_results",
    "S7_F2_paired_differences",
    "S7_F3_task_heatmap",
    "S7_F4_process_mechanisms",
    "S7_F5_exploratory",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def value(row: dict[str, str], field: str) -> float | None:
    text = row.get(field, "")
    return float(text) if text not in ("", "None") else None


def integer(row: dict[str, str], field: str) -> int:
    return int(float(row.get(field, 0) or 0))


def write_data(name: str, rows: list[dict]) -> Path:
    DATA.mkdir(parents=True, exist_ok=True)
    path = DATA / f"{name}.csv"
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    return path


def render_main() -> None:
    summaries = read_csv(TABLES / "S7_T1_model_condition_summary.csv")
    processes = read_csv(TABLES / "S7_T4_process_metrics.csv")
    core = {(row["model"], row["condition"]): row for row in summaries if row["split"] == "all" and row["condition"] in ("C0", "C1")}
    order = sorted(MODELS, key=lambda model: value(core[(model, "C0")], "verifier_pass_rate") or 0)
    y = np.arange(len(order))

    fig = plt.figure(figsize=(DOUBLE_COLUMN_IN, 3.25), layout="constrained")
    grid = fig.add_gridspec(1, 3, width_ratios=(2.45, 1.35, 1.45), wspace=0.12)
    ax_a, ax_b, ax_c = [fig.add_subplot(grid[0, index]) for index in range(3)]

    for position, model in enumerate(order):
        c0, c1 = core[(model, "C0")], core[(model, "C1")]
        r0, r1 = value(c0, "verifier_pass_rate"), value(c1, "verifier_pass_rate")
        assert r0 is not None and r1 is not None
        ax_a.plot([r0, r1], [position, position], color="#B8BEC8", linewidth=0.75, linestyle="--" if model == "gpt-5.6-sol" else "-")
        for condition, row, offset in (("C0", c0, -0.07), ("C1", c1, 0.07)):
            estimate = value(row, "verifier_pass_rate") or 0.0
            low, high = value(row, "wilson_low") or 0.0, value(row, "wilson_high") or 0.0
            interval_point(ax_a, position + offset, estimate, low, high, color=CONDITION_COLORS[condition], marker="o", open_marker=model == "gpt-5.6-sol")
    ax_a.axvspan(0.2, 0.8, color="#EEEEEE", alpha=0.65, zorder=0)
    ax_a.set_yticks(y, [model_label(model) + ("†" if model == "gpt-5.6-sol" else "") for model in order])
    ax_a.set_xlim(0, 1.16); ax_a.set_xlabel("Verifier pass rate (95% Wilson CI)")
    ax_a.legend(handles=[Line2D([], [], marker="o", color=CONDITION_COLORS["C0"], label="C0", linestyle="none"), Line2D([], [], marker="o", color=CONDITION_COLORS["C1"], label="C1", linestyle="none")], loc="lower right")
    despine(ax_a); panel_label(ax_a, "a")

    process_lookup = {(row["model"], row["condition"], row["metric"]): row for row in processes}
    for position, model in enumerate(order):
        style = model_style(model)
        if model == "gpt-5.6-sol":
            direct_label(ax_b, 2.0, position, "NA†", color=MUTED, fontsize=5.8)
            continue
        for metric, marker, shift in (("steps", "o", -0.07), ("assistant_turns", "D", 0.07)):
            values = [process_lookup[(model, condition, metric)] for condition in ("C0", "C1")]
            median = np.mean([value(row, "median") or 0 for row in values])
            q1 = np.mean([value(row, "q1") or 0 for row in values])
            q3 = np.mean([value(row, "q3") or 0 for row in values])
            ax_b.plot([q1, q3], [position + shift, position + shift], color=style["color"], linewidth=1.0)
            ax_b.plot(median, position + shift, marker=marker, color=style["color"], markerfacecolor="white" if metric == "assistant_turns" else style["color"], linestyle="none", markersize=3.5)
    ax_b.set_yticks(y, []); ax_b.set_xlabel("Per run, median [IQR]")
    ax_b.legend(handles=[Line2D([], [], marker="o", color=INK, linestyle="none", label="tool calls"), Line2D([], [], marker="D", markerfacecolor="white", color=INK, linestyle="none", label="assistant turns")], loc="lower right", fontsize=5.6)
    despine(ax_b); panel_label(ax_b, "b")

    flag_names = ["final_empty", "no_edit", "timeout"]
    matrix = []
    for model in order:
        pooled = [core[(model, condition)] for condition in ("C0", "C1")]
        denominator = sum(integer(row, "scheduled") for row in pooled)
        matrix.append([sum(integer(row, flag) for row in pooled) / denominator for flag in flag_names])
    annotated_heatmap(ax_c, np.asarray(matrix), [model_label(model) for model in order], ["final\nempty", "no\nedit", "timeout"], cmap="cividis", vmin=0, vmax=1, percent=True, decimals=0)
    ax_c.set_title("Core outcome flags", loc="left", pad=5); panel_label(ax_c, "c", x=-0.22)
    fig.text(0.01, -0.01, "† GPT is an uncontrolled Codex reference anchor; aligned r2 process metrics are unavailable.", fontsize=5.8, color=MUTED)
    save_figure(fig, FIG / STEMS[0])

    output = []
    for model in order:
        for condition in ("C0", "C1"):
            output.append({"model": model, "condition": condition, **core[(model, condition)]})
    write_data(STEMS[0], output)


def render_paired() -> None:
    rows = [row for row in read_csv(TABLES / "S7_T2_core_paired_differences.csv") if row["scope"] in ("all", "test_in", "test_out")]
    lookup = {(row["model"], row["scope"]): row for row in rows}
    y = np.arange(len(MODELS))
    fig, ax = plt.subplots(figsize=(DOUBLE_COLUMN_IN, 2.75), layout="constrained")
    offsets = {"all": 0.0, "test_in": -0.13, "test_out": 0.13}
    markers = {"all": "o", "test_in": "s", "test_out": "D"}
    for position, model in enumerate(MODELS):
        style = model_style(model)
        for scope in ("all", "test_in", "test_out"):
            row = lookup[(model, scope)]
            estimate = value(row, "mean_difference") or 0.0
            low, high = value(row, "bootstrap_low") or 0.0, value(row, "bootstrap_high") or 0.0
            interval_point(ax, position + offsets[scope], estimate, low, high, color=style["color"], marker=markers[scope], open_marker=model == "gpt-5.6-sol")
    ax.axvline(0, color="#7A7A7A", linewidth=0.7)
    ax.set_yticks(y, [model_label(model) + ("†" if model == "gpt-5.6-sol" else "") for model in MODELS])
    ax.set_xlabel("Task-paired difference in pass rate (C1 − C0)")
    ax.legend(handles=[Line2D([], [], marker=markers[scope], color=INK, linestyle="none", label=scope.replace("_", " ")) for scope in ("all", "test_in", "test_out")], loc="lower right", ncol=3)
    despine(ax); panel_label(ax, "a", x=-0.1)
    fig.text(0.01, -0.015, "Intervals are 10,000-draw paired task bootstrap intervals; no significance claim. † uncontrolled reference anchor.", fontsize=5.8, color=MUTED)
    save_figure(fig, FIG / STEMS[1]); write_data(STEMS[1], rows)


def render_tasks() -> None:
    rows = read_csv(TABLES / "S7_T3_task_distribution.csv")
    columns = [f"{model}_{condition}" for model in MODELS for condition in ("C0", "C1")]
    matrix = np.asarray([[value(row, column) if value(row, column) is not None else np.nan for column in columns] for row in rows])
    labels = [model_label(model).replace(" ", "\n", 1) + f"\n{condition}" for model in MODELS for condition in ("C0", "C1")]
    fig, ax = plt.subplots(figsize=(DOUBLE_COLUMN_IN, 5.3), layout="constrained")
    annotated_heatmap(ax, matrix, [row["task"].replace("test_in_", "").replace("test_out_", "") for row in rows], labels, cmap="cividis", vmin=0, vmax=1, percent=True, decimals=0, annotation_size=5.2)
    ax.set_xlabel("Model × condition"); ax.set_ylabel("Held-out task")
    ax.axhline(sum(row["split"] == "test_in" for row in rows) - 0.5, color="white", linewidth=1.4)
    panel_label(ax, "a", x=-0.12)
    fig.text(0.01, -0.005, "Cells are within-task repetition pass rates. GPT is shown as an uncontrolled reference anchor.", fontsize=5.8, color=MUTED)
    save_figure(fig, FIG / STEMS[2]); write_data(STEMS[2], rows)


def render_process() -> None:
    run_rows = read_csv(OUT / "run_metrics.csv")
    open_models = [model for model in MODELS if model != "gpt-5.6-sol"]

    def rate(model: str, condition: str, field: str, expected: str = "True") -> tuple[int, int, float]:
        selected = [row for row in run_rows if row["model"] == model and row["condition"] == condition and row["provider_error_protocol"] == "False" and row.get(field, "") not in ("", "None")]
        successes = sum(row[field] == expected for row in selected)
        return successes, len(selected), successes / len(selected) if selected else float("nan")

    fig, axes = plt.subplots(1, 3, figsize=(DOUBLE_COLUMN_IN, 2.7), layout="constrained")
    y = np.arange(len(open_models))
    export: list[dict] = []
    for position, model in enumerate(open_models):
        for condition, offset in (("C0", -0.08), ("C1", 0.08)):
            successes, denominator, estimate = rate(model, condition, "validated_after_last_edit_intent")
            low, high = wilson(successes, denominator)
            interval_point(axes[0], position + offset, estimate, low or 0, high or 0, color=CONDITION_COLORS[condition], marker="o")
            export.append({"panel": "validation", "model": model, "condition": condition, "successes": successes, "n": denominator, "rate": estimate})
        successes, denominator, estimate = rate(model, "C1", "activation", expected="explicit")
        low, high = wilson(successes, denominator)
        interval_point(axes[1], position, estimate, low or 0, high or 0, color=model_style(model)["color"], marker=model_style(model)["marker"])
        export.append({"panel": "explicit_activation", "model": model, "condition": "C1", "successes": successes, "n": denominator, "rate": estimate})
    axes[0].set_yticks(y, [model_label(model) for model in open_models]); axes[0].set_xlim(0, 1); axes[0].set_xlabel("Validation after final edit")
    axes[0].legend(handles=[Line2D([], [], marker="o", color=CONDITION_COLORS[c], linestyle="none", label=c) for c in ("C0", "C1")], loc="lower right")
    axes[1].set_yticks(y, []); axes[1].set_xlim(0, 1); axes[1].set_xlabel("Explicit skill reference, C1")
    for ax, label in zip(axes[:2], ("a", "b")):
        despine(ax); panel_label(ax, label)

    qwen_conditions = ["C0", "C1", "v1", "l3b"]
    positions = np.arange(len(qwen_conditions))
    for position, condition in enumerate(qwen_conditions):
        successes, denominator, estimate = rate("qwen3.5:9b", condition, "validated_after_last_edit_intent")
        low, high = wilson(successes, denominator)
        interval_point(axes[2], position, estimate, low or 0, high or 0, color=CONDITION_COLORS[condition], marker="o")
        export.append({"panel": "qwen_conditions", "model": "qwen3.5:9b", "condition": condition, "successes": successes, "n": denominator, "rate": estimate})
    axes[2].set_yticks(positions, qwen_conditions); axes[2].set_xlim(0, 1); axes[2].set_xlabel("Qwen validation rate")
    despine(axes[2]); panel_label(axes[2], "c")
    fig.text(0.01, -0.01, "Wilson intervals describe individual process proportions only; they are not condition-difference tests.", fontsize=5.8, color=MUTED)
    save_figure(fig, FIG / STEMS[3]); write_data(STEMS[3], export)


def render_exploratory() -> None:
    rows = read_csv(TABLES / "S7_T6_exploratory.csv")
    contrasts = [row for row in rows if row["layer"] == "unconditional_descriptive"]
    layers = [row for row in rows if row["layer"] != "unconditional_descriptive"]
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(DOUBLE_COLUMN_IN, 2.7), layout="constrained")
    labels = [row["comparison"].replace("_vs_", " − ").replace("_test_in", "\ntest_in").replace("_test_out", "\ntest_out").replace("_all", "\nall") for row in contrasts]
    y = np.arange(len(contrasts))
    for position, row in enumerate(contrasts):
        color = CONDITION_COLORS["v1"] if row["comparison"].startswith("v1") else CONDITION_COLORS["l3b"]
        interval_point(ax_a, position, value(row, "mean_difference") or 0, value(row, "bootstrap_low") or 0, value(row, "bootstrap_high") or 0, color=color, marker="o")
    ax_a.axvline(0, color="#777777", linewidth=0.7); ax_a.set_yticks(y, labels); ax_a.set_xlabel("Task-paired pass-rate difference")
    despine(ax_a); panel_label(ax_a, "a")

    labels_b = []
    for position, row in enumerate(layers):
        condition = "C1" if row["comparison"].startswith("C1") else "l3b"
        estimate = value(row, "verifier_pass_rate") or 0
        successes, denominator = integer(row, "verifier_pass"), integer(row, "runs")
        low, high = wilson(successes, denominator)
        interval_point(ax_b, position, estimate, low or 0, high or 0, color=CONDITION_COLORS[condition], marker="o")
        labels_b.append(f"{condition} · {'A ≥32' if row['layer'].startswith('A_') else 'B <32'}")
        direct_label(ax_b, 1.02, position, f"{successes}/{denominator}", fontsize=5.9)
    ax_b.set_yticks(np.arange(len(layers)), labels_b); ax_b.set_xlim(0, 1.15); ax_b.set_xlabel("Verifier pass rate")
    despine(ax_b); panel_label(ax_b, "b")
    fig.text(0.01, -0.01, "Exploratory only. Call-32 layers are post-assignment strata; panel (b) is not an effect estimate.", fontsize=5.8, color=MUTED)
    save_figure(fig, FIG / STEMS[4]); write_data(STEMS[4], rows)


def main() -> None:
    enforce_formal_s7_gate(ROOT / "STATUS.md", ROOT / "analysis" / "analysis_patch_manifest.json")
    if not (OUT / "analysis_manifest.json").exists():
        raise SystemExit("run python -m analysis.formal_s7_results first")
    configure_matplotlib()
    render_main(); render_paired(); render_tasks(); render_process(); render_exploratory()
    make_contact_sheet([FIG / f"{stem}.png" for stem in STEMS], FIG / "contact_sheet.png", columns=2)
    manifest = {
        "format": "publication-multipanel-formal-s7-v1",
        "figures": STEMS,
        "source_analysis_manifest": sha256(OUT / "analysis_manifest.json"),
        "figure_data_sha256": {path.name: sha256(path) for path in sorted(DATA.glob("*.csv"))},
    }
    (FIG / "figure_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    readme = [
        "# Formal S7 figures", "",
        "All figures use `verifier.json.passed` through the gated formal analysis. GPT-5.6 Sol is always an uncontrolled Codex reference anchor.", "",
        "- `S7_F1_main_results`: core pass rates, aligned r2 process depth, and non-exclusive outcome flags.",
        "- `S7_F2_paired_differences`: task-paired C1-minus-C0 differences with 10,000-draw bootstrap intervals.",
        "- `S7_F3_task_heatmap`: within-task repetition pass rates by model and core condition.",
        "- `S7_F4_process_mechanisms`: validation and explicit-reference mechanism measures.",
        "- `S7_F5_exploratory`: qwen v1/L3b descriptive comparisons and call-32 strata.", "",
        "Each figure is exported as PDF, SVG, and 300-dpi PNG. Plotting data are under `figures/s7/data/`; hashes are in `figure_manifest.json`.", "",
    ]
    (FIG / "README.md").write_text("\n".join(readme), encoding="utf-8")
    print(json.dumps({"figures": len(STEMS), "output": str(FIG), "contact_sheet": str(FIG / "contact_sheet.png")}))


if __name__ == "__main__":
    main()
