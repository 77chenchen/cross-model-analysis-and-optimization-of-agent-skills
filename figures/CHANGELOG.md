# Figure redesign changelog

Date: 2026-10-10. This change is visualization-only. It does not change data,
analysis conclusions, verifier-pass-v2.0.0, or any frozen experiment asset.

| Figure | Previous primary form | Publication form | Main visual changes | CSV SHA-256 unchanged |
|---|---|---|---|---|
| F1 | Single pass-rate bar chart | Three-panel forest/process/flag figure | Wilson intervals, direct n, calibration band, median/IQR trajectory context, annotated flag heatmap | Yes |
| F2 | Grouped bars | Slope chart + delta lollipop | Direct endpoint/delta labels and definition-focused comparison | Yes |
| F3 | Single flag bar chart | Flag heatmap + marginal dumbbell | Non-exclusive flags remain separate; pass/final-empty marginals are not misrepresented as a joint table | Yes |
| F4 | Write-share bars | Five small-multiple action heatmaps | Full read/write/command/other composition over trajectory deciles | Yes |
| F5 | Median-steps bar chart | Four process point/interval panels + run strips | Two validation definitions, rewrite/loop rates, relative first-edit position | Yes |
| F6 | Median-turns bar chart | Three aligned summary point panels | Turns, calls/turn, blind-write rate; n labeled directly | Yes |
| F7 | Input-token bars | Thin 100% composition bars + log-total point panel | Direct segment labels; only approved stacked-bar use | Yes |
| F8 | Transition-count bars | Two-panel alluvial transition view | Call-32 states and final transitions shown with direct counts | Yes |
| F9 | PABAK bars | κ/PABAK forest + 2×2 count heatmap | Bootstrap κ intervals, not-estimable labels, raw agreement counts | Yes |

## Frozen CSV hashes

| CSV | SHA-256 |
|---|---|
| `F1_dev_pass_rates.csv` | `333df019a9924cef72e85173a187e19e0d77d8777d64d9d530d09f6f8e1cfac0` |
| `F2_legacy_vs_verifier.csv` | `2f1e08fcb903bc73b770bd59644f0844422f2dbe349b88d67af3e369193ff457` |
| `F3_outcome_flags.csv` | `fc098c1dbffc1d98c2160485772ac3febd6d169ef5df90565c74774a2ce38e01` |
| `F4_actions_by_decile.csv` | `b1cb94270f28b88b525f5f6bc706e733cd85b8003a422351c485741ee5d20f8a` |
| `F5_process_metrics_raw.csv` | `679ca16de9f2335cd2c24dd3e9c546868c5a8732c0e9f96487470ab1808d820a` |
| `F5_process_metrics_summary.csv` | `6f3c10bb33f8ecf139592a0e9f2e5fc7fe3a573cdcb82d06e0ad7173e607c626` |
| `F6_turns_calls_blindwrite.csv` | `540cad3fbc7f639fbb12d21d4d8ef014593f1778bb2dd90bf5998da4a522e9be` |
| `F7_token_composition.csv` | `573d848ec4b9b8431fe5710492a7096455eac498b4323ab8803a93f6c1fe7b61` |
| `F8_l3b_transitions.csv` | `fbfe5d9acdd69db84927d0195f170898ae701956948f5f4c38469eb03eff8a34` |
| `F9_kappa_pabak.csv` | `2f632e61b8b43f658cc35a41f7d6cc4eeb07454193b8834a5f1de2a0a3186585` |

The same hashes are enforced by `analysis/test_figures.py` and embedded in
`figures/panel_manifest.json`.
