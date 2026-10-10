# Verifier-pass erratum for retained r2 cohorts

Date: 2026-10-10. This is a read-only analysis correction. It does not alter any task, verifier, fixture, skill, parser, prompt, schedule, runner, or completed artifact. Historical single-label outcome tables remain intact and are now explicitly **legacy**. The source data and script are [`verifier_pass_erratum_20261010.json`](../data/verifier_pass_erratum_20261010.json) and [`audit_verifier_pass_erratum.py`](../harness/audit_verifier_pass_erratum.py).

## Correct rule

The primary pass numerator is the frozen `verifier.json` field `passed: true`. It is independent of final-message content. A `provider_error` is excluded from the primary denominator; the sensitivity denominator includes it as a non-pass. Legacy pass is `legacy_outcome_category == "pass"` (or the historic `outcome_category` where that predecessor field is absent). It is preserved for auditing only.

| Cohort | Scheduled | Provider errors | Primary denominator | Legacy pass | Verifier pass | Difference |
|---|---:|---:|---:|---:|---:|---:|
| S4 r2 calibration | 180 | 5 | 175 | 102 (58.3%) | 110 (62.9%) | +8 |
| S5 r2 original | 36 | 8 | 28 | 8 (28.6%) | 18 (64.3%) | +10 |
| S5 eight replacements | 8 | 0 | 8 | 4 (50.0%) | 6 (75.0%) | +2 |
| S5 replacement-inclusive effective cohort | 36 | 0 | 36 | 12 (33.3%) | 24 (66.7%) | +12 |
| S6 L3b dev-validate, both conditions | 72 | 0 | 72 | 25 (34.7%) | 48 (66.7%) | +23 |
| S7 completed snapshot (2026-10-10 02:02:56 UTC) | 353 | 7 | 346 | 106 (30.6%) | 187 (54.0%) | +81 |

The S5 replacement-inclusive cohort excludes the eight immutable original provider-error records and includes the eight designated replacements; it is therefore again 36 records. No original record is overwritten or pooled into that effective denominator.

## S4 recalibration

The descriptive eligibility rule is 20%--80%, using the verifier-pass primary rate. It still selects qwen3.5:9b, and only qwen3.5:9b.

| Model | Primary denominator | Legacy pass | Verifier pass | Eligible at 20%--80%? |
|---|---:|---:|---:|---|
| gemma4:26b | 36 | 29 (80.6%) | 30 (83.3%) | no, ceiling |
| llama3.1:8b | 36 | 0 (0.0%) | 0 (0.0%) | no, floor |
| qwen3-coder-next | 36 | 30 (83.3%) | 30 (83.3%) | no, ceiling |
| qwen3.5:9b | 32 | 11 (34.4%) | 18 (56.3%) | **yes** |
| qwen3.8:27b | 35 | 32 (91.4%) | 32 (91.4%) | no, ceiling |

The selection decision is unchanged, so S7 remains locked and unmodified. The interpretation changes materially: qwen's r2 calibration was not a near-floor 34.4% system but a 56.3% verifier-pass system. Statements that used the old rate to motivate a floor effect or quantify its severity are withdrawn. The calibration is still descriptive and was not a cross-model ranking.

## S6 L3b dev-validate, reconstructed with verifier pass

| Condition / layer | Runs | Legacy pass | Verifier pass |
|---|---:|---:|---:|
| Baseline, all | 36 | 8 (22.2%) | 22 (61.1%) |
| L3b, all | 36 | 17 (47.2%) | 26 (72.2%) |
| Baseline A: reached call 32 | 9 | 1 (11.1%) | 2 (22.2%) |
| L3b A: reached call 32 / trigger occurred | 12 | 2 (16.7%) | 6 (50.0%) |
| Baseline B: ended before call 32 | 27 | 7 (25.9%) | 20 (74.1%) |
| L3b B: ended before call 32 | 24 | 15 (62.5%) | 20 (83.3%) |

The A-layer no-reminder negative control has 0/9 replayable partial-score increases and 2/9 verifier passes. In L3b's 12 triggered trajectories, 9/12 subsequently issued a validation command, 2/10 replayable trajectories increased partial score, and 6/12 verifier-passed. The two non-scoreable triggered records are retained; the partial-increase denominator is 10 solely because their replay/final partial pair is unavailable.

This reverses the scale of the earlier legacy-pass presentation, but it does not establish an L3b effect: reaching call 32 is a post-randomization, trajectory-dependent stratum; the A/B composition differs; and write-only replay does not reproduce `run_command` side effects. Updated wording is: *the fixed reminder was observed in 12 trajectories; its subsequent validation, partial-change, and verifier-pass quantities are descriptive mechanism observations in a small selected stratum.*

## S7 partial snapshot and provider-error clarification

The following is an operational snapshot only, not formal S7 analysis.

| Model / condition | Scheduled complete | Provider errors | Primary verifier pass | Legacy pass |
|---|---:|---:|---:|---:|
| qwen3.5:9b C0 | 90 | 2 | 43/88 (48.9%) | 19/88 (21.6%) |
| qwen3.5:9b C1 | 90 | 2 | 45/88 (51.1%) | 20/88 (22.7%) |
| qwen3.5:9b v1 | 60 | 0 | 38/60 (63.3%) | 24/60 (40.0%) |
| qwen3.5:9b L3b | 90 | 3 | 46/87 (52.9%) | 28/87 (32.2%) |
| gemma4:26b C0 | 11 | 0 | 6/11 (54.5%) | 6/11 (54.5%) |
| gemma4:26b C1 | 12 | 0 | 9/12 (75.0%) | 9/12 (75.0%) |

The older qwen snapshot reported one C0 and one C1 `provider_error` because it tabulated a single legacy category. The independent flag correctly counts two in each condition: in both conditions, one is categorised as `provider_error` and the other as `timeout`; all four retain `provider_error: true`. Every one of these four records nevertheless has a verifier result because the verifier is run against the retained workspace. For C0, one provider-error record verifier-passes and one fails; for C1, both fail. They are excluded from the primary numerator and denominator, so C0 is 43/88 rather than 44/88; the provider-as-non-pass sensitivity is 43/90. C1 is 45/88, with sensitivity 45/90. This is why `pass + verifier_fail = n` can be true in a complete-verifier table while `provider_error` is nonzero: provider error and verifier result are independent flags, not competing outcomes.

## S7 formal-analysis implementation check

The locked execution plan already specifies a provider-error exclusion but did not explicitly state that its pass source is `verifier.json.passed`. The current [`summarize_s7.py`](../harness/summarize_s7.py) instead derives pass from the `outcome` column emitted by `monitor_s7_metrics.py`, which in turn is `outcome_category`. This is non-compliant with the corrected primary-outcome rule. Neither file is changed here: the S7 execution lock and its live run are not modified mid-batch. Before formal analysis after run completion, a versioned, reviewable post-lock analysis patch must read verifier `passed` directly and record its own hash; no formal S7 result has been produced by the legacy summarizer.

The revised process-hypothesis document is [`s7_process_hypothesis_revision_20261010.md`](s7_process_hypothesis_revision_20261010.md). It makes validation-after-last-edit the sole primary process hypothesis, demotes rewrite/loop directions to secondary descriptive hypotheses, declares the explicit-reference prediction, and restricts v1 versus C1 to task-paired `test_in` using verifier pass.
