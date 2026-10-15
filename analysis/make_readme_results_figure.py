#!/usr/bin/env python3
"""Build the eight-model README result figure from the locked S7 table."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.patches import FancyBboxPatch, Patch
from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "results" / "tables" / "s7" / "S7_T1_model_condition_summary.csv"
OUT = ROOT / "figures" / "s7" / "verifier_pass_rates_by_model"
LOGOS = ROOT / "figures" / "s7" / "logos"
DATA_OUT = ROOT / "figures" / "s7" / "data" / "verifier_pass_rates_by_model.csv"

DISPLAY = {
    "ornith1.5:35b": "Ornith 1.5 35B",
    "qwen3.8:27b": "Qwen3.8 27B",
    "gpt-5.6-sol": "GPT-5.6 Sol",
    "glm-5.3-flash": "GLM-5.3 Flash",
    "gemma4:26b": "Gemma4 26B",
    "qwen3-coder-next": "Qwen3 Coder Next",
    "qwen3.5:9b": "Qwen3.5 9B",
    "llama3.1:8b": "Llama3.1 8B",
}

LOGO_FILE = {
    "ornith1.5:35b": "ornith.png",
    "qwen3.8:27b": "qwen.png",
    "gpt-5.6-sol": "openai.png",
    "glm-5.3-flash": "zai.png",
    "gemma4:26b": "google.png",
    "qwen3-coder-next": "qwen.png",
    "qwen3.5:9b": "qwen.png",
    "llama3.1:8b": "meta.png",
}

# Brand-adjacent, low-saturation colors. Color is redundant with row labels.
BRAND = {
    "ornith1.5:35b": "#C98B32",
    "qwen3.8:27b": "#5159E8",
    "gpt-5.6-sol": "#0B9B78",
    "glm-5.3-flash": "#315BE8",
    "gemma4:26b": "#3D83E8",
    "qwen3-coder-next": "#6559E6",
    "qwen3.5:9b": "#5964EB",
    "llama3.1:8b": "#1473E6",
}


mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "font.size": 9,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


def mix(color: str, target: str, amount: float) -> tuple[float, float, float]:
    base = np.asarray(mcolors.to_rgb(color))
    other = np.asarray(mcolors.to_rgb(target))
    return tuple(base * (1 - amount) + other * amount)


def load_rows() -> dict[str, dict[str, dict[str, float | int]]]:
    rows: dict[str, dict[str, dict[str, float | int]]] = {}
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            if raw["split"] != "all" or raw["condition"] not in {"C0", "C1"}:
                continue
            model = raw["model"]
            rows.setdefault(model, {})[raw["condition"]] = {
                "n": int(raw["primary_n"]),
                "passed": int(raw["verifier_pass"]),
                "rate": float(raw["verifier_pass_rate"]),
                "low": float(raw["wilson_low"]),
                "high": float(raw["wilson_high"]),
            }
    missing = set(DISPLAY) - set(rows)
    if missing:
        raise RuntimeError(f"Missing locked S7 rows for: {sorted(missing)}")
    for model in DISPLAY:
        if set(rows[model]) != {"C0", "C1"}:
            raise RuntimeError(f"Expected C0 and C1 for {model}")
    return rows


def write_source_data(rows: dict[str, dict[str, dict[str, float | int]]], order: list[str]) -> None:
    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = ["model", "condition", "primary_n", "verifier_pass", "pass_rate", "wilson_low", "wilson_high"]
    with DATA_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for model in order:
            for condition in ("C0", "C1"):
                item = rows[model][condition]
                writer.writerow(
                    {
                        "model": model,
                        "condition": condition,
                        "primary_n": item["n"],
                        "verifier_pass": item["passed"],
                        "pass_rate": f"{item['rate']:.12g}",
                        "wilson_low": f"{item['low']:.12g}",
                        "wilson_high": f"{item['high']:.12g}",
                    }
                )


def gradient_bar(
    ax: plt.Axes,
    y: float,
    width: float,
    height: float,
    left_color: tuple[float, float, float],
    right_color: tuple[float, float, float],
) -> None:
    if width <= 0:
        return
    grad = np.linspace(0, 1, 256)[None, :, None]
    left = np.asarray(left_color)[None, None, :]
    right = np.asarray(right_color)[None, None, :]
    image = left * (1 - grad) + right * grad
    image = np.repeat(image, 12, axis=0)
    patch = FancyBboxPatch(
        (0, y - height / 2), width, height,
        boxstyle=f"round,pad=0,rounding_size={height * 0.23}",
        linewidth=0, facecolor="none", transform=ax.transData,
    )
    ax.add_patch(patch)
    artist = ax.imshow(
        image,
        extent=(0, width, y - height / 2, y + height / 2),
        origin="lower",
        aspect="auto",
        interpolation="bicubic",
        zorder=2,
    )
    artist.set_clip_path(patch)


def add_logo(ax: plt.Axes, model: str, y: float) -> None:
    path = LOGOS / LOGO_FILE[model]
    with Image.open(path) as image:
        rgba = np.asarray(image.convert("RGBA"))
    zoom = 0.105 if model == "ornith1.5:35b" else 0.34
    if model == "glm-5.3-flash":
        zoom = 0.040
    box = AnnotationBbox(
        OffsetImage(rgba, zoom=zoom, interpolation="lanczos"),
        (-0.290, y),
        frameon=False,
        box_alignment=(0.5, 0.5),
        xycoords="data",
        pad=0,
        zorder=8,
    )
    ax.add_artist(box)


def build() -> None:
    rows = load_rows()
    order = sorted(DISPLAY, key=lambda model: rows[model]["C0"]["rate"], reverse=True)
    write_source_data(rows, order)

    fig = plt.figure(figsize=(10.8, 7.0), facecolor="#F5F8FC")
    card = FancyBboxPatch(
        (0.018, 0.025), 0.964, 0.95,
        boxstyle="round,pad=0.012,rounding_size=0.022",
        transform=fig.transFigure,
        facecolor="white", edgecolor="#E1E7F0", linewidth=0.9, zorder=-10,
    )
    fig.patches.append(card)
    ax = fig.add_axes((0.075, 0.13, 0.865, 0.73))
    ax.set_facecolor("white")

    centers = np.arange(len(order), dtype=float)
    bar_height = 0.28
    offset = 0.18
    for i, model in enumerate(order):
        base = BRAND[model]
        c0 = rows[model]["C0"]
        c1 = rows[model]["C1"]
        y_c1, y_c0 = centers[i] - offset, centers[i] + offset

        gradient_bar(ax, y_c0, float(c0["rate"]), bar_height, mix(base, "#FFFFFF", 0.72), mix(base, "#FFFFFF", 0.50))
        gradient_bar(ax, y_c1, float(c1["rate"]), bar_height, mix(base, "#FFFFFF", 0.16), mix(base, "#182FE5", 0.10))

        for item, y in ((c0, y_c0), (c1, y_c1)):
            rate = float(item["rate"])
            low = float(item["low"])
            high = float(item["high"])
            ax.errorbar(
                rate, y,
                xerr=np.array([[rate - low], [high - rate]]),
                fmt="none", ecolor="#1C2533", elinewidth=1.05, capsize=3.0, capthick=1.05, zorder=5,
            )

        if float(c1["rate"]) >= 0.14:
            ax.text(max(0.025, float(c1["low"]) - 0.015), y_c1, f"{100*float(c1['rate']):.1f}%",
                    ha="right", va="center", color="white", fontsize=7.4, fontweight="bold", zorder=7)
        else:
            ax.text(float(c1["high"]) + 0.012, y_c1, f"{100*float(c1['rate']):.1f}%",
                    ha="left", va="center", color="#172033", fontsize=7.4, fontweight="bold", zorder=7,
                    bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 0.5})
        if float(c0["rate"]) >= 0.14:
            ax.text(max(0.025, float(c0["low"]) - 0.015), y_c0, f"{100*float(c0['rate']):.1f}%",
                    ha="right", va="center", color="#172033", fontsize=7.4, fontweight="bold", zorder=7)
        else:
            ax.text(float(c0["high"]) + 0.012, y_c0, f"{100*float(c0['rate']):.1f}%",
                    ha="left", va="center", color="#172033", fontsize=7.4, fontweight="bold", zorder=7,
                    bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 0.5})

        add_logo(ax, model, centers[i])
        ax.text(-0.245, centers[i], DISPLAY[model], ha="left", va="center",
                fontsize=9.4, fontweight="bold", color="#111827", clip_on=False)
        n0, n1 = int(c0["n"]), int(c1["n"])
        n_label = f"n={n0}/condition" if n0 == n1 else f"n={n0}/{n1}"
        ax.text(1.035, centers[i], n_label, ha="left", va="center", fontsize=7.6, color="#526078")

    ax.set_xlim(-0.34, 1.12)
    ax.set_ylim(len(order) - 0.45, -0.55)
    ax.set_yticks([])
    ax.set_xticks(np.linspace(0, 1, 6), [f"{int(x*100)}%" for x in np.linspace(0, 1, 6)])
    ax.set_xlabel("Verifier pass rate (95% Wilson interval)", labelpad=11, color="#334155")
    ax.tick_params(axis="x", direction="out", length=4, width=0.8, colors="#526078")
    ax.spines["left"].set_position(("data", 0))
    ax.spines["left"].set_color("#526078")
    ax.spines["bottom"].set_color("#526078")
    ax.grid(axis="x", color="#DDE5EF", linewidth=0.75, zorder=0)
    ax.grid(axis="y", visible=False)
    for y in centers[:-1] + 0.5:
        ax.axhline(y, xmin=0.0, xmax=0.93, color="#EEF2F7", linewidth=0.7, zorder=0)

    fig.text(0.075, 0.925, "Verifier pass rates across eight model configurations",
             ha="left", va="center", fontsize=15, fontweight="bold", color="#111827")
    fig.text(0.075, 0.889, "C0 (no skill) versus C1 (fixed skill); primary denominators exclude retry-exhausted provider errors.",
             ha="left", va="center", fontsize=8.5, color="#64748B")

    legend = [
        Patch(facecolor="#C9D2E4", edgecolor="none", label="C0 · no skill (light tint)"),
        Patch(facecolor="#4254DF", edgecolor="none", label="C1 · fixed skill (saturated tint)"),
    ]
    fig.legend(handles=legend, loc="upper right", bbox_to_anchor=(0.936, 0.932), ncol=2,
               frameon=False, fontsize=8.3, handlelength=1.8, columnspacing=1.5)

    fig.canvas.draw()
    try:
        from audit_panel_alignment import require_matplotlib_panel_alignment
    except ImportError:
        require_matplotlib_panel_alignment = None
    if require_matplotlib_panel_alignment is not None:
        qa = OUT.parent / "qa"
        qa.mkdir(parents=True, exist_ok=True)
        require_matplotlib_panel_alignment(
            fig,
            json_out=qa / f"{OUT.name}.alignment.json",
            overlay_svg=qa / f"{OUT.name}.alignment.svg",
            tolerance_pt=1.5,
            gutter_tolerance_pt=1.5,
            require_panel_labels=False,
            strict=True,
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.035)
    fig.savefig(OUT.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.035)
    fig.savefig(OUT.with_suffix(".png"), dpi=300, bbox_inches="tight", pad_inches=0.035)
    fig.savefig(OUT.with_suffix(".tiff"), dpi=600, bbox_inches="tight", pad_inches=0.035)
    svg = OUT.with_suffix(".svg")
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)


if __name__ == "__main__":
    build()
