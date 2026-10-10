# B5-r2 blinded human--LLM-judge agreement results

Date: 2026-10-10. These results follow the pre-registered scoring procedure in
`docs/b5_r2_human_kappa_protocol_20261010.md`. The input passed
`harness/check_b5_r2_human_review.py`: 24 unique blinded packets, each with a
valid failure-mode-only annotation. No packet was marked unscorable.

The machine-readable result is
`data/b5_r2_human_review_results.json`, reproduced by:

```sh
python3 harness/score_b5_r2_human_review.py
```

## Summary

There were 24 scorable human--LLM-judge pairs. Macro Cohen's kappa across the
five labels with non-zero variance was 0.588 (10,000-draw packet bootstrap 95%
interval: 0.434--0.771). Macro PABAK across all eight labels was 0.677
(0.552--0.781). Exact eight-label-set agreement was 25.0% (8.3%--41.7%).

| failure mode | observed agreement | kappa | bootstrap 95% interval | PABAK |
|---|---:|---:|---:|---:|
| premature implementation | 100.0% | not estimable | -- | 1.000 |
| repeated exploration | 70.8% | not estimable | -- | 0.417 |
| ineffective debugging loop | 66.7% | 0.226 | 0.071--0.538 | 0.333 |
| insufficient validation | 70.8% | 0.425 | 0.057--0.750 | 0.417 |
| missed constraint | 83.3% | 0.676 | 0.385--0.917 | 0.667 |
| premature completion | 91.7% | not estimable | -- | 0.833 |
| tool misuse | 91.7% | 0.780 | 0.429--1.000 | 0.833 |
| file corruption | 95.8% | 0.833 | 0.467--1.000 | 0.917 |

Kappa is not estimable for premature implementation, repeated exploration, or
premature completion because at least one rater has zero variance for that
label. They are excluded from macro kappa as pre-specified; PABAK remains
reported. Some bootstrap draws also have zero variance, so each per-label
kappa interval records only estimable resamples in the JSON result.

## Interpretation and limits

This is an audit of a single LLM judge against one human researcher, not
independent inter-annotator reliability. The sample is fixed and small (24
packets), task text and behavioral traces prevent complete blinding, and the
intervals are consequently wide. `empty_termination` remains a mechanical
terminal-log flag outside the human label set and outside all agreement
statistics. These values support reporting the judge's labels descriptively;
they do not validate those labels as ground truth.
