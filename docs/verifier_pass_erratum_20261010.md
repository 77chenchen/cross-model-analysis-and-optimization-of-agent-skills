# Verifier-pass erratum for retained r2 cohorts

Date: 2026-10-10. This is a read-only analysis correction. It does not alter any task, verifier, fixture, skill, parser, prompt, schedule, runner, or completed artifact. Historical single-label outcome tables remain intact and are now explicitly **legacy**. The source data and script are [`verifier_pass_erratum_20261010.json`](../data/verifier_pass_erratum_20261010.json) and [`audit_verifier_pass_erratum.py`](../harness/audit_verifier_pass_erratum.py).

## Correct rule

The primary pass numerator is the frozen `verifier.json` field `passed: true`. It is independent of final-message content. A `provider_error` is excluded from the primary denominator; the sensitivity denominator includes it as a non-pass. Legacy pass is `legacy_outcome_category == "pass"` (or the historic `outcome_category` where that predecessor field is absent). It is preserved for auditing only.

| Cohort | Scheduled | Protocol provider errors | Primary denominator | Legacy pass | Verifier pass | Difference |
|---|---:|---:|---:|---:|---:|---:|
| S4 r2 calibration | 180 | 5 | 175 | 102 (58.3%) | 110 (62.9%) | +8 |
| S5 r2 original | 36 | 8 | 28 | 8 (28.6%) | 18 (64.3%) | +10 |
| S5 eight replacements | 8 | 0 | 8 | 4 (50.0%) | 6 (75.0%) | +2 |
| S5 replacement-inclusive effective cohort | 36 | 0 | 36 | 12 (33.3%) | 24 (66.7%) | +12 |
| S6 L3b dev-validate, both conditions | 72 | 0 | 72 | 25 (34.7%) | 48 (66.7%) | +23 |
| S7 completed snapshot (2026-10-10 02:19:28 UTC) | 362 | 5 (flag count: 7) | 357 | 113 (31.7%) | 194 (54.3%) | +81 |

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
| qwen3.5:9b C0 | 90 | 1 (flag count: 2) | 43/89 (48.3%) | 19/89 (21.3%) |
| qwen3.5:9b C1 | 90 | 1 (flag count: 2) | 45/89 (50.6%) | 20/89 (22.5%) |
| qwen3.5:9b v1 | 60 | 0 | 38/60 (63.3%) | 24/60 (40.0%) |
| qwen3.5:9b L3b | 90 | 3 | 46/87 (52.9%) | 28/87 (32.2%) |
| gemma4:26b C0 | 16 | 0 | 11/16 (68.8%) | 11/16 (68.8%) |
| gemma4:26b C1 | 16 | 0 | 11/16 (68.8%) | 11/16 (68.8%) |

The older qwen snapshot reported one C0 and one C1 `provider_error` because it tabulated a single legacy category. The independent flag counts two in each condition: in both, one is categorised as `provider_error` and the other as `timeout`; all four retain `provider_error: true`. The next section corrects the denominator treatment: a transport-exhaustion provider error is excluded, while a 20-minute runner timeout is a completed non-pass and stays in the denominator.

## S7 formal-analysis implementation check

The locked execution plan already specifies a provider-error exclusion but did not explicitly state that its pass source is `verifier.json.passed`. The current [`summarize_s7.py`](../harness/summarize_s7.py) instead derives pass from the `outcome` column emitted by `monitor_s7_metrics.py`, which in turn is `outcome_category`. This is non-compliant with the corrected primary-outcome rule. Neither file is changed here: the S7 execution lock and its live run are not modified mid-batch. Before formal analysis after run completion, a versioned, reviewable post-lock analysis patch must read verifier `passed` directly and record its own hash; no formal S7 result has been produced by the legacy summarizer.

The revised process-hypothesis document is [`s7_process_hypothesis_revision_20261010.md`](s7_process_hypothesis_revision_20261010.md). It makes validation-after-last-edit the sole primary process hypothesis, demotes rewrite/loop directions to secondary descriptive hypotheses, declares the explicit-reference prediction, and restricts v1 versus C1 to task-paired `test_in` using verifier pass.

## Addendum: L3b transition table and exact small-sample checks

The table below restricts the transition analysis to A-layer trajectories whose
write-only replay provides a call-32 partial score. “Already pass at 32” means
that replayed verifier partial equals 1.0; “not pass at 32” is strictly below
1.0. Final outcome always uses the frozen verifier's boolean `passed` field.

| Call-32 status | Baseline | L3b |
|---|---:|---:|
| Reached call 32 (A layer) | 9 | 12 |
| Already pass at call 32 | 2 | 5 |
| Not pass at call 32 | 7 | 6 |
| Call-32 replay unavailable | 0 | 1 |
| Final pass among not-pass-at-32 | 0/7 | 1/6 |

