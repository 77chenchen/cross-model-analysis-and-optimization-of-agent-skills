# S7 formal result summary

Date: 2026-10-11. Analysis version: `s7-formal-v1.0.0`; primary outcome:
`verifier.json.passed`; paired bootstrap unit: task; draws: 10,000; seed:
701009.

## Integrity and denominators

All 870 scheduled run directories contain `metadata.json` and
`verifier.json`, and all 870 verifiers expose a Boolean `passed` field. Five
qwen3.5:9b retry-exhausted transport failures are excluded from the primary
denominator and counted as failures in the scheduled-run sensitivity view.
Hard timeout and max-step runs remain denominator failures. GPT has no active
provider errors after the owner-authorized overwrite described in
`s7_postcompletion_gpt_rerun_deviation_20261011.md`.

Three malformed event lines occur in one
`qwen3.8:27b/test_out_c03_consolidate/C0/r3` trajectory. They are skipped only
for process metrics and listed in the analysis manifest; its frozen verifier
outcome is unaffected. GPT process metrics are not aligned to r2 and are
reported as unavailable.

## Core C0/C1 results

| model | C0 verifier pass | C1 verifier pass | task-paired C1-C0 | paired bootstrap 95% |
|---|---:|---:|---:|---:|
| qwen3.5:9b | 43/89 (48.3%) | 45/89 (50.6%) | +1.9 pp | [-6.9, +10.6] pp |
| gemma4:26b | 33/54 (61.1%) | 36/54 (66.7%) | +5.6 pp | [0.0, +14.8] pp |
| qwen3.8:27b | 45/54 (83.3%) | 46/54 (85.2%) | +1.9 pp | [-3.7, +7.4] pp |
| qwen3-coder-next | 33/54 (61.1%) | 34/54 (63.0%) | +1.9 pp | [-7.4, +13.0] pp |
| llama3.1:8b | 0/54 (0.0%) | 0/54 (0.0%) | 0.0 pp | [0.0, 0.0] pp |
| gpt-5.6-sol† | 44/54 (81.5%) | 44/54 (81.5%) | 0.0 pp | [-5.6, +5.6] pp |

† Uncontrolled Codex reference anchor; descriptive only.

The controlled model panel does not show a consistent C1 advantage across
models or splits. The point differences are small relative to task-level
uncertainty, and llama remains a complete floor. `test_in_b11_bucket` is the
only all-zero controlled core task; no task is an all-one ceiling. Excluding
`test_in_b09_phone` changes qwen's all-task estimate from +1.9 to +4.4 points
and its test-in estimate from +5.0 to +9.1 points. That view is sensitivity
analysis only: the task has clustered historical timeouts but no demonstrated
verifier defect.

## Preregistered process hypotheses

The qwen monitoring observation that generated the validation hypothesis
replicates within qwen: C1 minus C0 validation-after-final-edit is -25.0 points
at the task level, bootstrap interval [-38.9, -9.4]. It does not independently
generalize. The corresponding differences are +11.1 points for gemma, 0.0 for
qwen3.8, -1.9 for qwen-coder, and +38.9 for llama. GPT has no aligned r2
process measure.

Explicit C1 skill-reference rates are 34.8% for qwen3.5, 70.4% for gemma,
0.0% for qwen3.8, 0.0% for qwen-coder, and 1.9% for llama. The preregistered
prediction of monotonic increase with model capability is not supported by
this locked parser. Behavioral activation remains a separate process metric,
not an activation stratum.

## Exploratory conditions

v1 is explicitly referenced in 48/60 qwen runs (80.0%). Relative to C1 on the
12 test-in tasks, validation-after-final-edit rises by 45.0 task-level points
[26.7, 63.3], while verifier-pass difference is effectively 0.0 points
[-11.7, 13.3]. Thus the mechanism is observable, but no corresponding outcome
improvement is observed. This is descriptive, not an efficacy claim.

L3b triggers in 11/87 protocol-usable runs. Its unconditional task-paired
pass difference from C1 is +3.1 points [-4.4, 11.9]. In the post-assignment A
layer (at least 32 calls), C1 passes 3/12 and L3b 2/11; in the B layer, C1
passes 42/77 and L3b 44/76. These layer differences cannot identify a reminder
effect and are reported only as mechanism diagnostics.

## Interpretation boundary

The formal evidence supports neither a general claim that v0 improves coding
success nor a general claim that written skills never help. It shows small,
model- and split-dependent pass-rate changes in this synthetic task pool, one
clear qwen process change, and no v1 outcome change despite higher activation
and validation. Under the preregistered rule requiring mechanism activation
plus observable outcome improvement, v1 does not meet the threshold; L3b is
too rarely triggered and post-assignment-stratified to support that judgment.

Machine-readable results are under `results/tables/s7/`; figures are under
`figures/s7/`; hashes and parse anomalies are recorded in
`results/s7/analysis_manifest.json`.
