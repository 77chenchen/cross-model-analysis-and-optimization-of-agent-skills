# Publication figures

All data-bearing marks are rendered by `analysis/make_figures.py` from the
immutable CSV files in `figures/data/`. The script checks every CSV SHA-256
before and after rendering and never rewrites a CSV. Outputs are double-column
width (7.0 in), with vector PDF/SVG, 300 dpi PNG, and 600 dpi TIFF variants.
Typography,
model/condition encodings, and export settings are centralized in
`analysis/style.py`; reusable panel/interval/heatmap helpers are in
`analysis/figure_templates.py`.

These figures use completed pre-S7 dev/calibration data only. They contain no
formal S7 result. `--formal-s7` remains blocked until `STATUS.md` is 870/870 and
the verifier-pass-v2 patch hash matches. The optional Figure 1 radar is not
generated because the frozen pre-S7 CSVs do not contain five reliable axes.

Reproduce with:

```bash
python3.13 -m venv .venv-figures
.venv-figures/bin/python -m pip install -r analysis/requirements-figures.txt
.venv-figures/bin/python -m analysis.make_figures
.venv-figures/bin/python -m unittest analysis.test_figures -v
```

The Python environment requires matplotlib, NumPy, Pillow, and colorspacious.
`figures/qa/` contains full-severity deuteranomaly and protanomaly simulations,
panel-alignment overlays, PDF text-size audits, and collision-audit reports.

## Figure 1 — Dev benchmark and trajectory context

- **Panels:** (a) Cleveland/forest plot of S4 dev calibration verifier-pass
  rates, ordered by rate, with Wilson 95% intervals and the 20–80% calibration
  band; (b) median/IQR tool calls and median assistant turns; (c) heatmap of
  `final_empty`, `max_steps_reached`, and timeout flags.
- **Source:** `F1_dev_pass_rates.csv`, `F5_process_metrics_raw.csv`,
  `F6_turns_calls_blindwrite.csv`, and `F3_outcome_flags.csv` at source snapshot
  `d5479a28b3a07ecc6f7dc559abc65ebae4536690`.
- **n:** pass-rate panel displays the per-model protocol denominator directly;
  process panels use the n recorded in their source CSVs.
- **Scope note:** the frozen pre-S7 CSV has only v0 dev calibration, so this
  version does not invent C0/C1/v1 points or a GPT reference-anchor row. The
  condition dumbbell remains a gated post-S7 output.

## Figure 2 — Pass-outcome definition reconciliation

- **Panels:** (a) slope chart from legacy outcome pass to
  `verifier.json.passed`; (b) verifier-minus-legacy rate change.
- **Source:** `F2_legacy_vs_verifier.csv`, four completed pre-S7 queues.
- **n/interval:** denominators are stored in the CSV; this definitional audit
  does not attach inferential intervals.

## Figure 3 — Non-exclusive run flags

- **Panels:** (a) model × flag annotated heatmap; (b) verifier-pass and
  final-empty marginal point comparison.
- **Source:** `F3_outcome_flags.csv`, 36 scheduled S4 runs per model.
- **Scope note:** the immutable CSV contains marginals, not the joint 2×2 cell
  counts, so panel (b) is explicitly marginal rather than a reconstructed
  cross-tabulation.

## Figure 4 — Trajectory action structure

- **Panels:** one annotated action-type × trajectory-decile heatmap per model;
  stronger calibration models occupy the first row and the weak/lower-bound
  models the second row.
- **Source:** `F4_actions_by_decile.csv`; tool calls classified mechanically as
  read, write, command, or other.
- **n/interval:** cells are within-model, within-decile proportions; no interval
  is asserted for this descriptive composition view.

## Figure 5 — Mechanical process metrics

- **Panels:** validation under the intent and successful-command definitions;
  any whole-file rewrite; any repeated-action loop; relative first-edit
  position.
- **Source:** `F5_process_metrics_raw.csv`.
- **Summary:** points are run-level observations. Binary panels show run
  proportions; first-edit position shows the median. Error bars are 5,000-draw
  bootstrap 95% intervals with seed 31010. The frozen CSV has no task ID, so
  these are run-level descriptive intervals, not task-paired inference.

## Figure 6 — Assistant/tool-call structure

- **Panels:** horizontal summary bars for assistant turns/run, tool
  calls/assistant turn, and blind-write fraction. These frozen inputs provide
  one summary per model, so bars are clearer than pseudo-distribution dots.
- **Source:** `F6_turns_calls_blindwrite.csv`, dev-diagnose post hoc summaries,
  n=18 per model.
- **Scope note:** only medians/rates were frozen in the CSV, so an ECDF or violin
  would fabricate an unavailable distribution; the figure uses summary points.

## Figure 7 — Token composition and scale

- **Panels:** (a) thin 100% horizontal token-composition bars with direct labels
  (the only stacked bars in the figure set); (b) total recorded median tokens on
  a logarithmic scale.
- **Source:** `F7_token_composition.csv`, n=36 per model.
- **Definition:** totals are sums of the frozen median component fields and are
  descriptive rather than a median of per-run totals.

## Figure 8 — L3b call-32 state transitions

- **Panels:** paired transition-count bar charts for baseline and L3b A-layer
  runs; bars separate already-passed, newly-passed, final non-pass, and any
  unclassified runs without implying unavailable individual-level flows.
- **Source:** `F8_l3b_transitions.csv` from the S6 replay audit.
- **n/interpretation:** node and conversion counts are printed directly. The
  diagram is descriptive and is not an effect estimate or significance test.

## Figure 9 — Human–judge agreement

- **Panels:** (a) forest plot of Cohen's κ with bootstrap 95% intervals and
  PABAK point estimates, with raw agreement counts; (b) annotated human × judge
  2×2 counts for every label.
- **Source:** `F9_kappa_pabak.csv`, 24 blinded packets. Labels with zero marginal
  variance show κ as not estimable and retain PABAK/raw counts.

## QA artifacts

- `contact_sheet.png`: all nine main PNGs.
- `qa/*_deuteranopia.png`: full-severity deuteranomaly simulations.
- `qa/*_protanopia.png`: full-severity protanomaly simulations.
- `qa/*.alignment.{json,svg}`: final-layout alignment records and overlays.
- `qa/text/*.json`: final-PDF text-size reports (all text runs are at least 5 pt).
- `qa/collision/*.json`: collision audits. Figure 4 has only intentional
  heatmap-label/filled-cell warnings; every figure has zero blocking collisions.
- `panel_manifest.json`: panel counts, bootstrap settings, and frozen CSV hashes.
