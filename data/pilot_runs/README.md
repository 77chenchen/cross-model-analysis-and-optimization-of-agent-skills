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
