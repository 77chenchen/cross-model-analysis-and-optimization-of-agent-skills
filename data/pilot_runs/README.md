# Pilot execution log

`pilot_a01_label_parser` is a calibration task, not a formal benchmark task. All six target models were run once with Skill A v0 and an externally owned hidden verifier.

| Model | External verifier | Events | Completed shell commands |
|---|---|---:|---:|
| `gpt-5.6-sol` | pass | 24 | 7 |
| `qwen3.8:27b` | pass | 14 | 4 |
| `qwen3.5:9b` | fail | 19 | 5 |
| `gemma4:26b` | pass | 19 | 7 |
| `llama3.1:8b` | fail | 5 | 0 |
| `qwen3-coder-next` | pass | 29 | 8 |

The verifier admission checks were executed separately: a correct fixture passed, while the immutable buggy seed and a shortcut fixture both failed. This single calibration task suggests a useful capability gradient, but task-level evidence requires the remaining pilot pool before setting formal difficulty.

## Runner smoke run

`pilot_a02_config_parser` was run once on `qwen3.5:9b` through the generic
pilot runner. The external verifier failed; the run is retained with raw
trajectory, normalized actions, hashes, and verifier output. Its purpose is
to confirm that failed outcomes are recorded rather than dropped, so it is
not a cross-model result or a formal comparison.

The retry of A02 on the same model also failed the external verifier. Both
timestamped run directories are retained; neither is overwritten. In contrast,
the first B01 run on `qwen3.8:27b` passed all external checks. These are
single-run calibration observations only.

## D5 paired pilot comparison (2026-10-07)

Eight fresh qwen3.5:9b calibration runs compared frozen Skill A/B `v0` and
the D4 `v1` intervention across A03, A05, B03, and B05. Every external
verifier failed (v0: 0/4; v1: 0/4), and every trajectory ended normally.
The matrix TSV and constrained descriptive summary are retained in
`data/diagnostics/d5_qwen35_20261007/`; this is not a formal result or an
efficacy conclusion.

## D2 weak-model pilot batch (2026-10-07)

Four single runs on exact SoC model ID `qwen3.5:9b` (provider `soclaas`),
each with frozen Skill protocol v0 injected by the runner. Calibration
only; no cross-model ranking or formal benchmark claim.

| Task | External verifier | Run directory |
|---|---|---|
| `pilot_a03_record_deduplication` | fail | `pilot_a03_record_deduplication__qwen3.5_9b__20261007T022548Z` |
| `pilot_a05_version_parser` | fail | `pilot_a05_version_parser__qwen3.5_9b__20261007T022857Z` |
| `pilot_b03_duplicate_audit` | fail | `pilot_b03_duplicate_audit__qwen3.5_9b__20261007T023034Z` |
| `pilot_b05_date_validation` | fail | `pilot_b05_date_validation__qwen3.5_9b__20261007T023106Z` |

No infrastructure interruptions: all four trajectories end in
`turn.completed`, and no rerun was required. All failed outcomes are
retained unmodified.
