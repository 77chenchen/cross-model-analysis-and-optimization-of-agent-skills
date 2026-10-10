# B5-r2 human-vs-LLM agreement protocol

Date: 2026-10-10. Committed before human annotation starts; it affects no S7
condition or execution asset.

Human review uses failure modes only (`stage_events: []`). The eight
substantive binary labels are `premature_implementation`,
`repeated_exploration`, `ineffective_debugging_loop`,
`insufficient_validation`, `missed_constraint`, `premature_completion`,
`tool_misuse`, and `file_corruption`. `none_observed` means all eight are
absent. `unscorable` is retained and counted but excludes that packet from
primary agreement. `empty_termination` is a mechanical terminal-log flag,
never a human label or κ input.

The paired unit is a packet; comparator is the frozen blinded LLM-judge label.
For every substantive label, report binary Cohen's kappa when estimable, macro
average of estimable label kappas, exact eight-label set-match rate, per-label
PABAK (`2 × observed binary agreement − 1`), and macro PABAK. Use 10,000
packet-level bootstrap resamples, fixed seed `20261010`, and percentile 95%
intervals for every reported statistic.

If either rater has zero variance for a label, its κ is `not estimable`, is
excluded from macro κ, and PABAK remains reported. In bootstrap samples,
non-estimable κ replicates are omitted and their number reported; if none are
estimable the interval is `not estimable`. Exact-match and PABAK remain defined
for scorable packets. No κ value, interval, or agreement result is calculated
or written before a complete human JSONL passes validation.

Any later report must state: there is one human annotator, who is the
researcher; this is human-vs-LLM-judge agreement rather than independent
inter-annotator reliability; blinding is incomplete because task content and
behavioral traces reveal context; and the fixed 24-packet sample is small, so
agreement estimates and bootstrap intervals are imprecise.
