"""Reusable annotations, intervals, heatmaps, and visual-QA helpers."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Callable, Iterable, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from colorspacious import cspace_convert
from PIL import Image, ImageDraw, ImageFont

from analysis.style import INK, MUTED


def panel_label(ax: mpl.axes.Axes, label: str, *, x: float = -0.12, y: float = 1.04) -> None:
    ax.text(x, y, f"({label})", transform=ax.transAxes, ha="left", va="bottom", fontsize=9, weight="bold")


def direct_label(ax: mpl.axes.Axes, x: float, y: float, text: str, **kwargs: object) -> None:
    defaults = {"ha": "left", "va": "center", "fontsize": 6.7, "color": INK, "clip_on": False}
    defaults.update(kwargs)
    ax.text(x, y, text, **defaults)


def interval_point(
    ax: mpl.axes.Axes,
    y: float,
    estimate: float,
    low: float,
    high: float,
    *,
    color: str,
    marker: str = "o",
    open_marker: bool = False,
    zorder: int = 4,
) -> None:
    ax.plot([low, high], [y, y], color=color, linewidth=1.15, solid_capstyle="round", zorder=zorder - 1)
    ax.plot([low, low], [y - 0.045, y + 0.045], color=color, linewidth=0.7, zorder=zorder - 1)
    ax.plot([high, high], [y - 0.045, y + 0.045], color=color, linewidth=0.7, zorder=zorder - 1)
    ax.plot(
        estimate,
        y,
        marker=marker,
        markerfacecolor="white" if open_marker else color,
        markeredgecolor=color,
        markeredgewidth=0.9,
        linestyle="none",
        zorder=zorder,
    )


def annotated_heatmap(
    ax: mpl.axes.Axes,
    matrix: np.ndarray,
    row_labels: Sequence[str],
    col_labels: Sequence[str],
    *,
    cmap: str = "cividis",
    vmin: float | None = None,
    vmax: float | None = None,
    percent: bool = False,
    decimals: int = 0,
    annotation_size: float = 5.8,
) -> mpl.image.AxesImage:
    values = np.asarray(matrix, dtype=float)
    finite = values[np.isfinite(values)]
    lower = float(np.min(finite)) if vmin is None and finite.size else (vmin or 0.0)
    upper = float(np.max(finite)) if vmax is None and finite.size else (vmax or 1.0)
    if math.isclose(lower, upper):
        upper = lower + 1.0
    image = ax.imshow(values, cmap=cmap, vmin=lower, vmax=upper, aspect="auto", interpolation="nearest")
    ax.set_xticks(np.arange(len(col_labels)), labels=col_labels)
    ax.set_yticks(np.arange(len(row_labels)), labels=row_labels)
    ax.tick_params(length=0)
    normalizer = mpl.colors.Normalize(vmin=lower, vmax=upper)
    colour_map = mpl.colormaps[cmap]
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            value = values[i, j]
            if not np.isfinite(value):
                label = "–"
                rgba = (1, 1, 1, 1)
            else:
                label = f"{100 * value:.{decimals}f}%" if percent else f"{value:.{decimals}f}"
                rgba = colour_map(normalizer(value))
            luminance = 0.2126 * rgba[0] + 0.7152 * rgba[1] + 0.0722 * rgba[2]
            ax.text(j, i, label, ha="center", va="center", fontsize=annotation_size, color="white" if luminance < 0.48 else "#202020")
    for spine in ax.spines.values():
        spine.set_visible(False)
    return image


def bootstrap_interval(
    values: Iterable[float],
    statistic: Callable[[np.ndarray], float] = np.median,
    *,
    iterations: int = 5000,
    seed: int = 31010,
) -> tuple[float, float]:
    array = np.asarray(list(values), dtype=float)
    if array.size == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    samples = rng.choice(array, size=(iterations, array.size), replace=True)
    estimates = np.apply_along_axis(statistic, 1, samples)
    return tuple(float(x) for x in np.quantile(estimates, [0.025, 0.975]))


def simulate_cvd(source: Path, destination: Path, cvd_type: str) -> None:
    """Write a full-severity CVD preview without altering the source figure."""
    image = Image.open(source).convert("RGB")
    rgb = np.asarray(image, dtype=float) / 255.0
    specification = {"name": "sRGB1+CVD", "cvd_type": cvd_type, "severity": 100}
    simulated = np.clip(cspace_convert(rgb, specification, "sRGB1"), 0.0, 1.0)
    destination.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.uint8(np.round(simulated * 255))).save(destination, dpi=(300, 300))


def make_contact_sheet(images: Sequence[Path], destination: Path, *, columns: int = 3) -> None:
    thumbs: list[tuple[Path, Image.Image]] = []
    for path in images:
        image = Image.open(path).convert("RGB")
        image.thumbnail((720, 460), Image.Resampling.LANCZOS)
        thumbs.append((path, image.copy()))
    cell_w, cell_h = 750, 505
    rows = math.ceil(len(thumbs) / columns)
    sheet = Image.new("RGB", (cell_w * columns, cell_h * rows), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, (path, image) in enumerate(thumbs):
        row, col = divmod(index, columns)
        x = col * cell_w + (cell_w - image.width) // 2
        y = row * cell_h + 25
        sheet.paste(image, (x, y))
        draw.text((col * cell_w + 12, row * cell_h + 7), path.stem, fill="#252525", font=font)
    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination, dpi=(180, 180))
