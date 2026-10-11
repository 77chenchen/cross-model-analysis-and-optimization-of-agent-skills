#!/usr/bin/env python3
"""Render the README-facing, vector S7 core-results bar chart.

This is a presentation-only view of the formal S7 summary table.  It does not
recompute, filter, or alter the gated verifier-pass results.
"""
from __future__ import annotations

import csv
import json
from hashlib import sha256
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from matplotlib.transforms import blended_transform_factory

# Required for selectable SVG text and portable sans-serif fallbacks.
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
plt.rcParams.update({"svg.fonttype": "none", "pdf.fonttype": 42})

from analysis.style import GRID, INK, MUTED, configure_matplotlib, despine, model_label
from analysis.verifier_pass_v2 import ROOT


TABLE = ROOT / "results" / "tables" / "s7" / "S7_T1_model_condition_summary.csv"
OUT = ROOT / "figures" / "s7"
STEM = OUT / "S7_F1_bar_results"

ORDER = [
    "qwen3.8:27b",
    "gpt-5.6-sol",
    "gemma4:26b",
    "qwen3-coder-next",
    "qwen3.5:9b",
    "llama3.1:8b",
]

# Vendor-family palette. Monograms are original identifiers, not copied logos.
BRAND_COLORS = {
    "qwen3.8:27b": "#615CED",      # Qwen / Alibaba family
    "gpt-5.6-sol": "#10A37F",       # OpenAI family
    "gemma4:26b": "#4285F4",        # Google / Gemma family
    "qwen3-coder-next": "#615CED", # Qwen / Alibaba family
    "qwen3.5:9b": "#615CED",       # Qwen / Alibaba family
    "llama3.1:8b": "#0866FF",      # Meta / Llama family
}

BADGES = {
    "qwen3.8:27b": "Q",
    "gpt-5.6-sol": "GPT",
    "gemma4:26b": "G",
    "qwen3-coder-next": "Q",
    "qwen3.5:9b": "Q",
    "llama3.1:8b": "L",
}


def read_rows() -> list[dict[str, str]]:
    with TABLE.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def blend(color: str, target: str, amount: float) -> str:
    """Blend two hex colors; used to make a vector-only bar gradient."""
    source_rgb = tuple(int(color[index:index + 2], 16) for index in (1, 3, 5))
    target_rgb = tuple(int(target[index:index + 2], 16) for index in (1, 3, 5))
    mixed = tuple(round((1 - amount) * left + amount * right) for left, right in zip(source_rgb, target_rgb))
    return "#" + "".join(f"{channel:02x}" for channel in mixed)


def vector_gradient_barh(ax: plt.Axes, y: float, width: float, height: float, base: str, condition: str) -> None:
    """Draw an all-vector horizontal gradient as adjacent bar rectangles."""
    steps = 48
    if condition == "C0":
        start, end = blend(base, "#FFFFFF", 0.86), blend(base, "#FFFFFF", 0.50)
        edge = blend(base, "#FFFFFF", 0.22)
    else:
        start, end = blend(base, "#FFFFFF", 0.42), base
        edge = blend(base, "#000000", 0.16)
    for index in range(steps):
        left = width * index / steps
        segment_width = width / steps
        color = blend(start, end, (index + 0.5) / steps)
        ax.barh(y, segment_width, left=left, height=height, color=color, edgecolor="none", align="center", zorder=3)
    if width > 0:
        ax.barh(y, width, height=height, color="none", edgecolor=edge, linewidth=0.55, align="center", zorder=3.5)


