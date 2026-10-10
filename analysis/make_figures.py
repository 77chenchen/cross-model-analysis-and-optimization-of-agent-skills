#!/usr/bin/env python3
"""Render publication-style pre-S7 figures from the immutable figure CSVs.

The module never rewrites source CSVs. Formal S7 figures remain guarded by the
verifier-pass-v2 completion gate.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch

from analysis.figure_templates import (
    annotated_heatmap,
    bootstrap_interval,
    direct_label,
    interval_point,
    make_contact_sheet,
    panel_label,
    simulate_cvd,
)
from analysis.style import (
    CONDITION_COLORS,
    DOUBLE_COLUMN_IN,
    INK,
    MUTED,
    configure_matplotlib,
    despine,
    model_label,
    model_style,
    save_figure,
)
from analysis.verifier_pass_v2 import ROOT, enforce_formal_s7_gate


FIG = ROOT / "figures"
DATA = FIG / "data"
QA = FIG / "qa"
BOOTSTRAP_SEED = 31010
BOOTSTRAP_ITERATIONS = 5000

CSV_SHA256 = {
    "F1_dev_pass_rates.csv": "333df019a9924cef72e85173a187e19e0d77d8777d64d9d530d09f6f8e1cfac0",
    "F2_legacy_vs_verifier.csv": "2f1e08fcb903bc73b770bd59644f0844422f2dbe349b88d67af3e369193ff457",
    "F3_outcome_flags.csv": "fc098c1dbffc1d98c2160485772ac3febd6d169ef5df90565c74774a2ce38e01",
    "F4_actions_by_decile.csv": "b1cb94270f28b88b525f5f6bc706e733cd85b8003a422351c485741ee5d20f8a",
    "F5_process_metrics_raw.csv": "679ca16de9f2335cd2c24dd3e9c546868c5a8732c0e9f96487470ab1808d820a",
    "F5_process_metrics_summary.csv": "6f3c10bb33f8ecf139592a0e9f2e5fc7fe3a573cdcb82d06e0ad7173e607c626",
    "F6_turns_calls_blindwrite.csv": "540cad3fbc7f639fbb12d21d4d8ef014593f1778bb2dd90bf5998da4a522e9be",
    "F7_token_composition.csv": "573d848ec4b9b8431fe5710492a7096455eac498b4323ab8803a93f6c1fe7b61",
    "F8_l3b_transitions.csv": "fbfe5d9acdd69db84927d0195f170898ae701956948f5f4c38469eb03eff8a34",
    "F9_kappa_pabak.csv": "2f632e61b8b43f658cc35a41f7d6cc4eeb07454193b8834a5f1de2a0a3186585",
}

FIGURE_STEMS = [
    "F1_dev_pass_rates",
    "F2_legacy_vs_verifier",
    "F3_outcome_flags",
    "F4_actions_by_decile",
    "F5_process_metrics",
    "F6_turns_calls_blindwrite",
    "F7_token_composition",
    "F8_l3b_transitions",
    "F9_kappa_pabak",
]

FIGURE_PANEL_COUNTS = {
    "F1_dev_pass_rates": 3,
    "F2_legacy_vs_verifier": 2,
    "F3_outcome_flags": 2,
    "F4_actions_by_decile": 5,
    "F5_process_metrics": 4,
    "F6_turns_calls_blindwrite": 3,
    "F7_token_composition": 2,
    "F8_l3b_transitions": 2,
    "F9_kappa_pabak": 2,
}


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(row: dict[str, str], key: str) -> float:
    return float(row[key])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_csv_hashes() -> None:
    discovered = {path.name for path in DATA.glob("*.csv")}
    expected = set(CSV_SHA256)
    if discovered != expected:
        raise RuntimeError(f"figure CSV set changed: missing={sorted(expected-discovered)}, added={sorted(discovered-expected)}")
    bad = {name: (CSV_SHA256[name], sha256(DATA / name)) for name in sorted(expected) if sha256(DATA / name) != CSV_SHA256[name]}
    if bad:
        raise RuntimeError(f"immutable figure CSV hash mismatch: {bad}")


def sorted_models_from_f1() -> list[str]:
    rows = read_csv("F1_dev_pass_rates.csv")
    return [row["model"] for row in sorted(rows, key=lambda item: number(item, "rate"))]


def render_figure1() -> None:
    pass_rows = {row["model"]: row for row in read_csv("F1_dev_pass_rates.csv")}
    raw = read_csv("F5_process_metrics_raw.csv")
    turns = {row["model"]: row for row in read_csv("F6_turns_calls_blindwrite.csv")}
    flags = read_csv("F3_outcome_flags.csv")
    models = sorted_models_from_f1()
    y = np.arange(len(models))

    fig = plt.figure(figsize=(DOUBLE_COLUMN_IN, 3.15), layout="constrained")
    grid = fig.add_gridspec(1, 3, width_ratios=(2.5, 1.25, 1.45), wspace=0.14)
    ax_a = fig.add_subplot(grid[0, 0])
    ax_b = fig.add_subplot(grid[0, 1], sharey=ax_a)
    ax_c = fig.add_subplot(grid[0, 2])

    ax_a.axvspan(0.2, 0.8, color="#EEEEEE", zorder=0)
    ax_a.text(0.5, 0.96, "20–80% calibration band", transform=ax_a.get_xaxis_transform(), ha="center", va="top", color=MUTED, fontsize=6.2)
    for pos, model in zip(y, models):
        row = pass_rows[model]
        style = model_style(model)
        interval_point(ax_a, pos, number(row, "rate"), number(row, "wilson_low"), number(row, "wilson_high"), color=style["color"], marker=style["marker"], open_marker=style["fill"] == "none")
        direct_label(ax_a, 1.015, pos, f"n={int(number(row, 'n'))}", color=MUTED, fontsize=6.2)
    ax_a.set_yticks(y, [model_label(model) for model in models])
    ax_a.set_xlim(-0.02, 1.11)
    ax_a.set_xticks(np.linspace(0, 1, 6))
    ax_a.set_xlabel("Verifier pass rate (Wilson 95% CI)")
    ax_a.set_title("Dev calibration (v0)", loc="left", pad=5)
    despine(ax_a)
    panel_label(ax_a, "a")

    grouped: dict[str, list[float]] = {model: [] for model in models}
    for row in raw:
        grouped[row["model"]].append(number(row, "steps"))
    for pos, model in zip(y, models):
        values = np.asarray(grouped[model], dtype=float)
        q1, median, q3 = np.quantile(values, [0.25, 0.5, 0.75])
        style = model_style(model)
        ax_b.plot([q1, q3], [pos + 0.08, pos + 0.08], color=style["color"], linewidth=1.3)
        ax_b.plot(median, pos + 0.08, marker=style["marker"], color=style["color"], linestyle="none", markersize=4.2)
        if model in turns:
            ax_b.plot(number(turns[model], "assistant_turns_median"), pos - 0.09, marker="o", markerfacecolor="white", markeredgecolor=style["color"], linestyle="none", markersize=4.0)
    ax_b.set_xlabel("Count / run")
    ax_b.set_title("Trajectory length", loc="left", pad=5)
    ax_b.tick_params(axis="y", labelleft=False)
    despine(ax_b)
    ax_b.legend(handles=[Line2D([], [], marker="D", color=INK, linestyle="-", label="tool calls: median + IQR", markersize=3.8), Line2D([], [], marker="o", markerfacecolor="white", markeredgecolor=INK, linestyle="none", label="assistant turns: median", markersize=3.8)], loc="lower right", fontsize=5.8, handlelength=1.8)
    panel_label(ax_b, "b", x=-0.16)

    chosen_flags = ["final_empty", "max_steps_reached", "timeout"]
    lookup = {(row["model"], row["flag"]): number(row, "rate") for row in flags}
    matrix = np.array([[lookup.get((model, flag), np.nan) for flag in chosen_flags] for model in models])
    annotated_heatmap(ax_c, matrix, [model_label(model) for model in models], ["final\nempty", "max\nsteps", "timeout"], cmap="cividis", vmin=0, vmax=1, percent=True, annotation_size=5.4)
    ax_c.set_title("Run flags", loc="left", pad=5)
    panel_label(ax_c, "c", x=-0.2)
    save_figure(fig, FIG / "F1_dev_pass_rates")


def render_figure2() -> None:
    rows = read_csv("F2_legacy_vs_verifier.csv")
    cohorts: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        cohorts.setdefault(row["cohort"], {})[row["metric"]] = row
    names = list(cohorts)
    labels = {"S4": "S4 calibration", "S5_original": "S5 original", "S5_replacement_inclusive": "S5 effective", "S6_L3b": "S6 / L3b"}
    up, flat, down = "#2A9D8F", "#777777", "#B35C44"

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(DOUBLE_COLUMN_IN, 3.05), gridspec_kw={"width_ratios": (1.2, 1)}, layout="constrained")
    left_label_y = {"S4": 0.60, "S5_original": 0.22, "S5_replacement_inclusive": 0.38, "S6_L3b": 0.48}
    right_label_y = {"S4": 0.56, "S5_original": 0.64, "S5_replacement_inclusive": 0.73, "S6_L3b": 0.82}
    for cohort in names:
        legacy = number(cohorts[cohort]["legacy_pass"], "rate")
        verifier = number(cohorts[cohort]["verifier_pass"], "rate")
        delta = verifier - legacy
        color = up if delta > 1e-10 else down if delta < -1e-10 else flat
        ax_a.plot([0, 1], [legacy, verifier], color=color, linewidth=1.1, alpha=0.9)
        ax_a.scatter([0, 1], [legacy, verifier], color=color, s=20, zorder=3, edgecolor="white", linewidth=0.45)
        label_left = left_label_y[cohort]
        label_right = right_label_y[cohort]
        ax_a.plot([-0.01, -0.12], [legacy, label_left], color=color, linewidth=0.45, alpha=0.8)
        ax_a.plot([1.01, 1.10], [verifier, label_right], color=color, linewidth=0.45, alpha=0.8)
        direct_label(ax_a, -0.135, label_left, labels.get(cohort, cohort), ha="right", fontsize=6.3)
        direct_label(ax_a, 1.115, label_right, f"{verifier:.2f}  ({delta:+.2f})", fontsize=6.2, color=color)
    ax_a.set_xlim(-0.5, 1.42)
    ax_a.set_ylim(0, 1)
    ax_a.set_xticks([0, 1], ["Legacy outcome", "Verifier passed"])
    ax_a.set_ylabel("Pass rate")
    despine(ax_a)
    panel_label(ax_a, "a")

    ypos = np.arange(len(names))
    for pos, cohort in zip(ypos, names):
        legacy = number(cohorts[cohort]["legacy_pass"], "rate")
        verifier = number(cohorts[cohort]["verifier_pass"], "rate")
        delta = verifier - legacy
        color = up if delta > 1e-10 else down if delta < -1e-10 else flat
        ax_b.plot([0, delta], [pos, pos], color=color, linewidth=1.25)
        ax_b.plot(delta, pos, marker="o", color=color, linestyle="none")
        direct_label(ax_b, delta + 0.012, pos, f"{delta:+.3f}", color=color)
    ax_b.axvline(0, color="#AAAAAA", linewidth=0.7)
    ax_b.set_yticks(ypos, [labels.get(name, name) for name in names])
    ax_b.set_xlabel("Verifier − legacy pass rate")
    ax_b.set_xlim(-0.03, max(0.43, max(number(cohorts[x]["verifier_pass"], "rate") - number(cohorts[x]["legacy_pass"], "rate") for x in names) + 0.09))
    despine(ax_b)
    panel_label(ax_b, "b")
    save_figure(fig, FIG / "F2_legacy_vs_verifier")


def render_figure3() -> None:
    rows = read_csv("F3_outcome_flags.csv")
    models = sorted_models_from_f1()
    flags = ["verifier_pass", "final_empty", "timeout", "max_steps_reached", "provider_error_protocol"]
    labels = ["pass", "final empty", "timeout", "max steps", "provider error"]
    lookup = {(row["model"], row["flag"]): number(row, "rate") for row in rows}
    matrix = np.array([[lookup.get((model, flag), np.nan) for flag in flags] for model in models])

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(DOUBLE_COLUMN_IN, 3.2), gridspec_kw={"width_ratios": (1.42, 1)}, layout="constrained")
    annotated_heatmap(ax_a, matrix, [model_label(x) for x in models], labels, cmap="cividis", vmin=0, vmax=1, percent=True, annotation_size=5.6)
    ax_a.set_title("Non-exclusive run flags", loc="left", pad=5)
    panel_label(ax_a, "a")

    y = np.arange(len(models))
    for pos, model in zip(y, models):
        pass_rate = lookup[(model, "verifier_pass")]
        empty_rate = lookup[(model, "final_empty")]
        color = model_style(model)["color"]
        ax_b.plot([pass_rate, empty_rate], [pos, pos], color="#B8B8B8", linewidth=0.8)
        ax_b.plot(pass_rate, pos, marker="o", color=color, linestyle="none", label="pass" if pos == 0 else None)
        ax_b.plot(empty_rate, pos, marker="s", markerfacecolor="white", markeredgecolor=color, linestyle="none", label="final empty" if pos == 0 else None)
    ax_b.set_yticks(y, [model_label(x) for x in models])
    ax_b.set_xlim(-0.03, 1.03)
    ax_b.set_xlabel("Run fraction")
    ax_b.set_title("Pass and final-empty marginals", loc="left", pad=5)
    ax_b.legend(loc="lower right")
    despine(ax_b)
    panel_label(ax_b, "b")
    save_figure(fig, FIG / "F3_outcome_flags")


def render_figure4() -> None:
    rows = read_csv("F4_actions_by_decile.csv")
    models = ["qwen3.8:27b", "qwen3-coder-next", "gemma4:26b", "qwen3.5:9b", "llama3.1:8b"]
    actions = ["read", "write", "command", "other"]
    lookup = {(row["model"], int(row["decile"]), row["action_type"]): number(row, "proportion") for row in rows}
    fig, axes = plt.subplots(2, 3, figsize=(DOUBLE_COLUMN_IN, 4.75), layout="constrained")
    for index, (ax, model) in enumerate(zip(axes.flat, models)):
        matrix = np.array([[lookup.get((model, decile, action), 0.0) for decile in range(1, 11)] for action in actions])
        annotated_heatmap(ax, matrix, actions, [str(x) for x in range(1, 11)], cmap="cividis", vmin=0, vmax=1, percent=True, annotation_size=4.5)
        ax.set_title(model_label(model), loc="left", pad=4, color=model_style(model)["color"])
        ax.set_xlabel("Trajectory decile")
        panel_label(ax, chr(ord("a") + index), x=-0.17)
    legend_ax = axes[1, 2]
    legend_ax.axis("off")
    legend_ax.text(0.05, 0.78, "Cell value", weight="bold", fontsize=8, transform=legend_ax.transAxes)
    legend_ax.text(0.05, 0.65, "Share of tool actions within\neach model × trajectory decile.", fontsize=7, color=MUTED, transform=legend_ax.transAxes)
    gradient = np.linspace(0, 1, 256)[None, :]
    inset = legend_ax.inset_axes([0.05, 0.42, 0.75, 0.10])
    inset.imshow(gradient, cmap="cividis", aspect="auto", vmin=0, vmax=1)
    inset.set_xticks([0, 255], ["0%", "100%"])
    inset.set_yticks([])
    for spine in inset.spines.values():
        spine.set_visible(False)
    save_figure(fig, FIG / "F4_actions_by_decile")


def draw_distribution_panel(ax: mpl.axes.Axes, raw: list[dict[str, str]], models: list[str], field: str, *, transform=lambda value, row: value, statistic=np.median, xlabel: str, letter: str) -> None:
    rng = np.random.default_rng(BOOTSTRAP_SEED + ord(letter))
    for pos, model in enumerate(models):
        values = np.asarray([transform(number(row, field), row) for row in raw if row["model"] == model], dtype=float)
        style = model_style(model)
        jitter = rng.uniform(-0.095, 0.095, size=len(values))
        ax.scatter(values, pos + jitter, s=7, alpha=0.27, color=style["color"], linewidths=0, zorder=2)
        estimate = float(statistic(values))
        low, high = bootstrap_interval(values, statistic=statistic, iterations=BOOTSTRAP_ITERATIONS, seed=BOOTSTRAP_SEED + pos)
        interval_point(ax, pos, estimate, low, high, color=style["color"], marker=style["marker"])
    ax.set_yticks(np.arange(len(models)), [model_label(x) for x in models])
    ax.set_xlabel(xlabel)
    despine(ax)
    panel_label(ax, letter)


def render_figure5() -> None:
    raw = read_csv("F5_process_metrics_raw.csv")
    models = sorted_models_from_f1()
    fig, axes = plt.subplots(1, 4, figsize=(DOUBLE_COLUMN_IN, 3.45), sharey=True, layout="constrained")
    ax = axes[0]
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    for pos, model in enumerate(models):
        style = model_style(model)
        for offset, field, marker, open_marker in ((0.09, "validation_primary", "o", False), (-0.09, "validation_sensitivity", "s", True)):
            values = np.asarray([number(row, field) for row in raw if row["model"] == model])
            jitter = rng.uniform(-0.035, 0.035, len(values))
            ax.scatter(values, pos + offset + jitter, s=6, alpha=0.22, color=style["color"], linewidths=0)
            estimate = float(np.mean(values))
            low, high = bootstrap_interval(values, statistic=np.mean, iterations=BOOTSTRAP_ITERATIONS, seed=BOOTSTRAP_SEED + pos)
            interval_point(ax, pos + offset, estimate, low, high, color=style["color"], marker=marker, open_marker=open_marker)
    ax.set_yticks(np.arange(len(models)), [model_label(x) for x in models])
    ax.set_xlim(-0.05, 1.05)
    ax.set_xlabel("Validation rate")
    ax.legend(handles=[Line2D([], [], marker="o", color=INK, linestyle="none", label="intent rule"), Line2D([], [], marker="s", markerfacecolor="white", markeredgecolor=INK, linestyle="none", label="successful command")], loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=5.8)
    despine(ax)
    panel_label(ax, "a")
    draw_distribution_panel(axes[1], raw, models, "write_rewrites", transform=lambda value, row: float(value > 0), statistic=np.mean, xlabel="Runs with rewrite", letter="b")
    draw_distribution_panel(axes[2], raw, models, "loops", transform=lambda value, row: float(value > 0), statistic=np.mean, xlabel="Runs with loop", letter="c")
    draw_distribution_panel(axes[3], raw, models, "first_edit", transform=lambda value, row: value / max(number(row, "steps"), 1), statistic=np.median, xlabel="First-edit position", letter="d")
    for axis in axes[1:]:
        axis.tick_params(axis="y", labelleft=False)
    save_figure(fig, FIG / "F5_process_metrics")


def render_figure6() -> None:
    rows = {row["model"]: row for row in read_csv("F6_turns_calls_blindwrite.csv")}
    models = sorted_models_from_f1()
    specs = [("assistant_turns_median", "Assistant turns / run", "a"), ("calls_per_turn_median", "Tool calls / turn", "b"), ("blind_write_rate", "Blind-write fraction", "c")]
    fig, axes = plt.subplots(1, 3, figsize=(DOUBLE_COLUMN_IN, 3.05), sharey=True, layout="constrained")
    for ax, (field, xlabel, letter) in zip(axes, specs):
        for pos, model in enumerate(models):
            value = number(rows[model], field)
            style = model_style(model)
            ax.plot(value, pos, marker=style["marker"], color=style["color"], linestyle="none", markersize=4.6)
            direct_label(ax, value, pos - 0.18, f"n={int(number(rows[model], 'n'))}", ha="center", fontsize=5.6, color=MUTED)
        ax.set_yticks(np.arange(len(models)), [model_label(x) for x in models])
        ax.set_xlabel(xlabel)
        despine(ax)
        panel_label(ax, letter)
    for axis in axes[1:]:
        axis.tick_params(axis="y", labelleft=False)
    save_figure(fig, FIG / "F6_turns_calls_blindwrite")


def draw_token_stack(ax: mpl.axes.Axes, rows: dict[str, dict[str, str]], models: list[str]) -> None:
    """F7-only whitelist: thin horizontal 100% stacked token-composition bars."""
    components = ["input_tokens", "cached_tokens", "output_tokens", "reasoning_tokens"]
    labels = ["input", "cached", "output", "reasoning"]
    colours = ["#4E79A7", "#A0CBE8", "#F28E2B", "#B07AA1"]
    left = np.zeros(len(models))
    for component, label, colour in zip(components, labels, colours):
        values = np.array([number(rows[model], component) for model in models])
        totals = np.array([sum(number(rows[model], item) for item in components) for model in models])
        shares = np.divide(values, totals, out=np.zeros_like(values), where=totals > 0)
        ax.barh(np.arange(len(models)), shares, left=left, height=0.35, color=colour, edgecolor="white", linewidth=0.35, label=label)
        for pos, (start, share) in enumerate(zip(left, shares)):
            if share >= 0.075:
                ax.text(start + share / 2, pos, f"{100*share:.0f}%", ha="center", va="center", fontsize=5.7, color="white" if colour != "#A0CBE8" else INK)
        left += shares
    ax.set_yticks(np.arange(len(models)), [model_label(x) for x in models])
    ax.set_xlim(0, 1)
    ax.set_xlabel("Share of recorded tokens")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=4, columnspacing=0.8, handlelength=1.1)
    despine(ax)


def render_figure7() -> None:
    rows = {row["model"]: row for row in read_csv("F7_token_composition.csv")}
    models = sorted_models_from_f1()
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(DOUBLE_COLUMN_IN, 3.05), gridspec_kw={"width_ratios": (1.45, 1)}, layout="constrained")
    draw_token_stack(ax_a, rows, models)
    panel_label(ax_a, "a")
    components = ["input_tokens", "cached_tokens", "output_tokens", "reasoning_tokens"]
    for pos, model in enumerate(models):
        total = sum(number(rows[model], item) for item in components)
        style = model_style(model)
        ax_b.plot(total, pos, marker=style["marker"], color=style["color"], linestyle="none", markersize=4.8)
        direct_label(ax_b, total * 1.08, pos, f"{total:,.0f}", color=style["color"], fontsize=6.2)
    ax_b.set_xscale("log")
    ax_b.set_yticks(np.arange(len(models)), [model_label(x) for x in models])
    ax_b.set_xlabel("Median recorded tokens / run (log scale)")
    despine(ax_b)
    panel_label(ax_b, "b")
    save_figure(fig, FIG / "F7_token_composition")


def curved_flow(ax: mpl.axes.Axes, start: tuple[float, float], end: tuple[float, float], count: int, color: str, maximum: int) -> None:
    if count <= 0:
        return
    vertices = [start, (0.38, start[1]), (0.62, end[1]), end]
    path = MplPath(vertices, [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4])
    ax.add_patch(PathPatch(path, fill=False, edgecolor=color, linewidth=0.8 + 5.0 * count / max(maximum, 1), alpha=0.55, capstyle="round"))


def draw_transition_panel(ax: mpl.axes.Axes, condition: str, values: dict[str, int], letter: str) -> None:
    total = values["A_layer_runs"]
    already = values["already_pass_at_32"]
    not_pass = values["not_pass_at_32"]
    converted = values["final_pass_among_not_pass_at_32"]
    unknown = max(0, total - already - not_pass)
    colour = CONDITION_COLORS[condition]
    start = {"pass": (0.08, 0.76), "not": (0.08, 0.33), "unknown": (0.08, 0.08)}
    end = {"pass": (0.92, 0.72), "fail": (0.92, 0.27), "unknown": (0.92, 0.06)}
    curved_flow(ax, start["pass"], end["pass"], already, colour, total)
    curved_flow(ax, start["not"], end["pass"], converted, "#2A9D8F", total)
    curved_flow(ax, start["not"], end["fail"], not_pass - converted, "#8C6D62", total)
    curved_flow(ax, start["unknown"], end["unknown"], unknown, MUTED, total)
    nodes = [(*start["pass"], already, "passed @32"), (*start["not"], not_pass, "not passed @32"), (*end["pass"], already + converted, "final pass"), (*end["fail"], not_pass - converted, "final non-pass")]
    if unknown:
        nodes.extend([(*start["unknown"], unknown, "unclassified @32"), (*end["unknown"], unknown, "unclassified")])
    for x, y, count, label in nodes:
        ax.scatter(x, y, s=22 + 9 * count, color=colour if x < 0.5 else "#555555", edgecolor="white", linewidth=0.5, zorder=5)
        direct_label(ax, x - 0.025 if x < 0.5 else x + 0.025, y, f"{label}\n{count}", ha="right" if x < 0.5 else "left", fontsize=6.2)
    ax.text(0.5, 0.94, "Baseline" if condition == "baseline" else "L3b", ha="center", va="center", fontsize=8, weight="bold", color=colour)
    ax.text(0.5, 0.88, f"conversion among not-passed @32: {converted}/{not_pass}", ha="center", va="center", fontsize=6.5, color=INK)
    ax.set_xlim(-0.08, 1.08)
    ax.set_ylim(-0.02, 1.02)
    ax.axis("off")
    panel_label(ax, letter, x=-0.02)


def render_figure8() -> None:
    rows = read_csv("F8_l3b_transitions.csv")
    grouped: dict[str, dict[str, int]] = {}
    for row in rows:
        grouped.setdefault(row["condition"], {})[row["state"]] = int(number(row, "count"))
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(DOUBLE_COLUMN_IN, 3.15), layout="constrained")
    draw_transition_panel(ax_a, "baseline", grouped["baseline"], "a")
    draw_transition_panel(ax_b, "l3b", grouped["l3b"], "b")
    fig.text(0.5, 0.01, "Descriptive call-32 state transitions; not an effect estimate.", ha="center", va="bottom", color=MUTED, fontsize=6.6)
    save_figure(fig, FIG / "F8_l3b_transitions")


def render_figure9() -> None:
    rows = read_csv("F9_kappa_pabak.csv")
    label_map = {"premature_implementation": "Premature implementation", "repeated_exploration": "Repeated exploration", "ineffective_debugging_loop": "Debugging loop", "insufficient_validation": "Insufficient validation", "missed_constraint": "Missed constraint", "premature_completion": "Premature completion", "tool_misuse": "Tool misuse", "file_corruption": "File corruption"}
    rows = sorted(rows, key=lambda row: number(row, "pabak"))
    y = np.arange(len(rows))
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(DOUBLE_COLUMN_IN, 4.0), gridspec_kw={"width_ratios": (1.25, 1)}, layout="constrained")
    for pos, row in zip(y, rows):
        estimable = row["kappa_estimable"].lower() == "true"
        if estimable:
            interval_point(ax_a, pos + 0.09, number(row, "kappa"), number(row, "kappa_low"), number(row, "kappa_high"), color="#3B6EA5", marker="o")
        else:
            direct_label(ax_a, -0.07, pos + 0.09, "κ n/e", ha="left", fontsize=5.8, color=MUTED)
        ax_a.plot(number(row, "pabak"), pos - 0.09, marker="D", markerfacecolor="white", markeredgecolor="#D55E00", linestyle="none", markersize=4.0)
        agreement = int(number(row, "human_positive_judge_positive") + number(row, "human_negative_judge_negative"))
        direct_label(ax_a, 1.025, pos, f"{agreement}/24", fontsize=6.1)
    ax_a.axvline(0, color="#A7A7A7", linewidth=0.7)
    ax_a.set_yticks(y, [label_map[row["label"]] for row in rows])
    ax_a.set_xlim(-0.11, 1.16)
    ax_a.set_xlabel("Agreement coefficient")
    ax_a.legend(handles=[Line2D([], [], marker="o", color="#3B6EA5", label="Cohen's κ (bootstrap 95% CI)"), Line2D([], [], marker="D", markerfacecolor="white", markeredgecolor="#D55E00", linestyle="none", label="PABAK")], loc="lower left", bbox_to_anchor=(0.0, 1.0), fontsize=5.9, ncol=2, columnspacing=0.8)
    despine(ax_a)
    panel_label(ax_a, "a")

    columns = ["human_positive_judge_positive", "human_positive_judge_negative", "human_negative_judge_positive", "human_negative_judge_negative"]
    matrix = np.array([[number(row, column) for column in columns] for row in rows])
    annotated_heatmap(ax_b, matrix, [label_map[row["label"]] for row in rows], ["H+ / J+", "H+ / J−", "H− / J+", "H− / J−"], cmap="cividis", vmin=0, vmax=24, decimals=0, annotation_size=5.8)
    ax_b.set_title("Human × judge counts", loc="left", pad=5)
    panel_label(ax_b, "b", x=-0.17)
    save_figure(fig, FIG / "F9_kappa_pabak")


def write_panel_manifest() -> None:
    payload = {"format": "publication-multipanel-v2", "panel_counts": FIGURE_PANEL_COUNTS, "csv_sha256": CSV_SHA256, "bootstrap": {"iterations": BOOTSTRAP_ITERATIONS, "seed": BOOTSTRAP_SEED}}
    (FIG / "panel_manifest.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_qa() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    for stem in FIGURE_STEMS:
        source = FIG / f"{stem}.png"
        simulate_cvd(source, QA / f"{stem}_deuteranopia.png", "deuteranomaly")
        simulate_cvd(source, QA / f"{stem}_protanopia.png", "protanomaly")
    make_contact_sheet([FIG / f"{stem}.png" for stem in FIGURE_STEMS], FIG / "contact_sheet.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--formal-s7", action="store_true")
    parser.add_argument("--skip-qa", action="store_true")
    args = parser.parse_args()
    if args.formal_s7:
        enforce_formal_s7_gate(ROOT / "STATUS.md", ROOT / "analysis/analysis_patch_manifest.json")
        raise SystemExit("S7 gate passed; formal figures require the post-completion analysis commit")
    configure_matplotlib()
    verify_csv_hashes()
    render_figure1()
    render_figure2()
    render_figure3()
    render_figure4()
    render_figure5()
    render_figure6()
    render_figure7()
    render_figure8()
    render_figure9()
    write_panel_manifest()
    if not args.skip_qa:
        render_qa()
    verify_csv_hashes()
    print(json.dumps({"figures": len(FIGURE_STEMS), "panels": sum(FIGURE_PANEL_COUNTS.values()), "csv_hashes_unchanged": True, "output": str(FIG)}))


if __name__ == "__main__":
    main()
