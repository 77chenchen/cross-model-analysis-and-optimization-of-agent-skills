# D5 qwen3.5:9b pilot v0/v1 comparison

This is a one-repetition-per-condition calibration comparison on four frozen
pilot tasks. Each condition used a fresh workspace, exact model ID
`qwen3.5:9b`, the same SoC provider, and runner commit `2339adf`; the planned
difference was only the injected skill version.

| Task | v0 verifier | v1 verifier | v0 actions | v1 actions |
|---|---:|---:|---:|---:|
| A03 record deduplication | fail | fail | 33 | 8 |
| A05 version parser | fail | fail | 13 | 20 |
| B03 duplicate audit | fail | fail | 37 | 15 |
| B05 date validation | fail | fail | 21 | 9 |

Primary outcome: v0 passed 0/4 and v1 passed 0/4. Every trajectory ended in
`turn.completed`; runner exit `1` denotes the external verifier's valid fail
outcome, not an infrastructure interruption.

No efficacy conclusion follows: there is one stochastic run per condition,
all outcomes are pilot-only, and the comparison has no independent blinded
annotation. Action counts changed, but are descriptive process signals rather
than evidence of improvement. The next step is to inspect v1 trajectories,
revise only through a pre-specified intervention process if justified, then
use more repetitions before formal analysis.