def main() -> None:
    configure_matplotlib()
    plt.rcParams.update({"font.size": 8.5, "axes.labelsize": 8.5, "ytick.labelsize": 9.2, "xtick.labelsize": 8.0})
    rows = [row for row in read_rows() if row["split"] == "all" and row["condition"] in {"C0", "C1"}]
    core = {(row["model"], row["condition"]): row for row in rows}
    missing = [(model, condition) for model in ORDER for condition in ("C0", "C1") if (model, condition) not in core]
    if missing:
        raise SystemExit(f"Missing S7 rows: {missing}")

    # Wide, one-panel layout optimised for a README preview and downloadable PDF.
    fig, ax = plt.subplots(figsize=(7.2, 4.25))
    fig.subplots_adjust(left=0.42, right=0.975, top=0.83, bottom=0.23)
    y = np.arange(len(ORDER))
    offsets = {"C0": 0.18, "C1": -0.18}
    height = 0.30

    for condition in ("C0", "C1"):
        values = np.asarray([float(core[(model, condition)]["verifier_pass_rate"]) for model in ORDER])
        lower = np.asarray([float(core[(model, condition)]["wilson_low"]) for model in ORDER])
        upper = np.asarray([float(core[(model, condition)]["wilson_high"]) for model in ORDER])
        for position, (model, estimate) in enumerate(zip(ORDER, values)):
            vector_gradient_barh(ax, position + offsets[condition], estimate, height, BRAND_COLORS[model], condition)
        ax.errorbar(values, y + offsets[condition], xerr=np.vstack((values - lower, upper - values)),
                    fmt="none", color=INK, linewidth=0.75, capsize=2.2, capthick=0.75, zorder=4)

    ax.set_xlim(0, 1.12)
    ax.set_ylim(len(ORDER) - 0.48, -0.60)
    ax.set_yticks(y, [model_label(model) + ("†" if model == "gpt-5.6-sol" else "") for model in ORDER])
    ax.set_xticks(np.arange(0, 1.01, 0.2), [f"{tick:.0%}" for tick in np.arange(0, 1.01, 0.2)])
    ax.set_xlabel("Verifier pass rate (95% Wilson interval)", labelpad=9)
    ax.xaxis.grid(True, color=GRID, linewidth=0.55, zorder=0)
    ax.tick_params(axis="y", length=0, pad=10)
    despine(ax)

    # Model-family monograms sit to the immediate left of their names.
    badge_transform = blended_transform_factory(ax.transAxes, ax.transData)
    for position, model in enumerate(ORDER):
        text, color = BADGES[model], BRAND_COLORS[model]
        ax.scatter([-0.520], [position], s=265, marker="o", color=color, transform=badge_transform,
                   clip_on=False, zorder=8)
        ax.text(-0.520, position, text, transform=badge_transform, ha="center", va="center", clip_on=False,
                color="white", fontsize=5.2 if text == "GPT" else 7.1, fontweight="bold", zorder=9)

    for position, model in enumerate(ORDER):
        n = int(core[(model, "C0")]["primary_n"])
        ax.text(1.035, position, f"n = {n}", ha="left", va="center", fontsize=7.0, color=MUTED)

    legend = ax.legend(handles=[
        Patch(facecolor="#DEE0E4", edgecolor="#979CA4", label="C0 · light vendor tint"),
        Patch(facecolor="#59616D", edgecolor="#343A43", label="C1 · saturated vendor tint"),
    ], loc="upper left", bbox_to_anchor=(0.0, 1.16), ncol=2, handlelength=1.35,
       columnspacing=1.8, frameon=False, borderaxespad=0)
    for entry in legend.get_texts():
        entry.set_color(MUTED)
    ax.text(0.0, -0.175,
            "† GPT-5.6 Sol is a sampling-uncontrolled reference anchor.  Primary denominator excludes retry-exhausted provider errors.\n"
            "Each bar uses a vendor-family vector gradient; model badges are original monograms, not vendor logos.",
            transform=ax.transAxes, ha="left", va="top", fontsize=6.5, color=MUTED, linespacing=1.45)

    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(STEM.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.05)
    fig.savefig(STEM.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.05)
    fig.savefig(STEM.with_suffix(".png"), dpi=300, bbox_inches="tight", pad_inches=0.05)
    fig.savefig(STEM.with_suffix(".tiff"), dpi=600, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    # Preserve the visual SVG while keeping repository whitespace checks clean.
    svg_path = STEM.with_suffix(".svg")
    svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")

    metadata = {
        "figure": STEM.name,
        "source": str(TABLE.relative_to(ROOT)),
        "source_sha256": sha256(TABLE.read_bytes()).hexdigest(),
        "definition": "Grouped C0/C1 verifier pass rates with Wilson intervals; all formal S7 tasks.",
        "color_scheme": "Vendor-family colors; C0 uses a light vector gradient and C1 a saturated vector gradient.",
        "model_badges": "Original monograms; not vendor logos.",
    }
    (OUT / f"{STEM.name}.metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
