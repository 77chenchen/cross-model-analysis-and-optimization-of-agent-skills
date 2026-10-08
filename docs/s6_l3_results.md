# S6 L3 dev-validate result

The independent L3 runtime condition ran gemma4:26b on each of the six locked
`dev_validate` tasks three times (18 new observations). The matched S5 v0
reference has the same model, task set, and repetition count, but consists of
independent fresh samples.

| condition | runs | passes | pass rate | mean partial score |
|---|---:|---:|---:|---:|
| S5 v0 | 18 | 13 | 0.722 | 0.889 |
| S6 L3 | 18 | 15 | 0.833 | 0.944 |

L3's no-edit or compile-failure repair branch fired in **0/18** runs. Thus the
pass-rate difference is an unpaired difference between fresh samples, not
evidence that L3 caused an improvement: the intervention's intended mechanism
was never activated. A04 remained 0/3 pass with partial score 2/3 under both
conditions.

Decision: there is no mechanism-tested, observable L3 uplift on dev-validate.
Do not proceed to S7 from this condition. Retain the result and redesign a
separately pre-specified guardrail only if future dev-diagnose evidence shows
an activation opportunity.
