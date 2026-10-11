# Formal S7 figures

All figures use `verifier.json.passed` through the gated formal analysis. GPT-5.6 Sol is always an uncontrolled Codex reference anchor.

- `S7_F1_main_results`: core pass rates, aligned r2 process depth, and non-exclusive outcome flags.
- `S7_F2_paired_differences`: task-paired C1-minus-C0 differences with 10,000-draw bootstrap intervals.
- `S7_F3_task_heatmap`: within-task repetition pass rates by model and core condition.
- `S7_F4_process_mechanisms`: validation and explicit-reference mechanism measures.
- `S7_F5_exploratory`: qwen v1/L3b descriptive comparisons and call-32 strata.

Each figure is exported as PDF, SVG, and 300-dpi PNG. Plotting data are under `figures/s7/data/`; hashes are in `figure_manifest.json`.
