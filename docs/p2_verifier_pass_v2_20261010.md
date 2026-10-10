# P2 verifier-pass analysis patch

Date: 2026-10-10. Version: `verifier-pass-v2.0.0`. Primary module SHA-256:
`72b1e0b8252566ccf0f408a7c4311c939157be9d33cb016a385ea95efd218bcc`.
The hash and version are recorded in `analysis/analysis_patch_manifest.json`.

This is an analysis-only patch. It changes no execution asset or completed
record. The sole primary outcome is `verifier.json.passed`. Retry-exhausted
transport failures (`provider_error_protocol`) are excluded from the primary
numerator and denominator; sensitivity treats them as failures. Hard timeout
and max-steps records remain in the denominator.

## Tests and entry points

`python3 -m unittest analysis.test_verifier_pass_v2 -v` passes five tests:
legacy/new agreement without empty final output; divergence with empty final
output while the new result equals the verifier; provider exclusion with hard
timeout retained; A04 and b09 sensitivity views; and refusal of incomplete S7.

`harness/summarize_s7.py` now exits with an explicit error because it reads the
legacy outcome column. The versioned formal entry is
`python3 -m analysis.summarize_s7_v2`. It refuses to run unless `STATUS.md`
reports exactly 870/870 and the recorded module hash matches the file. During
this patch check, the expected refusal occurred because S7 was incomplete.

## Retained-cohort reconciliation

| Cohort | Scheduled | Protocol errors | Primary n | Legacy pass | Verifier pass | Difference |
|---|---:|---:|---:|---:|---:|---:|
| S4 | 180 | 5 | 175 | 102 | 110 | +8 |
| S5 original | 36 | 8 | 28 | 8 | 18 | +10 |
| S5 replacements | 8 | 0 | 8 | 4 | 6 | +2 |
| S5 replacement-inclusive | 36 | 0 | 36 | 12 | 24 | +12 |
| S6 baseline plus L3b | 72 | 0 | 72 | 25 | 48 | +23 |

The machine-readable table contains all-task, exclude-A04, exclude-b09, and
exclude-both views. A04 occurs in the dev cohorts; b09 is a test-only task and
therefore leaves the retained dev rows unchanged. Removing A04 changes the
denominators but not the pass numerators in these cohorts.

The current S7 audit is written only to
`data/s7_monitoring/verifier_pass_v2_interim.json`, with the literal watermark
`INTERIM MONITORING — NOT FORMAL S7 RESULTS`. It is operational monitoring,
not a condition comparison or result.
