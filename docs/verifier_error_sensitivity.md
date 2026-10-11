# Verifier no-named-check sensitivity

This local-only sensitivity excludes eligible runs where `verifier.json` has no named checks and `passed` is false. It does not replace the preregistered primary outcome, which retains such runs as failures.

## Composition

Categories are mutually exclusive within the no-named-check subset. `verifier_exception_or_abnormal_exit` is a nonempty verifier error not matching timeout or parsing patterns; no non-zero agent-process exits were observed in this subset, so the non-zero entries are verifier exceptions. `output_unparseable` uses a literal parse/decode marker in that error. Zero values are retained for clarity.

| Model | Condition | Eligible n | Verifier timeout | Verifier exception / abnormal exit | Output unparseable | No named check, passed=false | Total excluded |
|---|---|---:|---:|---:|---:|---:|---:|
| qwen3.5:9b | C0 | 89 | 0 | 4 | 0 | 1 | 5 |
| qwen3.5:9b | C1 | 89 | 0 | 4 | 0 | 1 | 5 |
| gemma4:26b | C0 | 54 | 0 | 6 | 0 | 0 | 6 |
| gemma4:26b | C1 | 54 | 0 | 5 | 0 | 0 | 5 |
| qwen3.8:27b | C0 | 54 | 0 | 2 | 0 | 0 | 2 |
| qwen3.8:27b | C1 | 54 | 0 | 2 | 0 | 0 | 2 |
| qwen3-coder-next | C0 | 54 | 0 | 4 | 0 | 0 | 4 |
| qwen3-coder-next | C1 | 54 | 0 | 5 | 0 | 0 | 5 |
| llama3.1:8b | C0 | 54 | 0 | 0 | 0 | 0 | 0 |
| llama3.1:8b | C1 | 54 | 0 | 0 | 0 | 1 | 1 |
| gpt-5.6-sol | C0 | 54 | 0 | 2 | 0 | 0 | 2 |
| gpt-5.6-sol | C1 | 54 | 0 | 3 | 0 | 0 | 3 |

## Sensitivity pass rates and task-paired difference

The condition rows give verifier-pass rates after the exclusion. The difference row averages within-task C1-minus-C0 repeat pass rates over tasks with at least one retained run in both conditions; its interval is a fixed-seed 10,000-draw paired bootstrap and is descriptive.

| Model | Row | Primary n | Excluded | Sensitivity n | Pass n | Pass rate | C1-C0 task pp [95% bootstrap] |
|---|---|---:|---:|---:|---:|---:|---|
| qwen3.5:9b | C0 | 89 | 5 | 84 | 43 | 51.2% | |
| qwen3.5:9b | C1 | 89 | 5 | 84 | 45 | 53.6% | |
| qwen3.5:9b | C1-C0 paired tasks (n=18) | | | | | | +0.9 [-8.9, +10.0] |
| gemma4:26b | C0 | 54 | 6 | 48 | 33 | 68.8% | |
| gemma4:26b | C1 | 54 | 5 | 49 | 36 | 73.5% | |
| gemma4:26b | C1-C0 paired tasks (n=16) | | | | | | +6.2 [+0.0, +16.7] |
| qwen3.8:27b | C0 | 54 | 2 | 52 | 45 | 86.5% | |
| qwen3.8:27b | C1 | 54 | 2 | 52 | 46 | 88.5% | |
| qwen3.8:27b | C1-C0 paired tasks (n=18) | | | | | | +1.9 [-3.7, +7.4] |
| qwen3-coder-next | C0 | 54 | 4 | 50 | 33 | 66.0% | |
| qwen3-coder-next | C1 | 54 | 5 | 49 | 34 | 69.4% | |
| qwen3-coder-next | C1-C0 paired tasks (n=17) | | | | | | +3.9 [-7.8, +17.6] |
| llama3.1:8b | C0 | 54 | 0 | 54 | 0 | 0.0% | |
| llama3.1:8b | C1 | 54 | 1 | 53 | 0 | 0.0% | |
| llama3.1:8b | C1-C0 paired tasks (n=18) | | | | | | +0.0 [+0.0, +0.0] |
| gpt-5.6-sol | C0 | 54 | 2 | 52 | 44 | 84.6% | |
| gpt-5.6-sol | C1 | 54 | 3 | 51 | 44 | 86.3% | |
| gpt-5.6-sol | C1-C0 paired tasks (n=17) | | | | | | +2.0 [+0.0, +5.9] |
