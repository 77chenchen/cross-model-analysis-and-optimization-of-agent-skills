| Scope | Model | Condition | Scheduled | Retry-exhausted provider errors | Primary n | Verifier pass | Pass rate | Wilson 95% interval | Task-paired C1-C0 | Paired-bootstrap 95% interval |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| All runs as recorded | Ornith1.5 35B | C0 | 54 | 2 | 52 | 45 | 86.5% | [74.7%, 93.3%] | — | — |
| All runs as recorded | Ornith1.5 35B | C1 | 54 | 2 | 52 | 44 | 84.6% | [72.5%, 92.0%] | -1.9 pp | [-16.7, 9.3] pp |
| Exclude `test_out_c02_sessions` | Ornith1.5 35B | C0 | 51 | 1 | 50 | 43 | 86.0% | [73.8%, 93.0%] | — | — |
| Exclude `test_out_c02_sessions` | Ornith1.5 35B | C1 | 51 | 2 | 49 | 41 | 83.7% | [71.0%, 91.5%] | -2.0 pp | [-17.6, 9.8] pp |

Primary denominators exclude only retry-exhausted provider errors. The paired contrast aggregates repetitions within tasks and uses the frozen 10,000-draw task bootstrap. Three of the six Ornith records for `test_out_c02_sessions` carried a task-tree hash that did not match the frozen seed; the sensitivity view excludes all six records from that task. The direction and interpretation are unchanged.
