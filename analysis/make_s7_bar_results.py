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
from tempfile import TemporaryDirectory

import cairosvg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import pymupdf
from PIL import Image

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

VENDOR_ICONS = {
    "qwen3.8:27b": "alibabacloud.svg",
    "gpt-5.6-sol": "openai.svg",
    "gemma4:26b": "google.svg",
    "qwen3-coder-next": "alibabacloud.svg",
    "qwen3.5:9b": "alibabacloud.svg",
    "llama3.1:8b": "meta.svg",
}
ICON_DIR = OUT / "assets" / "vendor-icons"


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


def add_vector_vendor_icons(pdf_path: Path) -> None:
    """Overlay SVG-derived logo PDFs without rasterizing the final vector PDF."""
    document = pymupdf.open(pdf_path)
    page = document[0]
    words = page.get_text("words", sort=True)
    # First word in the visible model label, in the same plotted order.
    anchors = {
        "qwen3.8:27b": "Qwen3.8",
        "gpt-5.6-sol": "GPT-5.6",
        "gemma4:26b": "Gemma4",
        "qwen3-coder-next": "Qwen3",
        "qwen3.5:9b": "Qwen3.5",
        "llama3.1:8b": "Llama3.1",
    }
    with TemporaryDirectory(prefix="skilltraj-icons-") as temporary:
        directory = Path(temporary)
        for model in ORDER:
            anchor = next((word for word in words if word[4] == anchors[model]), None)
            if anchor is None:
                raise RuntimeError(f"Could not place vendor icon for {model}")
            source = ICON_DIR / VENDOR_ICONS[model]
            logo_pdf = directory / f"{model}.pdf"
            cairosvg.svg2pdf(url=str(source), write_to=str(logo_pdf), output_width=120, output_height=120)
            icon_doc = pymupdf.open(logo_pdf)
            x0, y0, _x1, y1, *_ = anchor
            # The unusually long Qwen Coder label reaches the left crop edge.
            # Keep that one mark beside (rather than before) its text so that
            # all six provider marks remain visible in the final PDF.
            if model == "qwen3-coder-next":
                last_word = next((word for word in words if word[4] == "Next" and abs(word[1] - y0) < 1.0), anchor)
                rect = pymupdf.Rect(last_word[2] + 4, y0 - 3.0, last_word[2] + 24, y1 + 3.0)
            else:
                rect = pymupdf.Rect(x0 - 25, y0 - 3.0, x0 - 5, y1 + 3.0)
            page.show_pdf_page(rect, icon_doc, 0, keep_proportion=True, overlay=True)
            icon_doc.close()
        rewritten = pdf_path.with_name(pdf_path.stem + ".icons.pdf")
        document.save(rewritten, garbage=4, deflate=True)
    document.close()
    rewritten.replace(pdf_path)


def render_pdf_preview(pdf_path: Path, png_path: Path, tiff_path: Path) -> None:
    """Create README and archival raster previews from the final icon-bearing PDF."""
    document = pymupdf.open(pdf_path)
    for dpi, path, image_format in ((300, png_path, "PNG"), (600, tiff_path, "TIFF")):
        pixmap = document[0].get_pixmap(matrix=pymupdf.Matrix(dpi / 72, dpi / 72), alpha=False)
        image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
        image.save(path, format=image_format, dpi=(dpi, dpi))
    document.close()


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
    # Leave enough room for the longest model label and its vendor mark.  The
    # Qwen Coder label otherwise begins at the page edge and clips its icon.
    fig.subplots_adjust(left=0.56, right=0.975, top=0.83, bottom=0.23)
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
            "Each bar uses a vendor-family vector gradient; left labels use vendor application icons for identification only.",
            transform=ax.transAxes, ha="left", va="top", fontsize=6.5, color=MUTED, linespacing=1.45)

    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(STEM.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.05)
    fig.savefig(STEM.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    add_vector_vendor_icons(STEM.with_suffix(".pdf"))
    render_pdf_preview(STEM.with_suffix(".pdf"), STEM.with_suffix(".png"), STEM.with_suffix(".tiff"))
    # Preserve the visual SVG while keeping repository whitespace checks clean.
    svg_path = STEM.with_suffix(".svg")
    svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")

    metadata = {
        "figure": STEM.name,
        "source": str(TABLE.relative_to(ROOT)),
        "source_sha256": sha256(TABLE.read_bytes()).hexdigest(),
        "definition": "Grouped C0/C1 verifier pass rates with Wilson intervals; all formal S7 tasks.",
        "color_scheme": "Vendor-family colors; C0 uses a light vector gradient and C1 a saturated vector gradient.",
        "vendor_icons": "OpenAI, Google, Meta, and Alibaba Cloud application icons; source details in assets/vendor-icons/manifest.json.",
    }
    (OUT / f"{STEM.name}.metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
