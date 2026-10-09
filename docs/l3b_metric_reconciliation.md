# L3b and predecessor metric reconciliation

The sole current definition of `max_steps_reached` is: a run reaches the
runner's 40 completed-tool-call cap and records the independent
`max_steps_reached` flag. Its denominator is the explicitly named run cohort;
provider errors are included only when the cohort is the original raw cohort,
and replacements are used only in the replacement-inclusive cohort.

| Historical number | Cohort / denominator | Provider-error treatment | Flag status |
|---|---|---|---|
| B4 6/36 | Original B3/S5 raw 36 runs | Includes the eight historical provider errors in denominator; none were max-step | Reconstructed from terminal path before the independent flag |
| B5 3/36 | B3/S5 non-errors plus eight fresh replacements | The eight historical provider errors are removed and replaced; no provider errors remain | New independent flag |
| dev-diagnose 2/18 | Original B3/S5 six dev-diagnose tasks × three repeats | No replacement runs; original cohort only | Reconstructed from terminal path |
| L3b baseline 7/36 | Completed dev-validate baseline condition | No provider errors | New independent flag |
| L3b condition 5/36 | Completed dev-validate L3b condition | No provider errors | New independent flag |

These quantities are descriptive counts from different cohorts, not estimates
to pool or compare as if they came from one common denominator.

## Outcome and behavior reconstruction

For the L3b revision, abnormal exits (`provider_error`, `timeout`, context,
max-step) are classified first. Normal completions are then evaluated using
compile and frozen-verifier results. `final_empty` is independent behavior,
including among runs whose verifier passes. The previous `empty_termination`
field is preserved unmodified as `legacy_outcome` in the revised data.

## Analysis status

Pre-registered items: L3b trigger count, post-trigger validation, max-step
rate, and descriptive pass/partial reporting. Post-hoc exploratory items:
outcome reconstruction, final-empty cross-tabs, write-only replay to call 32,
the A-layer negative control, and task-paired bootstrap of incremental partial
scores. Wilson intervals are only single-proportion uncertainty intervals; no
Wilson interval is used as a condition-difference test.
