# S7 qwen3.5:9b interim monitoring snapshot

> **Superseded for activation and outcome interpretation.** See
> [`s7_qwen_monitoring_revision_20261010.md`](s7_qwen_monitoring_revision_20261010.md)
> for the non-exclusive outcome flags, explicit/behaviour-only activation split,
> task-paired distributions, and call-32 negative-control check. This original
> snapshot is retained as a historical monitoring artifact.

Date: 2026-10-10. The qwen3.5:9b schedule is complete (330/330 cells). This
is operational monitoring only. Formal analysis remains prohibited until all
870 S7 cells complete; no condition, schedule, prompt, or metric definition
was changed in response to these figures.

## Complete outcome distribution

`final_empty` is an independent flag, not a mutually exclusive outcome.
`verifier_timeout` is zero in every condition.

| condition | n | pass | verifier fail | timeout | max steps | verifier timeout | provider error | final empty |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C0 | 90 | 19 | 19 | 1 | 6 | 0 | 1 | 52 (57.8%) |
| C1 | 90 | 20 | 17 | 1 | 10 | 0 | 1 | 53 (58.9%) |
| v1 exploratory | 60 | 24 | 9 | 0 | 5 | 0 | 0 | 27 (45.0%) |
| L3b exploratory | 90 | 28 | 23 | 0 | 4 | 0 | 3 | 39 (43.3%) |

`empty_termination` remains a legacy mutually-exclusive label and is retained
in the machine data: C0 44, C1 41, v1 22, and L3b 32. Its count differs from
`final_empty` because a run may be otherwise classified (for example timeout)
while having no final visible text.

## Process metrics (monitoring only)

| condition | mean steps | validation after last edit | mean first edit position | mean write-file rewrites | mean loops | heuristic activation | final empty |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0 | 11.82 | 64.4% | 3.81 | 2.68 | 1.06 | 70.0% | 57.8% |
| C1 | 12.92 | 37.8% | 3.63 | 4.56 | 2.26 | 65.6% | 58.9% |
| v1 exploratory | 12.30 | 76.7% | 3.40 | 3.03 | 1.27 | 98.3% | 45.0% |
| L3b exploratory | 12.17 | 45.6% | 3.72 | 2.72 | 1.10 | 61.1% | 43.3% |

Definitions are fixed in `harness/monitor_s7_metrics.py`: a write-file rewrite
is total `write_file` calls minus unique written paths; a loop is repeated
identical tool-name/arguments at least three times; activation is the existing
`skill-activation-heuristic-v1` (explicit skill reference, otherwise observed
edit plus validation, otherwise not observed). These metrics monitor runner
behavior only. They are not statistical comparisons or claims that either
exploratory condition is effective.

The machine-readable monitoring files are
`data/s7_monitoring/run_metrics.csv` and
`data/s7_monitoring/condition_monitoring.json`.
