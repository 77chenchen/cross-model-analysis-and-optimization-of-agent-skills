# Behavior--outcome cross-tab

> Scope: S4 `dev_diagnose`, v0 only; descriptive and post hoc. Strong is
> gemma4:26b, qwen3.8:27b, and qwen3-coder-next; weak is qwen3.5:9b.
> The outcome is `verifier.json.passed`. Retry-exhausted provider errors
> are excluded from the primary cells.

| Mechanical behavior | Strong pass | Strong fail | Weak pass | Weak fail |
|---|---:|---:|---:|---:|
| Read before edit | 47/47 (100.0%) | 6/6 (100.0%) | 10/10 (100.0%) | 8/8 (100.0%) |
| Validation after last edit (intent) | 33/47 (70.2%) | 6/6 (100.0%) | 3/10 (30.0%) | 5/8 (62.5%) |
| Avoid repeated full-file write | 36/47 (76.6%) | 5/6 (83.3%) | 8/10 (80.0%) | 6/8 (75.0%) |
| Reread after last edit | 12/47 (25.5%) | 3/6 (50.0%) | 2/10 (20.0%) | 4/8 (50.0%) |

## Mechanical definitions

- **Read before edit:** a successful `read_file` occurs before the first successful `write_file`.
- **Validation after last edit (intent):** after the last successful `write_file`, a `run_command` argument matches the frozen validation-intent rule (`test`, `pytest`, `unittest`, `py_compile`, or a Python invocation of a `.py` file). Command success is not required by this intent indicator.
- **Avoid repeated full-file write:** the run edits at least once and no path receives more than one successful `write_file`. A no-edit run is not credited.
- **Reread after last edit:** a successful `read_file` occurs after the last successful `write_file`.

The table contains 71 usable runs; 1 retry-exhausted provider-error run(s) were excluded.
The four cells are observational strata, not randomized conditions, so their differences are mechanism descriptions rather than effect estimates.
