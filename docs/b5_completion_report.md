# B5 completion report

Date: 2026-10-09. This report covers protocol-required replacement and blind
review work only. It does not run L3b or any test task.

## Replacement batch

The eight immutable B3/S5 `provider_error` (HTTP 502) records were retained.
Eight fresh replacement run IDs completed sequentially at
`worker_concurrency=1`. None encountered a retryable transport failure, so
their `request_retry_count` is zero; the retry policy was unit-tested with a
synthetic 502 before use. Three replacements ended at the 40-call ceiling and
are independently labeled `max_steps_reached` while retaining the legacy
`empty_termination` label. This confirms that the new flag is not silently
merged into the old category.

| view | runs | provider errors | pass denominator | passes | pass rate |
|---|---:|---:|---:|---:|---:|
| Original S5 only | 36 | 8 | 28 | 8 | 28.6% |
| Original non-errors + eight replacements | 36 | 0 | 36 | 12 | 33.3% |

These are two reporting views, not an intervention comparison. In both views,
provider errors are excluded from the pass-rate denominator and reported by
count. The replacement-inclusive outcomes are 12 pass, 16 ordinary
empty-termination, three max-steps, and five verifier-fail.

## Blind review and human packets

A new fixed-seed sample of 24 anonymous packets was created from the 36 r2
baseline runs. The 24 LLM judge outputs passed the blinded-field and JSON
structure check. The public packet directory omits run, task, model, provider,
condition, and verifier/pass labels; the private mapping remains local and
ignored. These 24 are the only future source for reported human-vs-judge
Cohen's kappa. The prior packet set remains method-validation-only and will
not enter kappa.

## Scope and next gate

`STATUS.md` records B5 as 8/8 replacements and 24/24 judge outputs. L3b is
fully preregistered but has **0/72** runs and requires a new explicit user
approval. Test-in and test-out remain untouched.
