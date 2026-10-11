# Mechanical failure classification

> Scope: verifier-failing qwen3.5:9b runs in S4 `dev_diagnose` and
> formal S7 C0/C1; the lower comparison rows cover the three strong S7
> models. Retry-exhausted transport errors are excluded. Flags are mechanical
> and non-exclusive; a run can appear in several columns.

| Cohort | Failed runs n | No edit | Final empty | Timeout | Compile error | Max steps reached | Other terminal state |
|---|---:|---:|---:|---:|---:|---:|---:|
| S4 dev_diagnose / qwen3.5:9b | 8 | 0 | 3 | 0 | 0 | 0 | 5 |
| S7 / qwen3.5:9b / C0 | 46 | 4 | 27 | 1 | 1 | 5 | 19 |
| S7 / qwen3.5:9b / C1 | 44 | 2 | 27 | 1 | 1 | 8 | 17 |
| Combined weak target | 98 | 6 | 57 | 2 | 2 | 13 | 41 |
| S7 / gemma4:26b / C0+C1 | 39 | 1 | 1 | 0 | 0 | 1 | 38 |
| S7 / qwen3-coder-next / C0+C1 | 41 | 2 | 4 | 0 | 0 | 4 | 37 |
| S7 / qwen3.8:27b / C0+C1 | 17 | 0 | 0 | 0 | 0 | 0 | 17 |

`Other terminal state` means none of the five named terminal flags was set; it does **not** mean no verifier failure. It is intentionally separate from the named verifier checks below. No new judge request was made.

## Failed verifier checks

| Cohort | Failed verifier check | Count | Denominator (failed runs) |
|---|---|---:|---:|
| S4 dev_diagnose / qwen3.5:9b | `duplicates` | 3 | 8 |
| S4 dev_diagnose / qwen3.5:9b | `invalid` | 2 | 8 |
| S4 dev_diagnose / qwen3.5:9b | `no_mutation` | 3 | 8 |
| S4 dev_diagnose / qwen3.5:9b | `verifier_error_no_named_check` | 3 | 8 |
| S7 / qwen3.5:9b / C0 | `hidden_boundary` | 17 | 46 |
| S7 / qwen3.5:9b / C0 | `normal` | 31 | 46 |
| S7 / qwen3.5:9b / C0 | `verifier_error_no_named_check` | 7 | 46 |
| S7 / qwen3.5:9b / C1 | `hidden_boundary` | 16 | 44 |
| S7 / qwen3.5:9b / C1 | `normal` | 32 | 44 |
| S7 / qwen3.5:9b / C1 | `verifier_error_no_named_check` | 7 | 44 |
| Combined weak target | `duplicates` | 3 | 98 |
| Combined weak target | `hidden_boundary` | 33 | 98 |
| Combined weak target | `invalid` | 2 | 98 |
| Combined weak target | `no_mutation` | 3 | 98 |
| Combined weak target | `normal` | 63 | 98 |
| Combined weak target | `verifier_error_no_named_check` | 17 | 98 |
| S7 / gemma4:26b / C0+C1 | `hidden_boundary` | 9 | 39 |
| S7 / gemma4:26b / C0+C1 | `normal` | 15 | 39 |
| S7 / gemma4:26b / C0+C1 | `verifier_error_no_named_check` | 17 | 39 |
| S7 / qwen3-coder-next / C0+C1 | `hidden_boundary` | 11 | 41 |
| S7 / qwen3-coder-next / C0+C1 | `normal` | 21 | 41 |
| S7 / qwen3-coder-next / C0+C1 | `verifier_error_no_named_check` | 15 | 41 |
| S7 / qwen3.8:27b / C0+C1 | `hidden_boundary` | 5 | 17 |
| S7 / qwen3.8:27b / C0+C1 | `normal` | 3 | 17 |
| S7 / qwen3.8:27b / C0+C1 | `verifier_error_no_named_check` | 9 | 17 |

## Judge-coverage gap retained for audit

The existing 24 blinded judge packets cover none of the 98 in-scope weak-target failures. The earlier judge taxonomy therefore remains a coverage-gap observation, not a prevalence estimate. This mechanical table does not use judge labels.

## `final_empty` conditional denominators

Scope is all completed S7 C0+C1 records for qwen3.5:9b and the three strong comparison models, including any protocol provider-error records because this is a descriptive behavior rate. `verifier_pass` remains the frozen verifier field; these conditional rates are not causal estimates.

| Model | All runs n | Final empty n (%) | Pass among final-empty | Non-final-empty n | Pass among non-final-empty | Provider-error records |
|---|---:|---:|---:|---:|---:|---:|
| qwen3.5:9b | 180 | 105 (58.3%) | 50/105 (47.6%) | 75 | 39/75 (52.0%) | 2 |
| gemma4:26b | 108 | 2 (1.9%) | 1/2 (50.0%) | 106 | 68/106 (64.2%) | 0 |
| qwen3.8:27b | 108 | 0 (0.0%) | 0/0 (NA) | 108 | 91/108 (84.3%) | 0 |
| qwen3-coder-next | 108 | 7 (6.5%) | 3/7 (42.9%) | 101 | 64/101 (63.4%) | 0 |

## `final_empty` conditional denominators

Scope is all completed S7 C0+C1 records for qwen3.5:9b and the three strong comparison models, including any protocol provider-error records because this is a descriptive behavior rate. `verifier_pass` remains the frozen verifier field; these conditional rates are not causal estimates.

| Model | All runs n | Final empty n (%) | Pass among final-empty | Non-final-empty n | Pass among non-final-empty | Provider-error records |
|---|---:|---:|---:|---:|---:|---:|
| qwen3.5:9b | 180 | 105 (58.3%) | 50/105 (47.6%) | 75 | 39/75 (52.0%) | 2 |
| gemma4:26b | 108 | 2 (1.9%) | 1/2 (50.0%) | 106 | 68/106 (64.2%) | 0 |
| qwen3.8:27b | 108 | 0 (0.0%) | 0/0 (NA) | 108 | 91/108 (84.3%) | 0 |
| qwen3-coder-next | 108 | 7 (6.5%) | 3/7 (42.9%) | 101 | 64/101 (63.4%) | 0 |
