#!/usr/bin/env python3
"""Create manuscript figures from frozen analysis tables; never edits source CSVs."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
WEAK = "#D55E00"
STRONG = "#0072B2"
INK = "#292929"
GRID = "#D8D8D8"
GRAY = "#777777"
BLUE = "#3B6EA5"

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
    "mathtext.fontset": "stix",
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "axes.linewidth": 0.6,
    "axes.edgecolor": INK,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def read(name: str) -> list[dict[str, str]]:
    with (FIG / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def save(fig: plt.Figure, name: str) -> None:
    fig.canvas.draw()
    if len([axis for axis in fig.axes if axis.get_visible()]) >= 2:
        try:
            from audit_panel_alignment import require_matplotlib_panel_alignment
        except ImportError:
            require_matplotlib_panel_alignment = None
        if require_matplotlib_panel_alignment is not None:
            qa = FIG / "qa"
            qa.mkdir(parents=True, exist_ok=True)
            require_matplotlib_panel_alignment(
                fig,
                json_out=qa / f"{Path(name).stem}.alignment.json",
                overlay_svg=qa / f"{Path(name).stem}.alignment.svg",
                tolerance_pt=1.5,
                gutter_tolerance_pt=1.5,
                require_panel_labels=False,
                strict=True,
                exemptions=[{
                    "panels": ["a", "b", "c"],
                    "checks": ["panel-width", "horizontal-gutter"],
                    "reason": "Intentional asymmetric outcome, depth, and flag panels.",
                }],
            )
    output = FIG / name
    fig.savefig(output, format="pdf", bbox_inches="tight", pad_inches=0.04)
    fig.savefig(output.with_suffix(".svg"), format="svg", bbox_inches="tight", pad_inches=0.04)
    fig.savefig(output.with_suffix(".png"), format="png", dpi=300, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(output.with_suffix(".tiff"), format="tiff", dpi=600, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def main_results() -> None:
    core = [r for r in read("S7_T1_model_condition_summary.csv")
            if r["split"] == "all" and r["condition"] in ("C0", "C1")]
    process = read("S7_T4_process_metrics.csv")
    models = sorted({r["model"] for r in core}, key=lambda m: float(next(
        r for r in core if r["model"] == m and r["condition"] == "C0")["verifier_pass_rate"]))
    by = {(r["model"], r["condition"]): r for r in core}
    proc = {(r["model"], r["condition"], r["metric"]): r for r in process}
    # Eight rows remain legible at the manuscript's 5.5-inch text width.
    fig = plt.figure(figsize=(5.5, 4.05), layout="constrained")
    grid = fig.add_gridspec(1, 3, width_ratios=(2.55, 1.15, 1.35), wspace=0.16)
    a, b, c = [fig.add_subplot(grid[0, i]) for i in range(3)]
    y = np.arange(len(models))
    a.axvspan(.2, .8, color="#E7E7E7", zorder=0)
    for i, model in enumerate(models):
        r0, r1 = by[(model, "C0")], by[(model, "C1")]
        p0, p1 = float(r0["verifier_pass_rate"]), float(r1["verifier_pass_rate"])
        a.plot([p0, p1], [i, i], color="#A0A0A0", linewidth=.6,
               linestyle="--" if model == "gpt-5.6-sol" else "-", zorder=1)
        for r, off, marker, color in ((r0, -.08, "o", GRAY), (r1, .08, "D", BLUE)):
            est, low, high = [float(r[k]) for k in ("verifier_pass_rate", "wilson_low", "wilson_high")]
            a.errorbar(est, i + off, xerr=[[est-low], [high-est]], fmt=marker,
                       color=color, ecolor=color, capsize=2, markersize=3.7,
                       markerfacecolor="white" if model == "gpt-5.6-sol" else color,
                       markeredgewidth=.8, linewidth=.8, zorder=3)
        a.text(1.27, i, f"n={int(r0['scheduled'])}", ha="right", va="center", fontsize=7)
    a.set_xlim(0, 1.32); a.set_xticks(np.arange(0, 1.01, .2))
    a.set_yticks(y, [m.replace(":", "\u2009:") for m in models]); a.invert_yaxis()
    a.set_xlabel("Verifier pass (Wilson 95% CI)", fontsize=7.2)
    a.set_title("(a) Core outcomes", loc="left", fontsize=9, fontweight="bold")
    a.grid(axis="x", color=GRID, linewidth=.45); a.set_axisbelow(True)
    a.tick_params(axis="both", labelsize=7, direction="out")
    a.spines["top"].set_visible(False); a.spines["right"].set_visible(False)

    b.set_title("(b) Run depth", loc="left", fontsize=9, fontweight="bold")
    for i, model in enumerate(models):
        if model == "gpt-5.6-sol":
            b.text(8, i, "n/a", ha="center", va="center", fontsize=7, color=GRAY)
            continue
        for metric, marker, off, filled in (("steps", "o", -.11, True), ("assistant_turns", "D", .11, False)):
            rows = [proc[(model, cond, metric)] for cond in ("C0", "C1")]
            q1 = np.mean([float(r["q1"]) for r in rows]); med = np.mean([float(r["median"]) for r in rows]); q3 = np.mean([float(r["q3"]) for r in rows])
            b.plot([q1, q3], [i+off, i+off], color=INK, linewidth=.9)
            b.plot(med, i+off, marker=marker, markersize=3.5, markeredgecolor=INK,
                   markerfacecolor=INK if filled else "white", linestyle="none")
    b.set_xlim(0, 24); b.set_xticks([0, 5, 10, 15, 20]); b.set_yticks(y, [])
    b.set_ylim(len(models) - .5, -.5)
    b.set_xlabel("Median [IQR]", fontsize=7.2); b.tick_params(axis="both", labelsize=7, direction="out")
    b.spines["top"].set_visible(False); b.spines["right"].set_visible(False)

    flag_names = ["final_empty", "no_edit", "timeout"]
    mat = []
    for model in models:
        rows = [by[(model, cond)] for cond in ("C0", "C1")]
        den = sum(int(r["scheduled"]) for r in rows)
        mat.append([sum(int(r[k]) for r in rows)/den for k in flag_names])
    mat = np.asarray(mat)
    c.imshow(mat, cmap="cividis", vmin=0, vmax=1, aspect="auto")
    c.set_title("(c) Run flags", loc="left", fontsize=9, fontweight="bold")
    c.set_xticks(range(3), ["final\nempty", "no\nedit", "timeout"], rotation=0, ha="center")
    c.set_yticks(y, [m.replace(":", "\u2009:") for m in models])
    c.tick_params(axis="both", labelsize=7, direction="out")
    for i in range(len(models)):
        for j in range(3):
            v = mat[i, j]
            c.text(j, i, f"{v:.0%}", ha="center", va="center", fontsize=7,
                   color="white" if v < .35 else "#151515")
    c.set_xticks(np.arange(-.5, 3, 1), minor=True); c.set_yticks(np.arange(-.5, len(models), 1), minor=True)
    c.grid(which="minor", color="white", linewidth=.6); c.tick_params(which="minor", bottom=False, left=False)
    c.spines["top"].set_visible(False); c.spines["right"].set_visible(False)
    save(fig, "main_results.pdf")


def decoupling() -> None:
    core = read("S7_T2_core_paired_differences.csv")
    proc = read("S7_T7_process_paired.csv")
    exploratory = read("S7_T6_exploratory.csv")
    q = "qwen3.5:9b"
    core_row = next(x for x in core if x["model"] == q and x["scope"] == "all")
    val_core = next(x for x in proc if x["model"] == q and x["scope"] == "all"
                    and x["metric"] == "validated_after_last_edit_intent")
    v1_row = next(x for x in exploratory if x["comparison"] == "v1_vs_C1_test_in")
    val_v1 = next(x for x in proc if x["model"] == q and x["scope"] == "test_in"
                  and x["contrast"] == "v1-C1"
                  and x["metric"] == "validated_after_last_edit_intent")
    items = [
        ("C1 − C0: post-edit validation", float(val_core["mean_difference"]),
         float(val_core["bootstrap_low"]), float(val_core["bootstrap_high"]), 18, WEAK),
        ("C1 − C0: verifier pass", float(core_row["mean_difference"]),
         float(core_row["bootstrap_low"]), float(core_row["bootstrap_high"]), 18, STRONG),
        ("v1 − C1: post-edit validation", float(val_v1["mean_difference"]),
         float(val_v1["bootstrap_low"]), float(val_v1["bootstrap_high"]), 12, WEAK),
        ("v1 − C1: verifier pass", float(v1_row["mean_difference"]),
         float(v1_row["bootstrap_low"]), float(v1_row["bootstrap_high"]), 12, STRONG),
    ]
    fig, ax = plt.subplots(figsize=(5.5, 2.65), layout="constrained")
    y = np.arange(len(items))[::-1]
    for yi, (label, est, lo, hi, n, color) in zip(y, items):
        ax.errorbar(est * 100, yi, xerr=[[max(0, (est - lo) * 100)], [max(0, (hi - est) * 100)]],
                    fmt="o", color=color, ecolor=color, capsize=2.5, markersize=4, linewidth=1.1)
        ax.text(82, yi, f"n={n} tasks", va="center", ha="right", fontsize=7, color=INK)
    ax.axvline(0, color="#666666", linewidth=0.8, linestyle=(0, (3, 2)))
    ax.set_yticks(y, [x[0] for x in items])
    ax.set_xlim(-50, 88)
    ax.set_xticks(np.arange(-40, 81, 20))
    ax.set_xlabel("Task-paired difference (percentage points; 95% paired-bootstrap interval)")
    ax.grid(axis="x", color=GRID, linewidth=0.45)
    ax.set_axisbelow(True)
    save(fig, "decoupling.pdf")


def legacy_accounting() -> None:
    rows = read("legacy_vs_verifier.csv")
    fig, ax = plt.subplots(figsize=(5.5, 2.6), layout="constrained")
    y = np.arange(len(rows))[::-1]
    for yi, row in zip(y, rows):
        n = int(row["denominator"])
        legacy = int(row["legacy_pass"]) / n
        verified = int(row["verifier_pass"]) / n
        ax.plot([legacy, verified], [yi, yi], color="#777777", linewidth=0.9, zorder=1)
        ax.scatter([legacy], [yi], marker="o", facecolors="white", edgecolors="#777777", s=24, zorder=2)
        ax.scatter([verified], [yi], marker="D", color=STRONG, s=20, zorder=3)
        ax.text(legacy, yi + 0.14, f"{int(row['legacy_pass'])}/{n}", ha="center", va="bottom", fontsize=7.0)
        ax.text(verified, yi - 0.14, f"{int(row['verifier_pass'])}/{n}", ha="center", va="top", fontsize=7.0)
    ax.set_yticks(y, [row["queue"] for row in rows])
    ax.set_xlim(0, 0.82)
    ax.set_xticks(np.arange(0, 0.81, 0.2), [f"{x:.0%}" for x in np.arange(0, 0.81, 0.2)])
    ax.set_xlabel("Share of usable runs passing")
    ax.grid(axis="x", color=GRID, linewidth=0.45)
    ax.set_axisbelow(True)
    save(fig, "legacy_vs_verifier.pdf")


def behavior_grid() -> None:
    rows = read("behavior_outcome_crosstab.csv")
    columns = [
        ("strong-pass", "strong-pass_rate", "strong-pass_count", "strong-pass_n"),
        ("strong-fail", "strong-fail_rate", "strong-fail_count", "strong-fail_n"),
        ("weak-pass", "weak-pass_rate", "weak-pass_count", "weak-pass_n"),
        ("weak-fail", "weak-fail_rate", "weak-fail_count", "weak-fail_n"),
    ]
    labels = {
        "read_before_edit": "Read before edit",
        "validation_after_edit": "Validate after edit",
        "avoids_rewrite": "Avoid repeated full-file write",
        "reread_after_edit": "Reread after edit",
    }
    values = np.asarray([[float(row[c[1]]) for c in columns] for row in rows])
    fig, ax = plt.subplots(figsize=(5.5, 3.1), layout="constrained")
    im = ax.imshow(values, cmap="cividis", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(4), [c[0].replace("-", "\n") for c in columns])
    ax.set_yticks(np.arange(len(rows)), [labels[row["behavior"]] for row in rows])
    for i, row in enumerate(rows):
        for j, (_, rate, count, n) in enumerate(columns):
            pct = 100 * float(row[rate])
            ax.text(j, i, f'{int(row[count])}/{int(row[n])}\n{pct:.1f}%',
                    ha="center", va="center", fontsize=7,
                    color="white" if pct < 58 else "#151515")
    ax.set_title("Mechanical behavior rates by development outcome cell", loc="left")
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.025)
    cb.set_label("Proportion of runs")
    cb.set_ticks([0, .25, .5, .75, 1])
    cb.set_ticklabels(["0", ".25", ".50", ".75", "1"])
    save(fig, "behavior_outcome.pdf")


def failure_flags() -> None:
    # Counts and denominators are transcribed from the frozen mechanical taxonomy table.
    labels = ["No edit", "Final message empty", "Timeout", "Compile error", "Step limit"]
    weak = np.array([6, 57, 2, 2, 13], dtype=float) / 98 * 100
    strong = np.array([3, 5, 0, 0, 5], dtype=float) / 97 * 100
    weak_n, strong_n = 98, 97
    fig, ax = plt.subplots(figsize=(5.5, 2.8), layout="constrained")
    y = np.arange(len(labels))
    h = 0.34
    ax.barh(y + h / 2, weak, h, color=WEAK, label=f"qwen3.5:9b (n={weak_n})")
    ax.barh(y - h / 2, strong, h, color=STRONG, label=f"Three strong models (n={strong_n})")
    for ys, vals, counts in ((y + h / 2, weak, [6, 57, 2, 2, 13]),
                             (y - h / 2, strong, [3, 5, 0, 0, 5])):
        for yy, vv, cc in zip(ys, vals, counts):
            ax.text(vv + 0.5, yy, f"{cc} ({vv:.1f}%)", va="center", fontsize=7.0)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 66)
    ax.set_xlabel("Share of verifier-failing runs with flag (%)")
    ax.grid(axis="x", color=GRID, linewidth=0.45)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=2, loc="lower right")
    save(fig, "failure_flags.pdf")


if __name__ == "__main__":
    main_results()
    decoupling()
    legacy_accounting()
    behavior_grid()
    failure_flags()
