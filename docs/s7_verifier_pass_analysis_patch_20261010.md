# Formal S7 verifier-pass analysis patch

Date: 2026-10-10. This post-run analysis patch is prepared before formal S7
analysis and is independent of the locked live runner. It does not alter the
execution lock or produce a formal result from the incomplete S7 cohort.

## Source and primary rule

The patch is [`summarize_s7_verifier_pass.py`](../harness/summarize_s7_verifier_pass.py).
Its primary outcome is only `verifier.json.passed == true`. It reads each run's
metadata, frozen verifier result, and (when present) `runtime_r2.json` directly;
it never uses the legacy `outcome_category` as a pass source.

`provider_error_protocol` is a derived field for retry-exhausted request
transport (`outcome_category == provider_error` or `runtime.provider_error`).
Those records are excluded from the primary denominator. The retained broad
`outcome_flags.provider_error` is legacy diagnostic data only: a killed hard
timeout may carry it and remains a denominator failure. The report also emits
the provider-as-non-pass sensitivity denominator.

## Version and regression tests

At preparation, the patch SHA-256 is
`d9b76ff452ceefa50c8788013386001340cd3485a3f91373333344cd06c90406`.
It is recorded again in every summary it emits. Run:

```sh
python3 -m unittest discover -s tests -v
```

The two regression fixtures establish that (1) on a normal non-empty-final
record the legacy and verifier pass values agree, and (2) on an empty-final
record labelled legacy `empty_termination`, the new result equals the frozen
verifier field and differs from legacy pass. The test suite passed at patch
preparation. A future source edit necessarily changes the recorded hash and
requires rerunning these tests before formal analysis.

## Outputs

The patch produces task × condition pass distributions and the pre-registered
task-level paired C1-minus-C0 bootstrap summary. It retains legacy-pass and
final-empty counts only for reconciliation. All formal results also receive a
with/without-`test_in_b09_phone` task sensitivity presentation.
