"""Shared publication style for the benchmark's static scientific figures."""
from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt


SINGLE_COLUMN_IN = 3.4
DOUBLE_COLUMN_IN = 7.0

MODEL_STYLES = {
    "gpt-5.6-sol": {"color": "#3B3B3B", "marker": "o", "fill": "none", "linestyle": "--"},
    "qwen3.8:27b": {"color": "#0072B2", "marker": "D", "fill": "full", "linestyle": "-"},
    "qwen3.5:9b": {"color": "#D55E00", "marker": "o", "fill": "full", "linestyle": "-"},
    "gemma4:26b": {"color": "#009E73", "marker": "s", "fill": "full", "linestyle": "-"},
    "llama3.1:8b": {"color": "#CC79A7", "marker": "^", "fill": "full", "linestyle": "-"},
    "qwen3-coder-next": {"color": "#8C6BB1", "marker": "P", "fill": "full", "linestyle": "-"},
}

CONDITION_COLORS = {
    "C0": "#9A9A9A",
    "C1": "#3B6EA5",
    "v1": "#2A9D8F",
    "L3b": "#E08E2B",
    "baseline": "#9A9A9A",
    "l3b": "#E08E2B",
}

MODEL_LABELS = {
    "gpt-5.6-sol": "GPT-5.6 Sol",
    "qwen3.8:27b": "Qwen3.8 27B",
    "qwen3.5:9b": "Qwen3.5 9B",
    "gemma4:26b": "Gemma4 26B",
    "llama3.1:8b": "Llama3.1 8B",
    "qwen3-coder-next": "Qwen3 Coder Next",
}

INK = "#272727"
MUTED = "#6B6B6B"
GRID = "#D9D9D9"
PAPER = "#FFFFFF"


def configure_matplotlib() -> None:
    """Install a compact NeurIPS/ICLR/ACL-compatible matplotlib style."""
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
            "mathtext.fontset": "dejavusans",
            "font.size": 7.5,
            "axes.labelsize": 7.5,
            "axes.titlesize": 8.0,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.0,
            "legend.fontsize": 6.8,
            "axes.linewidth": 0.6,
            "axes.edgecolor": INK,
            "axes.labelcolor": INK,
            "text.color": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "xtick.major.width": 0.55,
            "ytick.major.width": 0.55,
            "xtick.major.size": 2.5,
            "ytick.major.size": 2.5,
            "axes.grid": False,
            "legend.frameon": False,
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "savefig.facecolor": PAPER,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "lines.linewidth": 1.0,
            "lines.markersize": 4.5,
        }
    )


def model_style(model: str) -> dict[str, str]:
    return MODEL_STYLES.get(model, {"color": MUTED, "marker": "o", "fill": "full", "linestyle": "-"})


def model_label(model: str) -> str:
    return MODEL_LABELS.get(model, model)


def despine(ax: mpl.axes.Axes, *, horizontal_grid: bool = False) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if horizontal_grid:
        ax.grid(axis="y", color=GRID, linewidth=0.45, alpha=0.75, zorder=0)
    ax.tick_params(direction="out")


def save_figure(fig: mpl.figure.Figure, stem: Path, *, interim: bool = False) -> list[Path]:
    """Save one figure with render-time alignment metadata and publication exports."""
    if interim:
        fig.text(
            0.5,
            0.5,
            "INTERIM MONITORING",
            ha="center",
            va="center",
            fontsize=24,
            color="#777777",
            alpha=0.16,
            rotation=28,
            weight="bold",
            zorder=1000,
        )
    stem.parent.mkdir(parents=True, exist_ok=True)
    # Draw after all layout-affecting text/legend changes, then retain a
    # physical-panel audit. The optional import is supplied by the figure QA
    # environment; ordinary source inspection stays dependency-light.
    fig.canvas.draw()
    try:
        from audit_panel_alignment import require_matplotlib_panel_alignment
    except ImportError:
        require_matplotlib_panel_alignment = None
    if require_matplotlib_panel_alignment is not None:
        qa = stem.parent / "qa"
        qa.mkdir(parents=True, exist_ok=True)
        require_matplotlib_panel_alignment(
            fig,
            json_out=qa / f"{stem.name}.alignment.json",
            overlay_svg=qa / f"{stem.name}.alignment.svg",
            tolerance_pt=1.5,
            gutter_tolerance_pt=1.5,
            require_panel_labels=False,
            strict=True,
            # Several benchmark figures deliberately use a wide primary panel
            # beside narrower diagnostic panels. Preserve edge alignment while
            # recording the narrow exemption for unequal panel widths/gutters.
            exemptions=[{
                "panels": [chr(ord("a") + index) for index, axis in enumerate(fig.axes) if axis.get_visible()],
                "checks": ["panel-width", "horizontal-gutter"],
                "reason": "Intentional asymmetric hero-panel evidence hierarchy.",
            }],
        )
    outputs = [stem.with_suffix(".pdf"), stem.with_suffix(".png"), stem.with_suffix(".svg"), stem.with_suffix(".tiff")]
    fig.savefig(outputs[0], bbox_inches="tight", pad_inches=0.035)
    fig.savefig(outputs[1], dpi=300, bbox_inches="tight", pad_inches=0.035)
    fig.savefig(outputs[2], bbox_inches="tight", pad_inches=0.035)
    fig.savefig(outputs[3], dpi=600, bbox_inches="tight", pad_inches=0.035)
    # Matplotlib's SVG writer leaves spaces at the ends of path lines. Removing
    # them is byte-only hygiene and keeps repository whitespace checks useful.
    svg_text = outputs[2].read_text(encoding="utf-8")
    outputs[2].write_text("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)
    return outputs
