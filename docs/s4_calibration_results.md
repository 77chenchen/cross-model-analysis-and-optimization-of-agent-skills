# S4 calibration results

Descriptive calibration only: frozen Skill v0, 12 frozen pilot tasks, and three fresh runs per model-task condition (216 runs total). Tasks—not repeats—are the intended statistical unit. Temperature and seed could not be set through the current CLI; costs are null because a verified provider price card was unavailable.

| Model | Runs | Passes | Pass rate | Mean partial score | Outcome counts | Tasks with 20%–80% pass rate |
|---|---:|---:|---:|---:|---|---:|
| `gemma4:26b` | 36 | 27 | 0.750 | 0.889 | `{'empty_termination': 3, 'pass': 27, 'verifier_fail': 6}` | 5/12 |
| `gpt-5.6-sol` | 36 | 33 | 0.917 | 0.972 | `{'pass': 33, 'verifier_fail': 3}` | 0/12 |
| `llama3.1:8b` | 36 | 0 | 0.000 | 0.153 | `{'verifier_fail': 36}` | 0/12 |
| `qwen3-coder-next` | 36 | 32 | 0.889 | 0.940 | `{'pass': 32, 'verifier_fail': 4}` | 1/12 |
| `qwen3.5:9b` | 36 | 0 | 0.000 | 0.174 | `{'empty_termination': 35, 'verifier_fail': 1}` | 0/12 |
| `qwen3.8:27b` | 36 | 33 | 0.917 | 0.972 | `{'pass': 33, 'verifier_fail': 3}` | 0/12 |

## Calibration decision

`gemma4:26b` is the recommended primary weak target for the next dev-only phase: it has 5/12 task conditions with observed pass rates from 20% to 80%, while retaining a 0.750 aggregate pass rate and a 0.889 mean partial score. This is a calibration selection, not a cross-model ranking.

`qwen3.5:9b` is at a floor on this pool: 0/36 passes, with 35/36 recorded as `empty_termination` and one `verifier_fail`. Skill text alone is unlikely to resolve that operational termination pattern; retain it only as a documented floor condition or use a simpler pool / runtime-guardrail condition. `llama3.1:8b` is also at a floor (0/36), but its failures are all `verifier_fail`, not empty terminations.

The full task-by-model descriptive table is `data/calibration_runs/s4_model_task_summary.csv`; individual-run values, including tokens and action counts, are in `s4_run_table.csv`.
