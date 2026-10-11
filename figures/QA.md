# Figure QA record

Date: 2026-10-11. This record covers the visualization-only publication
refresh. It does not alter a CSV, the verifier-pass-v2.0.0 outcome definition,
or any frozen experimental asset.

## Evidence map

| Figure family | Question answered | Statistical status |
|---|---|---|
| F1 / S7_F1 | How do verifier-pass rates and basic trajectory context vary across models and conditions? | F1 is pre-S7 calibration; S7_F1 is formal, with the GPT row labelled as an uncontrolled reference. |
| F2 / S7_F2 | How does a pass-definition correction change rates, and what are task-paired C1 minus C0 differences? | F2 is a definitional audit; S7_F2 reports paired bootstrap intervals. |
| F3 / S7_F3 | Which non-exclusive run flags and task-level pass distributions occur? | Descriptive; flags are not collapsed into a single outcome. |
| F4--F7 / S7_F4 | How are actions, process measures, turn structure, and token use distributed? | Descriptive process evidence. |
| F8 / S7_F5 | What call-32 and exploratory strata are observed? | Descriptive only; not an effect estimate. F8 uses aggregate bars because individual-level flows are unavailable. |
| F9 | How closely do human and judge labels agree? | Agreement evidence with raw counts and intervals. |

## Render contract and checks

- Every data-bearing figure is generated in Python/matplotlib from its existing
  CSV inputs. No generated image was used for data marks.
- Final exports: editable vector PDF and SVG, 300 dpi PNG, and 600 dpi TIFF.
- `analysis.test_figures` verifies frozen CSV SHA-256 values, export presence,
  PNG resolution, multi-panel structure, and the stored collision/text audits.
- PDF text audit: 14/14 figures have no text runs below 5 pt.
- Collision audit: 14/14 figures have zero blocking findings. F4 has nine
  expected review-only warnings because numeric heatmap labels intentionally
  overlay their own filled cells; visual inspection confirmed no text-text
  collision or clipped label.
- Panel alignment audit: 12 figures pass; S7_F2 and S7_F3 are marked not
  applicable because they are intentionally single-panel evidence views. Wide
  hero-panel layouts have an explicit, recorded width/gutter exemption while
  retaining aligned panel edges.
- Color-vision simulations for deuteranopia and protanopia are in `qa/` for
  the pre-S7 set; their visual encodings also use marker shape and line style.

Re-run the full visual QA after changing a rendering function:

```bash
PYTHONPATH=/Users/wangqichen/.codex/skills/nature-figure/scripts \
  python -m analysis.make_figures
PYTHONPATH=/Users/wangqichen/.codex/skills/nature-figure/scripts \
  python -m analysis.make_s7_figures
python -m unittest analysis.test_figures -v
```
