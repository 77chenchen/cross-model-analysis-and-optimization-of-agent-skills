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
