# B3 S5 r2 dev baseline

Date: 2026-10-08
Status: completed; r2 cohort only.

The pre-registered r2 target, `qwen3.5:9b`, ran frozen Skill v0 on every
locked pilot/dev task three times (36 fresh workspaces). Temperature 0.5 and
seed 20261008 were transmitted; seed transport acceptance is recorded but the
provider did not echo a deterministic seed. No CLI run, GPT anchor, or test
task is pooled into this result.

| Analysis view | Runs | Passes | Pass rate | Mean partial |
|---|---:|---:|---:|---:|
| Including known-defective A04 | 36 | 8 | 0.222 | 0.738 |
| Excluding A04 | 33 | 8 | 0.242 | 0.784 |

The exclusive legacy outcomes are 8 pass, 15 `empty_termination`, 8
`provider_error`, and 5 `verifier_fail`. Nonexclusive flags are retained in
the accompanying summary rather than collapsed into one diagnosis. In
particular, a partial score can remain high despite an empty final or provider
error because the agent may have edited enough implementation behavior before
the terminal event.

This is a new r2 baseline, not a comparison to legacy CLI S5: B2 established
that those runner paths are not exchangeable. It supplies the calibrated weak
target baseline for later, separately authorized dev-only intervention work;
it does not justify a skill intervention claim by itself.

Task-level values are in `data/b3_s5_r2_results/task_summary.csv`, with both
A04 views and flag counts in `summary.json`.
