# S8-b fresh-task mechanism study: results

S8-b was a development-only study on 24 newly authored and independently
admitted repository-repair tasks. It used one target model (`qwen3.5:9b`), four
interleaved prompt conditions, and two repetitions per task (192 scheduled
runs). This study does not replace or revise the held-out cross-model result.

## Primary outcome

The primary outcome is `verifier.json.passed`. Retry-exhausted transport
errors are excluded from the primary numerator and denominator; timeouts and
step-limit outcomes remain failures. Repetitions were averaged within each
task-condition cell before the fixed-seed, 10,000-draw paired bootstrap.

| Condition | Passed / usable | Pass rate | 95% Wilson interval | Difference vs. generic control | 95% task-paired bootstrap interval |
|---|---:|---:|---:|---:|---:|
| C1 (v0 skill) | 27/44 | 61.4% | [46.6%, 74.3%] | +6.25 pp | [−8.33, +20.83] pp |
| Externalized process | 25/47 | 53.2% | [39.2%, 66.7%] | 0.00 pp | [−18.75, +18.75] pp |
| Imitation process | 26/45 | 57.8% | [43.3%, 71.0%] | +4.17 pp | [−10.42, +20.83] pp |
| Length-matched generic control | 26/47 | 55.3% | [41.2%, 68.6%] | reference | reference |

None of the three pre-specified contrasts met the efficacy rule because every
paired interval included zero. The scheduled-run sensitivity, which counts
retry-exhausted provider errors as failures, yields rates of 56.3%, 52.1%,
54.2%, and 54.2%, respectively.

## Process measures

Relative to the generic control, the externalized-process condition changed
task-paired validation after the last edit by +10.4 percentage points (95%
paired-bootstrap interval [−4.2, +25.0]) and post-edit rereading by +31.3
points ([+14.6, +47.9]). The imitation condition changed rereading by +18.8
points ([0.0, +35.4]) and validation by −2.1 points ([−18.8, +14.6]). C1
changed those measures by −10.4 points ([−29.2, +6.3]) and −18.8 points
([−37.5, 0.0]), respectively.

The locked activation parser classified nearly every usable run as activated,
including 46/47 generic-control runs. It therefore did not distinguish prompt
conditions in this cohort. The process measures above are mechanical
trajectory summaries, not evidence that the model explicitly followed the
supplied instruction.

## Interpretation

The fresh-task study reproduces the separation between visible workflow and
verified correctness. Externalizing the requested sequence increased
post-edit rereading, but its task-paired pass difference from the
length-matched generic control was exactly 0.0 percentage points. Imitation
also increased rereading without a paired interval excluding zero for pass.
Because this is a development-only, one-model study with two repetitions per
cell, the estimates describe this task pool and are not a new held-out claim.

Source tables: [`results/tables/s8b/`](../results/tables/s8b/). Publication
figure: [`paper/figures/s8b_mechanism.pdf`](../paper/figures/s8b_mechanism.pdf).
