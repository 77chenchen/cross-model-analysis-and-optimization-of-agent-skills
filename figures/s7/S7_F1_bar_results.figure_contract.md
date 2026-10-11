# Figure contract: S7 core results bar chart

- **Core conclusion:** Across the formal S7 model panel, C0 and C1 verifier-pass estimates can be compared directly, with their within-condition Wilson intervals visible.
- **Results-level question:** How do C0 and C1 pass rates differ across the six model configurations on the full held-out task pool?
- **Archetype:** quantitative single-panel comparison.
- **Output:** vector PDF and SVG plus 300-dpi PNG for README rendering.
- **Sample unit:** one completed run; `provider_error_protocol` rows are excluded from each displayed primary denominator.
- **Statistics:** bars show `verifier.json.passed / primary_n`; error bars are 95% Wilson intervals for each individual condition, not tests of C1 minus C0.
- **Source:** `results/tables/s7/S7_T1_model_condition_summary.csv`, `split=all` and conditions C0/C1.
- **Visual encoding:** each model uses a vendor-family color; C0 is rendered as a light all-vector gradient and C1 as a saturated all-vector gradient. Colored circles are original family monograms, not vendor trademarks or logos.