For transparency, all comparisons use two-sided Fisher exact tests and exact
Clopper--Pearson 95% intervals for each condition's proportion. These are
descriptive uncertainty summaries, not effect claims.

| Comparison: final verifier pass | Baseline, exact 95% CI | L3b, exact 95% CI | Fisher two-sided p |
|---|---:|---:|---:|
| A layer | 2/9 = 22.2% [2.8%, 60.2%] | 6/12 = 50.0% [21.0%, 79.0%] | 0.367 |
| B layer (ended before call 32) | 20/27 = 74.1% [53.4%, 89.0%] | 20/24 = 83.3% [62.4%, 95.3%] | 0.508 |
| Not pass at call 32 only | 0/7 = 0.0% [0.0%, 41.0%] | 1/6 = 16.7% [0.4%, 64.2%] | 0.462 |

Mechanism-layer composition differs materially (A-layer 2/9 versus 6/12),
while the B layer also differs. With these very small, trajectory-selected
denominators, the data cannot determine whether the reminder changes final
outcomes. The fixed reminder remains observable in 12 trajectories; no effect
claim is made.

### Why validation is both 11/12 and 9/12

The earlier 11/12 is retained as the **transport-success definition**: at
least one post-reminder `run_command` produced a successful tool execution
(`result.ok=true`), regardless of command content. The corrected 9/12 is the
stricter **validation-intent definition**: the post-reminder command text
contains one of `test`, `pytest`, `unittest`, or `py_compile`. The two excluded
trajectories only ran ad-hoc `python -c` function invocations after the
reminder; their tool transport succeeded, but they do not meet the declared
test-intent rule. Neither count asserts that a complete frozen verifier was
run by the model.

## Addendum: provider-error flag versus protocol denominator

`outcome_flags.provider_error` is an implementation-level non-exclusive flag,
not a clean transport-only outcome. In `outcomes.py`, it is set when the agent
process returns nonzero without a terminal `turn.completed`; a killed hard
timeout can therefore set it even when no endpoint error was established. The
formal runner then ORs this with `runtime.provider_error`, which is set after
all three retryable transport attempts fail.

| Run | Category | Why `provider_error` flag is true | Retries | Verifier | Primary denominator |
|---|---|---|---:|---|---|
| `...a09_header-C1-r4` | provider_error | third retry exhausted: 500 then 503/503 | 3 | fail | exclude |
| `...c02_sessions-C0-r3` | provider_error | third retry exhausted: 502/502/502 | 3 | pass | exclude |
| `...b09_phone-C0-r3` | timeout | 20-minute process-group kill; runtime absent, so nonzero exit set the broad flag | no completed runtime; two recorded failed requests before kill | fail | include as non-pass |
| `...b09_phone-C1-r4` | timeout | 20-minute process-group kill; runtime absent, so nonzero exit set the broad flag | no completed runtime/events to count | fail | include as non-pass |

Each run still receives a verifier result because the formal runner invokes the
frozen verifier against the workspace after the agent exits or is killed. Thus
the verifier may pass even for an excluded transport-exhaustion record; it is
not included in the primary numerator or denominator by protocol. The timeout
records, however, are content-level terminal outcomes and remain in the
primary denominator as failures. The prior all-flag exclusion (43/88 and
45/88) was too broad; the protocol-correct qwen values are 43/89 and 45/89.

## Addendum: llama3.1:8b zero-pass diagnosis

S4 contains 36 llama3.1:8b r2 records; the still-running S7 snapshot contains
zero llama records, so no S7 diagnosis is possible yet. In S4, all 36 final
responses were non-empty `stop` completions, all 36 runs made parseable tool
calls and wrote a file, and all 36 frozen verifiers failed. There were 130
tool calls total: 114 valid tool executions, zero invalid-JSON calls, zero
invalid-schema calls, and zero unknown-tool calls. Forty raw responses carried
tool calls; 40 assistant responses were `tool_calls`, followed by 36 terminal
`stop` responses.

There is nevertheless a concrete tool-use defect: 16 of 40 `run_command`
calls (across 13 runs) supplied `timeout_seconds: 300`, exceeding the declared
maximum of 120, and were rejected before command execution. This is an
argument-value/tool-usage mistake, not a tool-call serialization failure.
Together with edits in every trajectory and universal verifier failure, the
evidence supports a mixed diagnosis: a substantive task-solving/validation
floor is present, with avoidable tool-parameter mistakes contributing. It is
not the earlier CLI-style empty-output or unparseable-tool-call interface
failure.
