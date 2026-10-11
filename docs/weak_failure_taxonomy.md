# Weak-model failure taxonomy

> Scope: verifier-failing qwen3.5:9b runs in S4 `dev_diagnose` and
> formal S7 C0/C1. Retry-exhausted transport errors are excluded.
> The only judge labels used are `file_corruption`, `tool_misuse`, and
> `missed_constraint`, the three labels permitted as conclusion evidence
> by the human--judge agreement audit.

| Cohort | Failed runs n | Judge-covered n | File corruption | Tool misuse | Missed constraint | Other / unlabeled |
|---|---:|---:|---:|---:|---:|---:|
| S4 dev_diagnose | 8 | 0 | 0 | 0 | 0 | 8 |
| S7 C0 | 46 | 0 | 0 | 0 | 0 | 46 |
| S7 C1 | 44 | 0 | 0 | 0 | 0 | 44 |
| Combined | 98 | 0 | 0 | 0 | 0 | 98 |

Labels are non-exclusive, so the three named columns can overlap. `Other / unlabeled` means that none of the three reliable labels was present; it includes failures outside the existing blinded judge sample. No new judge request was made. Consequently, the S7 rows primarily document missing taxonomy coverage and must not be read as evidence that the three failure modes were absent.
