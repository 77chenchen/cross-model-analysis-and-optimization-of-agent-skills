#!/usr/bin/env python3
"""Render a dependency-free static SVG figure from S5 summaries."""
import csv
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "data/s5_results"
stages = list(csv.DictReader((RESULTS / "s5_stage_proportions.csv").open()))
failures = [r for r in csv.DictReader((RESULTS / "s5_failure_mode_rates.csv").open()) if r["failure_mode"] != "none_observed"]
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="560" viewBox="0 0 1200 560">', '<style>text{font-family:Arial,sans-serif;fill:#1f2937}.title{font-size:20px;font-weight:bold}.label{font-size:12px}.small{font-size:11px}</style>', '<rect width="1200" height="560" fill="white"/>']
parts.append('<text x="80" y="42" class="title">Blinded judge stage proportions</text><line x1="80" y1="430" x2="560" y2="430" stroke="#374151"/><line x1="80" y1="80" x2="80" y2="430" stroke="#374151"/>')
for i, row in enumerate(stages):
    value = float(row["proportion"]); x = 100 + i * 64; height = value * 1000
    parts.append(f'<rect x="{x}" y="{430-height:.1f}" width="40" height="{height:.1f}" fill="#4C78A8"/><text x="{x+20}" y="452" class="small" text-anchor="end" transform="rotate(-45 {x+20} 452)">{escape(row["stage"])}</text><text x="{x+20}" y="{422-height:.1f}" class="small" text-anchor="middle">{value:.2f}</text>')
parts.append('<text x="650" y="42" class="title">Blinded judge failure-mode occurrence</text><line x1="650" y1="80" x2="650" y2="430" stroke="#374151"/>')
for i, row in enumerate(failures):
    value = float(row["rate"]); y = 100 + i * 45; width = value * 1800
    parts.append(f'<text x="640" y="{y+17}" class="small" text-anchor="end">{escape(row["failure_mode"].replace("_", " "))}</text><rect x="660" y="{y}" width="{width:.1f}" height="25" fill="#E45756"/><text x="{670+width:.1f}" y="{y+18}" class="small">{value:.2f}</text>')
parts.append('</svg>')
(RESULTS / "s5_trajectory_patterns.svg").write_text("\n".join(parts) + "\n")
